import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import payments_gateway
import bold_gateway

router = APIRouter(prefix="/payments", tags=["Payments"])

# Bold (datáfono) → método que usamos en el reporte de caja.
BOLD_TO_METHOD = {
    "POS": "datafono",
    "NEQUI": "nequi",
    "DAVIPLATA": "daviplata",
    "PAY_BY_LINK": "card",
}

# Métodos que el cliente puede elegir en la app.
VALID_METHODS = ["bre_b", "nequi", "card"]

# Métodos manuales (los registra la cocina al cerrar el pedido).
# El cliente paga por su cuenta (transferencia/efectivo) y la cocina solo MARCA cuál fue.
VALID_MANUAL_METHODS = ["efectivo", "datafono", "nequi", "daviplata", "bre_b"]


# POST /payments — inicia el cobro de un pedido.
@router.post("/", response_model=schemas.PaymentInitOut)
def create_payment(payload: schemas.PaymentCreate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if payload.method is not None and payload.method not in VALID_METHODS:
        raise HTTPException(status_code=400, detail=f"Payment method '{payload.method}' is invalid.")

    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order is already paid")

    # SEGURIDAD: el monto sale del pedido (servidor), nunca del cliente.
    amount = order.total

    payment = models.Payment(
        order_id=order.id,
        amount=amount,
        method=payload.method,
        provider="bold",
        status="pending",
    )
    db.add(payment)
    db.flush()  # asigna id sin commit

    # Pedirle a la pasarela el cobro (stub mock por ahora) y guardar su referencia.
    charge = payments_gateway.create_charge(order_id=order.id, amount=amount, method=payload.method)
    payment.provider_ref = charge["provider_ref"]

    db.commit()
    db.refresh(payment)

    # Respuesta = los datos del pago + el QR dinámico para mostrar en pantalla.
    return schemas.PaymentInitOut(
        **schemas.PaymentOut.model_validate(payment).model_dump(),
        qr_url=charge["qr_url"],
    )


# POST /payments/manual — registrar pago en efectivo o datáfono (lo marca la cocina al cerrar).
@router.post("/manual", response_model=schemas.PaymentOut)
def create_manual_payment(payload: schemas.ManualPaymentCreate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if payload.method not in VALID_MANUAL_METHODS:
        raise HTTPException(status_code=400, detail=f"Manual method '{payload.method}' is invalid.")

    # No duplicar: si el pedido ya tiene un pago aprobado, no se registra otro.
    existing = (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order.id, models.Payment.status == "approved")
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Order already has an approved payment")

    payment = models.Payment(
        order_id=order.id,
        amount=order.total,   # SEGURIDAD: el monto sale del pedido, no del cliente
        method=payload.method,
        provider="manual",
        status="approved",    # un pago manual entra ya confirmado
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


# POST /payments/bold — inicia un cobro en el datáfono de Bold.
@router.post("/bold", response_model=schemas.BoldCheckoutOut)
def create_bold_payment(payload: schemas.BoldCheckoutCreate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if payload.payment_method not in BOLD_TO_METHOD:
        raise HTTPException(status_code=400, detail=f"Bold payment method '{payload.payment_method}' is invalid.")

    already = (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order.id, models.Payment.status == "approved")
        .first()
    )
    if already:
        raise HTTPException(status_code=400, detail="Order already has an approved payment")

    reference = str(uuid.uuid4())  # UUID único por orden → con esto casa el webhook
    payment = models.Payment(
        order_id=order.id,
        amount=order.total,                      # SEGURIDAD: el monto sale del pedido
        method=BOLD_TO_METHOD[payload.payment_method],
        provider="bold",
        status="pending",
        provider_ref=reference,
    )
    db.add(payment)
    db.flush()

    try:
        result = bold_gateway.create_checkout(
            total_amount=order.total,
            payment_method=payload.payment_method,
            reference=reference,
            user_email=payload.user_email,
        )
    except bold_gateway.BoldError as e:
        db.rollback()  # no guardamos un cobro que Bold rechazó al iniciar
        raise HTTPException(status_code=400, detail={"bold_error": e.detail})

    db.commit()
    db.refresh(payment)
    return schemas.BoldCheckoutOut(
        **schemas.PaymentOut.model_validate(payment).model_dump(),
        integration_id=result["integration_id"],
    )


# POST /payments/bold/webhook — Bold nos avisa el resultado del datáfono.
@router.post("/bold/webhook")
def bold_webhook(event: schemas.BoldWebhook, request: Request, db: Session = Depends(get_db)):
    # TODO seguridad: validar la FIRMA del webhook de Bold en sandbox/prod (el mock no firma).
    payment = (
        db.query(models.Payment)
        .filter(models.Payment.provider_ref == event.reference)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # IDEMPOTENCIA: el webhook puede llegar repetido; si ya está aprobado, no repetimos.
    if payment.status == "approved":
        return {"status": "already_processed"}

    if event.status == "APPROVED":
        payment.status = "approved"
    elif event.status == "REJECTED":
        payment.status = "declined"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown webhook status '{event.status}'")

    db.commit()
    return {"status": payment.status}


# POST /payments/webhook — la pasarela nos avisa el resultado del pago.
@router.post("/webhook")
def payment_webhook(event: schemas.PaymentWebhook, request: Request, db: Session = Depends(get_db)):
    # SEGURIDAD: validar la firma para que nadie falsifique un "pagado".
    if not payments_gateway.verify_webhook_signature(request.headers, event):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.provider_ref == event.provider_ref)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # IDEMPOTENCIA: el webhook puede llegar dos veces; si ya está aprobado, no repetimos.
    if payment.status == "approved":
        return {"status": "already_processed"}

    if event.status == "approved":
        # El pago es una pista APARTE del flujo de cocina (pago ≠ estado del pedido).
        # Solo marcamos el pago aprobado; el "pagado" se deriva de aquí (Order.is_paid).
        payment.status = "approved"
    elif event.status == "declined":
        payment.status = "declined"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown webhook status '{event.status}'")

    db.commit()
    return {"status": payment.status}


# GET /payments/{order_id}/status — respaldo: la pantalla consulta el estado del pago.
@router.get("/{order_id}/status", response_model=schemas.PaymentOut)
def payment_status(order_id: int, db: Session = Depends(get_db)):
    payment = (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order_id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

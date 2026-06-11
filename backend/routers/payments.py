from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import payments_gateway

router = APIRouter(prefix="/payments", tags=["Payments"])

# Métodos que el cliente puede elegir.
VALID_METHODS = ["bre_b", "nequi", "card"]


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
        payment.status = "approved"
        order = db.query(models.Order).filter(models.Order.id == payment.order_id).first()
        if order:
            order.status = "paid"  # ← solo aquí el pedido pasa a pagado
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

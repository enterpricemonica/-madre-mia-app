"""
Adaptador de la pasarela de pago.

POR AHORA es un STUB (mock) de Bold: genera datos falsos para poder construir
y probar todo el flujo sin el sandbox real. Cuando lleguen las credenciales de
Bold, se cambia SOLO este archivo (crear el cobro real vía su API y validar la
firma real del webhook) — el router no se toca.
"""
import uuid


def create_charge(order_id: int, amount: int, method: str | None) -> dict:
    """Crea un cobro en la pasarela y devuelve su referencia + el QR a mostrar.

    STUB: inventa una referencia y una URL de QR.
    REAL (futuro): POST a la API de Bold con el monto y el método.
    """
    provider_ref = f"mock-{order_id}-{uuid.uuid4().hex[:8]}"
    return {
        "provider_ref": provider_ref,
        "qr_url": f"https://sandbox.bold.example/qr/{provider_ref}",
    }


def verify_webhook_signature(headers, event) -> bool:
    """Valida la firma del webhook para que nadie pueda falsificar un 'pagado'.

    STUB: acepta todo.
    REAL (futuro): validar la firma que firma Bold/Wompi en el evento.
    """
    return True

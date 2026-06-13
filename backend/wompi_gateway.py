"""
Adapter de Wompi (pago online: el cliente paga desde su celular).

Por ahora solo contiene la **firma de integridad**: el hash que Wompi exige para
aceptar un cobro y así nadie pueda alterar el monto en el camino. Toda la config
sale del `.env` (URL, llaves, secretos) → se cambia entre sandbox / producción sin
tocar el código.

Más adelante (siguiente paso) este módulo también preparará el cobro y consultará
la transacción (`GET /transactions/<id>`).
"""
import hashlib
import hmac
import os

import httpx


class WompiError(Exception):
    """Error al hablar con Wompi (ej. transacción no encontrada). Lleva status y detalle."""

    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Wompi error {status_code}: {detail}")


def integrity_signature(
    reference: str,
    amount_in_cents: int,
    currency: str = "COP",
    secret: str | None = None,
) -> str:
    """Calcula la firma de integridad que pide Wompi para un cobro.

    Wompi la define como el SHA-256 de cuatro cosas **pegadas sin separador**:
        <referencia><monto_en_centavos><moneda><secreto_de_integridad>

    Sirve para que el monto no se pueda alterar entre el celular y Wompi: si alguien
    cambia el monto, la firma deja de cuadrar y Wompi rechaza el cobro.

    SEGURIDAD: el `secret` vive solo en el backend (nunca en el frontend). Por eso
    esta función corre en el servidor. Por defecto lo lee del `.env`; el parámetro
    `secret` existe para poder testear con el ejemplo oficial de la doc.
    """
    secret = secret or os.getenv("WOMPI_INTEGRITY_SECRET", "")
    payload = f"{reference}{amount_in_cents}{currency}{secret}"
    return hashlib.sha256(payload.encode()).hexdigest()


def prepare_checkout(reference: str, amount_cop: int, currency: str = "COP") -> dict:
    """Arma (y firma) los datos que el front necesita para abrir el Widget de Wompi.

    OJO — a diferencia de Bold, esto NO llama a Wompi por red. El Widget se abre en
    el celular del cliente con estos parámetros; Wompi crea la transacción cuando el
    cliente paga. La verificación contra Wompi viene después (GET /transactions/<id>).

    - `amount_cop` viene en PESOS (como guardamos los totales). Aquí lo pasamos a
      CENTAVOS (×100), que es lo que Wompi exige.
    - La firma se calcula con el monto YA en centavos (si no, no cuadra).

    SEGURIDAD: el monto y la referencia los pone el servidor (desde el pedido), no el
    cliente. Así nadie paga menos de lo que debe.
    """
    amount_in_cents = amount_cop * 100
    return {
        "public_key": os.getenv("WOMPI_PUBLIC_KEY", ""),
        "currency": currency,
        "amount_in_cents": amount_in_cents,
        "reference": reference,
        "signature": integrity_signature(reference, amount_in_cents, currency),
    }


def get_transaction(transaction_id: str) -> dict:
    """Consulta una transacción en Wompi — la FUENTE DE VERDAD del pago.

    Después de que el cliente paga, no confiamos en lo que diga el celular: le
    preguntamos a Wompi directamente "¿esta transacción quedó aprobada?".

    Devuelve el objeto `data` de Wompi (trae `status`, `reference`, `amount_in_cents`).
    `status` puede ser: APPROVED / DECLINED / VOIDED / ERROR / PENDING.
    Si Wompi responde con error (ej. no existe), lanza WompiError.
    """
    api_url = os.getenv("WOMPI_API_URL", "https://sandbox.wompi.co/v1")
    private_key = os.getenv("WOMPI_PRIVATE_KEY", "")

    response = httpx.get(
        f"{api_url}/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {private_key}"},
        timeout=15,
    )

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise WompiError(response.status_code, detail)

    return response.json()["data"]


def verify_event_signature(event: dict, secret: str | None = None) -> bool:
    """Verifica que un webhook de Wompi sea AUTÉNTICO (que de verdad lo mandó Wompi).

    Wompi firma así: concatena, EN ORDEN, los valores de los campos listados en
    `signature.properties` (rutas dentro de `data`, ej. "transaction.status"),
    luego el `timestamp`, luego el SECRETO DE EVENTOS, y le saca SHA-256.

    OJO: las `properties` se leen del evento cada vez — NO se hardcodean (Wompi avisa
    que pueden cambiar). Si alguien altera el monto o el estado sin el secreto, el
    checksum deja de cuadrar y rechazamos el evento.
    """
    secret = secret or os.getenv("WOMPI_EVENTS_SECRET", "")
    try:
        signature = event["signature"]
        properties = signature["properties"]
        checksum = signature["checksum"]
        data = event["data"]

        parts = []
        for prop in properties:           # ej. "transaction.status"
            value = data
            for key in prop.split("."):   # navega data["transaction"]["status"]
                value = value[key]
            parts.append(str(value))

        payload = "".join(parts) + str(event["timestamp"]) + secret
    except (KeyError, TypeError):
        return False  # evento malformado → no es válido

    computed = hashlib.sha256(payload.encode()).hexdigest()
    # compare_digest = comparación de tiempo constante (no filtra info por timing)
    return hmac.compare_digest(computed.lower(), str(checksum).lower())

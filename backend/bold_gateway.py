"""
Adapter de Bold (API Integrations / datáfono).

Le habla a Bold para iniciar un cobro en el datáfono. Toda la config sale del
`.env` (URL, llave, datáfono) → se cambia entre **mock / sandbox / producción**
sin tocar el código. Por defecto apunta al mock local (puerto 9000).
"""
import os

import httpx


class BoldError(Exception):
    """Error devuelto por Bold (AP00x). Lleva el status y el detalle."""

    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Bold error {status_code}: {detail}")


def _config():
    return {
        "url": os.getenv("BOLD_API_URL", "http://localhost:9000"),
        "key": os.getenv("BOLD_API_KEY", "mock-key"),
        "terminal_model": os.getenv("BOLD_TERMINAL_MODEL", "BOLD_S1"),
        "terminal_serial": os.getenv("BOLD_TERMINAL_SERIAL", "MOCK-0001"),
    }


def create_checkout(
    total_amount: int,
    payment_method: str,
    reference: str,
    user_email: str,
    taxes=0,
    tip_amount: int = 0,
) -> dict:
    """Inicia un cobro en el datáfono. Devuelve la respuesta de Bold (integration_id).
    SEGURIDAD: el monto lo manda quien llama (el servidor, desde el pedido), no el cliente.
    """
    cfg = _config()
    body = {
        "amount": {
            "currency": "COP",
            "taxes": taxes,
            "tip_amount": tip_amount,
            "total_amount": total_amount,
        },
        "payment_method": payment_method,
        "terminal_model": cfg["terminal_model"],
        "terminal_serial": cfg["terminal_serial"],
        "reference": reference,  # UUID único por orden → con esto casa el webhook
        "user_email": user_email,
    }

    response = httpx.post(
        f"{cfg['url']}/payments/app-checkout",
        json=body,
        headers={"Authorization": f"x-api-key {cfg['key']}"},
        timeout=15,
    )

    if response.status_code != 201:
        # Propagamos el error de Bold (AP002–AP006, etc.) a quien llamó.
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise BoldError(response.status_code, detail)

    return response.json()  # {integration_id, status}

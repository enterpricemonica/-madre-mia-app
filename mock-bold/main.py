"""
MOCK SERVER de Bold API Integrations (datáfonos).

Se hace pasar por Bold para poder desarrollar la integración SIN cuenta ni
datáfono reales. Replica los 3 endpoints, la auth por x-api-key, la lógica de
"montos mágicos" del sandbox, y DISPARA el webhook a la tienda unos segundos
después (simulando que el cliente pasó la tarjeta en el datáfono).

Correr:  uvicorn main:app --port 9000   (desde la carpeta mock-bold)
NO va a producción: es solo para desarrollo.
"""
import asyncio
import os
import uuid

import httpx
from fastapi import BackgroundTasks, Body, FastAPI, Header, HTTPException

app = FastAPI(title="Mock Bold API Integrations", version="1.0")

# A dónde mandar el webhook (el backend de la tienda) y cuánto "tarda el datáfono".
STORE_WEBHOOK_URL = os.getenv(
    "STORE_WEBHOOK_URL", "http://localhost:8000/payments/bold/webhook"
)
WEBHOOK_DELAY = float(os.getenv("MOCK_WEBHOOK_DELAY", "3"))  # segundos

VALID_METHODS = ["POS", "NEQUI", "DAVIPLATA", "PAY_BY_LINK"]
BOUND_TERMINALS = [{"terminal_model": "BOLD_S1", "terminal_serial": "MOCK-0001"}]

# Montos mágicos del sandbox de Bold → resultado simulado.
MAGIC = {
    111111: ("REJECTED", "INSUFFICIENT_FUNDS"),
    222222: ("REJECTED", "INVALID_PIN"),
    333333: ("REJECTED", "EXPIRED_CARD"),
    444444: ("REJECTED", "NETWORK_ERROR"),
    999999: ("REJECTED", "GENERAL_DECLINE"),
}


def _outcome(total_amount: int):
    """Decide el resultado del pago según el monto (igual que el sandbox de Bold)."""
    if total_amount in MAGIC:
        return MAGIC[total_amount]
    if 1000 <= total_amount <= 2_000_000:
        return ("APPROVED", None)
    return ("REJECTED", "OUT_OF_RANGE")


def _check_auth(authorization: str | None):
    """Bold exige el header  Authorization: x-api-key <llave>."""
    if not authorization or not authorization.startswith("x-api-key "):
        raise HTTPException(status_code=401, detail="Missing or invalid x-api-key")


def _ap_error(code: str, message: str):
    """Errores de Bold: AP00x → 400 (AP001 → 500)."""
    status = 500 if code == "AP001" else 400
    raise HTTPException(status_code=status, detail={"code": code, "message": message})


# ── GET /payments/payment-methods ──
@app.get("/payments/payment-methods")
def payment_methods(authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    return {"payment_methods": VALID_METHODS}


# ── GET /payments/binded-terminals ──
@app.get("/payments/binded-terminals")
def binded_terminals(authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    return {"terminals": BOUND_TERMINALS}


# ── POST /payments/app-checkout ──
@app.post("/payments/app-checkout", status_code=201)
def app_checkout(
    background_tasks: BackgroundTasks,
    body: dict = Body(...),
    authorization: str | None = Header(default=None),
):
    _check_auth(authorization)

    # Validaciones (replican los errores AP00x de Bold).
    amount = body.get("amount")
    if amount is None or "total_amount" not in amount:
        _ap_error("AP005", "Falta el campo amount.total_amount")
    if not all(k in body for k in ("payment_method", "terminal_model", "terminal_serial", "reference", "user_email")):
        _ap_error("AP005", "Falta un campo obligatorio")

    total = amount.get("total_amount")
    if not isinstance(total, int):
        _ap_error("AP006", "total_amount debe ser un entero")

    taxes = amount.get("taxes")
    if taxes is not None and not isinstance(taxes, (list, int)):
        _ap_error("AP002", "taxes mal formado")

    if body["payment_method"] not in VALID_METHODS:
        _ap_error("AP003", "Método de pago inactivo o inválido")

    bound = any(
        t["terminal_serial"] == body["terminal_serial"] for t in BOUND_TERMINALS
    )
    if not bound:
        _ap_error("AP004", "Datáfono no vinculado")

    # Todo bien → 201 + integration_id, y programamos el webhook (simula el datáfono).
    integration_id = str(uuid.uuid4())
    background_tasks.add_task(_fire_webhook, body["reference"], integration_id, total)
    return {"integration_id": integration_id, "status": "PENDING"}


async def _fire_webhook(reference: str, integration_id: str, total_amount: int):
    """Espera unos segundos (simula el datáfono) y notifica el resultado a la tienda."""
    await asyncio.sleep(WEBHOOK_DELAY)
    status, reason = _outcome(total_amount)
    payload = {
        "reference": reference,
        "integration_id": integration_id,
        "status": status,
        "reason": reason,
        "amount": total_amount,
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(STORE_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:  # el mock no debe caerse si la tienda no responde
        print(f"[mock-bold] no se pudo enviar el webhook: {e}")


@app.get("/")
def root():
    return {"message": "Mock Bold API Integrations 🤖 — solo para desarrollo"}

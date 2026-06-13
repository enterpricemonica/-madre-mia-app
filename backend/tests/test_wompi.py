"""
Adapter de Wompi (Wave 1) — TDD.

Por ahora cubre la **firma de integridad**. El caso principal usa el ejemplo
OFICIAL de la documentación de Wompi (docs.wompi.co) como "respuesta conocida":
si nuestra firma coincide con la de ellos, el algoritmo está bien.
"""
import hashlib

import pytest

import models
import wompi_gateway


# Secreto de eventos del ejemplo oficial de Wompi (lo usamos para firmar en los tests).
WOMPI_EVENT_SECRET = "prod_events_OcHnIzeBl5socpwByQ4hA52Em3USQ93Z"


def _signed_event(*, reference="ref-1", txn_id="txn-1", status="APPROVED",
                  amount_in_cents=1800000, timestamp=1530291411,
                  secret=WOMPI_EVENT_SECRET, checksum=None):
    """Construye un evento de Wompi con su checksum BIEN calculado (o uno falso)."""
    payload = f"{txn_id}{status}{amount_in_cents}{timestamp}{secret}"
    real = hashlib.sha256(payload.encode()).hexdigest()
    return {
        "event": "transaction.updated",
        "data": {"transaction": {
            "id": txn_id, "status": status, "amount_in_cents": amount_in_cents,
            "reference": reference, "payment_method_type": "NEQUI",
        }},
        "signature": {
            "properties": ["transaction.id", "transaction.status", "transaction.amount_in_cents"],
            "checksum": checksum or real,
        },
        "timestamp": timestamp,
    }


def _order(db, seed_table, total=18000):
    o = models.Order(table_id=seed_table.id, total=total)
    db.add(o); db.commit(); db.refresh(o)
    return o


class _FakeResp:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


# Ejemplo oficial de la doc de Wompi (verificado a mano).
WOMPI_DOC_REFERENCE = "sk8-438k4-xmxm392-sn2m"
WOMPI_DOC_AMOUNT = 2490000
WOMPI_DOC_SECRET = "prod_integrity_Z5mMke9x0k8gpErbDqwrJXMqsI6SFli6"
WOMPI_DOC_HASH = "37c8407747e595535433ef8f6a811d853cd943046624a0ec04662b17bbf33bf5"


# ── Coincide con el ejemplo oficial de Wompi ──
def test_integrity_signature_matches_wompi_doc_example():
    firma = wompi_gateway.integrity_signature(
        reference=WOMPI_DOC_REFERENCE,
        amount_in_cents=WOMPI_DOC_AMOUNT,
        secret=WOMPI_DOC_SECRET,
    )
    assert firma == WOMPI_DOC_HASH


# ── El secreto sale del .env si no se pasa explícito ──
def test_integrity_signature_reads_secret_from_env(monkeypatch):
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", WOMPI_DOC_SECRET)
    firma = wompi_gateway.integrity_signature(WOMPI_DOC_REFERENCE, WOMPI_DOC_AMOUNT)
    assert firma == WOMPI_DOC_HASH


# ── Si cambia el monto, la firma cambia (es el punto de la firma) ──
def test_integrity_signature_changes_when_amount_changes():
    f1 = wompi_gateway.integrity_signature("ref-1", 18000, secret="s3cr3t")
    f2 = wompi_gateway.integrity_signature("ref-1", 99999, secret="s3cr3t")
    assert f1 != f2


# ── prepare_checkout: pesos → centavos (×100) y arma el paquete del Widget ──
def test_prepare_checkout_converts_pesos_to_cents(monkeypatch):
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_abc")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "s3cr3t")

    data = wompi_gateway.prepare_checkout(reference="ref-1", amount_cop=18000)

    assert data["amount_in_cents"] == 1800000  # 18.000 pesos × 100
    assert data["currency"] == "COP"
    assert data["reference"] == "ref-1"
    assert data["public_key"] == "pub_test_abc"


# ── La firma del paquete usa el monto YA en centavos ──
def test_prepare_checkout_signs_with_cents(monkeypatch):
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_abc")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "s3cr3t")

    data = wompi_gateway.prepare_checkout(reference="ref-1", amount_cop=18000)

    esperada = wompi_gateway.integrity_signature("ref-1", 1800000, "COP", secret="s3cr3t")
    assert data["signature"] == esperada


# ── get_transaction: devuelve el objeto `data` de Wompi ──
def test_get_transaction_returns_data(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        return _FakeResp(200, {"data": {"id": "txn-1", "status": "APPROVED",
                                        "reference": "ref-1", "amount_in_cents": 1800000}})

    monkeypatch.setattr(wompi_gateway.httpx, "get", fake_get)

    data = wompi_gateway.get_transaction("txn-1")
    assert data["status"] == "APPROVED"
    assert data["reference"] == "ref-1"
    assert data["amount_in_cents"] == 1800000


# ── Manda la llave PRIVADA como Bearer y pega a la URL correcta ──
def test_get_transaction_sends_bearer_private_key(monkeypatch):
    monkeypatch.setenv("WOMPI_API_URL", "https://sandbox.wompi.co/v1")
    monkeypatch.setenv("WOMPI_PRIVATE_KEY", "prv_test_xyz")
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return _FakeResp(200, {"data": {"status": "APPROVED"}})

    monkeypatch.setattr(wompi_gateway.httpx, "get", fake_get)

    wompi_gateway.get_transaction("txn-1")
    assert captured["url"] == "https://sandbox.wompi.co/v1/transactions/txn-1"
    assert captured["headers"]["Authorization"] == "Bearer prv_test_xyz"


# ── Si Wompi responde error, lanza WompiError ──
def test_get_transaction_raises_on_error(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        return _FakeResp(404, {"error": {"type": "NOT_FOUND_ERROR"}})

    monkeypatch.setattr(wompi_gateway.httpx, "get", fake_get)

    with pytest.raises(wompi_gateway.WompiError) as exc:
        wompi_gateway.get_transaction("no-existe")
    assert exc.value.status_code == 404


# ── El endpoint crea el Payment (pending, wompi) y devuelve el paquete firmado del Widget ──
def test_create_wompi_payment(client, db_session, seed_table, monkeypatch):
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_abc")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "s3cr3t")
    order = _order(db_session, seed_table, 18000)

    r = client.post("/payments/wompi", json={"order_id": order.id})
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "wompi"
    assert body["status"] == "pending"
    assert body["amount"] == 18000             # del servidor (pesos)
    assert body["amount_in_cents"] == 1800000  # centavos para el Widget
    assert body["public_key"] == "pub_test_abc"
    assert body["currency"] == "COP"
    # la firma cuadra con la referencia devuelta
    assert body["signature"] == wompi_gateway.integrity_signature(
        body["reference"], 1800000, "COP", secret="s3cr3t")

    pay = db_session.query(models.Payment).filter_by(order_id=order.id).first()
    assert pay.provider_ref == body["reference"]  # con esto casa el webhook


def test_create_wompi_payment_unknown_order(client):
    r = client.post("/payments/wompi", json={"order_id": 9999})
    assert r.status_code == 404


def test_create_wompi_payment_rejects_if_already_paid(client, db_session, seed_table):
    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(
        order_id=order.id, amount=order.total, provider="wompi",
        status="approved", provider_ref="ref-ya",
    ))
    db_session.commit()

    r = client.post("/payments/wompi", json={"order_id": order.id})
    assert r.status_code == 400


# ── Firma de eventos: acepta la buena, rechaza la alterada ──
def test_verify_event_signature_accepts_valid():
    event = _signed_event()
    assert wompi_gateway.verify_event_signature(event, secret=WOMPI_EVENT_SECRET) is True


def test_verify_event_signature_rejects_bad_checksum():
    event = _signed_event(checksum="deadbeef")
    assert wompi_gateway.verify_event_signature(event, secret=WOMPI_EVENT_SECRET) is False


def test_verify_event_signature_rejects_tampered_amount():
    # El atacante cambia el monto pero NO puede recalcular el checksum (no tiene el secreto).
    event = _signed_event(amount_in_cents=100)        # checksum se calcula sobre 100...
    event["data"]["transaction"]["amount_in_cents"] = 9999999  # ...pero el body dice otra cosa
    assert wompi_gateway.verify_event_signature(event, secret=WOMPI_EVENT_SECRET) is False


def test_verify_event_signature_rejects_malformed():
    assert wompi_gateway.verify_event_signature({"data": {}}, secret="x") is False


# ── El webhook: firma OK + Wompi confirma APPROVED → marca pagado ──
def test_wompi_webhook_approves_and_marks_paid(client, db_session, seed_table, monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", WOMPI_EVENT_SECRET)
    monkeypatch.setattr(wompi_gateway, "get_transaction",
                        lambda txn_id: {"status": "APPROVED", "payment_method_type": "NEQUI"})

    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(
        order_id=order.id, amount=order.total, provider="wompi",
        status="pending", provider_ref="ref-abc",
    ))
    db_session.commit()

    event = _signed_event(reference="ref-abc", txn_id="txn-9")
    r = client.post("/payments/wompi/webhook", json=event)
    assert r.status_code == 200
    assert r.json()["status"] == "approved"

    db_session.refresh(order)
    assert order.is_paid is True
    pay = db_session.query(models.Payment).filter_by(order_id=order.id).first()
    assert pay.method == "nequi"  # el método real lo supimos al verificar


# ── SEGURIDAD: firma inválida → 401 y NO se marca pagado ──
def test_wompi_webhook_rejects_invalid_signature(client, db_session, seed_table, monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", WOMPI_EVENT_SECRET)
    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(
        order_id=order.id, amount=order.total, provider="wompi",
        status="pending", provider_ref="ref-abc",
    ))
    db_session.commit()

    event = _signed_event(reference="ref-abc", checksum="falso")
    r = client.post("/payments/wompi/webhook", json=event)
    assert r.status_code == 401

    db_session.refresh(order)
    assert order.is_paid is False  # nadie falsificó un pago


# ── Idempotencia: si ya está aprobado, no repite ──
def test_wompi_webhook_idempotent(client, db_session, seed_table, monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", WOMPI_EVENT_SECRET)
    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(
        order_id=order.id, amount=order.total, provider="wompi",
        status="approved", provider_ref="ref-abc",
    ))
    db_session.commit()

    event = _signed_event(reference="ref-abc")
    r = client.post("/payments/wompi/webhook", json=event)
    assert r.status_code == 200
    assert r.json()["status"] == "already_processed"


# ── Reintentos: /status prioriza el aprobado, no el rechazo viejo ──
def test_payment_status_prefers_approved_over_old_declined(client, db_session, seed_table):
    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(order_id=order.id, amount=order.total, provider="wompi",
                                  status="declined", provider_ref="ref-old"))
    db_session.commit()
    db_session.add(models.Payment(order_id=order.id, amount=order.total, provider="wompi",
                                  status="approved", provider_ref="ref-new"))
    db_session.commit()

    r = client.get(f"/payments/{order.id}/status")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"  # NO el declined más viejo


# ── Reintentos sin aprobado aún: /status devuelve el intento más reciente ──
def test_payment_status_returns_most_recent_when_none_approved(client, db_session, seed_table):
    order = _order(db_session, seed_table, 18000)
    db_session.add(models.Payment(order_id=order.id, amount=order.total, provider="wompi",
                                  status="declined", provider_ref="ref-old"))
    db_session.commit()
    db_session.add(models.Payment(order_id=order.id, amount=order.total, provider="wompi",
                                  status="pending", provider_ref="ref-new"))
    db_session.commit()

    r = client.get(f"/payments/{order.id}/status")
    assert r.json()["status"] == "pending"  # el reintento, no el rechazo viejo

"""
Adapter de Bold (Wave 2) — TDD. Probamos SIN red real: simulamos la respuesta de Bold.
Cubre: el adapter arma bien el body + la x-api-key, propaga errores de Bold, y el
endpoint crea el Payment (pending, provider=bold, monto del servidor, reference UUID).
"""
import pytest

import models
import bold_gateway


class _FakeResp:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


def _order(db, seed_table, total=18000):
    o = models.Order(table_id=seed_table.id, total=total)
    db.add(o); db.commit(); db.refresh(o)
    return o


# ── El adapter arma bien el cobro ──
def test_gateway_builds_body_and_returns_integration_id(monkeypatch):
    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _FakeResp(201, {"integration_id": "intg-123", "status": "PENDING"})

    monkeypatch.setattr(bold_gateway.httpx, "post", fake_post)

    result = bold_gateway.create_checkout(18000, "POS", "ref-1", "a@b.co")
    assert result["integration_id"] == "intg-123"
    assert captured["json"]["amount"]["total_amount"] == 18000
    assert captured["json"]["amount"]["currency"] == "COP"
    assert captured["json"]["reference"] == "ref-1"
    assert captured["json"]["payment_method"] == "POS"
    assert captured["headers"]["Authorization"].startswith("x-api-key ")
    assert captured["url"].endswith("/payments/app-checkout")


def test_gateway_raises_on_bold_error(monkeypatch):
    monkeypatch.setattr(
        bold_gateway.httpx, "post",
        lambda *a, **k: _FakeResp(400, {"code": "AP005", "message": "Falta un campo"}),
    )
    with pytest.raises(bold_gateway.BoldError):
        bold_gateway.create_checkout(18000, "POS", "ref-1", "a@b.co")


# ── El endpoint crea el Payment y devuelve el integration_id ──
def test_create_bold_payment(client, db_session, seed_table, monkeypatch):
    monkeypatch.setattr(
        bold_gateway, "create_checkout",
        lambda **kw: {"integration_id": "intg-xyz", "status": "PENDING"},
    )
    order = _order(db_session, seed_table, 18000)
    r = client.post("/payments/bold", json={
        "order_id": order.id, "payment_method": "POS", "user_email": "a@b.co",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["integration_id"] == "intg-xyz"
    assert body["amount"] == 18000        # del servidor
    assert body["status"] == "pending"
    assert body["provider"] == "bold"
    assert body["method"] == "datafono"   # POS → datafono (para el reporte)

    pay = db_session.query(models.Payment).filter_by(order_id=order.id).first()
    assert pay.provider_ref  # la reference UUID quedó guardada (con ella casa el webhook)


def test_create_bold_payment_rejects_bad_method(client, db_session, seed_table):
    order = _order(db_session, seed_table)
    r = client.post("/payments/bold", json={
        "order_id": order.id, "payment_method": "BITCOIN", "user_email": "a@b.co",
    })
    assert r.status_code == 400


def test_create_bold_payment_unknown_order(client):
    r = client.post("/payments/bold", json={
        "order_id": 9999, "payment_method": "POS", "user_email": "a@b.co",
    })
    assert r.status_code == 404


# ── El webhook de Bold ──
def _bold_payment(db, order, reference, status="pending"):
    p = models.Payment(
        order_id=order.id, amount=order.total, method="datafono",
        provider="bold", status=status, provider_ref=reference,
    )
    db.add(p); db.commit(); db.refresh(p)
    return p


def test_bold_webhook_approves_and_marks_paid(client, db_session, seed_table):
    order = _order(db_session, seed_table, 18000)
    _bold_payment(db_session, order, "ref-abc")

    r = client.post("/payments/bold/webhook", json={"reference": "ref-abc", "status": "APPROVED"})
    assert r.status_code == 200
    db_session.refresh(order)
    assert order.is_paid is True


def test_bold_webhook_rejected_does_not_pay(client, db_session, seed_table):
    order = _order(db_session, seed_table)
    _bold_payment(db_session, order, "ref-rej")

    client.post("/payments/bold/webhook", json={"reference": "ref-rej", "status": "REJECTED", "reason": "INSUFFICIENT_FUNDS"})
    db_session.refresh(order)
    assert order.is_paid is False
    assert db_session.query(models.Payment).filter_by(order_id=order.id).first().status == "declined"


def test_bold_webhook_is_idempotent(client, db_session, seed_table):
    order = _order(db_session, seed_table)
    _bold_payment(db_session, order, "ref-idem")

    client.post("/payments/bold/webhook", json={"reference": "ref-idem", "status": "APPROVED"})
    r2 = client.post("/payments/bold/webhook", json={"reference": "ref-idem", "status": "APPROVED"})  # otra vez
    assert r2.status_code == 200
    db_session.refresh(order)
    assert order.is_paid is True


def test_bold_webhook_unknown_payment(client):
    r = client.post("/payments/bold/webhook", json={"reference": "no-existe", "status": "APPROVED"})
    assert r.status_code == 404

"""
Router de pagos — TDD. Estos tests se escriben PRIMERO (en rojo) y luego el código.
Cubren la parte de PLATA:
  - el monto sale del SERVIDOR (del pedido), nunca del cliente,
  - el pago arranca `pending`,
  - el webhook marca `approved` + el pedido `paid`, de forma IDEMPOTENTE,
  - un pago rechazado NO marca el pedido como pagado.
Usa un STUB mock de Bold (todavía no hay sandbox).
"""
import models


def _make_order(db_session, seed_table, total=13000):
    order = models.Order(table_id=seed_table.id, total=total)
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def _ref_for(db_session, order_id):
    return db_session.query(models.Payment).filter_by(order_id=order_id).first().provider_ref


def test_create_payment_uses_order_total(client, db_session, seed_table):
    order = _make_order(db_session, seed_table, total=29000)
    r = client.post("/payments/", json={"order_id": order.id, "method": "bre_b"})
    assert r.status_code == 200
    body = r.json()
    assert body["amount"] == 29000     # el monto sale del pedido, no del cliente
    assert body["status"] == "pending"
    assert body["provider"] == "bold"
    assert body["qr_url"]              # hay un QR para mostrar en pantalla


def test_create_payment_rejects_unknown_order(client):
    r = client.post("/payments/", json={"order_id": 9999, "method": "bre_b"})
    assert r.status_code == 404


def test_create_payment_rejects_invalid_method(client, db_session, seed_table):
    order = _make_order(db_session, seed_table)
    r = client.post("/payments/", json={"order_id": order.id, "method": "bitcoin"})
    assert r.status_code == 400


def test_webhook_marks_payment_approved_and_order_paid(client, db_session, seed_table):
    order = _make_order(db_session, seed_table)
    client.post("/payments/", json={"order_id": order.id, "method": "bre_b"})
    ref = _ref_for(db_session, order.id)

    r = client.post("/payments/webhook", json={"provider_ref": ref, "status": "approved"})
    assert r.status_code == 200

    db_session.refresh(order)
    assert order.status == "paid"
    assert _status_of(db_session, order.id) == "approved"


def test_webhook_is_idempotent(client, db_session, seed_table):
    order = _make_order(db_session, seed_table)
    client.post("/payments/", json={"order_id": order.id, "method": "bre_b"})
    ref = _ref_for(db_session, order.id)

    client.post("/payments/webhook", json={"provider_ref": ref, "status": "approved"})
    r2 = client.post("/payments/webhook", json={"provider_ref": ref, "status": "approved"})  # otra vez
    assert r2.status_code == 200

    db_session.refresh(order)
    assert order.status == "paid"  # sigue pagado, sin romperse


def test_webhook_declined_does_not_mark_paid(client, db_session, seed_table):
    order = _make_order(db_session, seed_table)
    client.post("/payments/", json={"order_id": order.id, "method": "card"})
    ref = _ref_for(db_session, order.id)

    client.post("/payments/webhook", json={"provider_ref": ref, "status": "declined"})
    db_session.refresh(order)
    assert order.status != "paid"
    assert _status_of(db_session, order.id) == "declined"


def test_status_endpoint_reflects_payment(client, db_session, seed_table):
    order = _make_order(db_session, seed_table)
    client.post("/payments/", json={"order_id": order.id, "method": "nequi"})
    r = client.get(f"/payments/{order.id}/status")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


def _status_of(db_session, order_id):
    return db_session.query(models.Payment).filter_by(order_id=order_id).first().status

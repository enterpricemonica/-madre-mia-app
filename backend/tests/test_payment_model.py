"""
Pruebas del modelo Payment (todavía sin router).
Confirma los valores por defecto y la relación 1-a-1 con Order.
"""
import models


def test_payment_starts_pending_with_defaults(db_session, seed_table):
    order = models.Order(table_id=seed_table.id, total=13000)
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    pay = models.Payment(order_id=order.id, amount=order.total)
    db_session.add(pay)
    db_session.commit()
    db_session.refresh(pay)

    assert pay.status == "pending"   # un pago arranca pendiente
    assert pay.provider == "bold"    # pasarela por defecto
    assert pay.amount == 13000


def test_order_has_one_payment(db_session, seed_table):
    order = models.Order(table_id=seed_table.id, total=9000)
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    pay = models.Payment(order_id=order.id, amount=9000, method="bre_b")
    db_session.add(pay)
    db_session.commit()

    db_session.refresh(order)
    assert len(order.payments) == 1
    assert order.payments[0].method == "bre_b"

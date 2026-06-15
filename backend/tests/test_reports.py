"""
Reportes de ventas — TDD. Lo de PLATA (sumas del cuadre) con rigor alto.
Cubre: pago manual (efectivo/datafono), reporte agrupado por método,
que solo cuente el día pedido y solo pagos approved, descarga CSV, y que esté protegido.
"""
from datetime import datetime, date, timedelta
import models


def _order(db, seed_table, total):
    o = models.Order(table_id=seed_table.id, total=total)
    db.add(o); db.commit(); db.refresh(o)
    return o


def _approved_payment(db, order, method, amount, when=None):
    p = models.Payment(order_id=order.id, amount=amount, method=method, provider="x", status="approved")
    db.add(p); db.commit(); db.refresh(p)
    if when is not None:
        p.created_at = when  # forzamos una fecha (para probar "otros días")
        db.commit()
    return p


# ── Pago manual ──
def test_manual_payment_creates_approved(client, db_session, seed_table):
    order = _order(db_session, seed_table, 12000)
    r = client.post("/payments/manual", json={"order_id": order.id, "method": "efectivo"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "approved"
    assert body["method"] == "efectivo"
    assert body["amount"] == 12000  # monto del servidor


def test_manual_payment_accepts_the_five_methods(client, db_session, seed_table):
    for method in ["efectivo", "datafono", "nequi", "daviplata", "bre_b"]:
        order = _order(db_session, seed_table, 5000)
        r = client.post("/payments/manual", json={"order_id": order.id, "method": method})
        assert r.status_code == 200, method
        assert r.json()["method"] == method


def test_manual_payment_rejects_invalid_method(client, db_session, seed_table):
    order = _order(db_session, seed_table, 12000)
    r = client.post("/payments/manual", json={"order_id": order.id, "method": "bitcoin"})
    assert r.status_code == 400


def test_manual_payment_no_double_pay(client, db_session, seed_table):
    order = _order(db_session, seed_table, 12000)
    client.post("/payments/manual", json={"order_id": order.id, "method": "efectivo"})
    r2 = client.post("/payments/manual", json={"order_id": order.id, "method": "datafono"})
    assert r2.status_code == 400  # ya tiene un pago aprobado


# ── Reporte ──
def test_sales_report_groups_by_method(client, db_session, seed_table):
    today = (datetime.utcnow() - timedelta(hours=5)).date()  # hoy en Colombia
    o1 = _order(db_session, seed_table, 10000)
    o2 = _order(db_session, seed_table, 5000)
    o3 = _order(db_session, seed_table, 8000)
    _approved_payment(db_session, o1, "efectivo", 10000)
    _approved_payment(db_session, o2, "efectivo", 5000)
    _approved_payment(db_session, o3, "bre_b", 8000)

    r = client.get(f"/reports/sales?date={today.isoformat()}")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 23000
    assert body["count"] == 3
    assert body["by_method"]["efectivo"] == 15000
    assert body["by_method"]["bre_b"] == 8000


def test_sales_report_separates_tips_from_net_sales(client, db_session, seed_table):
    today = (datetime.utcnow() - timedelta(hours=5)).date()  # hoy en Colombia
    o = _order(db_session, seed_table, 20000)
    o.tip_amount = 1800              # propina que dejó el cliente (10%)
    db_session.commit()
    _approved_payment(db_session, o, "nequi", 21800)  # cobrado = 20000 + 1800

    body = client.get(f"/reports/sales?date={today.isoformat()}").json()
    assert body["total"] == 21800       # total cobrado (incluye propina)
    assert body["tips"] == 1800         # propina separada (para repartir)
    assert body["net_sales"] == 20000   # ventas del negocio, sin propina


def test_sales_report_ignores_other_days(client, db_session, seed_table):
    today = (datetime.utcnow() - timedelta(hours=5)).date()  # hoy en Colombia
    o1 = _order(db_session, seed_table, 10000)
    o2 = _order(db_session, seed_table, 7000)
    _approved_payment(db_session, o1, "efectivo", 10000)
    _approved_payment(db_session, o2, "efectivo", 7000, when=datetime.utcnow() - timedelta(days=1))

    r = client.get(f"/reports/sales?date={today.isoformat()}")
    assert r.json()["total"] == 10000  # solo el de hoy


def test_sales_report_ignores_pending(client, db_session, seed_table):
    today = (datetime.utcnow() - timedelta(hours=5)).date()  # hoy en Colombia
    o1 = _order(db_session, seed_table, 10000)
    _approved_payment(db_session, o1, "efectivo", 10000)
    o2 = _order(db_session, seed_table, 9999)
    db_session.add(models.Payment(order_id=o2.id, amount=9999, method="bre_b", provider="bold", status="pending"))
    db_session.commit()

    r = client.get(f"/reports/sales?date={today.isoformat()}")
    assert r.json()["total"] == 10000  # el pendiente NO cuenta


def test_sales_csv_download(client, db_session, seed_table):
    today = (datetime.utcnow() - timedelta(hours=5)).date()  # hoy en Colombia
    o1 = _order(db_session, seed_table, 10000)
    _approved_payment(db_session, o1, "efectivo", 10000)
    r = client.get(f"/reports/sales.csv?date={today.isoformat()}")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "efectivo" in r.text
    assert "10000" in r.text


def test_reports_require_auth(client_no_auth):
    r = client_no_auth.get("/reports/sales")
    assert r.status_code == 401  # sin token, rechaza

"""
Regresión del flujo de pedidos (la parte de PLATA → rigor alto).
Protege tres cosas que NO se pueden romper:
  1. El total se calcula en el SERVIDOR (no se confía en el cliente).
  2. No se aceptan ítems agotados.
  3. Las transiciones de estado válidas funcionan; las inválidas se rechazan.
"""


def test_total_is_calculated_on_the_server(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]  # 13000
    queso = seed_menu["queso"]  # 3000
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [
            {"item_id": arepa.id, "quantity": 2},
            {"item_id": queso.id, "quantity": 1},
        ],
    })
    assert r.status_code == 200
    assert r.json()["total"] == 13000 * 2 + 3000  # 29000


def test_order_type_defaults_to_dine_in(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 1}],
    })
    assert r.json()["order_type"] == "dine_in"
    assert r.json()["is_paid"] is False  # recién creado, aún sin pagar


def test_order_can_be_takeaway(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "order_type": "takeaway",
        "items": [{"item_id": arepa.id, "quantity": 1}],
    })
    assert r.status_code == 200
    assert r.json()["order_type"] == "takeaway"


def test_invalid_order_type_is_rejected(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "order_type": "teletransporte",
        "items": [{"item_id": arepa.id, "quantity": 1}],
    })
    assert r.status_code == 400


def test_unavailable_item_is_rejected(client, seed_menu, seed_table):
    agotado = seed_menu["agotado"]
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": agotado.id, "quantity": 1}],
    })
    assert r.status_code == 400


# ── Inventario (M10) ──
def test_order_decrements_stock(client, seed_menu, seed_table, db_session):
    arepa = seed_menu["arepa"]
    arepa.stock = 5
    db_session.commit()

    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 2}],
    })
    assert r.status_code == 200
    db_session.refresh(arepa)
    assert arepa.stock == 3   # 5 - 2 vendidas


def test_order_rejected_when_not_enough_stock(client, seed_menu, seed_table, db_session):
    arepa = seed_menu["arepa"]
    arepa.stock = 1
    db_session.commit()

    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 2}],  # pide 2, solo hay 1
    })
    assert r.status_code == 400
    db_session.refresh(arepa)
    assert arepa.stock == 1   # no se tocó (la venta se rechazó entera)


def test_unlimited_stock_is_not_decremented(client, seed_menu, seed_table, db_session):
    arepa = seed_menu["arepa"]  # stock None = ilimitado
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 3}],
    })
    assert r.status_code == 200
    db_session.refresh(arepa)
    assert arepa.stock is None   # sigue ilimitado


def test_order_needs_existing_table(client, seed_menu):
    arepa = seed_menu["arepa"]
    r = client.post("/orders/", json={
        "table_id": 9999,
        "items": [{"item_id": arepa.id, "quantity": 1}],
    })
    assert r.status_code == 404


def test_order_needs_at_least_one_item(client, seed_table):
    r = client.post("/orders/", json={"table_id": seed_table.id, "items": []})
    assert r.status_code == 400


def test_status_can_advance_to_paid(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]
    order_id = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 1}],
    }).json()["id"]

    r = client.patch(f"/orders/{order_id}/status", json={"status": "paid"})
    assert r.status_code == 200
    assert r.json()["status"] == "paid"


def test_invalid_status_is_rejected(client, seed_menu, seed_table):
    arepa = seed_menu["arepa"]
    order_id = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": arepa.id, "quantity": 1}],
    }).json()["id"]

    r = client.patch(f"/orders/{order_id}/status", json={"status": "teletransportado"})
    assert r.status_code == 400

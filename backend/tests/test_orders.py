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


def test_unavailable_item_is_rejected(client, seed_menu, seed_table):
    agotado = seed_menu["agotado"]
    r = client.post("/orders/", json={
        "table_id": seed_table.id,
        "items": [{"item_id": agotado.id, "quantity": 1}],
    })
    assert r.status_code == 400


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

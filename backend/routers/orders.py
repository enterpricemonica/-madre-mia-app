from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

# Tipos de pedido válidos: comer aquí o para llevar.
VALID_ORDER_TYPES = ["dine_in", "takeaway"]


# POST /orders — create a new order
@router.post("/", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    # PASO 1: Verificar que la mesa existe.
    table = db.query(models.Table).filter(models.Table.id == order.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    if order.order_type not in VALID_ORDER_TYPES:
        raise HTTPException(status_code=400, detail=f"Order type '{order.order_type}' is invalid.")

    # PASO 2: Crear el objeto Order (todavía sin total).
    new_order = models.Order(table_id=order.table_id, order_type=order.order_type)
    db.add(new_order)
    db.flush()  # asigna id a new_order sin hacer commit

    # PASO 3: Recorrer order.items y calcular el total LEYENDO PRECIOS DE LA BD.
    total = 0
    for line in order.items:
        menu_item = (
            db.query(models.MenuItem).filter(models.MenuItem.id == line.item_id).first()
        )
        if not menu_item or not menu_item.available:
            raise HTTPException(
                status_code=400, detail=f"Menu item {line.item_id} not available"
            )
        total += menu_item.price * line.quantity

        order_item = models.OrderItem(
            order_id=new_order.id,
            item_id=menu_item.id,
            quantity=line.quantity,
            notes=line.notes,
        )
        db.add(order_item)

    # PASO 4: Guardar el total en el pedido.
    new_order.total = total

    # PASO 5: Confirmar y devolver.
    db.commit()
    db.refresh(new_order)
    return new_order


# Estados válidos de un pedido (el flujo de la cocina)
VALID_STATUSES = ["received", "preparing", "ready", "delivered", "paid"]


# GET /orders — list all orders (newest first)
@router.get("/", response_model=List[schemas.OrderOut])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return orders


# GET /orders/{order_id} — get a single order
@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order   


# PATCH /orders/{order_id}/status — advance the order status
@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(order_id: int, payload: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Status '{payload.status}' is invalid.")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()      # Aplica los cambios en la base de datos
    db.refresh(order) # Actualiza nuestra variable con los datos nuevos
    return order

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from typing import List

router = APIRouter(prefix="/menu", tags=["Menu"])

# GET /menu — obtener todos los items del menu
@router.get("/", response_model=List[schemas.MenuItemOut])
def obtener_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).filter(
        models.MenuItem.disponible == True
    ).all()

# GET /menu/{id} — obtener un item especifico
@router.get("/{item_id}", response_model=schemas.MenuItemOut)
def obtener_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

# POST /menu — crear un item nuevo
@router.post("/", response_model=schemas.MenuItemOut)
def crear_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    nuevo = models.MenuItem(**item.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# PUT /menu/{id} — actualizar un item
@router.put("/{item_id}", response_model=schemas.MenuItemOut)
def actualizar_item(item_id: int, item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

# DELETE /menu/{id} — eliminar un item
@router.delete("/{item_id}")
def eliminar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(item)
    db.commit()
    return {"mensaje": "Item eliminado"}
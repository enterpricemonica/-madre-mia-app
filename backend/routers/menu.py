from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from typing import List

router = APIRouter(prefix="/menu", tags=["Menu"])

# GET /menu — get all available menu items
@router.get("/", response_model=List[schemas.MenuItemOut])
def get_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).filter(
        models.MenuItem.available == True
    ).all()

# GET /menu/{id} — get a single item
@router.get("/{item_id}", response_model=schemas.MenuItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# POST /menu — create a new item
@router.post("/", response_model=schemas.MenuItemOut)
def create_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    new_item = models.MenuItem(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# PUT /menu/{id} — update an item
@router.put("/{item_id}", response_model=schemas.MenuItemOut)
def update_item(item_id: int, item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

# DELETE /menu/{id} — delete an item
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(
        models.MenuItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}

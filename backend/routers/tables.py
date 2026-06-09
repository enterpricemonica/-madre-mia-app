from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from typing import List
import qrcode
import os

# URL del frontend (para los QR). En local: localhost; en producción
# se define la variable FRONTEND_URL con la URL real de Vercel.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter(prefix="/tables", tags=["Tables"])

# GET /tables — list all tables
@router.get("/", response_model=List[schemas.TableOut])
def get_tables(db: Session = Depends(get_db)):
    return db.query(models.Table).all()

# GET /tables/by-number/{number} — search a table by visible number
@router.get("/by-number/{number}", response_model=schemas.TableOut)
def get_table_by_number(number: int, db: Session = Depends(get_db)):
    table = db.query(models.Table).filter(models.Table.number == number).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

# POST /tables — create a new table
@router.post("/", response_model=schemas.TableOut)
def create_table(table: schemas.TableCreate, db: Session = Depends(get_db)):
    new_table = models.Table(**table.model_dump())
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table

# POST /tables/{id}/generate-qr — generate the QR for a table
@router.post("/{table_id}/generate-qr")
def generate_qr(table_id: int, db: Session = Depends(get_db)):
    table = db.query(models.Table).filter(
        models.Table.id == table_id
    ).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # URL the customer's phone will open
    url = f"{FRONTEND_URL}/table/{table.number}"

    # Generate the QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR image
    os.makedirs("../qr_codes", exist_ok=True)
    path = f"../qr_codes/table_{table.number}.png"
    img.save(path)

    # Save the URL in the database
    table.qr_code = url
    db.commit()

    return {"message": f"QR generated for table {table.number}", "url": url, "file": path}

# DELETE /tables/{id} — delete a table
@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(models.Table).filter(
        models.Table.id == table_id
    ).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(table)
    db.commit()
    return {"message": "Table deleted"}

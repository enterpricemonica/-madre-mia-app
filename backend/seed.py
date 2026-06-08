"""
Seed script: loads the restaurant menu into the database.

Run it from the `backend` folder:
    python seed.py

It is idempotent: it clears the menu_items table first, then inserts
the items in MENU below. Edit MENU with the real restaurant menu.
Prices are in Colombian pesos (COP) as whole integers (e.g. 8000 = $8.000).
"""
from database import SessionLocal, engine, Base
import models

# 👇 EDIT THIS LIST with the real menu from the restaurant.
MENU = [
    # name, description, price (COP), category, available
    {"name": "Arepa de queso",     "description": "Arepa rellena de queso costeño", "price": 8000,  "category": "Entradas",   "available": True},
    {"name": "Empanada de carne",  "description": "Empanada frita rellena de carne", "price": 3500,  "category": "Entradas",   "available": True},
    {"name": "Bandeja paisa",      "description": "Frijoles, arroz, carne, chicharrón, huevo y patacón", "price": 28000, "category": "Platos fuertes", "available": True},
    {"name": "Ajiaco santafereño", "description": "Sopa de pollo con tres papas y guascas", "price": 22000, "category": "Platos fuertes", "available": True},
    {"name": "Limonada de coco",   "description": "Limonada cremosa de coco",        "price": 9000,  "category": "Bebidas",    "available": True},
    {"name": "Jugo de lulo",       "description": "Jugo natural de lulo en agua",    "price": 7000,  "category": "Bebidas",    "available": True},
]


def seed():
    # Make sure tables exist before inserting
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing items so re-running gives a clean state
        deleted = db.query(models.MenuItem).delete()
        db.commit()

        for entry in MENU:
            db.add(models.MenuItem(**entry))
        db.commit()

        total = db.query(models.MenuItem).count()
        print(f"🧹 Removed {deleted} old item(s)")
        print(f"🌱 Inserted {len(MENU)} menu item(s) — {total} total in the database")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

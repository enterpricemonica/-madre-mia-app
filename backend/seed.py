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
    # --- AREPAS OCAÑERAS (Entradas / Platos Principales) ---
    {"name": "Queso costeño", "description": "Arepa rellena de queso costeño sin mantequilla", "price": 14000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Queso costeño con mantequilla", "description": "Arepa rellena de queso costeño con mantequilla", "price": 15000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Aguacate con queso costeño", "description": "Arepa rellena de queso costeño y aguacate", "price": 18000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Madurito con queso costeño", "description": "Arepa rellena de queso costeño y madurito", "price": 18000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Vegetariana", "description": "Aguacate + Queso Costeño + Madurito", "price": 21000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Vegana", "description": "Aguacate + Madurito + Hogao", "price": 21000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Garbanzo al curry", "description": "Garbanzo + Madurito + Aguacate + Semillas de Girasol", "price": 23000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Vegetariana con champiñón", "description": "Champiñon + hogao + Queso Costeño + Aguacate", "price": 22000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Choriqueso", "description": "Chorizo con Panela + Queso Costeño", "price": 24000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Pollo aguacate", "description": "Pollo en salsa de tomates asados + Aguacate", "price": 25000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Costillita", "description": "Aguacate + Costilla Ahumada + Hogao", "price": 27000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Albóndiga madurito", "description": "Carne de Albóndiga con jengibre y aceite de coco + Madurito", "price": 26000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Macarena", "description": "Chorizo con Panela + Queso Costeño + Aguacate", "price": 29000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Madre Mía", "description": "Pollo + Costilla ahumada de cerdo + Queso costeño + Aguacate", "price": 32000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Traviata", "description": "Carne de Albondiga aromatizada en jengibre y aceite de coco Madurito + queso + Aguacate", "price": 30000, "category": "Arepas Ocañeras", "available": True},
    {"name": "Chicharrón", "description": "Chicharron + Queso Costeño + Aguacate (Con Aguacate y Queso Costeño)", "price": 33000, "category": "Arepas Ocañeras", "available": True},

    # --- BEBIDAS CALIENTES ---
    {"name": "Café Vietnamita Leche Condensada", "description": "Café de origen preparado al estilo Vietnamita con leche condensada", "price": 10200, "category": "Bebidas Calientes", "available": True},
    {"name": "Café Vietnamita Negro", "description": "Café de origen preparado al estilo Vietnamita negro", "price": 9000, "category": "Bebidas Calientes", "available": True},
    {"name": "Prensa Francesa", "description": "Café filtrado en prensa francesa", "price": 8500, "category": "Bebidas Calientes", "available": True},
    {"name": "Americano", "description": "Café americano clásico", "price": 7500, "category": "Bebidas Calientes", "available": True},
    {"name": "Espresso", "description": "Café espresso concentrado", "price": 4000, "category": "Bebidas Calientes", "available": True},
    {"name": "Capuccino", "description": "Café capuccino con espuma de leche", "price": 9500, "category": "Bebidas Calientes", "available": True},
    {"name": "Latte", "description": "Café latte suave", "price": 8500, "category": "Bebidas Calientes", "available": True},
    {"name": "Té Negro / Té Verde Jazmín / Chai Latte", "description": "Té preparado en agua o Chai Latte", "price": 6500, "category": "Bebidas Calientes", "available": True},
    {"name": "Copa de Vino Caliente", "description": "Vino caliente aromatizado", "price": 16500, "category": "Bebidas Calientes", "available": True},
    {"name": "Agua de panela Caliente Madre Mía", "description": "Panela Orgánica, jengibre, cúrcuma y limón mandarino", "price": 9000, "category": "Bebidas Calientes", "available": True},

    # --- BEBIDAS FRÍAS ---
    {"name": "Copa de Vino", "description": "Copa de vino de la casa", "price": 15000, "category": "Bebidas Frías", "available": True},
    {"name": "Ginger Ale (Canada Dry)", "description": "Gaseosa Ginger Ale", "price": 8000, "category": "Bebidas Frías", "available": True},
    {"name": "Coca Cola", "description": "Gaseosa tradicional", "price": 8400, "category": "Bebidas Frías", "available": True},
    {"name": "Té Hatsu", "description": "Té embotellado Hatsu", "price": 9000, "category": "Bebidas Frías", "available": True},
    {"name": "Agua Hatsu / Agua Hatsu con Gas", "description": "Agua mineral Hatsu con o sin gas", "price": 5500, "category": "Bebidas Frías", "available": True},
    {"name": "Bretaña", "description": "Agua de soda Bretaña", "price": 6500, "category": "Bebidas Frías", "available": True},
    {"name": "Bretaña + Limón Mandarino", "description": "Agua de soda Bretaña acompañada con limón mandarino", "price": 8500, "category": "Bebidas Frías", "available": True},
    {"name": "Sodas Tropicales", "description": "Sabores: Frutos Rojos / Frutos Verdes / Frutos Tropicales", "price": 18500, "category": "Bebidas Frías", "available": True},

    # --- POSTRES ---
    {"name": "Torta de Brownie", "description": "Deliciosa torta de brownie", "price": 10000, "category": "Postres", "available": True},
    {"name": "Torta de Arequipe", "description": "Deliciosa torta sabor a arequipe", "price": 13000, "category": "Postres", "available": True},

    # --- ADICIONES Y OTROS ---
    {"name": "Adición Básica", "description": "Madurito / Queso / Aguacate / Hogao", "price": 7000, "category": "Adiciones", "available": True},
    {"name": "Adición Premium", "description": "Costilla / Chorizo con panela / Pollo en salsa de tomates asados / Carne de Albóndiga con jengibre y aceite de coco", "price": 9000, "category": "Adiciones", "available": True},
    {"name": "Café en Grano x 500 gramos", "description": "Bolsa de café en grano para llevar", "price": 35000, "category": "Otros", "available": True},
]


def seed():
    # Make sure tables exist before inserting
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        names_in_menu = {entry["name"] for entry in MENU}
        created = 0
        updated = 0

        # Upsert: for each item, update it if it already exists (by name),
        # or create it if it's new. We never DELETE, so we don't break the
        # foreign key from past orders that reference a dish.
        for entry in MENU:
            existing = (
                db.query(models.MenuItem)
                .filter(models.MenuItem.name == entry["name"])
                .first()
            )
            if existing:
                for key, value in entry.items():
                    setattr(existing, key, value)  # actualiza precio, descripción, etc.
                updated += 1
            else:
                db.add(models.MenuItem(**entry))
                created += 1

        # Soft-delete: any dish that is no longer in MENU gets hidden
        # (available = False) instead of deleted, so order history stays intact.
        hidden = 0
        for item in db.query(models.MenuItem).all():
            if item.name not in names_in_menu:
                item.available = False
                hidden += 1

        db.commit()
        print(f"🌱 Menú actualizado: {created} nuevos, {updated} actualizados, {hidden} ocultados")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

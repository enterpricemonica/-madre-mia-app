import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import menu, tables, orders, auth, settings, payments, reports, health

# Automatically create all tables in PostgreSQL
Base.metadata.create_all(bind=engine)


# Mini-migración: agrega columnas nuevas a tablas que ya existen (idempotente).
# create_all NO modifica tablas viejas. Para proyectos grandes se usa Alembic;
# a esta escala, este ALTER ... IF NOT EXISTS basta y hace seguro el deploy.
def ensure_columns():
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS image_url VARCHAR"))
        conn.execute(text("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS featured BOOLEAN DEFAULT false"))
        conn.execute(text("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS stock INTEGER"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_type VARCHAR DEFAULT 'dine_in'"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS tip_amount INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE theme ADD COLUMN IF NOT EXISTS logo_url VARCHAR DEFAULT '/logo.jpeg'"))
        conn.execute(text("ALTER TABLE theme ADD COLUMN IF NOT EXISTS bold_enabled BOOLEAN DEFAULT false"))
        conn.execute(text("ALTER TABLE theme ADD COLUMN IF NOT EXISTS name VARCHAR DEFAULT 'Madre Mía'"))
        conn.execute(text("ALTER TABLE theme ADD COLUMN IF NOT EXISTS tagline VARCHAR DEFAULT 'Arepas con Café de Origen'"))
        conn.execute(text("ALTER TABLE theme ADD COLUMN IF NOT EXISTS welcome VARCHAR DEFAULT 'Bienvenido 🫓'"))
        conn.commit()


ensure_columns()


# Create the admin user on startup from env vars (only if it doesn't exist yet)
def seed_admin():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        return
    from database import SessionLocal
    from auth import hash_password
    db = SessionLocal()
    try:
        exists = db.query(models.User).filter(models.User.username == username).first()
        if not exists:
            db.add(models.User(username=username, hashed_password=hash_password(password)))
            db.commit()
    finally:
        db.close()


seed_admin()

app = FastAPI(title="Madre Mia API", version="1.0")

# CORS — allow external connections (e.g. the customer's phone) during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION ---
app.include_router(menu.router)
app.include_router(tables.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(settings.router)
app.include_router(payments.router)
app.include_router(reports.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "Welcome to Madre Mia API 🫓"}


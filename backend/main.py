import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import menu, tables, orders, auth, settings, payments, reports, health


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database when the server STARTS, not when this module is imported.

    These three calls used to run at import time, which meant `import main`
    connected to whatever database the environment pointed at and altered it.
    That made the real app impossible to import from a test, so the test suite
    built a parallel app out of routers instead — and therefore never covered
    the CORS policy, the router wiring, or any route declared on `app` itself.

    Moving them here keeps the behaviour identical in production (Uvicorn runs
    the lifespan on boot) while making the module safe to import.
    """
    Base.metadata.create_all(bind=engine)
    ensure_columns()
    seed_admin()
    yield


app = FastAPI(title="Madre Mia API", version="1.0", lifespan=lifespan)

# --- CORS ---
#
# `allow_origins=["*"]` together with `allow_credentials=True` is a trap. Starlette
# does not send a literal "*" in that case: it echoes back whatever Origin the
# request carried, alongside `Allow-Credentials: true`. The result is that every
# website on the internet holds an authenticated grant to this API.
#
# Today the damage is limited because auth is a Bearer token in a header, and one
# site cannot read another's localStorage. But the day anyone moves the token to a
# cookie — an ordinary change — the API becomes trivially exploitable, silently.
#
# So the two settings are derived together and cannot be combined dangerously:
# a wildcard never carries credentials, and credentials require an explicit list.
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins_env:
    ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
    ALLOW_CREDENTIALS = True      # an explicit allowlist can safely carry credentials
else:
    # No allowlist configured: stay open so a forgotten env var never takes the
    # restaurant offline, but refuse credentials so the grant is worthless to a
    # third-party site.
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
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


import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import menu, tables, orders, auth

# Automatically create all tables in PostgreSQL
Base.metadata.create_all(bind=engine)


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

@app.get("/")
def root():
    return {"message": "Welcome to Madre Mia API 🫓"}

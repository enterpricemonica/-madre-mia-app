from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import menu, tables, orders

# Automatically create all tables in PostgreSQL
Base.metadata.create_all(bind=engine)

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

@app.get("/")
def root():
    return {"message": "Welcome to Madre Mia API 🫓"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import menu

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Madre Mia API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(menu.router)

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a Madre Mia API 🫓"}
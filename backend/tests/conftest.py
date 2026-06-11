"""
Configuración de pruebas.

Idea clave: NO tocamos la base de datos real. Cada test corre contra una
SQLite EN MEMORIA, recién creada y desechada al terminar. Reemplazamos la
dependencia `get_db` de la app por una sesión apuntando a esa SQLite.
"""
import os
import sys

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Asegura que la carpeta backend esté en el path (imports planos: database, models, routers)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import models  # noqa: E402  (registra todas las tablas en Base.metadata)
from database import Base, get_db  # noqa: E402
from routers import orders as orders_router  # noqa: E402
from routers import menu as menu_router  # noqa: E402
from routers import payments as payments_router  # noqa: E402


@pytest.fixture()
def db_session():
    """Una SQLite en memoria por test (StaticPool = una sola conexión compartida)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """App de prueba con los routers reales, pero con get_db apuntando a la SQLite."""
    app = FastAPI()
    app.include_router(menu_router.router)
    app.include_router(orders_router.router)
    app.include_router(payments_router.router)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def seed_menu(db_session):
    """Platos de prueba (datos mock): uno normal, una adición y uno agotado."""
    arepa = models.MenuItem(name="Arepa Ocañera", price=13000, category="Arepas", available=True)
    queso = models.MenuItem(name="Adición Queso", price=3000, category="Adiciones", available=True)
    agotado = models.MenuItem(name="Postre Agotado", price=8000, category="Postres", available=False)
    db_session.add_all([arepa, queso, agotado])
    db_session.commit()
    for x in (arepa, queso, agotado):
        db_session.refresh(x)
    return {"arepa": arepa, "queso": queso, "agotado": agotado}


@pytest.fixture()
def seed_table(db_session):
    """Una mesa de prueba (número 5)."""
    table = models.Table(number=5)
    db_session.add(table)
    db_session.commit()
    db_session.refresh(table)
    return table

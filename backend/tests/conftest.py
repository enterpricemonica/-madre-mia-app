"""
Configuración de pruebas.

Idea clave: NO tocamos la base de datos real. Cada test corre contra una
SQLite EN MEMORIA, recién creada y desechada al terminar. Reemplazamos la
dependencia `get_db` de la app por una sesión apuntando a esa SQLite.

Las pruebas usan la app REAL (`main.app`), no una copia armada aquí. Antes se
construía una app paralela con unos cuantos routers, porque importar `main`
tocaba la base de datos al momento de importarse. Eso dejaba sin cubrir el
CORS, el registro de routers y cualquier ruta declarada sobre `app`. Desde que
esa preparación vive en el `lifespan`, importar `main` es seguro.

`TestClient(app)` sin `with` NO ejecuta el lifespan, así que las pruebas nunca
crean tablas ni siembran el admin en la base real.
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
from routers import reports as reports_router  # noqa: E402
from routers import health as health_router  # noqa: E402
from auth import get_current_user  # noqa: E402
import main  # noqa: E402  (seguro de importar: no toca la BD hasta el lifespan)


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


def _build_app(db_session, auth=True):
    """Devuelve un cliente sobre la app REAL, con get_db apuntando a la SQLite.

    `main.app` es un objeto único compartido por todas las pruebas, así que las
    sustituciones se limpian antes de cada una: si quedaran de la prueba
    anterior, una prueba podría pasar por la sesión equivocada o por un admin
    simulado que no pidió.
    """
    app = main.app
    app.dependency_overrides.clear()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    if auth:
        app.dependency_overrides[get_current_user] = lambda: "test-admin"
    return TestClient(app)


@pytest.fixture()
def client(db_session):
    """App de prueba con admin simulado (las rutas protegidas pasan)."""
    return _build_app(db_session, auth=True)


@pytest.fixture()
def client_no_auth(db_session):
    """App de prueba SIN simular login (para verificar que las rutas protegidas rechazan)."""
    return _build_app(db_session, auth=False)


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

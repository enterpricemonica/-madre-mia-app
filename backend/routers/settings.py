from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULTS = dict(
    primary="#c89b3c", secondary="#8a7f72", success="#4a9d5b", danger="#c0392b",
    warning="#e0a92e", info="#5b8fa3", light="#fdf6ea", dark="#211b14",
)


# Trae el tema (o lo crea con los valores por defecto la primera vez)
def get_or_create_theme(db: Session):
    theme = db.query(models.Theme).first()
    if not theme:
        theme = models.Theme(id=1, **DEFAULTS)
        db.add(theme)
        db.commit()
        db.refresh(theme)
    return theme


# GET /settings/theme — público (el cliente lo necesita para pintar la app)
@router.get("/theme", response_model=schemas.ThemeOut)
def get_theme(db: Session = Depends(get_db)):
    return get_or_create_theme(db)


# PUT /settings/theme — protegido (solo admin cambia los colores)
@router.put("/theme", response_model=schemas.ThemeOut,
            dependencies=[Depends(get_current_user)])
def update_theme(payload: schemas.ThemeUpdate, db: Session = Depends(get_db)):
    theme = get_or_create_theme(db)
    for key, value in payload.model_dump().items():
        setattr(theme, key, value)
    db.commit()
    db.refresh(theme)
    return theme

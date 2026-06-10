from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# POST /auth/login — verifica usuario/contraseña y devuelve un token
@router.post("/login", response_model=schemas.TokenOut)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()
    # Mismo mensaje si falla el usuario O la contraseña (no revelar cuál)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}

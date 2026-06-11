from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ── MENU ITEMS ──
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category: str
    available: bool = True
    image_url: Optional[str] = None
    featured: bool = False

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemOut(MenuItemBase):
    id: int
    class Config:
        from_attributes = True

# ── TABLES ──
class TableBase(BaseModel):
    number: int
    active: bool = True

class TableCreate(TableBase):
    pass

class TableOut(TableBase):
    id: int
    qr_code: Optional[str] = None
    class Config:
        from_attributes = True

# ── ORDER ITEMS ──
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = 1
    notes: Optional[str] = None

class OrderItemOut(BaseModel):
    id: int
    item_id: int
    name: Optional[str] = None  # nombre del plato (lo trae la propiedad del modelo)
    quantity: int
    notes: Optional[str] = None
    class Config:
        from_attributes = True

# ── ORDERS ──
class OrderCreate(BaseModel):
    table_id: int
    items: List[OrderItemCreate]

class OrderOut(BaseModel):
    id: int
    table_id: int
    status: str
    total: int
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True

# ── ORDER STATUS UPDATE ──
class OrderStatusUpdate(BaseModel):
    status: str

# ── AUTH ──
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ── THEME (colores configurables, estilo Bootstrap) ──
class ThemeOut(BaseModel):
    primary: str
    secondary: str
    success: str
    danger: str
    warning: str
    info: str
    light: str
    dark: str
    class Config:
        from_attributes = True

class ThemeUpdate(ThemeOut):
    pass

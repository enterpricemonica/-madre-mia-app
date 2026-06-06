from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ── MENU ITEMS ──
class MenuItemBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: int
    categoria: str
    disponible: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemOut(MenuItemBase):
    id: int
    class Config:
        from_attributes = True

# ── MESAS ──
class MesaBase(BaseModel):
    numero: int
    activa: bool = True

class MesaCreate(MesaBase):
    pass

class MesaOut(MesaBase):
    id: int
    qr_code: Optional[str] = None
    class Config:
        from_attributes = True

# ── PEDIDO ITEMS ──
class PedidoItemCreate(BaseModel):
    item_id: int
    cantidad: int = 1
    notas: Optional[str] = None

class PedidoItemOut(BaseModel):
    id: int
    item_id: int
    cantidad: int
    notas: Optional[str] = None
    class Config:
        from_attributes = True

# ── PEDIDOS ──
class PedidoCreate(BaseModel):
    mesa_id: int
    items: List[PedidoItemCreate]

class PedidoOut(BaseModel):
    id: int
    mesa_id: int
    estado: str
    total: int
    creado_en: datetime
    items: List[PedidoItemOut] = []
    class Config:
        from_attributes = True
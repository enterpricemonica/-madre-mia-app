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
    order_type: str = "dine_in"   # dine_in (comer aquí) / takeaway (para llevar)
    items: List[OrderItemCreate]

class OrderOut(BaseModel):
    id: int
    table_id: int
    status: str
    order_type: str
    is_paid: bool = False         # derivado del pago (no es un estado de cocina)
    total: int
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True

# ── ORDER STATUS UPDATE ──
class OrderStatusUpdate(BaseModel):
    status: str

# ── PAYMENTS ──
# El cliente solo manda a qué pedido y (opcional) con qué método quiere pagar.
# El MONTO nunca lo manda el cliente: se calcula en el servidor desde el pedido.
class PaymentCreate(BaseModel):
    order_id: int
    method: Optional[str] = None  # bre_b / nequi / card

class PaymentOut(BaseModel):
    id: int
    order_id: int
    provider: str
    method: Optional[str] = None
    amount: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# Respuesta al INICIAR el cobro: el pago + el QR dinámico a mostrar en pantalla.
class PaymentInitOut(PaymentOut):
    qr_url: Optional[str] = None

# Lo que manda la pasarela en el webhook (forma simplificada; se adapta a Bold real luego).
class PaymentWebhook(BaseModel):
    provider_ref: str
    status: str  # approved / declined

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

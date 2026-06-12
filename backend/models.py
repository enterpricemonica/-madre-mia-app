from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Table(Base):
    __tablename__ = "tables"

    id      = Column(Integer, primary_key=True, index=True)
    number  = Column(Integer, unique=True, nullable=False)
    qr_code = Column(String, nullable=True)
    active  = Column(Boolean, default=True)

    orders  = relationship("Order", back_populates="table")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price       = Column(Integer, nullable=False)
    category    = Column(String, nullable=False)
    available   = Column(Boolean, default=True)
    image_url   = Column(String, nullable=True)  # ruta/URL de la foto (opcional)
    featured    = Column(Boolean, default=False)  # plato estrella (⭐ Favorito)


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    table_id   = Column(Integer, ForeignKey("tables.id"))
    status     = Column(String, default="received")
    order_type = Column(String, default="dine_in")  # dine_in (comer aquí) / takeaway (para llevar)
    total      = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    table      = relationship("Table", back_populates="orders")
    items      = relationship("OrderItem", back_populates="order")
    payments   = relationship("Payment", back_populates="order")  # puede haber varios intentos

    # "Pagado" se DERIVA de los pagos (pista aparte del flujo de cocina): basta uno aprobado.
    @property
    def is_paid(self):
        return any(p.status == "approved" for p in self.payments)


class OrderItem(Base):
    __tablename__ = "order_items"

    id        = Column(Integer, primary_key=True, index=True)
    order_id  = Column(Integer, ForeignKey("orders.id"))
    item_id   = Column(Integer, ForeignKey("menu_items.id"))
    quantity  = Column(Integer, default=1)
    notes     = Column(String, nullable=True)

    order     = relationship("Order", back_populates="items")
    item      = relationship("MenuItem")

    # Propiedad: el nombre del plato (leído desde la relación con MenuItem).
    # Así la cocina ve "Vegetariana" en vez de solo "item 14".
    @property
    def name(self):
        return self.item.name if self.item else None


class Payment(Base):
    __tablename__ = "payments"

    id           = Column(Integer, primary_key=True, index=True)
    order_id     = Column(Integer, ForeignKey("orders.id"), nullable=False)
    provider     = Column(String, default="bold")     # pasarela usada (por ahora: bold)
    provider_ref = Column(String, nullable=True)       # id de la transacción en la pasarela (casa el webhook)
    method       = Column(String, nullable=True)       # bre_b / nequi / card (lo elige el cliente)
    amount       = Column(Integer, nullable=False)     # monto cobrado en COP (enteros, sin decimales)
    status       = Column(String, default="pending")   # pending → approved / declined
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order        = relationship("Order", back_populates="payments")


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Theme(Base):
    __tablename__ = "theme"

    id        = Column(Integer, primary_key=True, index=True)  # siempre 1 (fila única)
    primary   = Column(String, default="#d9622b")
    secondary = Column(String, default="#8a7f76")
    success   = Column(String, default="#27ae60")
    danger    = Column(String, default="#c0392b")
    warning   = Column(String, default="#e0b13f")
    info      = Column(String, default="#3498db")
    light     = Column(String, default="#fff8f0")
    dark      = Column(String, default="#2e2a26")
    logo_url  = Column(String, default="/logo.jpeg")  # ruta/URL del logo (editable desde admin)

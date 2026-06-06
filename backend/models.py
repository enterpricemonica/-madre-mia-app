from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Mesa(Base):
    __tablename__ = "mesas"

    id         = Column(Integer, primary_key=True, index=True)
    numero     = Column(Integer, unique=True, nullable=False)
    qr_code    = Column(String, nullable=True)
    activa     = Column(Boolean, default=True)

    pedidos    = relationship("Pedido", back_populates="mesa")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio      = Column(Integer, nullable=False)
    categoria   = Column(String, nullable=False)
    disponible  = Column(Boolean, default=True)


class Pedido(Base):
    __tablename__ = "pedidos"

    id         = Column(Integer, primary_key=True, index=True)
    mesa_id    = Column(Integer, ForeignKey("mesas.id"))
    estado     = Column(String, default="recibido")
    total      = Column(Integer, default=0)
    creado_en  = Column(DateTime, default=datetime.utcnow)

    mesa       = relationship("Mesa", back_populates="pedidos")
    items      = relationship("PedidoItem", back_populates="pedido")


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id         = Column(Integer, primary_key=True, index=True)
    pedido_id  = Column(Integer, ForeignKey("pedidos.id"))
    item_id    = Column(Integer, ForeignKey("menu_items.id"))
    cantidad   = Column(Integer, default=1)
    notas      = Column(String, nullable=True)

    pedido     = relationship("Pedido", back_populates="items")
    item       = relationship("MenuItem")
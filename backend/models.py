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


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    table_id   = Column(Integer, ForeignKey("tables.id"))
    status     = Column(String, default="received")
    total      = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    table      = relationship("Table", back_populates="orders")
    items      = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id        = Column(Integer, primary_key=True, index=True)
    order_id  = Column(Integer, ForeignKey("orders.id"))
    item_id   = Column(Integer, ForeignKey("menu_items.id"))
    quantity  = Column(Integer, default=1)
    notes     = Column(String, nullable=True)

    order     = relationship("Order", back_populates="items")
    item      = relationship("MenuItem")

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .db import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)

    cliente_nombre = Column(String, nullable=False)
    mesa = Column(String, nullable=True)

    estado = Column(String, default="abierta")

    fecha_apertura = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pedidos = relationship("Pedido", back_populates="cuenta")
    factura = relationship("Factura", back_populates="cuenta", uselist=False)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)

    cuenta_id = Column(Integer, ForeignKey("cuentas.id"))

    producto = Column(String)
    precio = Column(Float)
    cantidad = Column(Integer)

    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cuenta = relationship("Cuenta", back_populates="pedidos")


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)

    cuenta_id = Column(Integer, ForeignKey("cuentas.id"))

    total = Column(Float)

    estado = Column(String)  # pagada | pendiente

    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cuenta = relationship("Cuenta", back_populates="factura")

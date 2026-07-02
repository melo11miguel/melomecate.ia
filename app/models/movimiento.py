from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(DateTime, nullable=False, default=func.now())
    tipo = Column(String(10), nullable=False)  # "gasto" o "ingreso"
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(5), default="COP")
    observaciones = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="movimientos")
    categoria = relationship("Categoria", back_populates="movimientos")

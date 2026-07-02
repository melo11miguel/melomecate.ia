from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True, nullable=False)
    color = Column(String(20), default="#d1d4dc")

    # Relaciones
    movimientos = relationship("Movimiento", back_populates="categoria")

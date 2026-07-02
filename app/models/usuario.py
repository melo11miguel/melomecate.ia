import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    fecha_nacimiento = Column(String(20), nullable=True)
    
    # Seguridad
    contrasena_hash = Column(String(255), nullable=False)
    totp_secret = Column(String(100), nullable=True)
    totp_activo = Column(Boolean, default=False)
    intentos_fallidos = Column(Integer, default=0)
    bloqueo_hasta = Column(DateTime, nullable=True)
    
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    movimientos = relationship("Movimiento", back_populates="usuario", cascade="all, delete-orphan")
    otps_usados = relationship("OTPUsado", back_populates="usuario", cascade="all, delete-orphan")

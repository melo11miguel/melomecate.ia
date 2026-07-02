from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class OTPUsado(Base):
    __tablename__ = "otp_usados"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    otp_code = Column(String(10), nullable=False)
    usado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="otps_usados")

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.categoria import CategoriaResponse

class MovimientoBase(BaseModel):
    tipo: str = Field(..., pattern="^(gasto|ingreso)$")
    descripcion: str
    monto: float
    moneda: str = "COP"
    observaciones: Optional[str] = None
    categoria_id: Optional[int] = None
    fecha: Optional[datetime] = None

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoResponse(MovimientoBase):
    id: int
    usuario_id: int
    creado_en: datetime
    categoria: Optional[CategoriaResponse] = None

    class Config:
        from_attributes = True

class MovimientoNLPRequest(BaseModel):
    texto: str

class MovimientoNLPResponse(BaseModel):
    tipo: str
    categoria: str
    descripcion: str
    valor: float
    moneda: str = "COP"

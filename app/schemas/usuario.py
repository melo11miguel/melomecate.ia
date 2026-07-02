from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id: int
    totp_activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True

class UsuarioRegisterResponse(UsuarioResponse):
    totp_secret: str

class LoginRequest(BaseModel):
    email: EmailStr
    contrasena: str
    otp_code: str

class TokenResponse(BaseModel):
    token: str
    usuario: UsuarioResponse

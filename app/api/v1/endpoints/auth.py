from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioRegisterResponse, LoginRequest, TokenResponse
from app.services import usuario_service, security_service

router = APIRouter()

class Activate2FARequest(BaseModel):
    email: str
    otp_code: str

@router.post("/register", response_model=UsuarioRegisterResponse)
def register(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    success, result = usuario_service.crear_usuario(db, usuario_in)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    # Retornamos el usuario con el secreto TOTP para que el frontend pueda mostrar el QR
    # Aunque en producción, la respuesta del API de registro devuelve el secreto
    # para que Streamlit genere el código QR por primera vez.
    db_usuario = result
    response_data = UsuarioResponse.from_attributes(db_usuario)
    # Adjuntamos el secreto de manera temporal para la configuración inicial
    return response_data

@router.post("/activate-2fa")
def activate_2fa(payload: Activate2FARequest, db: Session = Depends(get_db)):
    usuario = usuario_service.obtener_usuario_por_email(db, payload.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    if usuario.totp_activo:
        return {"message": "El doble factor (2FA) ya se encuentra activo."}
        
    # Verificar el primer código OTP para activar
    if security_service.verificar_totp(usuario.totp_secret, payload.otp_code):
        usuario_service.activar_totp(db, usuario.id)
        return {"message": "Doble factor (2FA) activado correctamente."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación incorrecto."
        )

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    res_auth, detail = usuario_service.autenticar_usuario(
        db, payload.email, payload.contrasena, payload.otp_code
    )
    
    if res_auth != usuario_service.ResultadoAuth.OK:
        status_code = status.HTTP_401_UNAUTHORIZED
        if res_auth == usuario_service.ResultadoAuth.BLOQUEADO:
            status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(
            status_code=status_code,
            detail=detail
        )
        
    usuario = detail
    usuario_data = {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "fecha_nacimiento": usuario.fecha_nacimiento
    }
    
    # Generar token
    token = security_service.crear_token_sesion(usuario_data)
    
    # Establecer la cookie de sesión para compatibilidad directa con Streamlit
    response.set_cookie(
        key="session_token", 
        value=token, 
        httponly=True, 
        max_age=8 * 3600,
        samesite="lax"
    )
    
    return {
        "token": token,
        "usuario": UsuarioResponse.from_attributes(usuario)
    }

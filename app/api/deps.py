from fastapi import Depends, HTTPException, status, Header, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services import security_service, usuario_service
from app.models.usuario import Usuario

def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
) -> Usuario:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif session_token:
        token = session_token
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionaron credenciales de sesión."
        )
        
    usuario_data = security_service.leer_token_sesion(token)
    if not usuario_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada. Inicia sesión de nuevo."
        )
        
    usuario = usuario_service.obtener_usuario_por_email(db, usuario_data["email"])
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado."
        )
    return usuario

import datetime
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.usuario import Usuario
from app.models.otp_usado import OTPUsado
from app.schemas.usuario import UsuarioCreate
from app.services import security_service

class ResultadoAuth(str, Enum):
    OK = "OK"
    CREDENCIALES_INVALIDAS = "CREDENCIALES_INVALIDAS"
    BLOQUEADO = "BLOQUEADO"
    OTP_REPLAY = "OTP_REPLAY"
    OTP_INVALIDO = "OTP_INVALIDO"
    OTP_NO_CONFIG = "OTP_NO_CONFIG"
    USUARIO_NO_EXISTE = "USUARIO_NO_EXISTE"

# Límite de intentos y tiempo de bloqueo (5 minutos)
MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 5

def obtener_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email.lower().strip()).first()

def crear_usuario(db: Session, usuario_in: UsuarioCreate) -> tuple[bool, str | Usuario]:
    """Crea un nuevo usuario en la base de datos y retorna su secreto TOTP inicial para configuración."""
    email_limpio = usuario_in.email.lower().strip()
    
    # Verificar si el usuario ya existe
    existe = obtener_usuario_por_email(db, email_limpio)
    if existe:
        return False, "El correo electrónico ya está registrado."
    
    # Hashear contraseña
    pwd_hash = security_service.hash_contrasena(usuario_in.contrasena)
    totp_sec = security_service.generar_secreto_totp()

    db_usuario = Usuario(
        nombre=usuario_in.nombre.strip(),
        email=email_limpio,
        telefono=usuario_in.telefono,
        fecha_nacimiento=usuario_in.fecha_nacimiento,
        contrasena_hash=pwd_hash,
        totp_secret=totp_sec,
        totp_activo=False
    )
    
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return True, db_usuario
    except Exception as e:
        db.rollback()
        return False, f"Error al registrar el usuario: {str(e)}"

def activar_totp(db: Session, usuario_id: int) -> bool:
    """Activa el TOTP (2FA) para el usuario especificado."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario:
        usuario.totp_activo = True
        db.commit()
        return True
    return False

def autenticar_usuario(db: Session, email: str, contrasena: str, otp_code: str) -> tuple[ResultadoAuth, str | Usuario]:
    """
    Autentica al usuario verificando credenciales, bloqueos, TOTP y replay-attacks de OTP.
    """
    usuario = obtener_usuario_por_email(db, email)
    if not usuario:
        return ResultadoAuth.USUARIO_NO_EXISTE, "El usuario no existe."

    ahora = datetime.datetime.now()

    # 1. Verificar si está bloqueado por intentos fallidos
    if usuario.bloqueo_hasta and usuario.bloqueo_hasta > ahora:
        minutos_restantes = int((usuario.bloqueo_hasta - ahora).total_seconds() / 60) + 1
        return ResultadoAuth.BLOQUEADO, f"Cuenta bloqueada temporalmente. Intenta de nuevo en {minutos_restantes} minuto(s)."

    # 2. Verificar la contraseña
    if not security_service.verificar_contrasena(contrasena, usuario.contrasena_hash):
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= MAX_INTENTOS:
            usuario.bloqueo_hasta = ahora + datetime.timedelta(minutes=MINUTOS_BLOQUEO)
            db.commit()
            return ResultadoAuth.BLOQUEADO, f"Demasiados intentos fallidos. Cuenta bloqueada por {MINUTOS_BLOQUEO} minutos."
        db.commit()
        intentos_restantes = MAX_INTENTOS - usuario.intentos_fallidos
        return ResultadoAuth.CREDENCIALES_INVALIDAS, f"Contraseña incorrecta. Te quedan {intentos_restantes} intentos."

    # 3. Verificar si el 2FA está configurado
    if not usuario.totp_activo:
        return ResultadoAuth.OTP_NO_CONFIG, "El doble factor (2FA) no ha sido configurado."

    # 4. Verificar replay attack del código OTP (reutilización)
    otp_usado = db.query(OTPUsado).filter(
        OTPUsado.usuario_id == usuario.id,
        OTPUsado.otp_code == otp_code
    ).first()
    
    if otp_usado:
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= MAX_INTENTOS:
            usuario.bloqueo_hasta = ahora + datetime.timedelta(minutes=MINUTOS_BLOQUEO)
        db.commit()
        return ResultadoAuth.OTP_REPLAY, "Este código OTP ya fue utilizado. Espera a que se genere uno nuevo."

    # 5. Verificar código OTP
    if not security_service.verificar_totp(usuario.totp_secret, otp_code):
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= MAX_INTENTOS:
            usuario.bloqueo_hasta = ahora + datetime.timedelta(minutes=MINUTOS_BLOQUEO)
            db.commit()
            return ResultadoAuth.BLOQUEADO, f"Demasiados intentos fallidos. Cuenta bloqueada por {MINUTOS_BLOQUEO} minutos."
        db.commit()
        intentos_restantes = MAX_INTENTOS - usuario.intentos_fallidos
        return ResultadoAuth.OTP_INVALIDO, f"Código OTP incorrecto. Te quedan {intentos_restantes} intentos."

    # 6. Éxito: Resetear intentos fallidos y registrar el OTP como usado
    usuario.intentos_fallidos = 0
    usuario.bloqueo_hasta = None
    
    nuevo_otp_usado = OTPUsado(usuario_id=usuario.id, otp_code=otp_code)
    db.add(nuevo_otp_usado)
    db.commit()
    
    return ResultadoAuth.OK, usuario

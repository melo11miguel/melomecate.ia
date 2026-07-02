import bcrypt
import pyotp
import json
import time
from cryptography.fernet import Fernet
from app.core.config import settings

# Inicializar Fernet con la clave secreta persistente en .env
_fernet = Fernet(settings.FERNET_KEY.encode())

def hash_contrasena(contrasena: str) -> str:
    """Genera el hash bcrypt de la contraseña con factor 8."""
    salt = bcrypt.gensalt(8)
    return bcrypt.hashpw(contrasena.encode(), salt).decode()

def verificar_contrasena(contrasena: str, contrasena_hash: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    try:
        return bcrypt.checkpw(contrasena.encode(), contrasena_hash.encode())
    except Exception:
        return False

def generar_secreto_totp() -> str:
    """Genera una clave secreta aleatoria Base32 para TOTP."""
    return pyotp.random_base32()

def verificar_totp(secreto: str, codigo: str) -> bool:
    """Verifica un código de verificación TOTP de 6 dígitos."""
    try:
        totp = pyotp.TOTP(secreto)
        return totp.verify(codigo, valid_window=1)
    except Exception:
        return False

def crear_token_sesion(usuario_data: dict, ttl_seg: int = 8 * 3600) -> str:
    """Cifra el payload del usuario para almacenarlo en una cookie."""
    payload = {
        "u": usuario_data,
        "exp": time.time() + ttl_seg
    }
    return _fernet.encrypt(json.dumps(payload).encode()).decode()

def leer_token_sesion(token: str) -> dict | None:
    """Descifra el token y retorna los datos del usuario si no ha expirado."""
    try:
        payload = json.loads(_fernet.decrypt(token.encode()))
        if time.time() > payload.get("exp", 0):
            return None
        return payload["u"]
    except Exception:
        return None

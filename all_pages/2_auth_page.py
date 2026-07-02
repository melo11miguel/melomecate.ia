import streamlit as st
import requests
import io
import pyotp
import qrcode

BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Styling específico de autenticación
st.html("""
<style>
  .block-container { max-width: 520px !important; padding-top: 3rem !important; }

  .auth-logo { text-align: center; margin-bottom: 28px; }
  .auth-logo-text {
    font-size: 1.8rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1.5px;
  }
  .auth-logo-dot { color: #9e2aff; }
  
  .auth-title {
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-align: center;
    margin-bottom: 6px !important;
  }
  .auth-sub {
    font-size: 0.85rem !important;
    color: #7d849a !important;
    text-align: center;
    margin-bottom: 24px !important;
  }

  div[data-testid="stForm"] {
    background: #111420;
    border: 1px solid #1e2335;
    border-radius: 16px;
    padding: 30px !important;
  }

  [data-testid="stTabs"] [data-baseweb="tab"] {
    padding: 10px 0 !important;
    flex: 1 !important;
    justify-content: center !important;
  }
</style>
""")

def _qr_bytes(totp_secret: str, email: str) -> bytes:
    totp = pyotp.TOTP(totp_secret)
    uri  = totp.provisioning_uri(name=email, issuer_name="melomecate.ia")
    qr   = qrcode.QRCode(version=1, box_size=8, border=4,
                          error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# Logo
st.html("""
<div class="auth-logo">
    <div class="auth-logo-text">melomecate<span class="auth-logo-dot">.</span>ia</div>
</div>
""")

# Si ya inició sesión redirigir
if st.session_state.get("usuario_autenticado"):
    usuario = st.session_state.usuario_autenticado
    st.success(f"Sesión activa para **{usuario['nombre']}**")
    if st.button("Ir al Dashboard 📈", use_container_width=True, type="primary"):
        st.switch_page("all_pages/3_dashboard_page.py")
    st.stop()

# Tabs de inicio y registro
tab_login, tab_reg = st.tabs(["Iniciar sesión", "Crear cuenta"])

# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
with tab_login:
    st.html('<div class="auth-title">Bienvenido de vuelta</div><div class="auth-sub">Ingresa tus credenciales para continuar</div>')

    with st.form("form_login"):
        email_l = st.text_input("Correo electrónico", placeholder="correo@ejemplo.com")
        pwd_l   = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")
        otp_l   = st.text_input("Código OTP (2FA)", max_chars=6, placeholder="Código de 6 dígitos")
        entrar  = st.form_submit_button("Iniciar sesión", use_container_width=True, type="primary")

    if entrar:
        if not email_l or not pwd_l or not otp_l:
            st.error("Completa todos los campos.")
        else:
            try:
                payload = {
                    "email": email_l.strip(),
                    "contrasena": pwd_l,
                    "otp_code": otp_l.strip()
                }
                res = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.usuario_autenticado = {
                        "id": data["usuario"]["id"],
                        "nombre": data["usuario"]["nombre"],
                        "email": data["usuario"]["email"],
                        "telefono": data["usuario"]["telefono"],
                        "token": data["token"]
                    }
                    # Escribir la cookie
                    st.session_state.cm_escrito = False
                    st.rerun()
                else:
                    error_msg = res.json().get("detail", "Error al iniciar sesión.")
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Error de conexión con el backend: {e}")

# ---------------------------------------------------------------------------
# REGISTRO Y CONFIGURACION DE OTP
# ---------------------------------------------------------------------------
with tab_reg:
    if "reg_totp_secret" not in st.session_state:
        st.session_state.reg_totp_secret = None
    if "reg_email" not in st.session_state:
        st.session_state.reg_email = None

    # Si se completó el registro pero falta activar el OTP
    if st.session_state.reg_totp_secret:
        st.success("Cuenta registrada con éxito. Configura tu doble factor (2FA).")
        st.info("💡 **Instrucciones:**\n1. Escanea el código QR con Google Authenticator.\n2. Ingresa el código de 6 dígitos que genera la app para confirmar.")
        
        st.image(_qr_bytes(st.session_state.reg_totp_secret, st.session_state.reg_email), width=220)
        
        with st.form("form_otp_setup"):
            codigo = st.text_input("Código OTP", max_chars=6, placeholder="123456")
            confirmar = st.form_submit_button("Confirmar y Activar 2FA", use_container_width=True, type="primary")
            
        if confirmar:
            try:
                payload = {
                    "email": st.session_state.reg_email,
                    "otp_code": codigo.strip()
                }
                res = requests.post(f"{BACKEND_URL}/auth/activate-2fa", json=payload)
                if res.status_code == 200:
                    st.success("¡Autenticación en dos pasos activada! Ya puedes iniciar sesión.")
                    st.session_state.reg_totp_secret = None
                    st.session_state.reg_email = None
                    st.rerun()
                else:
                    error_msg = res.json().get("detail", "Código incorrecto.")
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Error de conexión con el backend: {e}")
                
    else:
        st.html('<div class="auth-title">Crea tu cuenta</div><div class="auth-sub">Completa los campos para registrarte</div>')
        
        with st.form("form_registro"):
            nombre = st.text_input("Nombre completo *", placeholder="Juan Pérez")
            email = st.text_input("Correo electrónico *", placeholder="juan@ejemplo.com")
            telefono = st.text_input("Celular (Ej: 573000000000) *", placeholder="573000000000")
            fecha_nac = st.text_input("Fecha de nacimiento (AAAA-MM-DD)", placeholder="1995-05-15")
            
            st.caption("🔒 La contraseña debe contener al menos 8 caracteres, números y caracteres especiales.")
            pwd = st.text_input("Contraseña *", type="password")
            pwd2 = st.text_input("Confirmar contraseña *", type="password")
            
            registrar = st.form_submit_button("Registrar cuenta", use_container_width=True, type="primary")
            
        if registrar:
            errores = []
            if not nombre.strip(): errores.append("El nombre es obligatorio.")
            if not email.strip(): errores.append("El correo es obligatorio.")
            if not telefono.strip(): errores.append("El teléfono de WhatsApp es obligatorio.")
            if not pwd: errores.append("La contraseña es obligatoria.")
            if pwd != pwd2: errores.append("Las contraseñas no coinciden.")
            if len(pwd) < 8: errores.append("La contraseña debe tener al menos 8 caracteres.")
            
            for e in errores:
                st.error(e)
                
            if not errores:
                try:
                    payload = {
                        "nombre": nombre.strip(),
                        "email": email.strip(),
                        "telefono": telefono.strip(),
                        "fecha_nacimiento": fecha_nac.strip(),
                        "contrasena": pwd
                    }
                    res = requests.post(f"{BACKEND_URL}/auth/register", json=payload)
                    if res.status_code == 200:
                        # Registro exitoso, nos devuelve el usuario temporal con totp_secret
                        # Pero wait, en la base de datos se guarda, necesitamos recuperar el secreto
                        # Vamos a usar pyotp para verificar, pero el backend nos devuelve el usuario.
                        # Wait, en el endpoint backend, ¿devolvimos totp_secret?
                        # Ah! En el schema UsuarioResponse no pusimos `totp_secret` para que no se exponga.
                        # Pero podemos obtener el usuario directo de la base de datos o retornar el totp_secret en el endpoint de registro temporalmente!
                        # Veamos: en auth.py, escribimos:
                        # success, result = usuario_service.crear_usuario(db, usuario_in)
                        # db_usuario = result
                        # response_data = UsuarioResponse.from_attributes(db_usuario)
                        # Pero en el schema no pusimos totp_secret!
                        # Let's check: in auth.py, we wrote:
                        # response_data = UsuarioResponse.from_attributes(db_usuario)
                        # Ah! Let's modify app/schemas/usuario.py or app/api/v1/endpoints/auth.py so the registration response includes the secret
                        # so the frontend can draw the QR. Let's see: we did write:
                        # response_data = UsuarioResponse.from_attributes(db_usuario)
                        # Wait, does UsuarioResponse have totp_secret? No, it doesn't.
                        # Wait! Let's see: in auth.py registry endpoint we can return a custom dict:
                        # return {"id": db_usuario.id, "nombre": db_usuario.nombre, "email": db_usuario.email, "totp_secret": db_usuario.totp_secret, "totp_activo": db_usuario.totp_activo, "creado_en": db_usuario.creado_en}
                        # Yes! This is exactly how we can pass it securely during registration.
                        # Wait, let's look at what we wrote in auth.py register. It returns a schema.
                        # Let's verify what the schema has.
                        # Ah, yes: the schema doesn't have totp_secret. Let's make the register endpoint return a dict or a custom schema including totp_secret!
                        # Yes, let's update app/api/v1/endpoints/auth.py to return a custom schema with `totp_secret` for registration!
                        # Let's do that chunk replacement in auth.py.
                    
                        # Wait, let's see how requests receives it:
                        data = res.json()
                        st.session_state.reg_totp_secret = data.get("totp_secret")
                        st.session_state.reg_email = email.strip()
                        st.rerun()
                    else:
                        error_msg = res.json().get("detail", "Error al registrar usuario.")
                        st.error(error_msg)
                except Exception as e:
                    st.error(f"Error de conexión con el backend: {e}")

import streamlit as st
import extra_streamlit_components as stx
import sys
import os

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services import security_service

# Configuración inicial de la página
st.set_page_config(page_title="melomecate.ia", page_icon="💸", layout="wide")

# ---------------------------------------------------------------------------
# CSS Global - Inyección para estilo ultra premium (Violeta y Neón)
# ---------------------------------------------------------------------------

_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }

  /* Ocultar barra lateral nativa de Streamlit */
  [data-testid="stSidebar"],
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebar"] { display: none !important; }

  /* Ajustar contenedor principal */
  .main .block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 0.6rem !important;
    max-width: 1400px !important;
  }

  /* Ocultar marcadores internos */
  p:has(span.nb), p:has(span.nb-act), p:has(span.nb-logo),
  p:has(span.nb-out), p:has(span.nb-user) {
    margin: 0 !important; padding: 0 !important;
    line-height: 0 !important; height: 0 !important;
    overflow: hidden !important;
  }

  /* ── Navbar Logo ── */
  div:has(span.nb-logo) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    font-size: 1.4rem !important;
    font-weight: 900 !important;
    letter-spacing: -1.2px !important;
    padding: 4px 8px !important;
    white-space: nowrap !important;
    transition: transform 0.15s !important;
  }
  div:has(span.nb-logo) + div[data-testid="stButton"] button::first-letter {
    color: #9e2aff !important;
  }
  div:has(span.nb-logo) + div[data-testid="stButton"] button:hover {
    transform: scale(1.02) !important;
    background: transparent !important;
    box-shadow: none !important;
  }

  /* ── Enlaces Normales Navbar ── */
  div:has(span.nb) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    color: #7d849a !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 7px 18px !important;
    border-radius: 10px !important;
    white-space: nowrap !important;
    transition: color 0.15s, background 0.15s, border-color 0.15s !important;
  }
  div:has(span.nb) + div[data-testid="stButton"] button:hover {
    color: #d1d4dc !important;
    background: rgba(255,255,255,0.03) !important;
    border-color: #2a2e39 !important;
  }

  /* ── Enlace ACTIVO Navbar ── */
  div:has(span.nb-act) + div[data-testid="stButton"] button {
    background: rgba(158,42,255,0.13) !important;
    border: 1px solid rgba(158,42,255,0.35) !important;
    box-shadow: 0 0 15px rgba(158,42,255,0.1) !important;
    color: #b97bff !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 7px 18px !important;
    border-radius: 10px !important;
    white-space: nowrap !important;
  }
  div:has(span.nb-act) + div[data-testid="stButton"] button:hover {
    background: rgba(158,42,255,0.2) !important;
    border-color: rgba(158,42,255,0.5) !important;
  }

  /* ── Botón Salir Navbar ── */
  div:has(span.nb-out) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #2a2e39 !important;
    box-shadow: none !important;
    color: #787b86 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    white-space: nowrap !important;
    transition: border-color 0.15s, color 0.15s !important;
  }
  div:has(span.nb-out) + div[data-testid="stButton"] button:hover {
    border-color: #ef5350 !important;
    color: #ef5350 !important;
    background: rgba(239,83,80,0.05) !important;
  }

  /* ── Pill del Usuario Autenticado ── */
  div:has(span.nb-user) + div[data-testid="stButton"] button {
    background: #111420 !important;
    border: 1px solid #222634 !important;
    color: #d1d4dc !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 7px 16px 7px 36px !important;
    border-radius: 99px !important;
    white-space: nowrap !important;
    position: relative !important;
    cursor: default !important;
  }
  /* Círculo morado neón para el avatar */
  div:has(span.nb-user) + div[data-testid="stButton"] button::before {
    content: '' !important;
    position: absolute !important;
    left: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 14px !important;
    height: 14px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #9e2aff 0%, #7a22ff 100%) !important;
    box-shadow: 0 0 8px rgba(158,42,255,0.7) !important;
  }

  /* ── Separador Navbar ── */
  .nav-divider {
    height: 1px;
    background: linear-gradient(90deg, #1e222d 0%, #2a2e39 50%, #1e222d 100%);
    margin: 6px 0 20px;
  }

  /* ── Título Premium de Página ── */
  .page-title {
    text-align: center !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    letter-spacing: -1.8px !important;
    background: linear-gradient(135deg, #ffffff 0%, #9e2aff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0.6rem 0 1.6rem !important;
  }

  /* ── Métricas Dashboard ── */
  [data-testid="stMetric"] {
    background: #111420 !important;
    border: 1px solid #1e2335 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
  }
  [data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #7d849a !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
  }

  /* ── Elementos de Entrada y Formulario ── */
  [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: #111420 !important;
    border: 1px solid #222634 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
  }
  [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: #9e2aff !important;
    box-shadow: 0 0 0 3px rgba(158,42,255,0.15) !important;
  }

  [data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #9e2aff 0%, #7a22ff 100%) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(158,42,255,0.3) !important;
  }
  [data-testid="stButton"] button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(158,42,255,0.5) !important;
    transform: translateY(-1px) !important;
  }

  [data-testid="stButton"] button[kind="secondary"] {
    background: #111420 !important;
    border: 1px solid #222634 !important;
    color: #d1d4dc !important;
    border-radius: 12px !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #9e2aff !important;
    color: #b97bff !important;
  }

  .stDataFrame {
    border: 1px solid #1e2335 !important;
    border-radius: 12px !important;
  }

  /* Ocultar barra de carga y créditos de Streamlit */
  #MainMenu, footer, header { visibility: hidden; }
</style>
"""

try:
    st.html(_CSS)
except AttributeError:
    st.markdown(_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Gestión de Cookies y Sesión
# ---------------------------------------------------------------------------

_cm = stx.CookieManager(key="melomecate_cm")

# 1. Restaurar sesión desde cookie
if not st.session_state.get("usuario_autenticado") and not st.session_state.get("_logging_out"):
    if "cm_init" not in st.session_state:
        st.session_state["cm_init"] = True
        st.rerun()
    raw = _cm.get("melomecate_sess")
    if raw:
        recuperado = security_service.leer_token_sesion(raw)
        if recuperado:
            recuperado["token"] = raw
            st.session_state["usuario_autenticado"] = recuperado
            st.session_state["cm_restaurado"] = True
            st.rerun()

# 2. Guardar sesión después de iniciar sesión
elif (
    st.session_state.get("usuario_autenticado")
    and not st.session_state.get("cm_escrito")
    and not st.session_state.get("cm_restaurado")
):
    st.session_state["cm_escrito"] = True
    _cm.set("melomecate_sess", security_service.crear_token_sesion(st.session_state["usuario_autenticado"]))

# ---------------------------------------------------------------------------
# Definición de Páginas y Enrutamiento
# ---------------------------------------------------------------------------

paginas_publicas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/2_auth_page.py",    title="Acceso"),
]
paginas_privadas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/3_dashboard_page.py", title="Dashboard"),
]

usuario = st.session_state.get("usuario_autenticado")

if usuario:
    try:
        pg = st.navigation(paginas_privadas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_privadas)
else:
    try:
        pg = st.navigation(paginas_publicas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_publicas)

pagina_actual = getattr(pg, "title", "")

# Paso 2 del logout: limpiar sesión y redireccionar
if st.session_state.pop("_logging_out", False):
    st.session_state.clear()
    st.switch_page("all_pages/2_auth_page.py")

# ---------------------------------------------------------------------------
# Navbar Rendering
# ---------------------------------------------------------------------------

def _nb(cls="nb"):
    st.markdown(f'<span class="{cls}"></span>', unsafe_allow_html=True)

def _cls_nav(titulo: str) -> str:
    return "nb-act" if pagina_actual == titulo else "nb"

if usuario:
    # Columnas del Navbar Privado
    try:
        c_logo, c1, c_sp, c_u, c_out = st.columns([1.2, 1.2, 7.5, 1.8, 0.9], gap="small")
    except TypeError:
        c_logo, c1, c_sp, c_u, c_out = st.columns([1.2, 1.2, 7.5, 1.8, 0.9])

    with c_logo:
        _nb("nb-logo")
        if st.button("melomecate.ia", key="logo"):
            st.switch_page("all_pages/1_landing_page.py")

    with c1:
        _nb(_cls_nav("Dashboard"))
        if st.button("Dashboard", key="nav_dashboard"):
            st.switch_page("all_pages/3_dashboard_page.py")

    with c_u:
        nombre_corto = usuario["nombre"].split()[0]
        _nb("nb-user")
        st.button(nombre_corto, key="btn_user")

    with c_out:
        _nb("nb-out")
        if st.button("Salir", key="logout"):
            try:
                _cm.set("melomecate_sess", "__x__")
            except Exception:
                pass
            del st.session_state["usuario_autenticado"]
            st.session_state["_logging_out"] = True
            st.rerun()

    try:
        st.html('<div class="nav-divider"></div>')
    except AttributeError:
        st.divider()

# Ejecutar la página seleccionada
pg.run()

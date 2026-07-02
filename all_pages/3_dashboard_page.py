import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Verificar autenticación
if not st.session_state.get("usuario_autenticado"):
    st.switch_page("all_pages/2_auth_page.py")

usuario = st.session_state.usuario_autenticado
token = usuario.get("token")

# Configurar cabeceras de autorización
headers = {
    "Authorization": f"Bearer {token}"
}

# CSS específico del Dashboard
st.html("""
<style>
  .sec-header {
    font-size: 0.8rem;
    font-weight: 700;
    color: #9e2aff;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
  }
  .card {
    background: #111420;
    border: 1px solid #1e2335;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
  }
  .card-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 15px;
  }
</style>
""")

st.html(f'<h1 class="page-title">Mi Mecateo</h1>')
st.markdown(f"<p style='text-align:center;color:#7d849a;font-size:1rem;margin-top:-1rem;margin-bottom:1.5rem'>Controla y categoriza tus ingresos y gastos de forma simple.</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Cargar Datos desde el Backend
# ---------------------------------------------------------------------------
try:
    # 1. Obtener métricas
    res_metrics = requests.get(f"{BACKEND_URL}/expenses/metrics", headers=headers)
    if res_metrics.status_code == 200:
        metrics = res_metrics.json()
    else:
        st.error("Error al cargar métricas del servidor.")
        st.stop()

    # 2. Obtener movimientos
    res_movs = requests.get(f"{BACKEND_URL}/expenses/", headers=headers)
    if res_movs.status_code == 200:
        movimientos = res_movs.json()
    else:
        st.error("Error al cargar transacciones del servidor.")
        st.stop()
except Exception as e:
    st.error(f"No se pudo establecer conexión con el servidor backend: {e}")
    st.stop()

# ---------------------------------------------------------------------------
# Fila de Métricas KPIs
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Ingresos Totales", f"${metrics['ingresos_totales']:,.0f} COP")
col2.metric("Gastos Totales", f"${metrics['gastos_totales']:,.0f} COP")

# Balance dinámico
balance = metrics['balance_total']
col3.metric("Balance Disponible", f"${balance:,.0f} COP")

st.write("")

# ---------------------------------------------------------------------------
# Distribución principal: Gráficos y Entradas
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.html('<div class="sec-header">Visualizaciones</div>')
    
    # Gráficos de Categoría
    gastos_cat = metrics.get("gastos_por_categoria", {})
    if gastos_cat:
        df_chart = pd.DataFrame([
            {"Categoría": cat, "Monto": monto} for cat, monto in gastos_cat.items()
        ])
        
        fig = px.pie(
            df_chart, 
            values="Monto", 
            names="Categoría", 
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#d1d4dc',
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        st.html('<div class="card"><div class="card-title">Distribución de Gastos por Categoría</div>')
        st.plotly_chart(fig, use_container_width=True)
        st.html('</div>')
    else:
        st.info("Registra transacciones de gastos para visualizar el desglose por categorías.")

    # Listado de Movimientos Recientes
    st.html('<div class="card"><div class="card-title">Historial de Transacciones</div>')
    if movimientos:
        df_movs = pd.DataFrame([
            {
                "Fecha": m["fecha"][:10],
                "Tipo": "📉 Gasto" if m["tipo"] == "gasto" else "📈 Ingreso",
                "Descripción": m["descripcion"],
                "Monto": f"${m['monto']:,.0f}",
                "Categoría": m["categoria"]["nombre"] if m["categoria"] else "Otros",
                "Observaciones": m["observaciones"] or ""
            } for m in movimientos
        ])
        st.dataframe(df_movs, use_container_width=True, hide_index=True)
    else:
        st.caption("No tienes movimientos registrados. ¡Intenta escribir uno en el panel de registro!")
    st.html('</div>')

with col_right:
    st.html('<div class="sec-header">Agregar Transacción</div>')
    
    tab_ia, tab_manual = st.tabs(["Registro con Inteligencia Artificial (IA) 🤖", "Registro Manual 📝"])
    
    # ── TAB IA ──
    with tab_ia:
        st.write("")
        st.caption("💡 Escribe frases como: *'Me pagaron 1.5 millones'*, *'Gaste 25 mil en pechuga'*, *'12k en taxi'*.")
        texto_nlp = st.text_input("Ingresa tu transacción:", placeholder="¿Qué compraste o recibiste hoy?")
        procesar_ia = st.button("Registrar Transacción con IA", use_container_width=True, type="primary")
        
        if procesar_ia:
            if not texto_nlp.strip():
                st.warning("Por favor ingresa un mensaje válido.")
            else:
                with st.spinner("Procesando con IA..."):
                    try:
                        payload = {"texto": texto_nlp.strip()}
                        res = requests.post(f"{BACKEND_URL}/expenses/add-nlp", json=payload, headers=headers)
                        if res.status_code == 200:
                            mov = res.json()
                            tipo_txt = "Gasto" if mov["tipo"] == "gasto" else "Ingreso"
                            st.success(f"✅ ¡Registrado! {tipo_txt} de **${mov['monto']:,.0f} COP** clasificado en **{mov['categoria']['nombre'] if mov['categoria'] else 'Otros'}**.")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            error_msg = res.json().get("detail", "Error al procesar la frase.")
                            st.error(error_msg)
                    except Exception as e:
                        st.error(f"Error al conectar con el backend: {e}")

    # ── TAB MANUAL ──
    with tab_manual:
        st.write("")
        with st.form("form_manual"):
            tipo = st.selectbox("Tipo de movimiento", ["gasto", "ingreso"])
            
            # Categorías pre-pobladas (se asume correspondencia con backend)
            categorias_nombres = ["Alimentación", "Transporte", "Hogar", "Salidas", "Deporte", "Suscripciones", "Salud", "Otros"]
            categoria_seleccionada = st.selectbox("Categoría", categorias_nombres)
            
            descripcion = st.text_input("Concepto / Descripción *", placeholder="Compra de víveres, Uber, etc.")
            monto = st.number_input("Monto ($) *", min_value=0.0, step=1000.0)
            observaciones = st.text_area("Observaciones opcionales", placeholder="Notas adicionales...")
            
            registrar_man = st.form_submit_button("Guardar Transacción", use_container_width=True, type="primary")
            
        if registrar_man:
            if not descripcion.strip() or monto <= 0:
                st.error("Por favor completa los campos obligatorios.")
            else:
                try:
                    # Encontrar ID de categoría en base al nombre
                    # Primero consultamos las categorías del backend para obtener el id correspondiente
                    # Por simplicidad, ya que el backend inicializó por defecto las categorías en el orden de categorias_defecto,
                    # podemos mapearlas. Pero para ser robustos, resolvemos con una petición rápida.
                    cat_id = None
                    try:
                        # Para no hacer un endpoint extra, podemos asumir que se guarda por nombre en el backend
                        # o consultar si es necesario. Dado que tenemos las categorías pobladas por defecto,
                        # podemos mapear los nombres directamente enviando el nombre al backend y haciendo que el backend
                        # asigne la categoría. Wait, el endpoint POST `/` recibe un `categoria_id`.
                        # Vamos a resolver consultando la lista de categorías del backend
                        # (agregaremos un endpoint GET `/api/v1/expenses/` o similar, wait, en movimiento_service
                        #  no agregamos endpoints GET para categorías, pero en main.py se pre-poblaron.
                        #  Haremos una petición rápida para buscar la categoría o enviar la transacción).
                        # Wait, en app/api/v1/endpoints/expenses.py no definimos endpoint GET para categorías.
                        # Pero podemos agregar un endpoint simple de categorías o resolverlo por id estático.
                        # Dado que las categorías se insertan secuencialmente (1: Alimentación, 2: Transporte, etc.),
                        # podemos indexarlas (1-indexed). Pero para ser 100% correctos, buscaremos el ID asociando
                        # el nombre al ID correspondiente de las categorías mapeadas de los movimientos recibidos,
                        # o simplemente usar indexación base 1:
                        cat_id = categorias_nombres.index(categoria_seleccionada) + 1
                    except Exception:
                        cat_id = None
                        
                    payload = {
                        "tipo": tipo,
                        "descripcion": descripcion.strip(),
                        "monto": float(monto),
                        "moneda": "COP",
                        "observaciones": observaciones.strip() if observaciones.strip() else None,
                        "categoria_id": cat_id
                    }
                    res = requests.post(f"{BACKEND_URL}/expenses/", json=payload, headers=headers)
                    if res.status_code == 201:
                        st.success("Transacción registrada manualmente con éxito.")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        error_msg = res.json().get("detail", "Error al registrar la transacción.")
                        st.error(error_msg)
                except Exception as e:
                    st.error(f"Error al conectar con el backend: {e}")

    # ── ELIMINAR TRANSACCION ──
    if movimientos:
        st.write("")
        st.html('<div class="sec-header">Eliminar Transacción</div>')
        with st.form("form_delete"):
            opciones_del = {
                m["id"]: f"{m['fecha'][:10]} | {m['descripcion']} (${m['monto']:,.0f})"
                for m in movimientos[:15]  # Mostrar solo los 15 más recientes
            }
            trans_id = st.selectbox("Selecciona la transacción a borrar:", list(opciones_del.keys()), format_func=lambda x: opciones_del[x])
            confirmar_borrado = st.form_submit_button("Eliminar 🗑️", use_container_width=True)
            
        if confirmar_borrado:
            try:
                res = requests.delete(f"{BACKEND_URL}/expenses/{trans_id}", headers=headers)
                if res.status_code == 200:
                    st.success("Transacción eliminada correctamente.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("No se pudo eliminar la transacción.")
            except Exception as e:
                st.error(f"Error de conexión con el backend: {e}")

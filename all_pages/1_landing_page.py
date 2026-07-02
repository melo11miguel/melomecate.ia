import streamlit as st

# CSS específico de la landing page
st.html("""
<style>
  .block-container { padding-top: 0 !important; max-width: 100% !important; }

  .hero {
    background: linear-gradient(135deg, #090b11 0%, #111524 50%, #080a12 100%);
    padding: 90px 40px 80px;
    text-align: center;
    border-bottom: 1px solid #161a29;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: -40%;
    left: 50%;
    transform: translateX(-50%);
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, rgba(158,42,255,0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-tag {
    display: inline-block;
    background: rgba(158,42,255,0.12);
    color: #b97bff;
    border: 1px solid rgba(158,42,255,0.25);
    border-radius: 30px;
    padding: 6px 16px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 28px;
  }
  .hero-title {
    font-size: 3.4rem !important;
    font-weight: 900 !important;
    line-height: 1.15 !important;
    color: #ffffff !important;
    letter-spacing: -2px !important;
    margin: 0 0 24px !important;
  }
  .hero-title span {
    background: linear-gradient(135deg, #9e2aff 0%, #00f0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    font-size: 1.15rem !important;
    color: #7d849a !important;
    max-width: 600px;
    margin: 0 auto 40px !important;
    line-height: 1.7 !important;
  }

  .stats-bar {
    display: flex;
    justify-content: center;
    gap: 60px;
    padding: 30px 0;
    border-bottom: 1px solid #161a29;
    background: #090b11;
  }
  .stat-item { text-align: center; }
  .stat-num {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    display: block;
    background: linear-gradient(135deg, #ffffff 0%, #b97bff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .stat-lbl {
    font-size: 0.72rem;
    color: #5d6175;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 700;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    padding: 60px;
    background: #090b11;
  }
  .feat-card {
    background: #111420;
    border: 1px solid #1e2335;
    border-radius: 16px;
    padding: 32px 28px;
    transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  }
  .feat-card:hover {
    border-color: #9e2aff;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(158,42,255,0.06);
  }
  .feat-icon {
    width: 44px;
    height: 44px;
    background: rgba(158,42,255,0.1);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 20px;
    color: #b97bff;
    box-shadow: 0 0 10px rgba(158,42,255,0.15);
  }
  .feat-title {
    font-size: 1rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 10px;
  }
  .feat-desc {
    font-size: 0.85rem;
    color: #7d849a;
    line-height: 1.6;
  }

  .lp-footer {
    text-align: center;
    padding: 30px;
    background: #090b11;
    border-top: 1px solid #161a29;
    font-size: 0.8rem;
    color: #4a4e69;
  }
</style>
""")

usuario = st.session_state.get("usuario_autenticado")

bienvenida = (
    f'<div class="hero-tag">¡Hola de nuevo, {usuario["nombre"].split()[0]}!</div>'
    if usuario
    else '<div class="hero-tag">Finanzas Personales Simples</div>'
)

st.html(f"""
<div class="hero">
    {bienvenida}
    <div class="hero-title">Registra tus gastos por WhatsApp.<br><span>Controla tu presupuesto con IA.</span></div>
    <div class="hero-sub">
        Olvídate de las hojas de cálculo complejas. Envía un mensaje como "25 mil en pechuga" y dejas que la inteligencia artificial se encargue del resto.
    </div>
</div>
""")

# CTA
col_l, col_c, col_r = st.columns([2, 1.2, 2])
with col_c:
    if usuario:
        if st.button("Ir al Dashboard 📊", use_container_width=True, type="primary"):
            st.switch_page("all_pages/3_dashboard_page.py")
    else:
        if st.button("Comenzar Ahora 🚀", use_container_width=True, type="primary"):
            st.switch_page("all_pages/2_auth_page.py")

# Stats
st.html("""
<div class="stats-bar">
    <div class="stat-item">
        <span class="stat-num">WhatsApp</span>
        <span class="stat-lbl">Canal Principal</span>
    </div>
    <div class="stat-item">
        <span class="stat-num">Gemini 1.5</span>
        <span class="stat-lbl">Motor de IA</span>
    </div>
    <div class="stat-item">
        <span class="stat-num">1 Segundo</span>
        <span class="stat-lbl">Tiempo de Registro</span>
    </div>
    <div class="stat-item">
        <span class="stat-num">100%</span>
        <span class="stat-lbl">Privado y Seguro</span>
    </div>
</div>

<div class="features">
    <div class="feat-card">
        <div class="feat-icon">💬</div>
        <div class="feat-title">Integración con WhatsApp</div>
        <div class="feat-desc">
            Registra ingresos o gastos de forma natural enviando mensajes directamente al chat del bot, en cualquier momento y lugar.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🤖</div>
        <div class="feat-title">Clasificación con IA</div>
        <div class="feat-desc">
            Nuestra IA interpreta jergas locales de Colombia ("lucas", "barras", "palos", "k") y asigna la categoría correspondiente de forma automática.
        </div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📈</div>
        <div class="feat-title">Dashboard Analítico</div>
        <div class="feat-desc">
            Visualiza balances, flujos de efectivo y gráficos de torta de tus gastos por categorías en un panel web moderno y optimizado.
        </div>
    </div>
</div>

<div class="lp-footer">
    © 2026 melomecate.ia · Control de Finanzas Personales con IA · Medellín, Colombia
</div>
""")

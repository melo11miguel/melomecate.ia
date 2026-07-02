from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.categoria import Categoria
from app.api.router import api_router

# Inicializar las tablas de la base de datos automáticamente
Base.metadata.create_all(bind=engine)

# Pre-poblar las categorías por defecto
db = SessionLocal()
try:
    categorias_defecto = {
        "Alimentación": "#ff4b4b",      # Rojo
        "Transporte": "#4d4d4d",        # Gris oscuro
        "Hogar": "#00f0ff",             # Cian
        "Salidas": "#ffaa00",           # Naranja
        "Deporte": "#2962ff",           # Azul
        "Suscripciones": "#9e2aff",     # Violeta
        "Salud": "#26a69a",             # Verde azulado
        "Otros": "#787b86"              # Gris claro
    }
    for nombre, color in categorias_defecto.items():
        existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
        if not existe:
            cat = Categoria(nombre=nombre, color=color)
            db.add(cat)
    db.commit()
except Exception as e:
    print(f"Error al pre-poblar categorías: {e}")
finally:
    db.close()

app = FastAPI(
    title="melomecate.ia Backend API",
    description="API REST y Webhook de WhatsApp para finanzas personales impulsado por IA.",
    version="1.0.0"
)

# Configurar middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas principales
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "melomecate.ia",
        "description": "API REST para el Dashboard y Webhook para WhatsApp"
    }

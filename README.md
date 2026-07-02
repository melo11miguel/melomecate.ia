# melomecate.ia 💸

Aplicación de finanzas personales impulsada por inteligencia artificial (Gemini) y procesador de lenguaje natural con soporte para jergas colombianas. Permite a los usuarios registrar sus ingresos y gastos de forma conversacional a través de **WhatsApp** y visualizar sus balances y métricas a través de un **Dashboard web premium** en Streamlit.

---

## 🚀 Arquitectura del Proyecto

El sistema está diseñado siguiendo una arquitectura modular desacoplada:

1.  **FastAPI Backend (`/app`)**:
    *   **Autenticación**: Hashing de contraseñas (`bcrypt`), cookies cifradas (`Fernet`) y doble factor de autenticación TOTP (`pyotp`).
    *   **Servicio NLP/IA (`app/services/nlp_service.py`)**: Analizador híbrido. Si se provee una clave de Gemini, procesa los mensajes con modelos generativos avanzados en formato estructurado JSON. En caso contrario, realiza un parsing local robusto con expresiones regulares para expresiones colombianas ("lucas", "barras", "mil", "palos").
    *   **Base de Datos**: PostgreSQL / SQLite a través de SQLAlchemy ORM.
    *   **WhatsApp Webhook**: Endpoint de Meta para la recepción y confirmación automática de transacciones por mensajería en tiempo real.
2.  **Streamlit Frontend (`app_streamlit.py`)**:
    *   Menú superior premium (escondiendo la barra lateral nativa).
    *   Persistencia de sesión segura en cookies del navegador (`extra-streamlit-components`).
    *   Visualizaciones interactivas de gastos e ingresos usando Plotly.
    *   Ingreso manual y por lenguaje natural interactivo.

---

## 🛠️ Requisitos de Instalación

1.  Clonar este repositorio o inicializarlo en tu entorno de trabajo.
2.  Crear el entorno virtual de Python e instalar las dependencias:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```

---

## ⚙️ Configuración (`.env`)

Crea un archivo `.env` en la raíz del proyecto basándote en la plantilla `.env.example`:

```ini
DATABASE_URL=sqlite:///./melomecate.db
FERNET_KEY=E9p4eS09Wj3i1b4X8y5pQ7c3L5U8K6s3d1L8H9u2z3M=
GEMINI_API_KEY=tu_api_key_de_gemini
WHATSAPP_TOKEN=tu_token_de_whatsapp_api
WHATSAPP_VERIFY_TOKEN=my_secure_verify_token_123
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
```

---

## 🏃 Ejecución del Proyecto

### 1. Iniciar el Backend (FastAPI)
Ejecuta el servidor de desarrollo Uvicorn:
```bash
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
La documentación interactiva estará disponible en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Iniciar el Dashboard (Streamlit)
Abre otra terminal y ejecuta:
```bash
.venv\Scripts\python -m streamlit run app_streamlit.py --server.port 8501
```
El panel estará disponible en tu navegador en [http://localhost:8501](http://localhost:8501).

---

## 🧪 Pruebas Unitarias

Ejecuta el conjunto de pruebas para el analizador de texto:
```bash
.venv\Scripts\python tests/test_nlp.py
```

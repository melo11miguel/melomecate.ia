from fastapi import APIRouter
from app.api.v1.endpoints import auth, expenses, whatsapp

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Transacciones"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp Webhook"])

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.movimiento import (
    MovimientoCreate, MovimientoResponse, 
    MovimientoNLPRequest, MovimientoNLPResponse
)
from app.services import movimiento_service, nlp_service

router = APIRouter()

@router.post("/parse", response_model=MovimientoNLPResponse)
def parse_text(payload: MovimientoNLPRequest, current_user: Usuario = Depends(get_current_user)):
    """Analiza el texto ingresado pero NO lo guarda en la base de datos."""
    parsed = nlp_service.clasificar_mensaje(payload.texto)
    return parsed

@router.post("/add-nlp", response_model=MovimientoResponse)
def add_from_nlp(
    payload: MovimientoNLPRequest, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Analiza el texto ingresado y lo registra automáticamente en la base de datos."""
    try:
        movimiento = movimiento_service.crear_movimiento_nlp(
            db=db, 
            usuario_id=current_user.id, 
            texto=payload.texto
        )
        return movimiento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la transacción: {str(e)}"
        )

@router.post("/", response_model=MovimientoResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    movimiento_in: MovimientoCreate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Registra una transacción de forma manual."""
    try:
        movimiento = movimiento_service.crear_movimiento(
            db=db, 
            usuario_id=current_user.id, 
            movimiento_in=movimiento_in
        )
        return movimiento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la transacción: {str(e)}"
        )

@router.get("/", response_model=List[MovimientoResponse])
def get_transactions(
    tipo: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna la lista de transacciones del usuario autenticado."""
    return movimiento_service.obtener_movimientos_usuario(
        db=db, 
        usuario_id=current_user.id, 
        tipo=tipo, 
        categoria_id=categoria_id
    )

@router.delete("/{id}")
def delete_transaction(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina una transacción del usuario."""
    exito = movimiento_service.eliminar_movimiento(db=db, usuario_id=current_user.id, movimiento_id=id)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada o no pertenece al usuario."
        )
    return {"message": "Transacción eliminada correctamente."}

@router.get("/metrics")
def get_financial_metrics(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna métricas financieras agregadas para el dashboard."""
    return movimiento_service.obtener_metricas_usuario(db=db, usuario_id=current_user.id)

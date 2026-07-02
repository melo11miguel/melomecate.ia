from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime
from typing import List, Dict, Any, Optional

from app.models.movimiento import Movimiento
from app.models.categoria import Categoria
from app.schemas.movimiento import MovimientoCreate
from app.services import nlp_service

def obtener_o_crear_categoria(db: Session, nombre: str, color: str = "#d1d4dc") -> Categoria:
    """Obtiene una categoría por nombre (insensible a mayúsculas) o la crea si no existe."""
    nombre_limpio = nombre.strip().capitalize()
    categoria = db.query(Categoria).filter(func.lower(Categoria.nombre) == nombre_limpio.lower()).first()
    if not categoria:
        categoria = Categoria(nombre=nombre_limpio, color=color)
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
    return categoria

def obtener_categorias(db: Session) -> List[Categoria]:
    return db.query(Categoria).all()

def obtener_movimientos_usuario(
    db: Session, 
    usuario_id: int, 
    tipo: Optional[str] = None, 
    categoria_id: Optional[int] = None
) -> List[Movimiento]:
    """Retorna los movimientos de un usuario con opción de filtrado."""
    query = db.query(Movimiento).filter(Movimiento.usuario_id == usuario_id)
    if tipo:
        query = query.filter(Movimiento.tipo == tipo)
    if categoria_id:
        query = query.filter(Movimiento.categoria_id == categoria_id)
    return query.order_by(Movimiento.fecha.desc()).all()

def crear_movimiento(db: Session, usuario_id: int, movimiento_in: MovimientoCreate) -> Movimiento:
    """Crea un movimiento de forma manual."""
    db_movimiento = Movimiento(
        usuario_id=usuario_id,
        tipo=movimiento_in.tipo,
        descripcion=movimiento_in.descripcion,
        monto=movimiento_in.monto,
        moneda=movimiento_in.moneda,
        observaciones=movimiento_in.observaciones,
        categoria_id=movimiento_in.categoria_id,
        fecha=movimiento_in.fecha or datetime.datetime.now()
    )
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

def crear_movimiento_nlp(db: Session, usuario_id: int, texto: str, observaciones: Optional[str] = None) -> Movimiento:
    """
    Procesa el texto ingresado, clasifica la transacción e inserta el movimiento
    en la base de datos resolviendo automáticamente la categoría.
    """
    parsed = nlp_service.clasificar_mensaje(texto)
    
    # 1. Obtener o crear la categoría
    categoria = obtener_o_crear_categoria(db, parsed["categoria"])
    
    # 2. Registrar el movimiento
    db_movimiento = Movimiento(
        usuario_id=usuario_id,
        tipo=parsed["tipo"],
        descripcion=parsed["descripcion"],
        monto=parsed["valor"],
        moneda=parsed["moneda"],
        observaciones=observaciones or f"Mensaje procesado: '{texto}'",
        categoria_id=categoria.id,
        fecha=datetime.datetime.now()
    )
    
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

def eliminar_movimiento(db: Session, usuario_id: int, movimiento_id: int) -> bool:
    mov = db.query(Movimiento).filter(Movimiento.id == movimiento_id, Movimiento.usuario_id == usuario_id).first()
    if mov:
        db.delete(mov)
        db.commit()
        return True
    return False

def obtener_metricas_usuario(db: Session, usuario_id: int) -> Dict[str, Any]:
    """Calcula métricas agregadas del usuario: ingresos totales, gastos totales, balance y gastos por categoría."""
    movimientos = db.query(Movimiento).filter(Movimiento.usuario_id == usuario_id).all()
    
    ingresos = sum(m.monto for m in movimientos if m.tipo == "ingreso" and m.moneda == "COP")
    gastos = sum(m.monto for m in movimientos if m.tipo == "gasto" and m.moneda == "COP")
    balance = ingresos - gastos
    
    # Gastos por categoría
    gastos_por_cat = {}
    for m in movimientos:
        if m.tipo == "gasto" and m.moneda == "COP":
            nombre_cat = m.categoria.nombre if m.categoria else "Sin categoría"
            gastos_por_cat[nombre_cat] = gastos_por_cat.get(nombre_cat, 0.0) + m.monto

    return {
        "ingresos_totales": ingresos,
        "gastos_totales": gastos,
        "balance_total": balance,
        "gastos_por_categoria": gastos_por_cat,
        "total_movimientos": len(movimientos)
    }

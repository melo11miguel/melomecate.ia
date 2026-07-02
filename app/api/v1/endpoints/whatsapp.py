from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session
import requests
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.usuario import Usuario
from app.services import movimiento_service

logger = logging.getLogger(__name__)
router = APIRouter()

def enviar_mensaje_whatsapp(to_number: str, text: str):
    """Envía un mensaje de texto de WhatsApp de respuesta usando la API Cloud de WhatsApp."""
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.info(f"[WHATSAPP STUB] Enviando mensaje a {to_number}: '{text}'")
        return
        
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text
        }
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            logger.error(f"Error al enviar mensaje por WhatsApp API: {res.text}")
    except Exception as e:
        logger.error(f"Error de red al conectar con WhatsApp API: {e}")

@router.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Endpoint de verificación requerido por Meta al configurar el Webhook."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook de WhatsApp verificado exitosamente.")
        return Response(content=hub_challenge, media_type="text/plain")
        
    logger.warning("Fallo en la verificación del Webhook de WhatsApp.")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Token de verificación inválido."
    )

@router.post("/webhook")
async def recibir_mensaje(request: Request, db: Session = Depends(get_db)):
    """Recibe los mensajes de WhatsApp en tiempo real, los procesa e inserta en la base de datos."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Cuerpo de petición inválido.")
        
    # Validar que sea un evento de mensaje de WhatsApp
    if body.get("object") != "whatsapp_business_account":
        return {"status": "ignored"}
        
    try:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    for msg in value.get("messages", []):
                        if msg.get("type") == "text":
                            remitente = msg.get("from")  # Número de teléfono del remitente (ej. "573000000000")
                            texto_mensaje = msg.get("text", {}).get("body", "").strip()
                            
                            logger.info(f"Mensaje recibido de {remitente}: {texto_mensaje}")
                            
                            # 1. Buscar usuario por su número de teléfono
                            # Buscamos coincidencias con y sin el prefijo de país para tolerancia
                            usuario = db.query(Usuario).filter(
                                (Usuario.telefono == remitente) | 
                                (Usuario.telefono.like(f"%{remitente[-10:]}"))
                            ).first()
                            
                            if not usuario:
                                # Si no está registrado
                                msg_respuesta = (
                                    "¡Hola! Bienvenido a melomecate.ia. 🚀\n\n"
                                    "Aún no tienes este número de celular enlazado a una cuenta activa. "
                                    "Por favor regístrate en nuestro panel web y agrega tu número en tu perfil."
                                )
                                enviar_mensaje_whatsapp(remitente, msg_respuesta)
                                continue
                                
                            # 2. Procesar el texto y registrar transacción
                            try:
                                movimiento = movimiento_service.crear_movimiento_nlp(
                                    db=db, 
                                    usuario_id=usuario.id, 
                                    texto=texto_mensaje,
                                    observaciones=f"Registrado vía WhatsApp por {usuario.nombre}"
                                )
                                
                                # 3. Responder con confirmación estructurada
                                tipo_emoji = "📉 Gasto" if movimiento.tipo == "gasto" else "📈 Ingreso"
                                msg_respuesta = (
                                    f"✅ *{tipo_emoji} registrado con éxito*\n\n"
                                    f"💵 *Monto:* ${movimiento.monto:,.0f} COP\n"
                                    f"🏷️ *Categoría:* {movimiento.categoria.nombre if movimiento.categoria else 'Sin categoría'}\n"
                                    f"📝 *Concepto:* {movimiento.descripcion}\n\n"
                                    f"¡Sigue controlando tus mecates! 🎯"
                                )
                                enviar_mensaje_whatsapp(remitente, msg_respuesta)
                                
                            except Exception as e:
                                logger.error(f"Error procesando transacción NLP: {e}")
                                msg_respuesta = (
                                    "⚠️ Ocurrió un error al procesar tu mensaje. "
                                    "Asegúrate de incluir un valor y el concepto (Ej. 'Compré 25 mil en pechuga')."
                                )
                                enviar_mensaje_whatsapp(remitente, msg_respuesta)
                                
    except Exception as e:
        logger.error(f"Error general en webhook: {e}")
        
    return {"status": "processed"}

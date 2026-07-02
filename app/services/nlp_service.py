import re
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configurar el SDK de Gemini si hay clave de API disponible
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Categorías por defecto del sistema
CATEGORIAS_SISTEMA = {
    "alimentos": ["comida", "pechuga", "almuerzo", "cena", "restaurante", "mercado", "supermercado", "pan", "leche", "fruta", "carne"],
    "transporte": ["taxi", "uber", "bus", "gasolina", "pasajes", "transmilenio", "peaje", "moto", "carro", "parqueadero"],
    "hogar": ["arriendo", "luz", "agua", "internet", "gas", "servicios", "administracion", "reparacion", "muebles"],
    "salidas": ["cine", "fiesta", "cerveza", "salida", "bar", "rumba", "discoteca", "cafe", "postre", "helado"],
    "deporte": ["gimnasio", "suplementos", "gym", "straps", "proteina", "creatina", "mensualidad gym", "deportivas"],
    "suscripciones": ["netflix", "spotify", "ia", "chatgpt", "midjourney", "youtube", "amazon prime", "disney", "streaming"],
    "salud": ["medicina", "drogueria", "pastillas", "cita medica", "dentista", "eps", "seguro"],
    "otros": []
}

def parse_with_regex(texto: str) -> Dict[str, Any]:
    """
    Analiza un texto en español colombiano usando expresiones regulares.
    Devuelve un diccionario estructurado.
    """
    texto_lc = texto.lower().strip()

    # 1. Determinar el Tipo (gasto o ingreso)
    tipo = "gasto"
    palabras_ingreso = [
        "recibi", "recibí", "me pagaron", "consigne", "consigné", "consignacion", 
        "consignación", "consignaron", "ingreso", "gane", "gané", "sueldo", "salario", 
        "nomina", "nómina", "ventas", "venta", "pago de"
    ]
    # Si contiene palabras de ingreso pero no contiene palabras que contradigan, ej. "pago de arriendo" (gasto)
    es_ingreso = False
    for p in palabras_ingreso:
        if p in texto_lc:
            # Excepción: "pago de arriendo", "pago de luz" son gastos
            if p == "pago de" and any(x in texto_lc for x in ["arriendo", "luz", "agua", "gas", "internet", "suscripcion", "netflix", "gym"]):
                continue
            es_ingreso = True
            break
    
    if es_ingreso:
        tipo = "ingreso"

    # 2. Extraer el Valor / Monto
    monto = 0.0
    
    # Patrones numéricos y de texto (ej: "25 mil", "25k", "3.5 millones", "20 lucas", "15 barras", "2 palos")
    patrones_valor = [
        r'(\d+(?:[\.,]\d+)?)\s*(mil|k|lucas|barras|palos|millon|millones|millón)\b',
        r'(?:[\$]?)\s*(\d+(?:[\.,]\d+)?)\s*cop\b',
        r'(?:[\$])\s*(\d+(?:[\.,\s]?\d+)+)',
        r'\b(\d+(?:[\.,]?\d+)+)\b'
    ]

    valor_encontrado = False
    for pat in patrones_valor:
        match = re.search(pat, texto_lc)
        if match:
            num_str = match.group(1).replace(",", "").replace(" ", "")
            try:
                val = float(num_str)
                # Aplicar multiplicadores
                if len(match.groups()) > 1:
                    sufijo = match.group(2)
                    if sufijo in ["mil", "k", "lucas", "barras"]:
                        val *= 1000
                    elif sufijo in ["palos", "millon", "millones", "millón"]:
                        val *= 1000000
                
                monto = val
                valor_encontrado = True
                break
            except ValueError:
                continue

    # 3. Categorizar automáticamente basado en palabras clave
    categoria = "otros"
    for cat, palabras in CATEGORIAS_SISTEMA.items():
        if any(p in texto_lc for p in palabras):
            categoria = cat
            break

    # 4. Extraer Descripción
    # Intentamos quitar el valor numérico y palabras conectoras para dejar la descripción limpia.
    descripcion = texto
    # Quitar el monto del texto original
    if valor_encontrado:
        # Intentar extraer palabras que indiquen el concepto después de conectores
        match_concept = re.search(r'(?:en|de|para|por|un|una)\s+([a-zA-Záéíóúñ\s]+)', texto_lc)
        if match_concept:
            descripcion = match_concept.group(1).strip().capitalize()
        else:
            # Limpieza básica: quitar números
            desc_limpia = re.sub(r'\d+.*$', '', texto_lc)
            desc_limpia = re.sub(r'\b(gaste|gasto|compre|compré|pague|pagué|recibi|recibí|consigne|consigné)\b', '', desc_limpia)
            desc_limpia = desc_limpia.replace("$", "").strip()
            if desc_limpia:
                descripcion = desc_limpia.capitalize()
            else:
                descripcion = "Transacción registrada"

    return {
        "tipo": tipo,
        "categoria": categoria.capitalize(),
        "descripcion": descripcion,
        "valor": monto,
        "moneda": "COP"
    }

def parse_with_gemini(texto: str) -> Optional[Dict[str, Any]]:
    """
    Usa el modelo Gemini de Google para parsear y categorizar la transacción en formato JSON.
    """
    if not settings.GEMINI_API_KEY:
        return None
        
    prompt = f"""
    Eres un clasificador experto de transacciones financieras para Colombia.
    Analiza el siguiente texto escrito por un usuario y extrae la información en formato JSON.
    
    Texto del usuario: "{texto}"
    
    Debes clasificarlo y estructurarlo exactamente en este formato JSON:
    {{
      "tipo": "gasto" o "ingreso",
      "categoria": "Alimentación" o "Transporte" o "Hogar" o "Salidas" o "Deporte" o "Suscripciones" o "Salud" o "Otros",
      "descripcion": "Descripción concisa del artículo o servicio (sin el valor)",
      "valor": número decimal que representa la cantidad de dinero,
      "moneda": "COP" (a menos que se especifique otra como USD)
    }}
    
    Reglas de interpretación:
    1. Interpreta slang colombiano:
       - "lucas", "barras", "mil", "k" multiplican por 1,000 (ej. "25 lucas" -> 25000, "30 mil" -> 30000).
       - "palos", "millon", "millones" multiplican por 1,000,000 (ej. "2.5 palos" -> 2500000).
    2. Categorías válidas:
       - "Alimentación" (mercado, comida, restaurantes, snacks, etc.)
       - "Transporte" (taxis, buses, gasolina, peajes, parqueaderos, etc.)
       - "Hogar" (servicios públicos, arriendo, reparaciones, administración, etc.)
       - "Salidas" (cine, bares, discotecas, fiestas, restaurantes en plan de ocio, café, etc.)
       - "Deporte" (gimnasio, suplementos alimenticios, proteínas, straps, mensualidad, etc.)
       - "Suscripciones" (servicios de IA como ChatGPT, Netflix, Spotify, streaming, etc.)
       - "Salud" (citas médicas, medicamentos, droguería, EPS, etc.)
       - "Otros" (cualquier cosa que no encaje en las anteriores).
    3. Asegúrate de retornar ÚNICAMENTE el código JSON válido, sin textos adicionales, sin markdown (no utilices ```json).
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        # Normalizar y validar keys
        if "tipo" in data and "categoria" in data and "descripcion" in data and "valor" in data:
            # Asegurar tipo correcto
            data["valor"] = float(data["valor"])
            return data
    except Exception as e:
        logger.warning(f"Error calling Gemini API: {e}. Fallback to Regex parser.")
        
    return None

def clasificar_mensaje(texto: str) -> Dict[str, Any]:
    """
    Punto de entrada principal para clasificar mensajes.
    Prueba primero con Gemini API si está disponible, de lo contrario o si falla, usa expresiones regulares locales.
    """
    if settings.GEMINI_API_KEY:
        gemini_res = parse_with_gemini(texto)
        if gemini_res:
            return gemini_res
            
    return parse_with_regex(texto)

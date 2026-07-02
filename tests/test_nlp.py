import sys
import os

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.nlp_service import parse_with_regex

def test_regex_parser():
    print("Iniciando pruebas unitarias del analizador Regex...")
    
    pruebas = [
        {
            "texto": "Compre 25 mil en pechuga",
            "esperado": {"tipo": "gasto", "valor": 25000.0, "categoria": "Alimentos"}
        },
        {
            "texto": "Gaste 120k en arriendo",
            "esperado": {"tipo": "gasto", "valor": 120000.0, "categoria": "Hogar"}
        },
        {
            "texto": "Recibí 1.5 palos de sueldo",
            "esperado": {"tipo": "ingreso", "valor": 1500000.0, "categoria": "Otros"}
        },
        {
            "texto": "Me pagaron 30 lucas de un favor",
            "esperado": {"tipo": "ingreso", "valor": 30000.0, "categoria": "Otros"}
        },
        {
            "texto": "15 barras en taxi",
            "esperado": {"tipo": "gasto", "valor": 15000.0, "categoria": "Transporte"}
        },
        {
            "texto": "Pago de Netflix por 45 mil",
            "esperado": {"tipo": "gasto", "valor": 45000.0, "categoria": "Suscripciones"}
        }
    ]
    
    exitos = 0
    for i, p in enumerate(pruebas):
        res = parse_with_regex(p["texto"])
        val_ok = res["valor"] == p["esperado"]["valor"]
        tipo_ok = res["tipo"] == p["esperado"]["tipo"]
        cat_ok = res["categoria"] == p["esperado"]["categoria"]
        
        if val_ok and tipo_ok and cat_ok:
            print(f"  [OK] Prueba {i+1}: '{p['texto']}'")
            exitos += 1
        else:
            print(f"  [ERROR] Prueba {i+1}: '{p['texto']}' -> Obtenido: {res} | Esperado: {p['esperado']}")
            
    print(f"\nResumen: {exitos}/{len(pruebas)} exitosas.")
    assert exitos == len(pruebas), "Algunas pruebas de Regex fallaron."

if __name__ == "__main__":
    test_regex_parser()

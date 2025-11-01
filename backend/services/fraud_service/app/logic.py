from datetime import datetime

# --- Definición de Estados Finales ---
ESTADO_APROBADO = "APPROVED"
ESTADO_RECHAZADO = "REJECTED"

# --- Definición de Reglas de Fraude ---

def regla_monto_alto(monto: float) -> bool:
    """
    Regla 1: Verifica si el monto supera el límite.
    """
    return monto > 5000.00

def regla_ubicacion_riesgosa(ubicacion: str) -> bool:
    """
    Regla 2: Verifica si la transacción ocurre en una ubicación
    conocida por fraude.
    """
    ubicaciones_de_riesgo = {"Panamá", "Islas Caimán", "Suiza"}
    return ubicacion in ubicaciones_de_riesgo

def regla_hora_nocturna_riesgosa(hora_transaccion_str: str) -> bool:
    """
    Regla 3: Verifica si la transacción ocurre en horas de alto riesgo
    (ej. 2:00 AM - 4:00 AM).
    """
    try:
        hora_transaccion = datetime.fromisoformat(hora_transaccion_str)
        hora = hora_transaccion.hour
        return 2 <= hora < 4
    except (ValueError, TypeError):
        return False

# --- Motor de Reglas Principal ---

def aplicar_reglas_fraude(datos_transaccion: dict) -> str:
    """
    Aplica todas las reglas y retorna APPROVED o REJECTED.
    """
    
    reglas_activadas = []
    
    # Datos de entrada
    monto = datos_transaccion.get("monto", 0.0)
    ubicacion = datos_transaccion.get("ubicacion", "")
    hora_str = datos_transaccion.get("hora", "")

    # --- Aplicar Reglas ---
    if regla_monto_alto(monto):
        reglas_activadas.append("Monto_Alto")
        
    if regla_ubicacion_riesgosa(ubicacion):
        reglas_activadas.append("Ubicacion_Riesgosa")
        
    if regla_hora_nocturna_riesgosa(hora_str):
        reglas_activadas.append("Hora_Nocturna_Riesgosa")

    # --- Clasificación Final --- 
    if len(reglas_activadas) > 0:
        print(f" [!] ⚠️  Fraude detectado: {', '.join(reglas_activadas)}")
        return ESTADO_RECHAZADO
    else:
        print(f" [✓] ✅ Transacción aprobada")
        return ESTADO_APROBADO
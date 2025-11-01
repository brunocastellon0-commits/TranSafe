from datetime import datetime

# --- Definición de Estados Finales ---
ESTADO_NORMAL = "NORMAL"
ESTADO_SOSPECHOSO = "SOSPECHOSA"

# --- Definición de Reglas de Fraude ---

def regla_monto_alto(monto: float) -> bool:
    """
    Regla 1: Verifica si el monto supera el límite.
    """
    return monto > 5000.00

def regla_ubicacion_riesgosa(ubicacion: str) -> bool:
    """
    Regla 2: Verifica si la transacción ocurre en una ubicación
    conocida por fraude (simplificación de la regla de 'país diferente' ).
    """
    ubicaciones_de_riesgo = {"Panamá", "Islas Caimán", "Suiza"}
    return ubicacion in ubicaciones_de_riesgo

def regla_hora_nocturna_riesgosa(hora_transaccion_str: str) -> bool:
    """
    Regla 3: Verifica si la transacción ocurre en horas de alto riesgo
    (ej. 2:00 AM - 4:00 AM).
    """
    try:
        # El 'hora' viene como string ISO 8601 desde el JSON
        hora_transaccion = datetime.fromisoformat(hora_transaccion_str)
        hora = hora_transaccion.hour
        # Verifica si la hora está entre las 2 y las 4 AM
        return 2 <= hora < 4
    except (ValueError, TypeError):
        # Si la hora es inválida, no la marcamos como riesgosa
        return False

# --- Motor de Reglas Principal (La MEF) ---

def aplicar_reglas_fraude(datos_transaccion: dict) -> str:
    """
    Esta es la función principal del motor de reglas.
    Aplica todas las reglas (simulando la MEF)[cite: 17, 18].
    
    Estado Inicial: Recibido -> Procesando
    """
    
    reglas_activadas = []
    
    # Datos de entrada
    monto = datos_transaccion.get("monto", 0.0)
    ubicacion = datos_transaccion.get("ubicacion", "")
    hora_str = datos_transaccion.get("hora", "")

    # --- Aplicar Regla 1 ---
    if regla_monto_alto(monto):
        reglas_activadas.append("Monto_Alto")
        
    # --- Aplicar Regla 2 ---
    if regla_ubicacion_riesgosa(ubicacion):
        reglas_activadas.append("Ubicacion_Riesgosa")
        
    # --- Aplicar Regla 3 ---
    if regla_hora_nocturna_riesgosa(hora_str):
        reglas_activadas.append("Hora_Nocturna_Riesgosa")

    # --- Estado Final: Clasificar --- 
    if len(reglas_activadas) > 0:
        print(f" [!] Alerta de Fraude: {', '.join(reglas_activadas)}")
        return ESTADO_SOSPECHOSO
    else:
        return ESTADO_NORMAL
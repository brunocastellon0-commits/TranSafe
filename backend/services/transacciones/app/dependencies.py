# transactions_service/app/dependencies.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from .database import SessionLocal
from app.services.messaging import RabbitMQPublisher # 1. Importar el publicador

# Configurar logger
logger = logging.getLogger(__name__)

# --- Dependencia de Base de Datos ---

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de BD.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependencia de Mensajería (RabbitMQ) ---

# --- CAMBIO CLAVE ---
# 2. Inicializar el publicador UNA SOLA VEZ.
#    El 'host' debe ser 'rabbitmq' (el nombre del servicio en docker-compose).
#    La lógica de reintentos está AHORA DENTRO de RabbitMQPublisher.
try:
    logger.info("Intentando conectar a RabbitMQ al inicio...")
    publisher_instance = RabbitMQPublisher(host='rabbitmq')
except ConnectionError as e:
    logger.critical(f"CRÍTICO: No se pudo conectar a RabbitMQ al inicio. El servicio no funcionará. {e}")
    publisher_instance = None # El servicio cargará, pero fallará en las peticiones

def get_publisher() -> RabbitMQPublisher:
    """
    Inyección de dependencia para el publicador de RabbitMQ.
    Simplemente devuelve la instancia global.
    """
    if publisher_instance is None:
        # Esto pasará si RabbitMQ falló al inicio
        logger.error("get_publisher: publisher_instance es None. La conexión inicial falló.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Servicio de mensajería (RabbitMQ) no disponible."
        )
    
    # Devuelve la instancia única que creamos al inicio
    return publisher_instance

# --- Modelos Pydantic para el Usuario ---
# (Estos modelos son para el JWT, pero ya no deberías usarlos)

class TokenData(BaseModel):
    id: int | None = None

class User(BaseModel):
    id: int


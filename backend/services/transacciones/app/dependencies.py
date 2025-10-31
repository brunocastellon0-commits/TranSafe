# transactions_service/app/dependencies.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
import logging # Añadir import

from . import security 
from .database import SessionLocal
from app.services.messaging import RabbitMQPublisher # 1. Importar el publicador

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

# 2. Inicializar el publicador (como hicimos antes)
try:
    publisher = RabbitMQPublisher(host='localhost') 
except Exception as e:
    logging.error(f"Error fatal al inicializar RabbitMQPublisher: {e}")
    publisher = None

def get_publisher() -> RabbitMQPublisher:
    """
    Inyección de dependencia para el publicador de RabbitMQ.
    Maneja reconexión simple si es necesario.
    """
    global publisher
    if publisher is None or not publisher.connection or publisher.connection.is_closed:
        logging.warning("Intentando reconectar a RabbitMQ...")
        try:
            publisher = RabbitMQPublisher(host='rabbitmq')
        except Exception as e:
            logging.error(f"Fallo la reconexión a RabbitMQ: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Servicio de mensajería no disponible"
            )
            
    return publisher

# --- Modelos Pydantic para el Usuario ---
# (Tu código aquí - sin cambios)

class TokenData(BaseModel):
    """El contenido esperado de nuestro token JWT."""
    id: int | None = None

class User(BaseModel):
    """El modelo de usuario simplificado que usaremos en la app."""
    id: int

# --- Dependencia de Autenticación ---
# (Tu código aquí - sin cambios)

async def get_current_user(
    token: str = Depends(security.oauth2_scheme), 
) -> User:
    """
    Decodifica el token JWT, valida al usuario y devuelve
    un modelo simple de Usuario.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            security.SECRET_KEY, 
            algorithms=[security.ALGORITHM]
        )
        
        user_id_str = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id_str is None or token_type != "access":
            raise credentials_exception
            
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise credentials_exception
            
        token_data = TokenData(id=user_id)
        
    except JWTError:
        raise credentials_exception

    return User(id=token_data.id)
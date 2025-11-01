from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Carga las configuraciones desde el archivo .env
    """
    
    # URL de RabbitMQ (con un valor por defecto)
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # URL del servicio de transacciones
    TRANSACTIONS_SERVICE_URL: str
    
    class Config:
        env_file = "../.env" # Le decimos que suba un nivel para encontrar el .env

# Creamos una instancia única que usaremos en el worker
settings = Settings()
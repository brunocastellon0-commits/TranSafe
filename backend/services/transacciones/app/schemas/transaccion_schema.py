from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Estado basado en la Máquina de Estados Finitos (MEF) 
class TransactionStatus(str, Enum):
    PENDING = "PENDING"      # ← Cambiado de "PENDIENTE"
    APPROVED = "APPROVED"    # ← Cambiado de "NORMAL"
    REJECTED = "REJECTED"    # ← Cambiado de "SOSPECHOSA"

class TransactionBase(BaseModel):
    # Campos requeridos por las reglas de negocio 
    cuenta_origen: str
    cuenta_destino: str
    monto: float
    ubicacion: str

class TransactionCreate(TransactionBase):
    # Este es el schema que usa el endpoint de FastAPI para *recibir* la transacción
    pass

class TransactionInDBBase(TransactionBase):
    # Este es el schema completo, usado para respuestas de API y mensajes de RabbitMQ
    id: int
    hora: datetime
    status: TransactionStatus = TransactionStatus.PENDING # Estado inicial

    class Config:
        from_attributes = True # Permite a Pydantic leer datos desde modelos SQLAlchemy

class StatusUpdate(BaseModel):
    """Schema para actualizar solo el estado de una transacción"""
    status: TransactionStatus
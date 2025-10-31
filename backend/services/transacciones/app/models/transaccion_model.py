from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.schemas.transaccion_schema import TransactionStatus # Importamos el Enum de Pydantic

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    cuenta_origen = Column(String(50), index=True)
    cuenta_destino = Column(String(50), index=True)
    monto = Column(Float)
    ubicacion = Column(String(100))
    hora = Column(DateTime, default=datetime.utcnow)
    
    # Este campo es crucial para el worker [cite: 19]
    status = Column(
        SQLAlchemyEnum(TransactionStatus), 
        nullable=False, 
        default=TransactionStatus.PENDING
    )
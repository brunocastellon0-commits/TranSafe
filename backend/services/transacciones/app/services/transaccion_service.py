# transaction_services.py
from sqlalchemy.orm import Session
from app.models import transaccion_model 
from app.schemas.transaccion_schema import TransactionBase,TransactionCreate,TransactionInDBBase,TransactionStatus
from app.services.messaging import RabbitMQPublisher

def create_transaction_and_notify(
    db: Session, 
    publisher: RabbitMQPublisher, 
    transaction: TransactionCreate
) -> transaccion_model.Transaction: # <--- CORRECCIÓN 1: El tipo de retorno es la *clase*
    """
    Lógica de negocio principal:
    1. Crea la transacción en la DB con estado PENDIENTE.
    2. Publica la transacción completa en RabbitMQ para análisis.
    """
    
    # 1. Crear el modelo SQLAlchemy a partir del schema Pydantic
    # Instanciamos la *clase* 'Transaction' desde el *módulo* 'transaccion_model'
    db_transaction = transaccion_model.Transaction( # <--- CORRECCIÓN 2: Instanciar la clase
        cuenta_origen=transaction.cuenta_origen,
        cuenta_destino=transaction.cuenta_destino,
        monto=transaction.monto,
        ubicacion=transaction.ubicacion
    )
    
    # 2. Guardar en Base de Datos
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction) # Refrescar para obtener el 'id' y 'hora' generados por la DB

    # 3. Preparar el mensaje para RabbitMQ
    # Usamos 'TransactionInDBBase' directamente, sin el prefijo 'schemas.'
    message_data = TransactionInDBBase.from_orm(db_transaction).dict() # <--- CORRECCIÓN 3
    
    # 4. Publicar en RabbitMQ
    publisher.publish_message(message_data)
    
    # 5. Devolver el objeto creado
    return db_transaction
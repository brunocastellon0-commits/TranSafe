# transaction_services.py
from sqlalchemy.orm import Session
from app.models import transaccion_model 
from app.schemas.transaccion_schema import TransactionBase, TransactionCreate, TransactionInDBBase, TransactionStatus
from app.services.messaging import RabbitMQPublisher

def create_transaction_and_notify(
    db: Session, 
    publisher: RabbitMQPublisher, 
    transaction: TransactionCreate
) -> transaccion_model.Transaction:
    """
    Lógica de negocio principal:
    1. Crea la transacción en la DB con estado PENDIENTE.
    2. Publica la transacción completa en RabbitMQ para análisis.
    """
    
    # 1. Crear el modelo SQLAlchemy a partir del schema Pydantic
    db_transaction = transaccion_model.Transaction(
        cuenta_origen=transaction.cuenta_origen,
        cuenta_destino=transaction.cuenta_destino,
        monto=transaction.monto,
        ubicacion=transaction.ubicacion
    )
    
    # 2. Guardar en Base de Datos
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # 3. Preparar el mensaje para RabbitMQ
    message_data = TransactionInDBBase.from_orm(db_transaction).dict()
    
    # 4. Publicar en RabbitMQ
    publisher.publish_message(message_data)
    
    # 5. Devolver el objeto creado
    return db_transaction


def get_transaction_by_id(db: Session, transaction_id: int) -> transaccion_model.Transaction:
    """
    Busca una transacción por su ID.
    
    Args:
        db: Sesión de base de datos
        transaction_id: ID de la transacción a buscar
        
    Returns:
        Transaction object si existe, None si no se encuentra
    """
    return db.query(transaccion_model.Transaction).filter(
        transaccion_model.Transaction.id == transaction_id
    ).first()


def update_transaction_status(
    db: Session, 
    transaction_id: int, 
    new_status: TransactionStatus
) -> transaccion_model.Transaction:
    """
    Actualiza el estado de una transacción existente.
    
    Args:
        db: Sesión de base de datos
        transaction_id: ID de la transacción a actualizar
        new_status: Nuevo estado (PENDING, APPROVED, REJECTED)
        
    Returns:
        Transaction object actualizado, o None si no se encuentra
    """
    # Buscar la transacción
    transaction = get_transaction_by_id(db, transaction_id)
    
    if not transaction:
        return None
    
    # Actualizar el estado
    transaction.status = new_status
    db.commit()
    db.refresh(transaction)
    
    return transaction
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.transaccion_schema import TransactionBase, TransactionCreate, TransactionInDBBase, TransactionStatus, StatusUpdate
from app.services import transaccion_service
from app.dependencies import get_db, get_publisher, get_current_user
from app.dependencies import User # Importamos el Pydantic model 'User'

# Creamos un router de FastAPI
router = APIRouter(
    prefix="/transactions",  # Prefijo para todas las rutas en este archivo
    tags=["Transacciones"],  # Etiqueta para la documentación de Swagger/OpenAPI
)

@router.post(
    "/", 
    response_model=TransactionInDBBase,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva transacción"
)
def create_transaction_endpoint(
    # 1. Cuerpo de la petición: Validado contra el schema TransactionCreate
    transaction_data: TransactionCreate,
    
    # 2. Inyección de Dependencias:
    db: Session = Depends(get_db),
    publisher = Depends(get_publisher),
    
    # 3. Dependencia de Seguridad:
    # Si el token no es válido o está expirado, 'get_current_user'
    # lanzará una HTTPException 401 y esta función nunca se ejecutará.
    current_user: User = Depends(get_current_user) 
):
    """
    Endpoint para recibir una nueva transacción financiera.

    - **Autentica** al usuario vía JWT.
    - **Valida** los datos de entrada (`TransactionCreate`).
    - **Guarda** la transacción en MySQL (estado PENDIENTE).
    - **Publica** el mensaje en RabbitMQ para análisis de fraude.
    - **Retorna** la transacción creada con su ID y estado.
    
    (Nota: El 'current_user' se usa para autenticar, pero no es
    necesario pasarlo a la lógica de negocio a menos que
    quisiéramos ligar la transacción al usuario que la creó.)
    """
    
    try:
        # 4. Llamada a la Lógica de Negocio:
        # Pasamos la sesión de BD, el publicador y los datos validados.
        created_transaction = transaccion_service.create_transaction_and_notify(
            db=db,
            publisher=publisher,
            transaction=transaction_data
        )
        
        # 5. Respuesta:
        # FastAPI convertirá automáticamente el objeto de SQLAlchemy
        # a un JSON usando el 'response_model' (TransactionInDBBase).
        return created_transaction
        
    except HTTPException as http_err:
        # Si el publisher falló (503), lo relanzamos
        raise http_err
    except Exception as e:
        # 5. Manejo de Errores:
        # Captura genérica por si falla la BD o algo inesperado.
        print(f"Error inesperado al crear transacción: {e}") # Log del error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar la transacción."
        )


@router.patch(
    "/{transaction_id}/status",
    response_model=TransactionInDBBase,
    summary="Actualizar estado de una transacción (uso interno)"
)
def update_transaction_status_endpoint(
    transaction_id: int,
    status_update: StatusUpdate,  # ← CAMBIO: usa el schema StatusUpdate
    db: Session = Depends(get_db)
):
    """
    Endpoint interno para que el fraud_service actualice el estado
    de una transacción después de analizarla.
    
    **Nota de Seguridad:** En producción, este endpoint debería estar
    protegido (solo accesible desde la red interna o con autenticación
    de servicio a servicio).
    """
    
    # Buscar y actualizar la transacción
    updated_transaction = transaccion_service.update_transaction_status(
        db=db,
        transaction_id=transaction_id,
        new_status=status_update.status  # ← CAMBIO: accede al campo status
    )
    
    if not updated_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transacción {transaction_id} no encontrada"
        )
    
    return updated_transaction
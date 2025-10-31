# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- CORRECCIONES DE IMPORTACIÓN ---
# Usa '.' para importar módulos en el mismo directorio (paquete 'app')
from app.models import transaccion_model as  models 
from .database import engine
from .routes.transaccion_routes import router as transaction_router
# -----------------------------------

# 1. Creación de Tablas en la Base de Datos
# Esta línea ahora funcionará porque 'models' se importa correctamente
# y 'models.py' define 'Base'.
models.Base.metadata.create_all(bind=engine)

# 2. Instancia de la Aplicación FastAPI
app = FastAPI(
    title="Servicio de Transacciones",
    version="1.0.0"
)

# 3. Configuración de CORS
origins = [
    "http://localhost:3000",  
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,      
    allow_methods=["*"],         
    allow_headers=["*"],         
)

# 4. Inclusión de las Rutas de Transacciones
app.include_router(transaction_router)


# 5. Endpoint de Health Check
@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Endpoint simple para verificar que el servicio está
    corriendo y saludable.
    """
    return {"status": "ok", "service": "transactions_service"}
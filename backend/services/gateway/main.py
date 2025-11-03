# gateway/main.py
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from security import get_current_user, AUTH_SERVICE_URL

app = FastAPI(title="API Gateway")

# URLs de tus microservicios
# ⚠️ IMPORTANTE: El nombre debe coincidir con el nombre del servicio en docker-compose.yml
TRANSACCION_SERVICE_URL = "http://transactions_service:8001"  # ← Cambio aquí
# Si el nombre en docker-compose es diferente, ajusta esta línea

# --- Funciones de Proxy ---

async def proxy_request(client: httpx.AsyncClient, service_url: str, request: Request):
    """
    Función genérica para reenviar una petición a un microservicio.
    """
    try:
        url = f"{service_url}{request.url.path}"
        
        # Prepara la petición para el microservicio
        body = None
        if request.method not in ("GET", "HEAD"):
             body = await request.json()

        response = await client.request(
            method=request.method,
            url=url,
            json=body,
            params=request.query_params
        )
        
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPStatusError as e:
        # Reenviar el error exacto del microservicio
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=e.response.json()
        )
    except httpx.RequestError as req_err:
        # El servicio no está disponible - agregamos más detalles
        raise HTTPException(
            status_code=503,
            detail=f"Servicio en {service_url} no disponible. Error: {str(req_err)}"
        )

# --- RUTAS PÚBLICAS (Redirección a auth_service) ---

@app.post("/api/auth/register")
async def register(request: Request):
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

@app.post("/api/auth/login")
async def login(request: Request):
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

@app.post("/api/auth/refresh")
async def refresh(request: Request):
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

# --- RUTAS PROTEGIDAS (Validadas por el Gateway) ---

@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Obtiene el usuario actual. 
    Los datos provienen directamente de la dependencia 'get_current_user'.
    """
    return current_user

# Ruta de Transacciones
@app.post("/transactions/")
async def create_transaction(
    request: Request, 
    current_user: dict = Depends(get_current_user) 
):
    """
    Crea una nueva transacción.
    1. El Gateway valida el token JWT.
    2. Si es válido, reenvía la petición al servicio de transacciones.
    """
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, TRANSACCION_SERVICE_URL, request)
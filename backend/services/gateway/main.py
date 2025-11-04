# gateway/main.py
import httpx
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from security import get_current_user, AUTH_SERVICE_URL

app = FastAPI(title="API Gateway")

# ✅ CONFIGURACIÓN DE CORS MEJORADA
# Obtener orígenes permitidos desde variable de entorno o usar defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # URLs del frontend
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

# URLs de tus microservicios
TRANSACCION_SERVICE_URL = "http://transactions_service:8001"

print(f"🚀 Gateway iniciado")
print(f"🔒 CORS habilitado para: {cors_origins}")
print(f"🔗 Auth Service: {AUTH_SERVICE_URL}")
print(f"🔗 Transaction Service: {TRANSACCION_SERVICE_URL}")

# --- Funciones de Proxy ---

async def proxy_request(client: httpx.AsyncClient, service_url: str, request: Request, forward_auth: bool = False):
    """
    Función genérica para reenviar una petición a un microservicio.
    
    Args:
        client: Cliente HTTP asíncrono
        service_url: URL base del servicio destino
        request: Request de FastAPI
        forward_auth: Si True, reenvía el header Authorization al servicio
    """
    try:
        # Construir URL completa
        url = f"{service_url}{request.url.path}"
        
        # Preparar headers
        headers = dict(request.headers)
        # Remover headers problemáticos
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # Si no queremos reenviar auth, lo removemos
        if not forward_auth:
            headers.pop("authorization", None)
        
        # Prepara el body de la petición
        body = None
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            try:
                body = await request.json()
            except:
                body = None

        print(f"📤 {request.method} {url}")
        if body:
            print(f"📦 Body: {body}")

        # Hacer la petición al microservicio
        response = await client.request(
            method=request.method,
            url=url,
            json=body,
            params=request.query_params,
            headers=headers,
            timeout=30.0
        )
        
        response.raise_for_status()
        result = response.json()
        print(f"✅ Respuesta exitosa de {service_url}")
        return result
        
    except httpx.HTTPStatusError as e:
        # Reenviar el error exacto del microservicio
        error_detail = e.response.text
        try:
            error_detail = e.response.json()
        except:
            pass
        
        print(f"❌ Error {e.response.status_code} de {service_url}: {error_detail}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=error_detail
        )
    except httpx.RequestError as req_err:
        # El servicio no está disponible
        print(f"❌ Error conectando con {service_url}: {str(req_err)}")
        raise HTTPException(
            status_code=503,
            detail=f"Servicio no disponible: {str(req_err)}"
        )
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

# --- RUTAS DE SALUD ---

@app.get("/health")
async def health_check():
    """Endpoint de salud del gateway"""
    return {
        "status": "healthy",
        "service": "API Gateway",
        "auth_service": AUTH_SERVICE_URL,
        "transaction_service": TRANSACCION_SERVICE_URL,
        "cors_origins": cors_origins
    }

# --- RUTAS PÚBLICAS (Sin autenticación) ---

@app.post("/api/auth/register")
async def register(request: Request):
    """Registro de nuevo usuario"""
    print("🔐 Gateway: Redirigiendo registro a auth service")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

@app.post("/api/auth/login")
async def login(request: Request):
    """Login de usuario"""
    print("🔐 Gateway: Redirigiendo login a auth service")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

@app.post("/api/auth/refresh")
async def refresh(request: Request):
    """Refresh de token"""
    print("🔄 Gateway: Redirigiendo refresh a auth service")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request)

# --- RUTAS PROTEGIDAS (Requieren autenticación) ---

@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Obtiene el usuario actual"""
    print(f"👤 Gateway: Usuario autenticado - ID: {current_user.get('id')}")
    return current_user

@app.put("/api/auth/me")
async def update_me(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza información del usuario actual"""
    print(f"✏️ Gateway: Actualizando usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request, forward_auth=True)

@app.post("/api/auth/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Cierra sesión del usuario"""
    print(f"👋 Gateway: Cerrando sesión de usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request, forward_auth=True)

@app.post("/api/auth/logout-all")
async def logout_all(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Cierra todas las sesiones del usuario"""
    print(f"👋👋 Gateway: Cerrando todas las sesiones de usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, AUTH_SERVICE_URL, request, forward_auth=True)

@app.get("/api/auth/verify")
def verify_token(current_user: dict = Depends(get_current_user)):
    """Verifica si el token es válido"""
    return {"message": "Token válido", "user": current_user}

# --- RUTAS DE TRANSACCIONES ---

@app.post("/transactions/")
async def create_transaction(
    request: Request, 
    current_user: dict = Depends(get_current_user) 
):
    """Crea una nueva transacción"""
    print(f"💰 Gateway: Creando transacción para usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        # Agregar user_id al body
        body = await request.json()
        body['user_id'] = current_user.get('id')
        
        # Crear nueva request con el body modificado
        url = f"{TRANSACCION_SERVICE_URL}/transactions/"
        response = await client.post(url, json=body, timeout=30.0)
        response.raise_for_status()
        return response.json()

@app.get("/transactions/")
async def get_transactions(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todas las transacciones del usuario"""
    print(f"📋 Gateway: Obteniendo transacciones de usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, TRANSACCION_SERVICE_URL, request, forward_auth=True)

@app.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene una transacción específica"""
    print(f"🔍 Gateway: Obteniendo transacción {transaction_id} para usuario {current_user.get('id')}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, TRANSACCION_SERVICE_URL, request, forward_auth=True)

@app.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza una transacción"""
    print(f"✏️ Gateway: Actualizando transacción {transaction_id}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, TRANSACCION_SERVICE_URL, request, forward_auth=True)

@app.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Elimina una transacción"""
    print(f"🗑️ Gateway: Eliminando transacción {transaction_id}")
    async with httpx.AsyncClient() as client:
        return await proxy_request(client, TRANSACCION_SERVICE_URL, request, forward_auth=True)

# --- MANEJO DE ERRORES GLOBAL ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Maneja todas las excepciones HTTP"""
    print(f"❌ Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones generales no capturadas"""
    print(f"❌ Error no capturado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
# gateway/security.py
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 1. URLs de tus servicios
AUTH_SERVICE_URL = "http://auth_service:8000"

# 2. El 'tokenUrl' AHORA apunta al endpoint de login DEL PROPIO GATEWAY.
#    Esta es la ruta que el cliente (Swagger) usará para obtener el token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Esta dependencia se usa en las rutas protegidas del Gateway.
    
    1. Obtiene el token de la cabecera "Authorization".
    2. Llama al endpoint '/api/auth/me' del auth_service para validarlo.
    3. Si es válido (200 OK), devuelve los datos del usuario.
    4. Si es inválido (401) o el servicio falla, lanza un error 401.
    """
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Llamamos a tu endpoint 'GET /me' del auth_service
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/me", 
                headers=headers
            )
            
            # 4. Si auth_service dice 401 (inválido) o 500, lanzamos error
            response.raise_for_status() 
            
            # 5. Si todo OK, devolvemos los datos del usuario
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # Captura errores 401, 404, 500 del auth_service
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except httpx.RequestError:
            # Captura si el auth_service está caído
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de autenticación no disponible",
            )
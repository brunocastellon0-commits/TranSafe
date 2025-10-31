# transactions_service/app/security.py

from fastapi.security import OAuth2PasswordBearer
from .config import settings # Importa la configuración

# Este objeto le dice a FastAPI "ve a la URL /token para obtener el token",
# pero en realidad solo nos importa para que busque el 'Bearer' token.
# La URL /token vive en el auth_service, no aquí.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

# Necesitaremos estos valores para decodificar el token en dependencies.py
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
from datetime import datetime, timedelta
from typing import Optional, Tuple  # <-- MODIFICADO: Añadido Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# --- MODIFICADO ---
# 1. "argon2" es ahora el esquema por defecto (el primero de la lista).
# 2. "bcrypt" se marca como obsoleto (deprecated).
#    Esto significa que `passlib` PUEDE verificar hashes bcrypt,
#    pero NUNCA creará uno nuevo.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], 
    deprecated="bcrypt"
)
# --- FIN DE MODIFICACIÓN ---


# --- MODIFICADO ---
def verify_password(plain_password: str, hashed_password: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica si la contraseña coincide con el hash.
    Si el hash es obsoleto (bcrypt), genera un nuevo hash (argon2).
    
    Retorna una tupla: (es_valido, nuevo_hash_opcional)
    """
    # Esta función hace 3 cosas en 1 solo paso:
    # 1. Compara la contraseña con el hash (entiende si es bcrypt o argon2).
    # 2. Si es válida Y el hash es "bcrypt" (obsoleto), genera un nuevo hash "argon2".
    # 3. Si el hash ya es "argon2" (o no es obsoleto), nuevo_hash_opcional será None.
    return pwd_context.verify_and_update(plain_password, hashed_password)
# --- FIN DE MODIFICACIÓN ---


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña.
    (Ahora usará argon2 por defecto, ¡sin límite de 72 caracteres!)
    """
    return pwd_context.hash(password)

# --- TUS FUNCIONES JWT (Están perfectas, no necesitan cambios) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un refresh token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decodifica y verifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # Es mejor retornar None o lanzar una excepción específica
        return None
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_schema import (
    UserCreate, UserResponse, LoginRequest, Token, 
    RefreshTokenRequest, MessageResponse, UserWithToken, UserUpdate
)
from app.services.user_service import UserService
from app.services.token_services import TokenService
from app.dependencies import get_current_user, get_current_superuser
from app.models.user_model import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    # Crear usuario
    db_user = UserService.create_user(db, user)
    
    # Crear tokens
    tokens = TokenService.create_tokens(db_user, db)
    
    return {
        "user": db_user,
        "tokens": tokens
    }

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión y retorna tokens JWT"""
    # Autenticar usuario
    user = UserService.authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens
    tokens = TokenService.create_tokens(user, db)
    
    return tokens

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Genera un nuevo access token usando el refresh token"""
    # Verificar refresh token
    db_token = TokenService.verify_refresh_token(refresh_data.refresh_token, db)
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario
    user = UserService.get_user_by_id(db, db_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Revocar el refresh token antiguo
    TokenService.revoke_refresh_token(refresh_data.refresh_token, db)
    
    # Crear nuevos tokens
    tokens = TokenService.create_tokens(user, db)
    
    return tokens

@router.post("/logout", response_model=MessageResponse)
def logout(
    refresh_token: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cierra sesión revocando el refresh token"""
    TokenService.revoke_refresh_token(refresh_token.refresh_token, db)
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/logout-all", response_model=MessageResponse)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cierra todas las sesiones del usuario"""
    count = TokenService.revoke_all_user_tokens(current_user.id, db)
    return {"message": f"Se cerraron {count} sesiones"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza la información del usuario actual"""
    updated_user = UserService.update_user(db, current_user.id, user_update)
    return updated_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Obtiene un usuario por ID (solo superusuarios)"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.get("/verify", response_model=MessageResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    """Verifica si el token es válido"""
    return {"message": "Token válido"}
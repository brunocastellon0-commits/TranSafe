from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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
    try:
        print(f"📝 Intentando registrar usuario: {user.email}")
        print(f"📦 Datos recibidos: username={user.username}, email={user.email}")
        
        # ✅ CORREGIDO: Validar USERNAME (no 'name')
        if not user.username or not user.username.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario es requerido"
            )
        
        # Validar longitud del username
        if len(user.username.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario debe tener al menos 3 caracteres"
            )
        
        if len(user.username.strip()) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario no puede tener más de 100 caracteres"
            )
        
        # Validar que el email no esté vacío
        if not user.email or not user.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email es requerido"
            )
        
        # Validar longitud de contraseña
        if not user.password or len(user.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres"
            )
        
        # Verificar si el usuario ya existe
        existing_user = UserService.get_user_by_email(db, user.email)
        if existing_user:
            print(f"⚠️ Usuario ya existe: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear usuario
        db_user = UserService.create_user(db, user)
        print(f"✅ Usuario creado exitosamente: {db_user.email} (ID: {db_user.id})")
        
        # Crear tokens
        tokens = TokenService.create_tokens(db_user, db)
        print(f"✅ Tokens generados para usuario ID: {db_user.id}")
        
        return {
            "user": db_user,
            "tokens": tokens
        }
        
    except HTTPException:
        # Re-lanzar HTTPException tal cual
        raise
    except IntegrityError as e:
        # Error de integridad de base de datos (email duplicado, etc.)
        print(f"❌ Error de integridad: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    except Exception as e:
        # Cualquier otro error
        print(f"❌ Error inesperado en registro: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión y retorna tokens JWT"""
    try:
        print(f"🔐 Intento de login: {login_data.email}")
        
        # Validar datos de entrada
        if not login_data.email or not login_data.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email es requerido"
            )
        
        if not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña es requerida"
            )
        
        # Autenticar usuario
        user = UserService.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            print(f"❌ Credenciales inválidas para: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ Usuario autenticado: {user.email} (ID: {user.id})")
        
        # Crear tokens
        tokens = TokenService.create_tokens(user, db)
        print(f"✅ Tokens generados para usuario ID: {user.id}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar sesión"
        )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Genera un nuevo access token usando el refresh token"""
    try:
        print(f"🔄 Intentando refrescar token")
        
        # Verificar refresh token
        db_token = TokenService.verify_refresh_token(refresh_data.refresh_token, db)
        
        if not db_token:
            print(f"❌ Refresh token inválido o expirado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario
        user = UserService.get_user_by_id(db, db_token.user_id)
        if not user:
            print(f"❌ Usuario no encontrado: {db_token.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        print(f"✅ Refresh token válido para usuario ID: {user.id}")
        
        # Revocar el refresh token antiguo
        TokenService.revoke_refresh_token(refresh_data.refresh_token, db)
        
        # Crear nuevos tokens
        tokens = TokenService.create_tokens(user, db)
        print(f"✅ Nuevos tokens generados para usuario ID: {user.id}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado en refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al refrescar token"
        )

@router.post("/logout", response_model=MessageResponse)
def logout(
    refresh_token: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cierra sesión revocando el refresh token"""
    try:
        print(f"👋 Usuario {current_user.id} cerrando sesión")
        TokenService.revoke_refresh_token(refresh_token.refresh_token, db)
        print(f"✅ Sesión cerrada para usuario ID: {current_user.id}")
        return {"message": "Sesión cerrada exitosamente"}
    except Exception as e:
        print(f"❌ Error en logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )

@router.post("/logout-all", response_model=MessageResponse)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cierra todas las sesiones del usuario"""
    try:
        print(f"👋👋 Usuario {current_user.id} cerrando todas las sesiones")
        count = TokenService.revoke_all_user_tokens(current_user.id, db)
        print(f"✅ {count} sesiones cerradas para usuario ID: {current_user.id}")
        return {"message": f"Se cerraron {count} sesiones"}
    except Exception as e:
        print(f"❌ Error en logout-all: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesiones"
        )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    print(f"👤 Obteniendo info del usuario ID: {current_user.id}")
    return current_user

@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza la información del usuario actual"""
    try:
        print(f"✏️ Actualizando usuario ID: {current_user.id}")
        updated_user = UserService.update_user(db, current_user.id, user_update)
        print(f"✅ Usuario actualizado ID: {current_user.id}")
        return updated_user
    except Exception as e:
        print(f"❌ Error al actualizar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar usuario"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Obtiene un usuario por ID (solo superusuarios)"""
    try:
        print(f"🔍 Superusuario {current_user.id} consultando usuario ID: {user_id}")
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            print(f"❌ Usuario no encontrado: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al obtener usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuario"
        )

@router.get("/verify", response_model=MessageResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    """Verifica si el token es válido"""
    print(f"✅ Token válido para usuario ID: {current_user.id}")
    return {"message": "Token válido"}
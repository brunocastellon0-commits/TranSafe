from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.security import get_password_hash, verify_password
from typing import Optional

class UserService:
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Obtiene un usuario por username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crea un nuevo usuario"""
        # Verificar si el email ya existe
        if UserService.get_user_by_email(db, user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar si el username ya existe
        if UserService.get_user_by_username(db, user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está registrado"
            )
        
        # Crear usuario
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario.
        Verifica la contraseña y actualiza el hash si es obsoleto (e.g., bcrypt a argon2).
        """
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            return None
        
        # 'verify_password' ahora retorna una tupla: (is_valid, new_hash_or_none)
        is_valid, new_hash = verify_password(password, user.hashed_password)
        
        if not is_valid:
            return None
        
        # Si la verificación fue exitosa y se generó un nuevo hash (porque el
        # antiguo era obsoleto), se actualiza en la base de datos.
        if new_hash:
            user.hashed_password = new_hash
            db.add(user)
            db.commit()
            db.refresh(user)
            
        if not user.is_active:
            # Considerar lanzar una excepción HTTPException 403 (Forbidden)
            # si se desea un feedback más claro que un fallo de autenticación.
            return None
            
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Actualiza un usuario"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Usar model_dump (Pydantic v2) para obtener solo los campos seteados
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Si se actualiza el email, verificar que no exista
        if "email" in update_data:
            existing_user = UserService.get_user_by_email(db, update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
        
        # Si se actualiza el username, verificar que no exista
        if "username" in update_data:
            existing_user = UserService.get_user_by_username(db, update_data["username"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El username ya está registrado"
                )
        
        # Si se actualiza la contraseña, hashearla
        if "password" in update_data:
            # Se hashea la nueva contraseña y se elimina la clave 'password'
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user

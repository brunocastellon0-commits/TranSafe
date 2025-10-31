from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user_model import RefreshToken, User
from app.services.security import create_access_token, create_refresh_token, decode_token
from app.config import get_settings
from typing import Dict

settings = get_settings()

class TokenService:
    
    @staticmethod
    def create_tokens(user: User, db: Session) -> Dict[str, str]:
        """Crea access token y refresh token para un usuario"""
        # Crear access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Crear refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Guardar refresh token en la BD
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        db.add(db_refresh_token)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def verify_refresh_token(token: str, db: Session) -> RefreshToken:
        """Verifica si un refresh token es válido"""
        # Decodificar token
        payload = decode_token(token)
        if not payload:
            return None
        
        # Verificar tipo de token
        if payload.get("type") != "refresh":
            return None
        
        # Buscar en BD
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        ).first()
        
        if not db_token:
            return None
        
        # Verificar expiración
        if db_token.expires_at < datetime.utcnow():
            return None
        
        return db_token
    
    @staticmethod
    def revoke_refresh_token(token: str, db: Session) -> bool:
        """Revoca un refresh token"""
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if db_token:
            db_token.is_revoked = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_tokens(user_id: int, db: Session) -> int:
        """Revoca todos los refresh tokens de un usuario"""
        count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()
        return count
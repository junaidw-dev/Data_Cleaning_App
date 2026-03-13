import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status
from config import Config

class AuthService:
    """Authentication and security service."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create a JWT access token."""
        config = Config()
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, str]:
        """Verify and decode a JWT token."""
        config = Config()
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash an API key for storage."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(key.encode(), salt).decode()
    
    @staticmethod
    def verify_api_key(key: str, hashed: str) -> bool:
        """Verify an API key against its hash."""
        return bcrypt.checkpw(key.encode(), hashed.encode())
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key."""
        import secrets
        return f"sk_{secrets.token_urlsafe(32)}"

class PasswordResetService:
    """Password reset token management."""
    
    @staticmethod
    def create_reset_token(user_id: str) -> str:
        """Create a reset password token."""
        config = Config()
        payload = {
            "user_id": user_id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_reset_token(token: str) -> str:
        """Verify a reset token and return user_id."""
        config = Config()
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

"""
AutoPPM JWT Authentication Handler
Manages JWT tokens for user authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger
from config.settings import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTHandler:
    """JWT token management and validation"""
    
    def __init__(self):
        """Initialize JWT handler with settings"""
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                logger.warning("Token missing expiration")
                return None
            
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token expired")
                return None
            
            logger.info(f"Token verified for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from JWT token"""
        try:
            payload = self.verify_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    return int(user_id)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting user ID from token: {e}")
            return None
    
    def create_user_token(self, user_id: int, email: str, username: str) -> str:
        """Create JWT token for user authentication"""
        try:
            data = {
                "sub": str(user_id),
                "email": email,
                "username": username,
                "type": "access"
            }
            
            token = self.create_access_token(data)
            logger.info(f"User token created for user ID: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating user token: {e}")
            raise
    
    def create_zerodha_token(self, user_id: int, kite_user_id: str) -> str:
        """Create JWT token for Zerodha authentication"""
        try:
            data = {
                "sub": str(user_id),
                "kite_user_id": kite_user_id,
                "type": "zerodha_access"
            }
            
            token = self.create_access_token(data)
            logger.info(f"Zerodha token created for user ID: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating Zerodha token: {e}")
            raise


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


# Global JWT handler instance
jwt_handler = JWTHandler()


def get_jwt_handler() -> JWTHandler:
    """Get JWT handler instance"""
    return jwt_handler

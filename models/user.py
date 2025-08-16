"""
AutoPPM User Models
Database models for user management and Zerodha account integration
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from pydantic import BaseModel, Field

# Import Base from database connection
from database.connection import Base


class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Optional for OAuth-only users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Zerodha Account Information
    zerodha_user_id = Column(String(100), unique=True, index=True, nullable=True)
    zerodha_access_token = Column(Text, nullable=True)
    zerodha_refresh_token = Column(Text, nullable=True)
    zerodha_token_expires_at = Column(DateTime, nullable=True)
    
    # Profile Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Trading Preferences
    risk_tolerance = Column(String(50), default="moderate")  # low, moderate, high
    investment_horizon = Column(String(50), default="medium")  # short, medium, long
    preferred_strategies = Column(Text, nullable=True)  # JSON string of strategy preferences


class ZerodhaAccount(Base):
    """Zerodha account details model"""
    __tablename__ = "zerodha_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    kite_user_id = Column(String(100), nullable=False)
    kite_access_token = Column(Text, nullable=False)
    kite_refresh_token = Column(Text, nullable=True)
    kite_token_expires_at = Column(DateTime, nullable=False)
    
    # Account Details
    account_type = Column(String(50), nullable=True)  # equity, commodity, etc.
    broker_user_id = Column(String(100), nullable=True)
    broker_user_name = Column(String(255), nullable=True)
    
    # Connection Status
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic models for API requests/responses
class UserCreate(BaseModel):
    """User creation request model"""
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    password: Optional[str] = Field(None, description="Password (optional for OAuth)")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    risk_tolerance: str
    investment_horizon: str
    
    class Config:
        from_attributes = True


class ZerodhaConnection(BaseModel):
    """Zerodha connection request model"""
    request_token: str = Field(..., description="Request token from Zerodha")


class ZerodhaConnectionResponse(BaseModel):
    """Zerodha connection response model"""
    user_id: int
    kite_user_id: str
    account_type: Optional[str]
    broker_user_name: Optional[str]
    is_active: bool
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request model"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Authentication token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

"""
AutoPPM Market Data Models
Database models for market data storage and management
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, Text, Index
from pydantic import BaseModel, Field

# Import Base from database connection
from database.connection import Base


class MarketData(Base):
    """Real-time market data storage"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(BigInteger, nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    
    # Price Data
    last_price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    
    # Volume and Trading Data
    volume = Column(BigInteger, nullable=False)
    turnover = Column(Float, nullable=False)
    
    # OHLC Data
    ohlc_open = Column(Float, nullable=False)
    ohlc_high = Column(Float, nullable=False)
    ohlc_low = Column(Float, nullable=False)
    ohlc_close = Column(Float, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional Data
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_instrument_timestamp', 'instrument_token', 'timestamp'),
    )


class HistoricalData(Base):
    """Historical market data for backtesting"""
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(BigInteger, nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    
    # OHLCV Data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Date and Time
    date = Column(DateTime, nullable=False, index=True)
    interval = Column(String(10), nullable=False, default="day")  # day, minute, etc.
    
    # Additional Data
    turnover = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_date_interval', 'symbol', 'date', 'interval'),
        Index('idx_instrument_date_interval', 'instrument_token', 'date', 'interval'),
    )


class Instrument(Base):
    """Stock/Instrument information"""
    __tablename__ = "instruments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(BigInteger, nullable=False, unique=True, index=True)
    trading_symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    exchange = Column(String(20), nullable=False, index=True)
    
    # Instrument Details
    instrument_type = Column(String(20), nullable=False)  # EQ, FUT, OPT, etc.
    segment = Column(String(20), nullable=False)  # NSE, BSE, etc.
    
    # Trading Details
    lot_size = Column(Integer, nullable=False, default=1)
    tick_size = Column(Float, nullable=False, default=0.01)
    
    # Expiry (for derivatives)
    expiry = Column(DateTime, nullable=True)
    strike = Column(Float, nullable=True)
    
    # Status
    is_active = Column(String(1), nullable=False, default="Y")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trading_symbol_exchange', 'trading_symbol', 'exchange'),
        Index('idx_instrument_type_segment', 'instrument_type', 'segment'),
    )


class PortfolioSnapshot(Base):
    """Portfolio holdings snapshot"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    kite_user_id = Column(String(100), nullable=False, index=True)
    
    # Portfolio Data
    total_value = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    day_pnl = Column(Float, nullable=False)
    
    # Holdings Summary
    total_holdings = Column(Integer, nullable=False, default=0)
    total_positions = Column(Integer, nullable=False, default=0)
    
    # Timestamp
    snapshot_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_snapshot_time', 'user_id', 'snapshot_time'),
        Index('idx_kite_user_snapshot_time', 'kite_user_id', 'snapshot_time'),
    )


# Pydantic models for API requests/responses
class MarketDataResponse(BaseModel):
    """Market data response model"""
    symbol: str
    last_price: float
    change: Optional[float]
    change_percent: Optional[float]
    volume: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class HistoricalDataRequest(BaseModel):
    """Historical data request model"""
    symbol: str
    from_date: datetime
    to_date: datetime
    interval: str = Field(default="day", description="Data interval: day, minute, etc.")


class HistoricalDataResponse(BaseModel):
    """Historical data response model"""
    symbol: str
    data: List[dict]
    interval: str
    from_date: datetime
    to_date: datetime
    
    class Config:
        from_attributes = True


class InstrumentResponse(BaseModel):
    """Instrument response model"""
    instrument_token: int
    trading_symbol: str
    name: str
    exchange: str
    instrument_type: str
    lot_size: int
    tick_size: float
    
    class Config:
        from_attributes = True


class PortfolioSnapshotResponse(BaseModel):
    """Portfolio snapshot response model"""
    user_id: int
    total_value: float
    total_pnl: float
    day_pnl: float
    total_holdings: int
    snapshot_time: datetime
    
    class Config:
        from_attributes = True

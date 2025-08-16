"""
AutoPPM Data Ingestion Service
Handles real-time market data collection and portfolio synchronization
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from loguru import logger
from database.connection import get_database_session, create_tables
from models.market_data import MarketData, HistoricalData, Instrument, PortfolioSnapshot
from services.zerodha_service import get_zerodha_service
from config.settings import get_settings

settings = get_settings()


class DataIngestionService:
    """Service for ingesting market data and portfolio information"""
    
    def __init__(self):
        """Initialize data ingestion service"""
        self.zerodha_service = get_zerodha_service()
        self.is_running = False
        self.ingestion_interval = 5  # seconds
        self.last_sync = {}
        
        logger.info("Data ingestion service initialized")
    
    async def start_ingestion(self):
        """Start continuous data ingestion"""
        try:
            self.is_running = True
            logger.info("Starting data ingestion service...")
            
            # Create database tables if they don't exist
            create_tables()
            
            # Start ingestion tasks
            await asyncio.gather(
                self.market_data_ingestion_loop(),
                self.portfolio_sync_loop(),
                self.instrument_sync_loop()
            )
            
        except Exception as e:
            logger.error(f"Data ingestion service failed: {e}")
            self.is_running = False
            raise
    
    async def stop_ingestion(self):
        """Stop data ingestion service"""
        self.is_running = False
        logger.info("Data ingestion service stopped")
    
    async def market_data_ingestion_loop(self):
        """Continuous loop for market data ingestion"""
        while self.is_running:
            try:
                await self.ingest_market_data()
                await asyncio.sleep(self.ingestion_interval)
                
            except Exception as e:
                logger.error(f"Market data ingestion error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def portfolio_sync_loop(self):
        """Continuous loop for portfolio synchronization"""
        while self.is_running:
            try:
                await self.sync_portfolio_data()
                await asyncio.sleep(60)  # Sync portfolio every minute
                
            except Exception as e:
                logger.error(f"Portfolio sync error: {e}")
                await asyncio.sleep(60)
    
    async def instrument_sync_loop(self):
        """Continuous loop for instrument synchronization"""
        while self.is_running:
            try:
                await self.sync_instruments()
                await asyncio.sleep(3600)  # Sync instruments every hour
                
            except Exception as e:
                logger.error(f"Instrument sync error: {e}")
                await asyncio.sleep(3600)
    
    async def ingest_market_data(self):
        """Ingest real-time market data"""
        try:
            # Get active instruments from database
            instruments = self.get_active_instruments()
            
            if not instruments:
                logger.warning("No active instruments found for market data ingestion")
                return
            
            # Get market data for active instruments
            symbols = [inst.trading_symbol for inst in instruments]
            market_data = await self.get_market_data_batch(symbols)
            
            # Store market data in database
            if market_data:
                self.store_market_data(market_data)
                logger.info(f"Ingested market data for {len(market_data)} symbols")
            
        except Exception as e:
            logger.error(f"Market data ingestion failed: {e}")
    
    async def get_market_data_batch(self, symbols: List[str]) -> List[Dict]:
        """Get market data for multiple symbols"""
        try:
            # This would be implemented with real Zerodha API calls
            # For now, return mock data
            market_data = []
            
            for symbol in symbols:
                mock_data = {
                    "symbol": symbol,
                    "last_price": 100.0 + (hash(symbol) % 100),
                    "open_price": 99.0 + (hash(symbol) % 100),
                    "high_price": 101.0 + (hash(symbol) % 100),
                    "low_price": 98.0 + (hash(symbol) % 100),
                    "close_price": 100.0 + (hash(symbol) % 100),
                    "volume": 1000000 + (hash(symbol) % 1000000),
                    "turnover": 100000000.0 + (hash(symbol) % 100000000),
                    "timestamp": datetime.utcnow()
                }
                market_data.append(mock_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to get market data batch: {e}")
            return []
    
    def store_market_data(self, market_data: List[Dict]):
        """Store market data in database"""
        try:
            session = next(get_database_session())
            
            for data in market_data:
                # Create market data record
                market_record = MarketData(
                    instrument_token=hash(data["symbol"]) % 1000000,
                    symbol=data["symbol"],
                    exchange="NSE",
                    last_price=data["last_price"],
                    open_price=data["open_price"],
                    high_price=data["high_price"],
                    low_price=data["low_price"],
                    close_price=data["close_price"],
                    volume=data["volume"],
                    turnover=data["turnover"],
                    ohlc_open=data["open_price"],
                    ohlc_high=data["high_price"],
                    ohlc_low=data["low_price"],
                    ohlc_close=data["close_price"],
                    timestamp=data["timestamp"],
                    change=data["last_price"] - data["close_price"],
                    change_percent=((data["last_price"] - data["close_price"]) / data["close_price"]) * 100
                )
                
                session.add(market_record)
            
            session.commit()
            logger.info(f"Stored {len(market_data)} market data records")
            
        except Exception as e:
            logger.error(f"Failed to store market data: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    async def sync_portfolio_data(self):
        """Synchronize portfolio data from Zerodha"""
        try:
            # This would get portfolio data from Zerodha
            # For now, create mock portfolio snapshot
            portfolio_data = {
                "user_id": 1,
                "kite_user_id": "DS8714",  # From your logs
                "total_value": 100000.0,
                "total_pnl": 5000.0,
                "day_pnl": 250.0,
                "total_holdings": 5,
                "total_positions": 2,
                "snapshot_time": datetime.utcnow()
            }
            
            self.store_portfolio_snapshot(portfolio_data)
            logger.info("Portfolio data synchronized successfully")
            
        except Exception as e:
            logger.error(f"Portfolio sync failed: {e}")
    
    def store_portfolio_snapshot(self, portfolio_data: Dict):
        """Store portfolio snapshot in database"""
        try:
            session = next(get_database_session())
            
            snapshot = PortfolioSnapshot(**portfolio_data)
            session.add(snapshot)
            session.commit()
            
            logger.info("Portfolio snapshot stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store portfolio snapshot: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    async def sync_instruments(self):
        """Synchronize instrument data from Zerodha"""
        try:
            # This would get instrument data from Zerodha
            # For now, create mock instruments
            mock_instruments = [
                {
                    "instrument_token": 123456,
                    "trading_symbol": "RELIANCE",
                    "name": "Reliance Industries Limited",
                    "exchange": "NSE",
                    "instrument_type": "EQ",
                    "segment": "NSE",
                    "lot_size": 1,
                    "tick_size": 0.05
                },
                {
                    "instrument_token": 789012,
                    "trading_symbol": "TCS",
                    "name": "Tata Consultancy Services Limited",
                    "exchange": "NSE",
                    "instrument_type": "EQ",
                    "segment": "NSE",
                    "lot_size": 1,
                    "tick_size": 0.05
                }
            ]
            
            self.store_instruments(mock_instruments)
            logger.info("Instruments synchronized successfully")
            
        except Exception as e:
            logger.error(f"Instrument sync failed: {e}")
    
    def store_instruments(self, instruments: List[Dict]):
        """Store instruments in database"""
        try:
            session = next(get_database_session())
            
            for instrument_data in instruments:
                # Check if instrument already exists
                existing = session.query(Instrument).filter_by(
                    instrument_token=instrument_data["instrument_token"]
                ).first()
                
                if existing:
                    # Update existing instrument
                    for key, value in instrument_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new instrument
                    instrument = Instrument(**instrument_data)
                    session.add(instrument)
            
            session.commit()
            logger.info(f"Stored {len(instruments)} instruments")
            
        except Exception as e:
            logger.error(f"Failed to store instruments: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    def get_active_instruments(self) -> List[Instrument]:
        """Get active instruments from database"""
        try:
            session = next(get_database_session())
            instruments = session.query(Instrument).filter_by(is_active="Y").limit(100).all()
            return instruments
            
        except Exception as e:
            logger.error(f"Failed to get active instruments: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def get_market_data_history(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get historical market data for a symbol"""
        try:
            session = next(get_database_session())
            
            from_date = datetime.utcnow() - timedelta(days=days)
            
            data = session.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= from_date
            ).order_by(MarketData.timestamp.desc()).all()
            
            return [
                {
                    "timestamp": record.timestamp,
                    "last_price": record.last_price,
                    "volume": record.volume,
                    "change": record.change,
                    "change_percent": record.change_percent
                }
                for record in data
            ]
            
        except Exception as e:
            logger.error(f"Failed to get market data history: {e}")
            return []
        finally:
            if session:
                session.close()


# Global service instance
data_ingestion_service = DataIngestionService()


def get_data_ingestion_service() -> DataIngestionService:
    """Get data ingestion service instance"""
    return data_ingestion_service

"""
AutoPPM Database Connection
SQLAlchemy database setup and session management
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from loguru import logger
from config.settings import get_settings

settings = get_settings()

# Create database engine
def create_database_engine():
    """Create database engine with appropriate configuration"""
    try:
        if settings.environment == "development":
            # Development: SQLite with better performance
            engine = create_engine(
                settings.database_url,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=settings.debug
            )
        else:
            # Production: PostgreSQL
            engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=10,
                max_overflow=20
            )
        
        logger.info(f"Database engine created successfully: {settings.database_url}")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


# Create database engine instance
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Import and register all models
def register_models():
    """Register all models with the Base"""
    try:
        # Import all models to ensure they're registered
        from models.user import User, ZerodhaAccount
        from models.market_data import MarketData, HistoricalData, Instrument, PortfolioSnapshot
        from models.strategy import Strategy, StrategyExecution, StrategySignal, StrategyPerformance, StrategyBacktest
        
        logger.info("All models registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register models: {e}")
        raise


def get_database_session() -> Session:
    """Get database session"""
    try:
        session = SessionLocal()
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """Create all database tables"""
    try:
        # Register all models first
        register_models()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        raise


def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
        
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            result.fetchone()  # Execute the result
            logger.info("Database connection test successful")
            return True
            
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_database_info():
    """Get database information"""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            # Get table count
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            db_info = {
                "url": settings.database_url,
                "tables": tables,
                "table_count": len(tables),
                "environment": settings.environment
            }
            
            logger.info(f"Database info: {db_info}")
            return db_info
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return None


# Database event handlers
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance"""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()
        logger.info("SQLite performance optimizations applied")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Handle database connection checkout"""
    logger.debug("Database connection checked out")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Handle database connection checkin"""
    logger.debug("Database connection checked in")

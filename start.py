#!/usr/bin/env python3
"""
AutoPPM Startup Script
Handles environment setup and application launch
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger

def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'kiteconnect',
        'sqlalchemy',
        'jose',  # python-jose package
        'passlib',
        'pandas',
        'numpy',
        'loguru'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'jose':
                __import__('jose')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("All required packages are installed")

def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.error(".env file not found")
        logger.info("Copy env.example to .env and configure your settings")
        sys.exit(1)
    
    # Check required environment variables
    required_vars = [
        'ZERODHA_API_KEY',
        'ZERODHA_API_SECRET',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Please configure these in your .env file")
        sys.exit(1)
    
    logger.info("Environment configuration is valid")

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['logs', 'static', 'tests']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    logger.info("Directory structure verified")

def test_engines():
    """Test all trading engines"""
    logger.info("Testing trading engines...")
    
    # Test strategy engine
    logger.info("Testing strategy engine...")
    try:
        from engine.strategy_engine import get_strategy_engine
        strategy_engine = get_strategy_engine()
        logger.info("✅ Strategy engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Strategy engine initialization failed: {e}")
        return False
    
    # Test backtesting engine
    logger.info("Testing backtesting engine...")
    try:
        from engine.backtesting_engine import get_backtesting_engine
        backtesting_engine = get_backtesting_engine()
        logger.info("✅ Backtesting engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Backtesting engine initialization failed: {e}")
        return False
    
    # Test risk management engine
    logger.info("Testing risk management engine...")
    try:
        from engine.risk_management_engine import get_risk_management_engine
        risk_engine = get_risk_management_engine()
        logger.info("✅ Risk management engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Risk management engine initialization failed: {e}")
        return False
    
    # Test order management engine
    logger.info("Testing order management engine...")
    try:
        from engine.order_management_engine import get_order_management_engine
        order_engine = get_order_management_engine()
        logger.info("✅ Order management engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Order management engine initialization failed: {e}")
        return False
    
    # Test portfolio management engine
    logger.info("Testing portfolio management engine...")
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine
        portfolio_engine = get_portfolio_management_engine()
        logger.info("✅ Portfolio management engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Portfolio management engine initialization failed: {e}")
        return False
    
    # Test AutoPPM orchestrator
    logger.info("Testing AutoPPM orchestrator...")
    try:
        from engine.autoppm_orchestrator import get_autoppm_orchestrator
        orchestrator = get_autoppm_orchestrator()
        logger.info("✅ AutoPPM orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"❌ AutoPPM orchestrator initialization failed: {e}")
        return False
    
    logger.info("✅ All trading engines initialized successfully")
    return True

def start_application():
    """Start the AutoPPM application"""
    try:
        logger.info("Starting AutoPPM application...")
        
        # Import and run the main application
        from main import app
        import uvicorn
        
        # Get settings
        from config.settings import get_settings
        settings = get_settings()
        
        logger.info(f"Starting server on {settings.host}:{settings.port}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    logger.info("AutoPPM Startup Script")
    logger.info("=" * 50)
    
    try:
        # Run startup checks
        check_python_version()
        check_dependencies()
        check_environment()
        create_directories()
        
        # Test trading engines
        if not test_engines():
            logger.error("❌ Engine testing failed")
            sys.exit(1)
        
        logger.info("All startup checks passed")
        logger.info("=" * 50)
        
        # Start the application
        start_application()
        
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

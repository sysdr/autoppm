#!/usr/bin/env python3
"""
AutoPPM Database Initialization Script
Creates database tables and initial data
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import create_tables, check_database_connection, get_database_info
from loguru import logger


def main():
    """Initialize database"""
    try:
        logger.info("Starting AutoPPM database initialization...")
        
        # Check database connection
        if not check_database_connection():
            logger.error("Database connection failed")
            sys.exit(1)
        
        # Create tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Get database info
        db_info = get_database_info()
        if db_info:
            logger.info(f"Database initialized with {db_info['table_count']} tables")
            logger.info(f"Tables: {', '.join(db_info['tables'])}")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

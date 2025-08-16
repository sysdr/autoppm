#!/usr/bin/env python3
"""
AutoPPM Test Data Population Script
Populates database with test data for Week 2 testing
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_database_session, create_tables
from models.market_data import Instrument, MarketData, PortfolioSnapshot
from loguru import logger


def populate_instruments():
    """Populate instruments table with test data"""
    try:
        session = next(get_database_session())
        
        # Test instruments
        test_instruments = [
            Instrument(
                instrument_token=123456,
                trading_symbol="RELIANCE",
                name="Reliance Industries Limited",
                exchange="NSE",
                instrument_type="EQ",
                segment="NSE",
                lot_size=1,
                tick_size=0.05
            ),
            Instrument(
                instrument_token=789012,
                trading_symbol="TCS",
                name="Tata Consultancy Services Limited",
                exchange="NSE",
                instrument_type="EQ",
                segment="NSE",
                lot_size=1,
                tick_size=0.05
            ),
            Instrument(
                instrument_token=345678,
                trading_symbol="INFY",
                name="Infosys Limited",
                exchange="NSE",
                instrument_type="EQ",
                segment="NSE",
                lot_size=1,
                tick_size=0.05
            )
        ]
        
        for instrument in test_instruments:
            session.add(instrument)
        
        session.commit()
        logger.info(f"Added {len(test_instruments)} test instruments")
        
    except Exception as e:
        logger.error(f"Failed to populate instruments: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def populate_market_data():
    """Populate market data table with test data"""
    try:
        session = next(get_database_session())
        
        # Test market data
        test_market_data = [
            MarketData(
                instrument_token=123456,
                symbol="RELIANCE",
                exchange="NSE",
                last_price=2500.0,
                open_price=2480.0,
                high_price=2520.0,
                low_price=2470.0,
                close_price=2490.0,
                volume=1000000,
                turnover=2500000000.0,
                ohlc_open=2480.0,
                ohlc_high=2520.0,
                ohlc_low=2470.0,
                ohlc_close=2490.0,
                timestamp=datetime.utcnow(),
                change=10.0,
                change_percent=0.4
            ),
            MarketData(
                instrument_token=789012,
                symbol="TCS",
                exchange="NSE",
                last_price=3800.0,
                open_price=3780.0,
                high_price=3820.0,
                low_price=3770.0,
                close_price=3790.0,
                volume=800000,
                turnover=3040000000.0,
                ohlc_open=3780.0,
                ohlc_high=3820.0,
                ohlc_low=3770.0,
                ohlc_close=3790.0,
                timestamp=datetime.utcnow(),
                change=10.0,
                change_percent=0.26
            )
        ]
        
        for data in test_market_data:
            session.add(data)
        
        session.commit()
        logger.info(f"Added {len(test_market_data)} test market data records")
        
    except Exception as e:
        logger.error(f"Failed to populate market data: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def populate_portfolio_snapshots():
    """Populate portfolio snapshots table with test data"""
    try:
        session = next(get_database_session())
        
        # Test portfolio snapshot
        test_snapshot = PortfolioSnapshot(
            user_id=1,
            kite_user_id="DS8714",
            total_value=100000.0,
            total_pnl=5000.0,
            day_pnl=250.0,
            total_holdings=5,
            total_positions=2,
            snapshot_time=datetime.utcnow()
        )
        
        session.add(test_snapshot)
        session.commit()
        logger.info("Added test portfolio snapshot")
        
    except Exception as e:
        logger.error(f"Failed to populate portfolio snapshot: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def main():
    """Main function to populate test data"""
    try:
        logger.info("Starting test data population...")
        
        # Ensure tables exist
        create_tables()
        
        # Populate test data
        populate_instruments()
        populate_market_data()
        populate_portfolio_snapshots()
        
        logger.info("Test data population completed successfully!")
        
    except Exception as e:
        logger.error(f"Test data population failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

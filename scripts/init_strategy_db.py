#!/usr/bin/env python3
"""
Initialize Strategy Database
Creates strategy tables and populates with sample strategies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import create_tables, get_database_session
from models.strategy import Strategy
from loguru import logger


def create_sample_strategies():
    """Create sample trading strategies"""
    try:
        session = next(get_database_session())
        
        # Check if strategies already exist
        existing_count = session.query(Strategy).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing strategies, skipping creation")
            return
        
        # Sample strategies
        sample_strategies = [
            {
                "name": "Momentum Strategy",
                "description": "Follows trends using moving averages and RSI indicators",
                "strategy_type": "momentum",
                "category": "equity",
                "risk_level": "moderate",
                "parameters": {
                    "short_window": 20,
                    "long_window": 50,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "momentum_threshold": 0.02,
                    "position_size_pct": 0.1,
                    "stop_loss_pct": 0.05,
                    "take_profit_pct": 0.15
                },
                "default_parameters": {
                    "short_window": 20,
                    "long_window": 50,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "momentum_threshold": 0.02,
                    "position_size_pct": 0.1,
                    "stop_loss_pct": 0.05,
                    "take_profit_pct": 0.15
                },
                "is_active": True,
                "is_backtest_only": False
            },
            {
                "name": "Mean Reversion Strategy",
                "description": "Identifies overbought/oversold conditions using Bollinger Bands and RSI",
                "strategy_type": "mean_reversion",
                "category": "equity",
                "risk_level": "moderate",
                "parameters": {
                    "bollinger_window": 20,
                    "bollinger_std": 2.0,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "mean_reversion_threshold": 0.1,
                    "position_size_pct": 0.08,
                    "stop_loss_pct": 0.08,
                    "take_profit_pct": 0.12,
                    "max_hold_days": 15
                },
                "default_parameters": {
                    "bollinger_window": 20,
                    "bollinger_std": 2.0,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "mean_reversion_threshold": 0.1,
                    "position_size_pct": 0.08,
                    "stop_loss_pct": 0.08,
                    "take_profit_pct": 0.12,
                    "max_hold_days": 15
                },
                "is_active": True,
                "is_backtest_only": False
            },
            {
                "name": "Multi-Factor Strategy",
                "description": "Combines multiple technical and fundamental indicators for comprehensive analysis",
                "strategy_type": "multi_factor",
                "category": "equity",
                "risk_level": "moderate",
                "parameters": {
                    "ma_short_window": 20,
                    "ma_long_window": 50,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "volume_ma_window": 20,
                    "volume_threshold": 1.5,
                    "volatility_window": 20,
                    "volatility_threshold": 0.02,
                    "momentum_window": 10,
                    "momentum_threshold": 0.01,
                    "position_size_pct": 0.06,
                    "stop_loss_pct": 0.06,
                    "take_profit_pct": 0.18,
                    "max_hold_days": 25
                },
                "default_parameters": {
                    "ma_short_window": 20,
                    "ma_long_window": 50,
                    "rsi_window": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "volume_ma_window": 20,
                    "volume_threshold": 1.5,
                    "volatility_window": 20,
                    "volatility_threshold": 0.02,
                    "momentum_window": 10,
                    "momentum_threshold": 0.01,
                    "position_size_pct": 0.06,
                    "stop_loss_pct": 0.06,
                    "take_profit_pct": 0.18,
                    "max_hold_days": 25
                },
                "is_active": True,
                "is_backtest_only": False
            }
        ]
        
        # Create strategies
        for strategy_data in sample_strategies:
            strategy = Strategy(**strategy_data)
            session.add(strategy)
            logger.info(f"Created strategy: {strategy.name}")
        
        session.commit()
        logger.info(f"Successfully created {len(sample_strategies)} sample strategies")
        
    except Exception as e:
        logger.error(f"Failed to create sample strategies: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def main():
    """Main function"""
    try:
        logger.info("Starting strategy database initialization...")
        
        # Create tables
        create_tables()
        logger.info("Strategy tables created successfully")
        
        # Create sample strategies
        create_sample_strategies()
        logger.info("Strategy database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Strategy database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

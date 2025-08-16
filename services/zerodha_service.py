"""
AutoPPM Zerodha Service
Handles all interactions with Zerodha Kite Connect API
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from kiteconnect import KiteConnect
from loguru import logger
from config.settings import get_settings

settings = get_settings()


class ZerodhaService:
    """Service for Zerodha Kite Connect API interactions"""
    
    def __init__(self):
        """Initialize Zerodha service with API credentials"""
        self.api_key = settings.zerodha_api_key
        self.api_secret = settings.zerodha_api_secret
        self.redirect_uri = settings.zerodha_redirect_uri
        
        # Initialize Kite Connect instance
        self.kite = KiteConnect(api_key=self.api_key)
        
        logger.info("Zerodha service initialized")
    
    def get_login_url(self) -> str:
        """Generate Zerodha login URL for OAuth flow"""
        try:
            login_url = self.kite.login_url()
            logger.info(f"Generated Zerodha login URL: {login_url}")
            return login_url
        except Exception as e:
            logger.error(f"Error generating login URL: {e}")
            raise
    
    def generate_session(self, request_token: str) -> Dict:
        """Generate session using request token from Zerodha"""
        try:
            # Generate session
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.api_secret
            )
            
            # Extract session details
            access_token = data["access_token"]
            kite_user_id = data["user_id"]
            
            # Get user profile
            profile = self.kite.profile()
            
            session_data = {
                "access_token": access_token,
                "kite_user_id": kite_user_id,
                "profile": profile,
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            logger.info(f"Session generated for user: {kite_user_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Error generating session: {e}")
            raise
    
    def get_portfolio(self, access_token: str) -> Dict:
        """Get current portfolio holdings"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Get portfolio holdings
            holdings = self.kite.holdings()
            
            # Get portfolio positions
            positions = self.kite.positions()
            
            # Get margin details
            margins = self.kite.margins()
            
            portfolio_data = {
                "holdings": holdings,
                "positions": positions,
                "margins": margins,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Portfolio data retrieved successfully")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error retrieving portfolio: {e}")
            raise
    
    def get_market_data(self, access_token: str, symbols: List[str]) -> Dict:
        """Get real-time market data for given symbols"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Get quote for symbols
            quotes = self.kite.quote(symbols)
            
            market_data = {
                "quotes": quotes,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Market data retrieved for {len(symbols)} symbols")
            return market_data
            
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            raise
    
    def get_historical_data(self, access_token: str, symbol: str, 
                           from_date: datetime, to_date: datetime, 
                           interval: str = "day") -> List[Dict]:
        """Get historical data for a symbol"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Get historical data
            historical_data = self.kite.historical_data(
                instrument_token=symbol,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            logger.info(f"Historical data retrieved for {symbol}")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            raise
    
    def get_instruments(self, access_token: str, exchange: str = "NSE") -> List[Dict]:
        """Get list of instruments for an exchange"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Get instruments
            instruments = self.kite.instruments(exchange=exchange)
            
            logger.info(f"Instruments retrieved for {exchange}")
            return instruments
            
        except Exception as e:
            logger.error(f"Error retrieving instruments: {e}")
            raise
    
    def validate_token(self, access_token: str) -> bool:
        """Validate if access token is still valid"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Try to get profile (lightweight call)
            profile = self.kite.profile()
            
            logger.info("Access token validation successful")
            return True
            
        except Exception as e:
            logger.warning(f"Access token validation failed: {e}")
            return False
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        try:
            # Note: Zerodha doesn't provide refresh tokens in standard flow
            # This is a placeholder for future implementation
            logger.warning("Token refresh not implemented for Zerodha")
            raise NotImplementedError("Token refresh not supported by Zerodha")
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    def get_account_details(self, access_token: str) -> Dict:
        """Get account details and limits"""
        try:
            # Set access token
            self.kite.set_access_token(access_token)
            
            # Get account details
            profile = self.kite.profile()
            
            # Get margins
            margins = self.kite.margins()
            
            account_data = {
                "profile": profile,
                "margins": margins,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Account details retrieved successfully")
            return account_data
            
        except Exception as e:
            logger.error(f"Error retrieving account details: {e}")
            raise


# Global service instance
zerodha_service = ZerodhaService()


def get_zerodha_service() -> ZerodhaService:
    """Get Zerodha service instance"""
    return zerodha_service

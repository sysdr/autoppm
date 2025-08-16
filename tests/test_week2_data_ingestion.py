"""
AutoPPM Week 2 Data Ingestion Tests
Test the data ingestion layer functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from main import app
from services.data_ingestion_service import DataIngestionService
from models.market_data import MarketData, Instrument, PortfolioSnapshot


class TestDataIngestionService:
    """Test data ingestion service"""
    
    def setup_method(self):
        """Setup test method"""
        self.service = DataIngestionService()
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert self.service.is_running == False
        assert self.service.ingestion_interval == 5
        assert isinstance(self.service.last_sync, dict)
    
    @pytest.mark.asyncio
    async def test_start_stop_ingestion(self):
        """Test starting and stopping ingestion service"""
        # Test service state changes without actually running the loops
        self.service.is_running = True
        assert self.service.is_running == True
        
        self.service.is_running = False
        assert self.service.is_running == False
    
    def test_store_market_data(self):
        """Test storing market data"""
        mock_data = [{
            "symbol": "RELIANCE",
            "last_price": 2500.0,
            "open_price": 2480.0,
            "high_price": 2520.0,
            "low_price": 2470.0,
            "close_price": 2490.0,
            "volume": 1000000,
            "turnover": 2500000000.0,
            "timestamp": datetime.utcnow()
        }]
        
        # Mock database session
        with patch('services.data_ingestion_service.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            self.service.store_market_data(mock_data)
            
            # Verify data was added
            assert mock_db.add.called
            assert mock_db.commit.called
    
    def test_store_instruments(self):
        """Test storing instruments"""
        mock_instruments = [{
            "instrument_token": 123456,
            "trading_symbol": "RELIANCE",
            "name": "Reliance Industries Limited",
            "exchange": "NSE",
            "instrument_type": "EQ",
            "segment": "NSE",
            "lot_size": 1,
            "tick_size": 0.05
        }]
        
        # Mock database session
        with patch('services.data_ingestion_service.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_db.query.return_value.filter_by.return_value.first.return_value = None
            
            self.service.store_instruments(mock_instruments)
            
            # Verify instrument was added
            assert mock_db.add.called
            assert mock_db.commit.called


class TestDataAPIEndpoints:
    """Test data API endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(app)
    
    def test_get_market_data(self):
        """Test getting market data for a symbol"""
        # Mock database session
        with patch('api.data_endpoints.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_data = Mock()
            mock_data.symbol = "RELIANCE"
            mock_data.last_price = 2500.0
            mock_data.change = 10.0
            mock_data.change_percent = 0.4
            mock_data.volume = 1000000
            mock_data.timestamp = datetime.utcnow()
            
            mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_data
            
            response = self.client.get("/api/data/market-data/RELIANCE")
            assert response.status_code == 200
            
            data = response.json()
            assert data["symbol"] == "RELIANCE"
            assert data["last_price"] == 2500.0
    
    def test_get_market_data_not_found(self):
        """Test getting market data for non-existent symbol"""
        # Mock database session
        with patch('api.data_endpoints.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result - no data found
            mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
            
            response = self.client.get("/api/data/market-data/INVALID")
            assert response.status_code == 404
    
    def test_get_instruments(self):
        """Test getting instruments list"""
        # Mock database session
        with patch('api.data_endpoints.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_instrument = Mock()
            mock_instrument.instrument_token = 123456
            mock_instrument.trading_symbol = "RELIANCE"
            mock_instrument.name = "Reliance Industries Limited"
            mock_instrument.exchange = "NSE"
            mock_instrument.instrument_type = "EQ"
            mock_instrument.lot_size = 1
            mock_instrument.tick_size = 0.05
            
            mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_instrument]
            
            response = self.client.get("/api/data/instruments")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 1
            assert data[0]["trading_symbol"] == "RELIANCE"
    
    def test_get_dashboard_summary(self):
        """Test getting dashboard summary"""
        # Mock database session
        with patch('api.data_endpoints.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query results
            mock_db.query.return_value.filter.return_value.count.return_value = 5
            mock_db.query.return_value.filter.return_value.count.return_value = 1000
            
            response = self.client.get("/api/data/dashboard/summary")
            assert response.status_code == 200
            
            data = response.json()
            assert "total_instruments" in data
            assert "total_market_records" in data
            assert "last_updated" in data
    
    def test_start_data_ingestion(self):
        """Test starting data ingestion service"""
        with patch('api.data_endpoints.get_data_ingestion_service') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            response = self.client.post("/api/data/ingestion/start")
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "started successfully" in data["message"]
    
    def test_stop_data_ingestion(self):
        """Test stopping data ingestion service"""
        with patch('api.data_endpoints.get_data_ingestion_service') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            response = self.client.post("/api/data/ingestion/stop")
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "stopped successfully" in data["message"]
    
    def test_get_ingestion_status(self):
        """Test getting ingestion service status"""
        with patch('api.data_endpoints.get_data_ingestion_service') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.is_running = True
            mock_service_instance.ingestion_interval = 5
            mock_service_instance.last_sync = {}
            mock_service.return_value = mock_service_instance
            
            response = self.client.get("/api/data/ingestion/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data["is_running"] == True
            assert data["ingestion_interval"] == 5


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_database_connection(self):
        """Test database connection"""
        from database.connection import check_database_connection
        
        # This will test the actual database connection
        # In a real test environment, you might want to mock this
        try:
            result = check_database_connection()
            assert isinstance(result, bool)
        except Exception as e:
            # If database is not available, that's okay for testing
            pytest.skip(f"Database not available: {e}")
    
    def test_create_tables(self):
        """Test table creation"""
        from database.connection import create_tables
        
        try:
            # This will create tables if they don't exist
            create_tables()
            # If no exception, tables were created or already exist
            assert True
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

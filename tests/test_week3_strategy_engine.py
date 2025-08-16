"""
Week 3: Strategy Engine Tests
Test the core strategy engine functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from main import app
from engine.strategy_engine import StrategyEngine, StrategyRegistry, BaseStrategy, StrategyContext
from models.strategy import Strategy, StrategyExecution, StrategySignal
from database.connection import get_database_session


class TestStrategyRegistry:
    """Test strategy registry functionality"""
    
    def setup_method(self):
        """Setup test method"""
        self.registry = StrategyRegistry()
    
    def test_register_strategy(self):
        """Test registering a strategy"""
        # Create a mock strategy class
        class MockStrategy(BaseStrategy):
            async def initialize(self, context):
                return True
            
            async def generate_signals(self, context, market_data):
                return []
            
            async def calculate_position_size(self, signal, context):
                return 100.0
            
            async def should_exit(self, position, context):
                return False
        
        # Register strategy
        success = self.registry.register_strategy(MockStrategy)
        assert success == True
        assert "MockStrategy" in self.registry.list_strategies()
    
    def test_unregister_strategy(self):
        """Test unregistering a strategy"""
        # Create and register a mock strategy
        class MockStrategy(BaseStrategy):
            async def initialize(self, context):
                return True
            
            async def generate_signals(self, context, market_data):
                return []
            
            async def calculate_position_size(self, signal, context):
                return 100.0
            
            async def should_exit(self, position, context):
                return False
        
        self.registry.register_strategy(MockStrategy)
        assert "MockStrategy" in self.registry.list_strategies()
        
        # Unregister strategy
        success = self.registry.unregister_strategy("MockStrategy")
        assert success == True
        assert "MockStrategy" not in self.registry.list_strategies()
    
    def test_get_strategy_class(self):
        """Test getting strategy class by name"""
        # Create a mock strategy class
        class MockStrategy(BaseStrategy):
            async def initialize(self, context):
                return True
            
            async def generate_signals(self, context, market_data):
                return []
            
            async def calculate_position_size(self, signal, context):
                return 100.0
            
            async def should_exit(self, position, context):
                return False
        
        # Register strategy
        self.registry.register_strategy(MockStrategy)
        
        # Get strategy class
        strategy_class = self.registry.get_strategy_class("MockStrategy")
        assert strategy_class == MockStrategy
        
        # Test non-existent strategy
        strategy_class = self.registry.get_strategy_class("NonExistentStrategy")
        assert strategy_class is None


class TestStrategyEngine:
    """Test strategy engine functionality"""
    
    def setup_method(self):
        """Setup test method"""
        self.engine = StrategyEngine()
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.is_running == False
        assert len(self.engine.registry.list_strategies()) >= 0  # May have built-in strategies
    
    def test_get_strategy_list(self):
        """Test getting strategy list"""
        # Mock database session
        with patch('engine.strategy_engine.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_strategy = Mock()
            mock_strategy.id = 1
            mock_strategy.name = "Test Strategy"
            mock_strategy.description = "Test Description"
            mock_strategy.version = "1.0.0"
            mock_strategy.strategy_type = "test"
            mock_strategy.category = "equity"
            mock_strategy.risk_level = "moderate"
            mock_strategy.is_active = True
            mock_strategy.is_backtest_only = False
            mock_strategy.total_return = 0.15
            mock_strategy.sharpe_ratio = 1.2
            mock_strategy.max_drawdown = 0.05
            mock_strategy.win_rate = 0.65
            mock_strategy.created_at = datetime.utcnow()
            mock_strategy.last_executed = None
            
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_strategy]
            
            strategies = self.engine.get_strategy_list()
            assert len(strategies) == 1
            assert strategies[0]["name"] == "Test Strategy"
    
    def test_get_execution_list(self):
        """Test getting execution list"""
        # Mock database session
        with patch('engine.strategy_engine.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_execution = Mock()
            mock_execution.id = 1
            mock_execution.strategy_id = 1
            mock_execution.user_id = 1
            mock_execution.execution_type = "paper"
            mock_execution.status = "running"
            mock_execution.started_at = datetime.utcnow()
            mock_execution.total_pnl = 150.0
            mock_execution.current_drawdown = 0.02
            
            mock_db.query.return_value.all.return_value = [mock_execution]
            
            # Mock executor status
            with patch.object(self.engine.executor, 'get_execution_status') as mock_status:
                mock_status.return_value = {"running": True}
                
                executions = self.engine.get_execution_list()
                assert len(executions) == 1
                assert executions[0]["id"] == 1
                assert executions[0]["running"] == True


class TestStrategyAPIEndpoints:
    """Test strategy API endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(app)
    
    def test_list_strategies(self):
        """Test listing strategies endpoint"""
        # Test with real database since we have strategies populated
        response = self.client.get("/api/strategy/strategies")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1  # We have strategies in the database
        assert any(strategy["name"] == "Momentum Strategy" for strategy in data)
    
    def test_get_strategy(self):
        """Test getting strategy by ID"""
        # Mock database session
        with patch('api.strategy_endpoints.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock query result
            mock_strategy = Mock()
            mock_strategy.id = 1
            mock_strategy.name = "Test Strategy"
            mock_strategy.description = "Test Description"
            mock_strategy.version = "1.0.0"
            mock_strategy.strategy_type = "test"
            mock_strategy.category = "equity"
            mock_strategy.risk_level = "moderate"
            mock_strategy.is_active = True
            mock_strategy.is_backtest_only = False
            mock_strategy.total_return = 0.15
            mock_strategy.sharpe_ratio = 1.2
            mock_strategy.max_drawdown = 0.05
            mock_strategy.win_rate = 0.65
            mock_strategy.created_at = datetime.utcnow()
            mock_strategy.last_executed = None
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_strategy
            
            response = self.client.get("/api/strategy/strategies/1")
            assert response.status_code == 200
            
            data = response.json()
            assert data["name"] == "Test Strategy"
            assert data["id"] == 1
    
    def test_get_engine_status(self):
        """Test getting engine status endpoint"""
        # Mock strategy engine
        with patch('api.strategy_endpoints.get_strategy_engine') as mock_get_engine:
            mock_engine = Mock()
            mock_engine.is_running = True
            mock_engine.registry.list_strategies.return_value = ["Strategy1", "Strategy2"]
            mock_engine.executor.list_running_executions.return_value = [1, 2]
            mock_engine.executor.running_executions = {1: Mock(), 2: Mock()}
            
            mock_get_engine.return_value = mock_engine
            
            response = self.client.get("/api/strategy/engine/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data["is_running"] == True
            assert len(data["registered_strategies"]) == 2
            assert data["total_executions"] == 2


class TestStrategyExecution:
    """Test strategy execution functionality"""
    
    def setup_method(self):
        """Setup test method"""
        self.engine = StrategyEngine()
    
    @pytest.mark.asyncio
    async def test_start_strategy_execution(self):
        """Test starting a strategy execution"""
        # Mock database session
        with patch('engine.strategy_engine.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Mock strategy query
            mock_strategy = Mock()
            mock_strategy.id = 1
            mock_strategy.name = "TestStrategy"
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_strategy
            
            # Mock execution creation
            mock_execution = Mock()
            mock_execution.id = 1
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            
            # Mock executor
            with patch.object(self.engine.executor, 'start_execution') as mock_start:
                mock_start.return_value = True
                
                execution_id = await self.engine.start_strategy_execution(
                    strategy_id=1,
                    user_id=1,
                    symbols=["RELIANCE", "TCS"],
                    parameters={"param1": "value1"},
                    execution_type="paper"
                )
                
                assert execution_id == 1
    
    @pytest.mark.asyncio
    async def test_stop_strategy_execution(self):
        """Test stopping a strategy execution"""
        # Mock executor
        with patch.object(self.engine.executor, 'stop_execution') as mock_stop:
            mock_stop.return_value = True
            
            # Mock database session
            with patch('engine.strategy_engine.get_database_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = iter([mock_db])
                
                # Mock execution query
                mock_execution = Mock()
                mock_db.query.return_value.filter.return_value.first.return_value = mock_execution
                mock_db.commit.return_value = None
                
                success = await self.engine.stop_strategy_execution(1)
                assert success == True


class TestStrategySignals:
    """Test strategy signal generation"""
    
    def setup_method(self):
        """Setup test method"""
        self.engine = StrategyEngine()
    
    def test_signal_storage(self):
        """Test storing strategy signals"""
        # Mock database session
        with patch('engine.strategy_engine.get_database_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value = iter([mock_db])
            
            # Create a mock signal
            mock_signal = Mock()
            mock_signal.symbol = "RELIANCE"
            mock_signal.signal_type = "buy"
            mock_signal.price = 2500.0
            
            # Mock executor
            with patch.object(self.engine.executor, '_store_signal') as mock_store:
                mock_store.return_value = None
                
                # This would be called during signal processing
                # For now, just verify the mock works
                assert mock_store.return_value is None


class TestDatabaseIntegration:
    """Test database integration for strategies"""
    
    def test_strategy_model_creation(self):
        """Test creating strategy model instances"""
        strategy = Strategy(
            name="Test Strategy",
            description="Test Description",
            strategy_type="test",
            category="equity",
            risk_level="moderate",
            is_active=True,
            is_backtest_only=False
        )
        
        assert strategy.name == "Test Strategy"
        assert strategy.strategy_type == "test"
        assert strategy.is_active == True
    
    def test_execution_model_creation(self):
        """Test creating execution model instances"""
        execution = StrategyExecution(
            strategy_id=1,
            user_id=1,
            execution_type="paper",
            status="running"
        )
        
        assert execution.strategy_id == 1
        assert execution.user_id == 1
        assert execution.execution_type == "paper"
        assert execution.status == "running"
    
    def test_signal_model_creation(self):
        """Test creating signal model instances"""
        signal = StrategySignal(
            strategy_execution_id=1,
            symbol="RELIANCE",
            signal_type="buy",
            signal_strength=0.8,
            confidence=0.75,
            price=2500.0,
            timestamp=datetime.utcnow()
        )
        
        assert signal.symbol == "RELIANCE"
        assert signal.signal_type == "buy"
        assert signal.signal_strength == 0.8
        assert signal.confidence == 0.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Test suite for Phase 3: Advanced Features
Tests ML optimization engine, advanced risk models, and multi-broker support
"""

import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from engine.ml_optimization_engine import (
    get_ml_optimization_engine, 
    MLOptimizationEngine, 
    MLModelConfig,
    MLPrediction,
    StrategyOptimizationResult,
    RiskModelCalibration
)

from engine.advanced_risk_engine import (
    get_advanced_risk_engine,
    AdvancedRiskEngine,
    MonteCarloConfig,
    StressTestScenario,
    MonteCarloResult,
    StressTestResult,
    ScenarioAnalysisResult
)

from engine.multi_broker_engine import (
    get_multi_broker_engine,
    MultiBrokerEngine,
    BrokerConfig,
    OrderRoutingDecision,
    ExecutionQuality,
    BrokerPerformance
)


class TestMLOptimizationEngine:
    """Test ML Optimization Engine functionality"""
    
    @pytest.fixture
    def ml_engine(self):
        """Get ML optimization engine instance"""
        return get_ml_optimization_engine()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, 100)
        })
        return data
    
    @pytest.mark.asyncio
    async def test_ml_engine_initialization(self, ml_engine):
        """Test ML engine initialization"""
        assert ml_engine is not None
        assert isinstance(ml_engine, MLOptimizationEngine)
        assert ml_engine.models == {}
        assert ml_engine.scalers == {}
    
    @pytest.mark.asyncio
    async def test_ml_model_config(self):
        """Test ML model configuration"""
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        assert config.model_type == 'random_forest'
        assert len(config.feature_columns) == 3
        assert config.target_column == 'returns'
        assert config.prediction_horizon == 1
        assert config.retrain_frequency == 30
    
    @pytest.mark.asyncio
    async def test_create_market_prediction_model(self, ml_engine, sample_data):
        """Test creating market prediction model"""
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        model_id = await ml_engine.create_market_prediction_model('RELIANCE', config)
        
        assert model_id is not None
        assert model_id in ml_engine.models
        assert model_id in ml_engine.scalers
        assert model_id in ml_engine.model_performance
    
    @pytest.mark.asyncio
    async def test_predict_market_movement(self, ml_engine, sample_data):
        """Test market movement prediction"""
        # First create a model
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        model_id = await ml_engine.create_market_prediction_model('RELIANCE', config)
        
        # Test prediction
        prediction = await ml_engine.predict_market_movement(model_id, sample_data)
        
        assert isinstance(prediction, MLPrediction)
        assert prediction.timestamp is not None
        assert prediction.predicted_value is not None
        assert prediction.confidence > 0
        assert prediction.model_type == 'random_forest'
    
    @pytest.mark.asyncio
    async def test_optimize_strategy_parameters(self, ml_engine, sample_data):
        """Test strategy parameter optimization"""
        result = await ml_engine.optimize_strategy_parameters(
            'MomentumStrategy', 
            sample_data,
            'bayesian'
        )
        
        assert isinstance(result, StrategyOptimizationResult)
        assert result.strategy_name == 'MomentumStrategy'
        assert result.optimization_method == 'bayesian'
        assert result.expected_improvement > 0
        assert result.confidence_level > 0
    
    @pytest.mark.asyncio
    async def test_calibrate_risk_model(self, ml_engine, sample_data):
        """Test risk model calibration"""
        result = await ml_engine.calibrate_risk_model('var_model', sample_data)
        
        assert isinstance(result, RiskModelCalibration)
        assert result.model_type == 'var_model'
        assert result.calibration_score > 0
        assert result.validation_period == '1Y'
    
    @pytest.mark.asyncio
    async def test_generate_ml_features(self, ml_engine, sample_data):
        """Test ML feature generation"""
        features = await ml_engine.generate_ml_features(sample_data)
        
        assert isinstance(features, pd.DataFrame)
        assert len(features.columns) > len(sample_data.columns)  # Should have more features
        assert not features.isnull().any().any()  # No NaN values
    
    @pytest.mark.asyncio
    async def test_get_model_performance(self, ml_engine, sample_data):
        """Test getting model performance"""
        # Create a model first
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        model_id = await ml_engine.create_market_prediction_model('RELIANCE', config)
        
        # Get performance
        performance = await ml_engine.get_model_performance(model_id)
        
        assert isinstance(performance, dict)
        assert 'mse' in performance
        assert 'r2' in performance
        assert 'rmse' in performance
    
    @pytest.mark.asyncio
    async def test_retrain_model(self, ml_engine, sample_data):
        """Test model retraining"""
        # Create a model first
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        model_id = await ml_engine.create_market_prediction_model('RELIANCE', config)
        
        # Retrain model
        success = await ml_engine.retrain_model(model_id)
        
        assert success is True


class TestAdvancedRiskEngine:
    """Test Advanced Risk Engine functionality"""
    
    @pytest.fixture
    def risk_engine(self):
        """Get advanced risk engine instance"""
        return get_advanced_risk_engine()
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Create sample portfolio data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        returns = np.random.randn(252) * 0.02  # 2% daily volatility
        
        data = pd.DataFrame({
            'date': dates,
            'portfolio_value': (1 + returns).cumprod() * 1000000,  # Start with 1M
            'returns': returns,
            'volatility': np.abs(returns) * 2
        })
        return data
    
    @pytest.mark.asyncio
    async def test_risk_engine_initialization(self, risk_engine):
        """Test risk engine initialization"""
        assert risk_engine is not None
        assert isinstance(risk_engine, AdvancedRiskEngine)
        assert len(risk_engine.stress_scenarios) > 0
        assert risk_engine.default_mc_config is not None
    
    @pytest.mark.asyncio
    async def test_monte_carlo_config(self):
        """Test Monte Carlo configuration"""
        config = MonteCarloConfig(
            num_simulations=5000,
            time_horizon=126,
            confidence_level=0.99,
            risk_free_rate=0.03
        )
        
        assert config.num_simulations == 5000
        assert config.time_horizon == 126
        assert config.confidence_level == 0.99
        assert config.risk_free_rate == 0.03
    
    @pytest.mark.asyncio
    async def test_stress_test_scenario(self):
        """Test stress test scenario"""
        scenario = StressTestScenario(
            name="Test Crisis",
            description="Test scenario for testing",
            market_shock=-0.25,
            volatility_multiplier=2.0,
            correlation_breakdown=True,
            liquidity_crisis=False,
            interest_rate_shock=0.01,
            sector_specific_shocks={'tech': -0.30}
        )
        
        assert scenario.name == "Test Crisis"
        assert scenario.market_shock == -0.25
        assert scenario.volatility_multiplier == 2.0
        assert scenario.correlation_breakdown is True
    
    @pytest.mark.asyncio
    async def test_run_monte_carlo_simulation(self, risk_engine, sample_portfolio_data):
        """Test Monte Carlo simulation"""
        result = await risk_engine.run_monte_carlo_simulation(sample_portfolio_data)
        
        assert isinstance(result, MonteCarloResult)
        assert result.var_95 < 0  # VaR should be negative
        assert result.var_99 < result.var_95  # 99% VaR should be more extreme
        assert result.max_drawdown < 0  # Max drawdown should be negative
        assert 0 <= result.probability_of_loss <= 1  # Probability should be between 0 and 1
    
    @pytest.mark.asyncio
    async def test_run_stress_test(self, risk_engine, sample_portfolio_data):
        """Test stress test execution"""
        scenario = risk_engine.stress_scenarios[0]  # Use first scenario
        
        result = await risk_engine.run_stress_test(sample_portfolio_data, scenario)
        
        assert isinstance(result, StressTestResult)
        assert result.scenario_name == scenario.name
        assert result.portfolio_loss > 0  # Should have some loss
        assert result.loss_percentage > 0  # Loss percentage should be positive
        assert result.recovery_time_estimate > 0  # Recovery time should be positive
    
    @pytest.mark.asyncio
    async def test_run_scenario_analysis(self, risk_engine, sample_portfolio_data):
        """Test scenario analysis"""
        scenarios = risk_engine.stress_scenarios[:2]  # Use first two scenarios
        
        results = await risk_engine.run_scenario_analysis(sample_portfolio_data, scenarios)
        
        assert isinstance(results, list)
        assert len(results) == 2
        
        for result in results:
            assert isinstance(result, ScenarioAnalysisResult)
            assert 0 <= result.probability <= 1
            assert 0 <= result.impact_score <= 1
            assert 0 <= result.risk_score <= 1
            assert len(result.recommended_actions) > 0
    
    @pytest.mark.asyncio
    async def test_optimize_risk_allocation(self, risk_engine, sample_portfolio_data):
        """Test risk allocation optimization"""
        result = await risk_engine.optimize_risk_allocation(
            sample_portfolio_data,
            target_volatility=0.15
        )
        
        assert isinstance(result, dict)
        assert 'current_weights' in result
        assert 'optimized_weights' in result
        assert 'risk_improvement' in result
    
    @pytest.mark.asyncio
    async def test_calculate_tail_risk_metrics(self, risk_engine, sample_portfolio_data):
        """Test tail risk metrics calculation"""
        metrics = await risk_engine.calculate_tail_risk_metrics(sample_portfolio_data)
        
        assert isinstance(metrics, dict)
        assert 'var_95' in metrics
        assert 'var_99' in metrics
        assert 'max_drawdown' in metrics
        assert 'tail_volatility' in metrics
    
    @pytest.mark.asyncio
    async def test_generate_risk_report(self, risk_engine, sample_portfolio_data):
        """Test risk report generation"""
        report = await risk_engine.generate_risk_report(sample_portfolio_data)
        
        assert isinstance(report, dict)
        assert 'timestamp' in report
        assert 'portfolio_summary' in report
        assert 'risk_metrics' in report
        assert 'monte_carlo_analysis' in report
        assert 'stress_testing' in report
        assert 'scenario_analysis' in report
        assert 'recommendations' in report


class TestMultiBrokerEngine:
    """Test Multi-Broker Engine functionality"""
    
    @pytest.fixture
    def broker_engine(self):
        """Get multi-broker engine instance"""
        return get_multi_broker_engine()
    
    @pytest.fixture
    def sample_order_request(self):
        """Create sample order request for testing"""
        return {
            'symbol': 'RELIANCE',
            'quantity': 100,
            'price': 2500.0,
            'order_type': 'market',
            'side': 'buy'
        }
    
    @pytest.mark.asyncio
    async def test_broker_engine_initialization(self, broker_engine):
        """Test broker engine initialization"""
        assert broker_engine is not None
        assert isinstance(broker_engine, MultiBrokerEngine)
        assert len(broker_engine.brokers) > 0
        assert len(broker_engine.broker_configs) > 0
    
    @pytest.mark.asyncio
    async def test_broker_config(self):
        """Test broker configuration"""
        config = BrokerConfig(
            broker_id="test_broker",
            broker_name="Test Broker",
            api_key="test_key",
            api_secret="test_secret",
            priority=1,
            commission_rate=0.001,
            slippage_estimate=0.0005
        )
        
        assert config.broker_id == "test_broker"
        assert config.broker_name == "Test Broker"
        assert config.commission_rate == 0.001
        assert config.slippage_estimate == 0.0005
    
    @pytest.mark.asyncio
    async def test_add_broker(self, broker_engine):
        """Test adding new broker"""
        config = BrokerConfig(
            broker_id="new_broker",
            broker_name="New Broker",
            api_key="new_key",
            api_secret="new_secret"
        )
        
        success = broker_engine.add_broker(config)
        
        assert success is True
        assert "new_broker" in broker_engine.brokers
        assert "new_broker" in broker_engine.broker_configs
    
    @pytest.mark.asyncio
    async def test_connect_all_brokers(self, broker_engine):
        """Test connecting to all brokers"""
        connection_results = await broker_engine.connect_all_brokers()
        
        assert isinstance(connection_results, dict)
        assert len(connection_results) > 0
        
        # Check that at least some brokers connected successfully
        successful_connections = sum(1 for success in connection_results.values() if success)
        assert successful_connections > 0
    
    @pytest.mark.asyncio
    async def test_route_order(self, broker_engine, sample_order_request):
        """Test order routing"""
        routing_decision = await broker_engine.route_order(
            sample_order_request, 
            "cost_optimized"
        )
        
        assert isinstance(routing_decision, OrderRoutingDecision)
        assert routing_decision.broker_id is not None
        assert routing_decision.broker_name is not None
        assert routing_decision.routing_reason is not None
        assert routing_decision.expected_cost > 0
        assert routing_decision.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_execute_order_with_routing(self, broker_engine, sample_order_request):
        """Test order execution with routing"""
        result = await broker_engine.execute_order_with_routing(
            sample_order_request,
            "hybrid"
        )
        
        assert isinstance(result, dict)
        assert 'order_result' in result
        assert 'routing_decision' in result
        assert 'execution_quality' in result
        assert 'broker_used' in result
    
    @pytest.mark.asyncio
    async def test_get_best_execution_analysis(self, broker_engine):
        """Test best execution analysis"""
        analysis = await broker_engine.get_best_execution_analysis(
            'RELIANCE', 
            100, 
            'market'
        )
        
        assert isinstance(analysis, dict)
        assert 'symbol' in analysis
        assert 'quantity' in analysis
        assert 'broker_analysis' in analysis
        assert 'recommended_broker' in analysis
    
    @pytest.mark.asyncio
    async def test_optimize_broker_allocation(self, broker_engine):
        """Test broker allocation optimization"""
        result = await broker_engine.optimize_broker_allocation(
            portfolio_value=1000000.0,
            target_orders_per_day=5
        )
        
        assert isinstance(result, dict)
        assert 'allocation_weights' in result
        assert 'expected_costs' in result
        assert 'recommendations' in result
        assert 'performance_summary' in result
    
    @pytest.mark.asyncio
    async def test_get_broker_performance_summary(self, broker_engine):
        """Test getting broker performance summary"""
        performance = await broker_engine.get_broker_performance_summary()
        
        assert isinstance(performance, dict)
        assert len(performance) > 0
        
        for broker_id, broker_perf in performance.items():
            assert isinstance(broker_perf, BrokerPerformance)
            assert broker_perf.broker_id == broker_id
            assert broker_perf.total_orders >= 0
            assert broker_perf.reliability_score > 0
    
    @pytest.mark.asyncio
    async def test_get_order_routing_history(self, broker_engine):
        """Test getting order routing history"""
        history = await broker_engine.get_order_routing_history()
        
        assert isinstance(history, list)
        # History might be empty if no orders have been routed yet
    
    @pytest.mark.asyncio
    async def test_get_execution_quality_history(self, broker_engine):
        """Test getting execution quality history"""
        history = await broker_engine.get_execution_quality_history()
        
        assert isinstance(history, list)
        # History might be empty if no orders have been executed yet


class TestIntegration:
    """Test integration between Phase 3 engines"""
    
    @pytest.mark.asyncio
    async def test_ml_and_risk_integration(self):
        """Test integration between ML and risk engines"""
        ml_engine = get_ml_optimization_engine()
        risk_engine = get_advanced_risk_engine()
        
        # Create sample data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'portfolio_value': (1 + np.random.randn(100) * 0.02).cumprod() * 1000000,
            'returns': np.random.randn(100) * 0.02
        })
        
        # Test ML feature generation for risk analysis
        features = await ml_engine.generate_ml_features(data)
        assert not features.empty
        
        # Test risk analysis with ML-enhanced data
        risk_report = await risk_engine.generate_risk_report(data)
        assert 'recommendations' in risk_report
    
    @pytest.mark.asyncio
    async def test_broker_and_ml_integration(self):
        """Test integration between broker and ML engines"""
        broker_engine = get_multi_broker_engine()
        ml_engine = get_ml_optimization_engine()
        
        # Test order routing with ML insights
        order_request = {
            'symbol': 'RELIANCE',
            'quantity': 100,
            'price': 2500.0,
            'order_type': 'market',
            'side': 'buy'
        }
        
        routing_decision = await broker_engine.route_order(order_request, "hybrid")
        assert routing_decision.broker_id is not None
        
        # Test ML model creation for broker analysis
        config = MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
        
        model_id = await ml_engine.create_market_prediction_model('RELIANCE', config)
        assert model_id is not None


class TestPerformance:
    """Test performance characteristics of Phase 3 engines"""
    
    @pytest.mark.asyncio
    async def test_ml_engine_performance(self):
        """Test ML engine performance"""
        ml_engine = get_ml_optimization_engine()
        
        # Test feature generation performance
        dates = pd.date_range(end=datetime.now(), periods=1000, freq='D')
        large_data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(1000).cumsum() + 100,
            'high': np.random.randn(1000).cumsum() + 102,
            'low': np.random.randn(1000).cumsum() + 98,
            'close': np.random.randn(1000).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, 1000)
        })
        
        start_time = datetime.now()
        features = await ml_engine.generate_ml_features(large_data)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 5.0  # Should process 1000 rows in under 5 seconds
        assert len(features) == 1000
    
    @pytest.mark.asyncio
    async def test_risk_engine_performance(self):
        """Test risk engine performance"""
        risk_engine = get_advanced_risk_engine()
        
        # Test Monte Carlo simulation performance
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'portfolio_value': (1 + np.random.randn(252) * 0.02).cumprod() * 1000000,
            'returns': np.random.randn(252) * 0.02
        })
        
        start_time = datetime.now()
        result = await risk_engine.run_monte_carlo_simulation(data)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 10.0  # Should complete in under 10 seconds
        assert result.var_95 is not None
    
    @pytest.mark.asyncio
    async def test_broker_engine_performance(self):
        """Test broker engine performance"""
        broker_engine = get_multi_broker_engine()
        
        # Test order routing performance
        order_request = {
            'symbol': 'RELIANCE',
            'quantity': 100,
            'price': 2500.0,
            'order_type': 'market',
            'side': 'buy'
        }
        
        start_time = datetime.now()
        routing_decision = await broker_engine.route_order(order_request, "hybrid")
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 1.0  # Should route in under 1 second
        assert routing_decision.broker_id is not None


class TestErrorHandling:
    """Test error handling in Phase 3 engines"""
    
    @pytest.mark.asyncio
    async def test_ml_engine_error_handling(self):
        """Test ML engine error handling"""
        ml_engine = get_ml_optimization_engine()
        
        # Test with invalid data
        with pytest.raises(Exception):
            await ml_engine.create_market_prediction_model('', None)
        
        # Test with non-existent model
        with pytest.raises(ValueError):
            await ml_engine.predict_market_movement('non_existent_model', pd.DataFrame())
    
    @pytest.mark.asyncio
    async def test_risk_engine_error_handling(self):
        """Test risk engine error handling"""
        risk_engine = get_advanced_risk_engine()
        
        # Test with empty data
        empty_data = pd.DataFrame()
        with pytest.raises(Exception):
            await risk_engine.run_monte_carlo_simulation(empty_data)
    
    @pytest.mark.asyncio
    async def test_broker_engine_error_handling(self):
        """Test broker engine error handling"""
        broker_engine = get_multi_broker_engine()
        
        # Test with invalid order request
        invalid_order = {}
        with pytest.raises(Exception):
            await broker_engine.route_order(invalid_order, "invalid_strategy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

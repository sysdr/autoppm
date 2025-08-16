"""
Test UI Dashboard functionality
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from ui.portfolio_dashboard import PortfolioDashboard


class TestPortfolioDashboard:
    """Test Portfolio Dashboard functionality"""
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        dashboard = PortfolioDashboard()
        assert dashboard is not None
        assert dashboard.orchestrator is not None
        assert dashboard.ml_engine is not None
        assert dashboard.risk_engine is not None
        assert dashboard.broker_engine is not None
    
    def test_sample_portfolio_data(self):
        """Test sample portfolio data generation"""
        dashboard = PortfolioDashboard()
        data = dashboard._get_sample_portfolio_data()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 30  # 30 days of data
        assert 'total_value' in data.columns
        assert 'daily_return' in data.columns
        assert 'cumulative_return' in data.columns
    
    def test_metric_card_rendering(self):
        """Test metric card rendering"""
        dashboard = PortfolioDashboard()
        
        # Test positive change
        html = dashboard._render_metric_card("Test", "Value", "+5%", "positive")
        assert "🟢" in html
        
        # Test negative change
        html = dashboard._render_metric_card("Test", "Value", "-3%", "negative")
        assert "🔴" in html
        
        # Test neutral change
        html = dashboard._render_metric_card("Test", "Value", "0%", "neutral")
        assert "🟡" in html
    
    def test_portfolio_chart_creation(self):
        """Test portfolio chart creation"""
        dashboard = PortfolioDashboard()
        
        # Set up sample data
        dashboard._get_sample_portfolio_data()
        
        fig = dashboard._create_portfolio_chart()
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
    
    def test_risk_level_calculation(self):
        """Test risk level calculation"""
        dashboard = PortfolioDashboard()
        
        # Test with low volatility
        low_vol_data = pd.DataFrame({
            'daily_return': np.random.normal(0, 0.01, 30)  # 1% volatility
        })
        st.session_state.portfolio_data = low_vol_data
        
        risk_level = dashboard._calculate_risk_level()
        assert risk_level == "Low"
        
        # Test with high volatility
        high_vol_data = pd.DataFrame({
            'daily_return': np.random.normal(0, 0.03, 30)  # 3% volatility
        })
        st.session_state.portfolio_data = high_vol_data
        
        risk_level = dashboard._calculate_risk_level()
        assert risk_level == "High"
    
    def test_data_generation_methods(self):
        """Test data generation methods"""
        dashboard = PortfolioDashboard()
        
        # Test asset allocation
        allocation = dashboard._get_asset_allocation()
        assert isinstance(allocation, pd.DataFrame)
        assert 'asset' in allocation.columns
        assert 'value' in allocation.columns
        
        # Test sector exposure
        sectors = dashboard._get_sector_exposure()
        assert isinstance(sectors, pd.DataFrame)
        assert 'sector' in sectors.columns
        assert 'exposure' in sectors.columns
        
        # Test holdings data
        holdings = dashboard._get_holdings_data()
        assert isinstance(holdings, pd.DataFrame)
        assert 'Symbol' in holdings.columns
        assert 'Quantity' in holdings.columns
        
        # Test performance metrics
        metrics = dashboard._get_performance_metrics()
        assert isinstance(metrics, dict)
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
    
    def test_strategy_data_methods(self):
        """Test strategy data methods"""
        dashboard = PortfolioDashboard()
        
        # Test active strategies
        strategies = dashboard._get_active_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        # Test running strategies
        running = dashboard._get_running_strategies()
        assert isinstance(running, list)
        
        # Test strategy performance
        perf = dashboard._get_strategy_performance()
        assert isinstance(perf, pd.DataFrame)
        assert 'date' in perf.columns
        assert 'strategy' in perf.columns
    
    def test_risk_data_methods(self):
        """Test risk data methods"""
        dashboard = PortfolioDashboard()
        
        # Test current risk metrics
        risk_metrics = dashboard._get_current_risk_metrics()
        assert isinstance(risk_metrics, dict)
        assert 'var_95' in risk_metrics
        assert 'es_95' in risk_metrics
        
        # Test risk limits
        risk_limits = dashboard._get_risk_limits()
        assert isinstance(risk_limits, dict)
        assert 'max_position' in risk_limits
        assert 'max_sector' in risk_limits
        
        # Test risk alerts
        alerts = dashboard._get_risk_alerts()
        assert isinstance(alerts, list)
        assert len(alerts) > 0
    
    def test_trading_data_methods(self):
        """Test trading data methods"""
        dashboard = PortfolioDashboard()
        
        # Test recent orders
        orders = dashboard._get_recent_orders()
        assert isinstance(orders, list)
        
        # Test execution metrics
        exec_metrics = dashboard._get_execution_metrics()
        assert isinstance(exec_metrics, dict)
        assert 'avg_slippage' in exec_metrics
        assert 'fill_rate' in exec_metrics
        
        # Test broker performance
        broker_perf = dashboard._get_broker_performance()
        assert isinstance(broker_perf, dict)
        assert len(broker_perf) > 0
    
    def test_analytics_data_methods(self):
        """Test analytics data methods"""
        dashboard = PortfolioDashboard()
        
        # Test market predictions
        predictions = dashboard._generate_market_predictions()
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        
        # Test strategy optimization
        optimization = dashboard._optimize_all_strategies()
        assert isinstance(optimization, list)
        assert len(optimization) > 0
        
        # Test returns analysis
        returns = dashboard._get_returns_analysis()
        assert isinstance(returns, pd.DataFrame)
        assert 'returns' in returns.columns
        
        # Test correlation matrix
        correlation = dashboard._get_correlation_matrix()
        assert isinstance(correlation, pd.DataFrame)
        assert correlation.shape[0] == correlation.shape[1]  # Square matrix
    
    def test_broker_config_methods(self):
        """Test broker configuration methods"""
        dashboard = PortfolioDashboard()
        
        # Test broker configs
        configs = dashboard._get_broker_configs()
        assert isinstance(configs, dict)
        assert len(configs) > 0
        
        for broker_id, config in configs.items():
            assert 'name' in config
            assert 'is_active' in config
            assert 'priority' in config
            assert 'max_order_size' in config
            assert 'commission_rate' in config
    
    def test_order_placement(self):
        """Test order placement functionality"""
        dashboard = PortfolioDashboard()
        
        # Test successful order
        result = dashboard._place_order("RELIANCE", 100, "Market", "Buy", None, "Cost Optimized")
        assert result['success'] is True
        assert 'order_id' in result
        
        # Test with limit order
        result = dashboard._place_order("TCS", 50, "Limit", "Sell", 3500, "Hybrid")
        assert result['success'] is True
        assert 'order_id' in result
    
    def test_simulation_methods(self):
        """Test simulation methods"""
        dashboard = PortfolioDashboard()
        
        # Test Monte Carlo simulation
        mc_result = dashboard._run_monte_carlo_simulation()
        assert isinstance(mc_result, dict)
        assert 'var_95' in mc_result
        assert 'var_99' in mc_result
        assert 'max_drawdown' in mc_result
        
        # Test stress test
        stress_result = dashboard._run_stress_test("2008 Financial Crisis")
        assert isinstance(stress_result, dict)
        assert 'portfolio_loss' in stress_result
        assert 'recovery_time' in stress_result
        
        # Test scenario analysis
        scenarios = dashboard._run_scenario_analysis()
        assert isinstance(scenarios, list)
        assert len(scenarios) > 0
        
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'probability' in scenario
            assert 'risk_score' in scenario


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

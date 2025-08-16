"""
Test suite for Final Phase engines
Tests Production Deployment, Strategy Marketplace, and Advanced Analytics engines
"""

import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from engine.production_deployment_engine import (
    get_production_engine,
    ProductionDeploymentEngine,
    SystemMetrics,
    Alert,
    AlertRule,
    AutomationRule
)

from engine.strategy_marketplace_engine import (
    get_strategy_marketplace_engine,
    StrategyMarketplaceEngine,
    StrategyMetadata,
    StrategyReview,
    StrategyDownload
)

from engine.advanced_analytics_engine import (
    get_advanced_analytics_engine,
    AdvancedAnalyticsEngine,
    PerformanceMetrics,
    RiskMetrics,
    AttributionAnalysis,
    FactorAnalysis
)


class TestProductionDeploymentEngine:
    """Test Production Deployment Engine functionality"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = get_production_engine()
        assert engine is not None
        assert isinstance(engine, ProductionDeploymentEngine)
        assert engine.orchestrator is not None
        assert engine.ml_engine is not None
        assert engine.risk_engine is not None
        assert engine.broker_engine is not None
    
    def test_alert_rules_initialization(self):
        """Test alert rules initialization"""
        engine = get_production_engine()
        assert len(engine.alert_rules) > 0
        
        # Check specific alert rules
        rule_names = [rule.name for rule in engine.alert_rules]
        assert "High CPU Usage" in rule_names
        assert "High Memory Usage" in rule_names
        assert "Critical Portfolio Loss" in rule_names
    
    def test_automation_rules_initialization(self):
        """Test automation rules initialization"""
        engine = get_production_engine()
        assert len(engine.automation_rules) > 0
        
        # Check specific automation rules
        rule_names = [rule.name for rule in engine.automation_rules]
        assert "Daily Risk Assessment" in rule_names
        assert "Portfolio Rebalancing" in rule_names
        assert "System Backup" in rule_names
    
    def test_system_health_monitoring(self):
        """Test system health monitoring"""
        engine = get_production_engine()
        
        # Get system health
        health = engine.get_system_health()
        assert 'status' in health
        assert 'health_score' in health
        assert 'timestamp' in health
        assert 'active_alerts' in health
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment"""
        engine = get_production_engine()
        
        # Create a test alert
        test_alert = Alert(
            id="test_alert_001",
            type="warning",
            message="Test alert message",
            timestamp=datetime.now()
        )
        engine.active_alerts.append(test_alert)
        
        # Acknowledge alert
        success = engine.acknowledge_alert("test_alert_001", "test_user")
        assert success is True
        
        # Check alert state
        alert = engine.active_alerts[0]
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        engine = get_production_engine()
        
        summary = engine.get_performance_summary()
        assert isinstance(summary, dict)
        
        # Check if summary contains expected fields
        if 'message' not in summary:  # If metrics are available
            assert 'period' in summary
            assert 'average_cpu_usage' in summary
            assert 'average_memory_usage' in summary
            assert 'total_alerts' in summary
    
    def test_system_backup(self):
        """Test system backup functionality"""
        engine = get_production_engine()
        
        backup_result = engine.backup_system()
        assert isinstance(backup_result, dict)
        assert 'timestamp' in backup_result
        assert 'overall_status' in backup_result
    
    def test_alert_rule_management(self):
        """Test alert rule management"""
        engine = get_production_engine()
        
        # Add new alert rule
        new_rule = AlertRule(
            name="Test Alert Rule",
            condition="threshold",
            metric="test_metric",
            threshold=50.0,
            operator=">",
            severity="info"
        )
        
        success = engine.add_alert_rule(new_rule)
        assert success is True
        
        # Check if rule was added
        rule_names = [rule.name for rule in engine.alert_rules]
        assert "Test Alert Rule" in rule_names
    
    def test_automation_rule_management(self):
        """Test automation rule management"""
        engine = get_production_engine()
        
        # Add new automation rule
        new_rule = AutomationRule(
            name="Test Automation Rule",
            trigger="schedule",
            condition="0 12 * * *",  # Noon daily
            actions=["test_action"]
        )
        
        success = engine.add_automation_rule(new_rule)
        assert success is True
        
        # Check if rule was added
        rule_names = [rule.name for rule in engine.automation_rules]
        assert "Test Automation Rule" in rule_names


class TestStrategyMarketplaceEngine:
    """Test Strategy Marketplace Engine functionality"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = get_strategy_marketplace_engine()
        assert engine is not None
        assert isinstance(engine, StrategyMarketplaceEngine)
        assert engine.orchestrator is not None
        assert engine.ml_engine is not None
        assert engine.backtesting_engine is not None
    
    def test_available_strategies(self):
        """Test available strategies loading"""
        engine = get_strategy_marketplace_engine()
        assert len(engine.available_strategies) > 0
        
        # Check specific strategies
        strategy_names = [s.name for s in engine.available_strategies.values()]
        assert "Advanced Momentum Pro" in strategy_names
        assert "Mean Reversion Master" in strategy_names
        assert "ML Sentiment Trader" in strategy_names
    
    def test_strategy_search(self):
        """Test strategy search functionality"""
        engine = get_strategy_marketplace_engine()
        
        # Search by category
        momentum_strategies = engine.search_strategies(category="momentum")
        assert len(momentum_strategies) > 0
        assert all(s.category == "momentum" for s in momentum_strategies)
        
        # Search by risk level
        low_risk_strategies = engine.search_strategies(risk_level="low")
        assert len(low_risk_strategies) > 0
        assert all(s.risk_level == "low" for s in low_risk_strategies)
        
        # Search by rating
        high_rated_strategies = engine.search_strategies(min_rating=4.5)
        assert len(high_rated_strategies) > 0
        assert all(s.rating >= 4.5 for s in high_rated_strategies)
    
    def test_strategy_details(self):
        """Test strategy details retrieval"""
        engine = get_strategy_marketplace_engine()
        
        # Get first available strategy
        strategy_id = list(engine.available_strategies.keys())[0]
        strategy = engine.get_strategy_details(strategy_id)
        
        assert strategy is not None
        assert strategy.id == strategy_id
        assert hasattr(strategy, 'name')
        assert hasattr(strategy, 'description')
        assert hasattr(strategy, 'author')
        assert hasattr(strategy, 'version')
    
    def test_strategy_download(self):
        """Test strategy download functionality"""
        engine = get_strategy_marketplace_engine()
        
        # Download first available strategy
        strategy_id = list(engine.available_strategies.keys())[0]
        download_result = engine.download_strategy(strategy_id, "test_user")
        
        assert download_result['success'] is True
        assert download_result['strategy_id'] == strategy_id
        assert 'download_path' in download_result
        assert 'validation_result' in download_result
        
        # Check if strategy was added to downloaded strategies
        assert strategy_id in engine.downloaded_strategies
    
    def test_strategy_validation(self):
        """Test strategy validation"""
        engine = get_strategy_marketplace_engine()
        
        # Create a test strategy directory
        test_strategy_dir = Path("strategies/marketplace/test_strategy")
        test_strategy_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        (test_strategy_dir / "test_strategy.py").write_text("print('Hello World')")
        (test_strategy_dir / "config.yaml").write_text("name: Test Strategy")
        (test_strategy_dir / "metadata.yaml").write_text("id: test_001")
        
        # Test validation
        test_strategy = StrategyMetadata(
            id="test_001",
            name="Test Strategy",
            description="Test strategy for validation",
            author="Test Author",
            version="1.0.0",
            category="test",
            tags=["test"],
            risk_level="low",
            min_capital=1000,
            max_capital=10000,
            expected_return=10.0,
            max_drawdown=5.0,
            sharpe_ratio=1.0,
            strategy_file="test_strategy.py",
            config_file="config.yaml",
            documentation="",
            license="MIT",
            price=0.0,
            rating=4.0,
            downloads=0,
            last_updated=datetime.now()
        )
        
        validation_result = engine._validate_strategy(test_strategy_dir, test_strategy)
        assert validation_result['valid'] is True
        
        # Cleanup
        import shutil
        shutil.rmtree(test_strategy_dir)
    
    def test_strategy_reviews(self):
        """Test strategy review functionality"""
        engine = get_strategy_marketplace_engine()
        
        # Add a review
        review_result = engine.add_strategy_review(
            "strategy_001", "test_user", 5, "Excellent strategy!"
        )
        
        assert review_result['success'] is True
        assert 'review_id' in review_result
        
        # Get reviews
        reviews = engine.get_strategy_reviews("strategy_001")
        assert len(reviews) > 0
        assert reviews[0].rating == 5
        assert reviews[0].comment == "Excellent strategy!"
    
    def test_marketplace_statistics(self):
        """Test marketplace statistics"""
        engine = get_strategy_marketplace_engine()
        
        stats = engine.get_marketplace_stats()
        assert isinstance(stats, dict)
        assert 'total_strategies' in stats
        assert 'total_downloads' in stats
        assert 'total_reviews' in stats
        assert 'categories' in stats
        assert 'average_rating' in stats
    
    def test_strategy_update(self):
        """Test strategy update functionality"""
        engine = get_strategy_marketplace_engine()
        
        # First download a strategy
        strategy_id = list(engine.available_strategies.keys())[0]
        engine.download_strategy(strategy_id, "test_user")
        
        # Try to update (should fail if already up to date)
        update_result = engine.update_strategy(strategy_id)
        
        # Should either succeed or indicate already up to date
        assert 'success' in update_result
        if not update_result['success']:
            assert 'already up to date' in update_result['error']
    
    def test_strategy_removal(self):
        """Test strategy removal functionality"""
        engine = get_strategy_marketplace_engine()
        
        # First download a strategy
        strategy_id = list(engine.available_strategies.keys())[0]
        engine.download_strategy(strategy_id, "test_user")
        
        # Remove strategy
        removal_result = engine.remove_strategy(strategy_id)
        assert removal_result['success'] is True
        
        # Check if strategy was removed
        assert strategy_id not in engine.downloaded_strategies


class TestAdvancedAnalyticsEngine:
    """Test Advanced Analytics Engine functionality"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = get_advanced_analytics_engine()
        assert engine is not None
        assert isinstance(engine, AdvancedAnalyticsEngine)
        assert engine.orchestrator is not None
        assert engine.ml_engine is not None
        assert engine.risk_engine is not None
        assert engine.backtesting_engine is not None
    
    def test_portfolio_data_generation(self):
        """Test portfolio data generation"""
        engine = get_advanced_analytics_engine()
        
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        portfolio_data = engine._get_portfolio_data(start_date, end_date)
        assert isinstance(portfolio_data, pd.DataFrame)
        assert len(portfolio_data) > 0
        assert 'date' in portfolio_data.columns
        assert 'returns' in portfolio_data.columns
        assert 'portfolio_value' in portfolio_data.columns
    
    def test_benchmark_data_generation(self):
        """Test benchmark data generation"""
        engine = get_advanced_analytics_engine()
        
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        benchmark_data = engine._get_benchmark_data(start_date, end_date)
        assert isinstance(benchmark_data, pd.DataFrame)
        assert len(benchmark_data) > 0
        assert 'date' in benchmark_data.columns
        assert 'returns' in benchmark_data.columns
        assert 'benchmark_value' in portfolio_data.columns
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        engine = get_advanced_analytics_engine()
        
        # Generate test data
        portfolio_data = engine._get_portfolio_data("2023-01-01", "2023-12-31")
        benchmark_data = engine._get_benchmark_data("2023-01-01", "2023-12-31")
        
        # Calculate metrics
        metrics = engine._calculate_performance_metrics(portfolio_data, benchmark_data)
        
        assert isinstance(metrics, PerformanceMetrics)
        assert hasattr(metrics, 'total_return')
        assert hasattr(metrics, 'annualized_return')
        assert hasattr(metrics, 'sharpe_ratio')
        assert hasattr(metrics, 'max_drawdown')
        assert hasattr(metrics, 'win_rate')
    
    def test_risk_metrics_calculation(self):
        """Test risk metrics calculation"""
        engine = get_advanced_analytics_engine()
        
        # Generate test data
        portfolio_data = engine._get_portfolio_data("2023-01-01", "2023-12-31")
        benchmark_data = engine._get_benchmark_data("2023-01-01", "2023-12-31")
        
        # Calculate metrics
        metrics = engine._calculate_risk_metrics(portfolio_data, benchmark_data)
        
        assert isinstance(metrics, RiskMetrics)
        assert hasattr(metrics, 'var_95')
        assert hasattr(metrics, 'var_99')
        assert hasattr(metrics, 'beta')
        assert hasattr(metrics, 'alpha')
        assert hasattr(metrics, 'information_ratio')
    
    def test_attribution_analysis(self):
        """Test attribution analysis"""
        engine = get_advanced_analytics_engine()
        
        # Generate test data
        portfolio_data = engine._get_portfolio_data("2023-01-01", "2023-12-31")
        benchmark_data = engine._get_benchmark_data("2023-01-01", "2023-12-31")
        
        # Calculate attribution
        attribution = engine._calculate_attribution_analysis(portfolio_data, benchmark_data)
        
        assert isinstance(attribution, AttributionAnalysis)
        assert hasattr(attribution, 'total_attribution')
        assert hasattr(attribution, 'asset_allocation')
        assert hasattr(attribution, 'stock_selection')
        assert hasattr(attribution, 'sector_attribution')
    
    def test_factor_analysis(self):
        """Test factor analysis"""
        engine = get_advanced_analytics_engine()
        
        # Generate test data
        portfolio_data = engine._get_portfolio_data("2023-01-01", "2023-12-31")
        benchmark_data = engine._get_benchmark_data("2023-01-01", "2023-12-31")
        
        # Calculate factor analysis
        factor_analysis = engine._calculate_factor_analysis(portfolio_data, benchmark_data)
        
        assert isinstance(factor_analysis, FactorAnalysis)
        assert hasattr(factor_analysis, 'factors')
        assert hasattr(factor_analysis, 'factor_loadings')
        assert hasattr(factor_analysis, 'factor_returns')
        assert hasattr(factor_analysis, 'r_squared')
    
    def test_recommendations_generation(self):
        """Test recommendations generation"""
        engine = get_advanced_analytics_engine()
        
        # Create test metrics
        performance_metrics = PerformanceMetrics(
            total_return=0.15,
            annualized_return=0.12,
            volatility=0.18,
            sharpe_ratio=0.8,  # Below 1.0 threshold
            sortino_ratio=1.2,
            calmar_ratio=1.5,
            max_drawdown=-0.20,  # Below -0.15 threshold
            win_rate=0.45,  # Below 0.5 threshold
            profit_factor=1.8,
            average_win=0.02,
            average_loss=-0.015,
            largest_win=0.05,
            largest_loss=-0.03,
            total_trades=100,
            winning_trades=45,
            losing_trades=55,
            average_trade_duration=1.0,
            best_month=0.08,
            worst_month=-0.06,
            consecutive_wins=5,
            consecutive_losses=4
        )
        
        risk_metrics = RiskMetrics(
            var_95=-0.035,  # Below -0.03 threshold
            var_99=-0.05,
            expected_shortfall_95=-0.04,
            expected_shortfall_99=-0.06,
            tail_risk=0.025,
            beta=1.3,  # Above 1.2 threshold
            alpha=0.02,
            information_ratio=0.8,
            treynor_ratio=0.6,
            jensen_alpha=0.02,
            downside_deviation=0.15,
            semi_deviation=0.15,
            skewness=-0.1,
            kurtosis=3.2,
            correlation_with_market=0.85,  # Above 0.8 threshold
            sector_concentration=0.25,
            geographic_concentration=0.20,
            currency_exposure=0.05
        )
        
        recommendations = engine._generate_recommendations(performance_metrics, risk_metrics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendations
        recommendation_text = ' '.join(recommendations).lower()
        assert 'risk-adjusted returns' in recommendation_text
        assert 'stop-loss' in recommendation_text
        assert 'entry and exit criteria' in recommendation_text
        assert 'diversification' in recommendation_text
        assert 'hedging strategies' in recommendation_text
    
    def test_comprehensive_report_generation(self):
        """Test comprehensive report generation"""
        engine = get_advanced_analytics_engine()
        
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        report = engine.generate_comprehensive_report(start_date, end_date)
        
        assert isinstance(report, AnalyticsReport)
        assert report.period == f"{start_date} to {end_date}"
        assert report.timestamp is not None
        assert report.performance_metrics is not None
        assert report.risk_metrics is not None
        assert report.attribution_analysis is not None
        assert report.factor_analysis is not None
        assert len(report.recommendations) > 0
        assert len(report.charts) > 0
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        engine = get_advanced_analytics_engine()
        
        summary = engine.get_performance_summary('1Y')
        
        assert isinstance(summary, dict)
        assert 'period' in summary
        assert 'start_date' in summary
        assert 'end_date' in summary
        assert 'performance_metrics' in summary
        assert 'risk_metrics' in summary
        assert 'recommendations' in summary
    
    def test_strategy_comparison(self):
        """Test strategy comparison"""
        engine = get_advanced_analytics_engine()
        
        strategy_ids = ["strategy_001", "strategy_002"]
        comparison = engine.compare_strategies(strategy_ids, '1Y')
        
        assert isinstance(comparison, dict)
        assert len(comparison) == 2
        assert "strategy_001" in comparison
        assert "strategy_002" in comparison
    
    def test_benchmark_report(self):
        """Test benchmark report generation"""
        engine = get_advanced_analytics_engine()
        
        report = engine.generate_benchmark_report("NIFTY50", "1Y")
        
        assert isinstance(report, dict)
        assert 'benchmark_name' in report
        assert 'period' in report
        assert 'total_return' in report
        assert 'volatility' in report
        assert 'sharpe_ratio' in report
    
    def test_report_export(self):
        """Test report export functionality"""
        engine = get_advanced_analytics_engine()
        
        # Generate a report first
        report = engine.generate_comprehensive_report("2023-01-01", "2023-12-31")
        report_id = str(report.timestamp.timestamp())
        
        # Test HTML export
        html_result = engine.export_report(report_id, 'html')
        assert isinstance(html_result, str)
        assert html_result.endswith('.html')
        
        # Test unsupported format
        unsupported_result = engine.export_report(report_id, 'unsupported')
        assert "Unsupported format" in unsupported_result


class TestIntegration:
    """Test integration between Final Phase engines"""
    
    def test_engine_interoperability(self):
        """Test that all engines can work together"""
        production_engine = get_production_engine()
        marketplace_engine = get_strategy_marketplace_engine()
        analytics_engine = get_advanced_analytics_engine()
        
        # All engines should be initialized
        assert production_engine is not None
        assert marketplace_engine is not None
        assert analytics_engine is not None
        
        # Test that they can share data
        # This is a basic integration test
        assert True
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow"""
        # This would test a complete workflow from strategy download to analytics
        # For now, just verify all engines are accessible
        engines = [
            get_production_engine(),
            get_strategy_marketplace_engine(),
            get_advanced_analytics_engine()
        ]
        
        assert all(engine is not None for engine in engines)


class TestPerformance:
    """Test performance characteristics"""
    
    def test_report_generation_speed(self):
        """Test report generation performance"""
        engine = get_advanced_analytics_engine()
        
        import time
        start_time = time.time()
        
        report = engine.generate_comprehensive_report("2023-01-01", "2023-12-31")
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Report generation should complete within reasonable time
        assert generation_time < 30.0  # 30 seconds
        assert report is not None
    
    def test_strategy_search_speed(self):
        """Test strategy search performance"""
        engine = get_strategy_marketplace_engine()
        
        import time
        start_time = time.time()
        
        results = engine.search_strategies(category="momentum", min_rating=4.0)
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Search should complete quickly
        assert search_time < 1.0  # 1 second
        assert isinstance(results, list)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_dates(self):
        """Test handling of invalid dates"""
        engine = get_advanced_analytics_engine()
        
        # Test with invalid date format
        with pytest.raises(Exception):
            engine.generate_comprehensive_report("invalid-date", "2023-12-31")
    
    def test_missing_strategy(self):
        """Test handling of missing strategy"""
        engine = get_strategy_marketplace_engine()
        
        result = engine.get_strategy_details("nonexistent_strategy")
        assert result is None
    
    def test_invalid_alert_acknowledgment(self):
        """Test handling of invalid alert acknowledgment"""
        engine = get_production_engine()
        
        success = engine.acknowledge_alert("nonexistent_alert", "test_user")
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

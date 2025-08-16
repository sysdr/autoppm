"""
Advanced Analytics Engine for AutoPPM
Provides comprehensive performance insights, reporting, and advanced analytics
"""

import asyncio
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from engine.autoppm_orchestrator import get_autoppm_orchestrator
from engine.ml_optimization_engine import get_ml_optimization_engine
from engine.advanced_risk_engine import get_advanced_risk_engine
from engine.backtesting_engine import get_backtesting_engine


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_trade_duration: float
    best_month: float
    worst_month: float
    consecutive_wins: int
    consecutive_losses: int


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    var_95: float
    var_99: float
    expected_shortfall_95: float
    expected_shortfall_99: float
    tail_risk: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    downside_deviation: float
    semi_deviation: float
    skewness: float
    kurtosis: float
    correlation_with_market: float
    sector_concentration: float
    geographic_concentration: float
    currency_exposure: float


@dataclass
class AttributionAnalysis:
    """Performance attribution analysis"""
    total_attribution: float
    asset_allocation: float
    stock_selection: float
    interaction: float
    sector_attribution: Dict[str, float]
    factor_attribution: Dict[str, float]
    risk_attribution: Dict[str, float]


@dataclass
class FactorAnalysis:
    """Factor analysis results"""
    factors: List[str]
    factor_loadings: Dict[str, float]
    factor_returns: Dict[str, float]
    factor_contribution: Dict[str, float]
    r_squared: float
    residual_volatility: float


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    timestamp: datetime
    period: str
    performance_metrics: PerformanceMetrics
    risk_metrics: RiskMetrics
    attribution_analysis: AttributionAnalysis
    factor_analysis: FactorAnalysis
    recommendations: List[str]
    charts: Dict[str, str]  # chart_name -> chart_file_path


class AdvancedAnalyticsEngine:
    """
    Advanced Analytics Engine for AutoPPM
    
    Features:
    - Comprehensive performance analysis and reporting
    - Advanced risk analytics and attribution
    - Factor analysis and decomposition
    - Interactive charts and visualizations
    - Automated report generation
    - Performance benchmarking and comparison
    """
    
    def __init__(self):
        self.orchestrator = get_autoppm_orchestrator()
        self.ml_engine = get_ml_optimization_engine()
        self.risk_engine = get_advanced_risk_engine()
        self.backtesting_engine = get_backtesting_engine()
        
        # Configuration
        self.config = self._load_config()
        self.reports_dir = Path("reports/analytics")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Analytics state
        self.performance_history: List[PerformanceMetrics] = []
        self.risk_history: List[RiskMetrics] = []
        self.reports_history: List[AnalyticsReport] = []
        
        # Market data cache
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
        self.benchmark_data: Optional[pd.DataFrame] = None
        
        logger.info("Advanced Analytics Engine initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load analytics configuration"""
        return {
            'risk_free_rate': 0.05,  # 5% annual risk-free rate
            'market_benchmark': 'NIFTY50',
            'analysis_periods': ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'ALL'],
            'confidence_levels': [0.90, 0.95, 0.99],
            'factor_models': ['CAPM', 'Fama-French', 'Carhart', 'Custom'],
            'chart_formats': ['png', 'html', 'pdf'],
            'auto_reporting': True,
            'report_retention_days': 365
        }
    
    def generate_comprehensive_report(self, 
                                   start_date: str,
                                   end_date: str,
                                   portfolio_data: Optional[pd.DataFrame] = None,
                                   benchmark_data: Optional[pd.DataFrame] = None) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        try:
            logger.info(f"Generating comprehensive report from {start_date} to {end_date}")
            
            # Get portfolio data if not provided
            if portfolio_data is None:
                portfolio_data = self._get_portfolio_data(start_date, end_date)
            
            # Get benchmark data if not provided
            if benchmark_data is None:
                benchmark_data = self._get_benchmark_data(start_date, end_date)
            
            # Calculate all metrics
            performance_metrics = self._calculate_performance_metrics(portfolio_data, benchmark_data)
            risk_metrics = self._calculate_risk_metrics(portfolio_data, benchmark_data)
            attribution_analysis = self._calculate_attribution_analysis(portfolio_data, benchmark_data)
            factor_analysis = self._calculate_factor_analysis(portfolio_data, benchmark_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(performance_metrics, risk_metrics)
            
            # Generate charts
            charts = self._generate_analytics_charts(portfolio_data, benchmark_data, 
                                                   performance_metrics, risk_metrics)
            
            # Create report
            report = AnalyticsReport(
                timestamp=datetime.now(),
                period=f"{start_date} to {end_date}",
                performance_metrics=performance_metrics,
                risk_metrics=risk_metrics,
                attribution_analysis=attribution_analysis,
                factor_analysis=factor_analysis,
                recommendations=recommendations,
                charts=charts
            )
            
            # Store report
            self.reports_history.append(report)
            self._save_report(report)
            
            logger.info("Comprehensive report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            raise
    
    def _get_portfolio_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get portfolio data for analysis"""
        try:
            # In production, this would get actual portfolio data
            # For now, we'll generate sample data
            
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Generate realistic portfolio data
            np.random.seed(42)  # For reproducible results
            returns = np.random.normal(0.001, 0.02, len(date_range))  # 0.1% daily return, 2% volatility
            
            # Add some trend and seasonality
            trend = np.linspace(0, 0.1, len(date_range))
            seasonality = 0.005 * np.sin(2 * np.pi * np.arange(len(date_range)) / 252)
            returns = returns + trend + seasonality
            
            # Calculate cumulative returns
            cumulative_returns = (1 + returns).cumprod()
            
            # Create portfolio data
            portfolio_data = pd.DataFrame({
                'date': date_range,
                'returns': returns,
                'cumulative_returns': cumulative_returns,
                'portfolio_value': 1000000 * cumulative_returns,
                'benchmark_returns': returns + np.random.normal(0, 0.005, len(date_range)),
                'risk_free_rate': self.config['risk_free_rate'] / 252  # Daily risk-free rate
            })
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            raise
    
    def _get_benchmark_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get benchmark data for comparison"""
        try:
            # In production, this would get actual benchmark data
            # For now, we'll generate sample data
            
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Generate benchmark returns (slightly different from portfolio)
            np.random.seed(43)  # Different seed for benchmark
            benchmark_returns = np.random.normal(0.0008, 0.018, len(date_range))  # 0.08% daily return, 1.8% volatility
            
            # Add trend
            trend = np.linspace(0, 0.08, len(date_range))
            benchmark_returns = benchmark_returns + trend
            
            # Calculate cumulative returns
            cumulative_returns = (1 + benchmark_returns).cumprod()
            
            benchmark_data = pd.DataFrame({
                'date': date_range,
                'returns': benchmark_returns,
                'cumulative_returns': cumulative_returns,
                'benchmark_value': 1000000 * cumulative_returns
            })
            
            return benchmark_data
            
        except Exception as e:
            logger.error(f"Error getting benchmark data: {e}")
            raise
    
    def _calculate_performance_metrics(self, 
                                     portfolio_data: pd.DataFrame, 
                                     benchmark_data: pd.DataFrame) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        try:
            returns = portfolio_data['returns'].dropna()
            benchmark_returns = benchmark_data['returns'].dropna()
            
            # Basic return metrics
            total_return = (portfolio_data['portfolio_value'].iloc[-1] / portfolio_data['portfolio_value'].iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
            
            # Volatility
            volatility = returns.std() * np.sqrt(252)
            
            # Risk-adjusted returns
            excess_returns = returns - portfolio_data['risk_free_rate'].dropna()
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252)
            sortino_ratio = excess_returns.mean() / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Calmar ratio
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Trade analysis (simplified)
            # In production, this would analyze actual trades
            total_trades = len(returns)
            winning_trades = len(returns[returns > 0])
            losing_trades = len(returns[returns < 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Profit factor
            gross_profit = returns[returns > 0].sum()
            gross_loss = abs(returns[returns < 0].sum())
            profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
            
            # Average win/loss
            average_win = returns[returns > 0].mean() if winning_trades > 0 else 0
            average_loss = returns[returns < 0].mean() if losing_trades > 0 else 0
            
            # Largest win/loss
            largest_win = returns.max()
            largest_loss = returns.min()
            
            # Monthly analysis
            monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
            best_month = monthly_returns.max()
            worst_month = monthly_returns.min()
            
            # Consecutive wins/losses
            consecutive_wins = self._calculate_consecutive_wins(returns)
            consecutive_losses = self._calculate_consecutive_losses(returns)
            
            return PerformanceMetrics(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                average_trade_duration=1.0,  # Placeholder
                best_month=best_month,
                worst_month=worst_month,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            raise
    
    def _calculate_consecutive_wins(self, returns: pd.Series) -> int:
        """Calculate maximum consecutive wins"""
        try:
            wins = (returns > 0).astype(int)
            max_consecutive = 0
            current_consecutive = 0
            
            for win in wins:
                if win == 1:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
            
        except Exception as e:
            logger.error(f"Error calculating consecutive wins: {e}")
            return 0
    
    def _calculate_consecutive_losses(self, returns: pd.Series) -> int:
        """Calculate maximum consecutive losses"""
        try:
            losses = (returns < 0).astype(int)
            max_consecutive = 0
            current_consecutive = 0
            
            for loss in losses:
                if loss == 1:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
            
        except Exception as e:
            logger.error(f"Error calculating consecutive losses: {e}")
            return 0
    
    def _calculate_risk_metrics(self, 
                               portfolio_data: pd.DataFrame, 
                               benchmark_data: pd.DataFrame) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            returns = portfolio_data['returns'].dropna()
            benchmark_returns = benchmark_data['returns'].dropna()
            risk_free_rate = portfolio_data['risk_free_rate'].dropna()
            
            # Value at Risk and Expected Shortfall
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            expected_shortfall_95 = returns[returns <= var_95].mean()
            expected_shortfall_99 = returns[returns <= var_99].mean()
            
            # Tail risk
            tail_risk = returns[returns <= np.percentile(returns, 10)].std()
            
            # Beta and Alpha (CAPM)
            excess_returns = returns - risk_free_rate
            excess_benchmark = benchmark_returns - risk_free_rate
            
            # Calculate beta
            covariance = np.cov(excess_returns, excess_benchmark)[0, 1]
            benchmark_variance = np.var(excess_benchmark)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            # Calculate alpha
            alpha = excess_returns.mean() - beta * excess_benchmark.mean()
            
            # Information ratio
            tracking_error = (excess_returns - excess_benchmark).std()
            information_ratio = (excess_returns - excess_benchmark).mean() / tracking_error if tracking_error > 0 else 0
            
            # Treynor ratio
            treynor_ratio = excess_returns.mean() / beta if beta != 0 else 0
            
            # Jensen's alpha
            jensen_alpha = alpha
            
            # Downside deviation
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std()
            semi_deviation = downside_deviation
            
            # Higher moments
            skewness = returns.skew()
            kurtosis = returns.kurtosis()
            
            # Correlation with market
            correlation_with_market = returns.corr(benchmark_returns)
            
            # Placeholder values for complex metrics
            sector_concentration = 0.0  # Would calculate from actual portfolio
            geographic_concentration = 0.0  # Would calculate from actual portfolio
            currency_exposure = 0.0  # Would calculate from actual portfolio
            
            return RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                expected_shortfall_95=expected_shortfall_95,
                expected_shortfall_99=expected_shortfall_99,
                tail_risk=tail_risk,
                beta=beta,
                alpha=alpha,
                information_ratio=information_ratio,
                treynor_ratio=treynor_ratio,
                jensen_alpha=jensen_alpha,
                downside_deviation=downside_deviation,
                semi_deviation=semi_deviation,
                skewness=skewness,
                kurtosis=kurtosis,
                correlation_with_market=correlation_with_market,
                sector_concentration=sector_concentration,
                geographic_concentration=geographic_concentration,
                currency_exposure=currency_exposure
            )
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            raise
    
    def _calculate_attribution_analysis(self, 
                                      portfolio_data: pd.DataFrame, 
                                      benchmark_data: pd.DataFrame) -> AttributionAnalysis:
        """Calculate performance attribution analysis"""
        try:
            # Simplified attribution analysis
            # In production, this would use actual portfolio holdings and sector data
            
            returns = portfolio_data['returns'].dropna()
            benchmark_returns = benchmark_data['returns'].dropna()
            
            # Calculate excess return
            excess_return = returns.mean() - benchmark_returns.mean()
            
            # Simple attribution breakdown (placeholder)
            asset_allocation = excess_return * 0.4  # 40% of excess return
            stock_selection = excess_return * 0.5   # 50% of excess return
            interaction = excess_return * 0.1       # 10% of excess return
            
            # Sector attribution (placeholder)
            sectors = ['Technology', 'Financial', 'Healthcare', 'Consumer', 'Energy']
            sector_attribution = {sector: excess_return * 0.2 for sector in sectors}
            
            # Factor attribution (placeholder)
            factors = ['Market', 'Size', 'Value', 'Momentum', 'Quality']
            factor_attribution = {factor: excess_return * 0.2 for factor in factors}
            
            # Risk attribution (placeholder)
            risk_factors = ['Volatility', 'Beta', 'Correlation', 'Concentration']
            risk_attribution = {risk: excess_return * 0.25 for risk in risk_factors}
            
            return AttributionAnalysis(
                total_attribution=excess_return,
                asset_allocation=asset_allocation,
                stock_selection=stock_selection,
                interaction=interaction,
                sector_attribution=sector_attribution,
                factor_attribution=factor_attribution,
                risk_attribution=risk_attribution
            )
            
        except Exception as e:
            logger.error(f"Error calculating attribution analysis: {e}")
            raise
    
    def _calculate_factor_analysis(self, 
                                 portfolio_data: pd.DataFrame, 
                                 benchmark_data: pd.DataFrame) -> FactorAnalysis:
        """Calculate factor analysis"""
        try:
            # Simplified factor analysis
            # In production, this would use actual factor models and data
            
            returns = portfolio_data['returns'].dropna()
            benchmark_returns = benchmark_data['returns'].dropna()
            
            # Factor loadings (placeholder)
            factors = ['Market', 'Size', 'Value', 'Momentum', 'Quality']
            factor_loadings = {factor: np.random.uniform(-0.5, 0.5) for factor in factors}
            
            # Factor returns (placeholder)
            factor_returns = {factor: np.random.uniform(-0.001, 0.001) for factor in factors}
            
            # Factor contribution
            factor_contribution = {
                factor: factor_loadings[factor] * factor_returns[factor] 
                for factor in factors
            }
            
            # R-squared and residual volatility
            r_squared = 0.75  # Placeholder
            residual_volatility = returns.std() * np.sqrt(1 - r_squared)
            
            return FactorAnalysis(
                factors=factors,
                factor_loadings=factor_loadings,
                factor_returns=factor_returns,
                factor_contribution=factor_contribution,
                r_squared=r_squared,
                residual_volatility=residual_volatility
            )
            
        except Exception as e:
            logger.error(f"Error calculating factor analysis: {e}")
            raise
    
    def _generate_recommendations(self, 
                                performance_metrics: PerformanceMetrics, 
                                risk_metrics: RiskMetrics) -> List[str]:
        """Generate actionable recommendations"""
        try:
            recommendations = []
            
            # Performance-based recommendations
            if performance_metrics.sharpe_ratio < 1.0:
                recommendations.append("Consider improving risk-adjusted returns through better position sizing or risk management")
            
            if performance_metrics.max_drawdown > -0.15:
                recommendations.append("Implement stricter stop-loss mechanisms to reduce maximum drawdown")
            
            if performance_metrics.win_rate < 0.5:
                recommendations.append("Review entry and exit criteria to improve win rate")
            
            # Risk-based recommendations
            if risk_metrics.var_95 < -0.03:
                recommendations.append("Reduce portfolio risk through diversification or position sizing")
            
            if risk_metrics.beta > 1.2:
                recommendations.append("Consider reducing market beta exposure through hedging strategies")
            
            if risk_metrics.correlation_with_market > 0.8:
                recommendations.append("Increase portfolio diversification to reduce market correlation")
            
            # General recommendations
            if len(recommendations) == 0:
                recommendations.append("Portfolio performance is strong. Consider rebalancing to maintain optimal allocation")
            
            recommendations.append("Regular monitoring and rebalancing recommended")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def _generate_analytics_charts(self, 
                                 portfolio_data: pd.DataFrame, 
                                 benchmark_data: pd.DataFrame,
                                 performance_metrics: PerformanceMetrics,
                                 risk_metrics: RiskMetrics) -> Dict[str, str]:
        """Generate analytics charts"""
        try:
            charts = {}
            
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. Performance Comparison Chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Cumulative returns
            ax1.plot(portfolio_data['date'], portfolio_data['cumulative_returns'], 
                    label='Portfolio', linewidth=2)
            ax1.plot(benchmark_data['date'], benchmark_data['cumulative_returns'], 
                    label='Benchmark', linewidth=2)
            ax1.set_title('Cumulative Returns Comparison')
            ax1.set_ylabel('Cumulative Returns')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Drawdown
            cumulative_returns = portfolio_data['cumulative_returns']
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            ax2.fill_between(portfolio_data['date'], drawdown, 0, alpha=0.3, color='red')
            ax2.plot(portfolio_data['date'], drawdown, color='red', linewidth=2)
            ax2.set_title('Portfolio Drawdown')
            ax2.set_ylabel('Drawdown')
            ax2.set_xlabel('Date')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_path = self.reports_dir / f"performance_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['performance_comparison'] = str(chart_path)
            plt.close()
            
            # 2. Risk-Return Scatter
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Calculate rolling metrics
            rolling_window = 60
            rolling_returns = portfolio_data['returns'].rolling(rolling_window).mean() * 252
            rolling_vol = portfolio_data['returns'].rolling(rolling_window).std() * np.sqrt(252)
            
            ax.scatter(rolling_vol, rolling_returns, alpha=0.6, s=50)
            ax.axhline(y=performance_metrics.annualized_return, color='red', linestyle='--', 
                      label=f'Portfolio Avg: {performance_metrics.annualized_return:.2%}')
            ax.axhline(y=self.config['risk_free_rate'], color='green', linestyle='--', 
                      label=f'Risk-Free Rate: {self.config["risk_free_rate"]:.2%}')
            
            ax.set_xlabel('Volatility (Annualized)')
            ax.set_ylabel('Return (Annualized)')
            ax.set_title('Risk-Return Profile (Rolling 60-day)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            chart_path = self.reports_dir / f"risk_return_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['risk_return_scatter'] = str(chart_path)
            plt.close()
            
            # 3. Performance Metrics Dashboard
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Sharpe Ratio', 'Maximum Drawdown', 'Win Rate', 'Profit Factor'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Sharpe Ratio
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=performance_metrics.sharpe_ratio,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Sharpe Ratio"},
                delta={'reference': 1.0},
                gauge={'axis': {'range': [None, 3]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 1], 'color': "lightgray"},
                                {'range': [1, 2], 'color': "yellow"},
                                {'range': [2, 3], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 2}}),
                row=1, col=1)
            
            # Maximum Drawdown
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=abs(performance_metrics.max_drawdown * 100),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Max Drawdown (%)"},
                delta={'reference': 15},
                gauge={'axis': {'range': [0, 30]},
                       'bar': {'color': "red"},
                       'steps': [{'range': [0, 10], 'color': "green"},
                                {'range': [10, 20], 'color': "yellow"},
                                {'range': [20, 30], 'color': "red"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 20}}),
                row=1, col=2)
            
            # Win Rate
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=performance_metrics.win_rate * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Win Rate (%)"},
                delta={'reference': 50},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "green"},
                       'steps': [{'range': [0, 40], 'color': "red"},
                                {'range': [40, 60], 'color': "yellow"},
                                {'range': [60, 100], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 60}}),
                row=2, col=1)
            
            # Profit Factor
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=min(performance_metrics.profit_factor, 5.0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Profit Factor"},
                delta={'reference': 1.5},
                gauge={'axis': {'range': [0, 5]},
                       'bar': {'color': "blue"},
                       'steps': [{'range': [0, 1], 'color': "red"},
                                {'range': [1, 2], 'color': "yellow"},
                                {'range': [2, 5], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 2}}),
                row=2, col=2)
            
            fig.update_layout(height=600, title_text="Performance Metrics Dashboard")
            
            chart_path = self.reports_dir / f"metrics_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(str(chart_path))
            charts['metrics_dashboard'] = str(chart_path)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return {}
    
    def _save_report(self, report: AnalyticsReport):
        """Save analytics report"""
        try:
            # Save report data
            report_data = asdict(report)
            report_data['timestamp'] = report.timestamp.isoformat()
            
            report_file = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def get_performance_summary(self, period: str = '1Y') -> Dict[str, Any]:
        """Get performance summary for a specific period"""
        try:
            # Calculate period dates
            end_date = datetime.now()
            if period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            elif period == '3Y':
                start_date = end_date - timedelta(days=1095)
            elif period == '5Y':
                start_date = end_date - timedelta(days=1825)
            else:
                start_date = end_date - timedelta(days=365)  # Default to 1Y
            
            # Generate report
            report = self.generate_comprehensive_report(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            return {
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'performance_metrics': asdict(report.performance_metrics),
                'risk_metrics': asdict(report.risk_metrics),
                'recommendations': report.recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def compare_strategies(self, strategy_ids: List[str], period: str = '1Y') -> Dict[str, Any]:
        """Compare multiple strategies"""
        try:
            comparison_results = {}
            
            for strategy_id in strategy_ids:
                # Get strategy performance (placeholder)
                # In production, this would get actual strategy data
                strategy_performance = self._get_strategy_performance(strategy_id, period)
                comparison_results[strategy_id] = strategy_performance
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error comparing strategies: {e}")
            return {'error': str(e)}
    
    def _get_strategy_performance(self, strategy_id: str, period: str) -> Dict[str, Any]:
        """Get strategy performance data"""
        # Placeholder implementation
        return {
            'strategy_id': strategy_id,
            'period': period,
            'total_return': np.random.uniform(0.05, 0.25),
            'sharpe_ratio': np.random.uniform(0.8, 2.0),
            'max_drawdown': np.random.uniform(-0.20, -0.05),
            'win_rate': np.random.uniform(0.4, 0.7)
        }
    
    def generate_benchmark_report(self, benchmark_name: str, period: str = '1Y') -> Dict[str, Any]:
        """Generate benchmark analysis report"""
        try:
            # Placeholder implementation
            # In production, this would analyze actual benchmark data
            
            return {
                'benchmark_name': benchmark_name,
                'period': period,
                'total_return': 0.15,
                'volatility': 0.18,
                'sharpe_ratio': 1.2,
                'max_drawdown': -0.12,
                'correlation_with_portfolio': 0.75,
                'analysis': f"Benchmark {benchmark_name} analysis for {period} period"
            }
            
        except Exception as e:
            logger.error(f"Error generating benchmark report: {e}")
            return {'error': str(e)}
    
    def export_report(self, report_id: str, format: str = 'pdf') -> str:
        """Export report in specified format"""
        try:
            # Find report
            report = None
            for r in self.reports_history:
                if str(r.timestamp.timestamp()) == report_id:
                    report = r
                    break
            
            if not report:
                return "Report not found"
            
            # Export based on format
            if format == 'pdf':
                return self._export_to_pdf(report)
            elif format == 'excel':
                return self._export_to_excel(report)
            elif format == 'html':
                return self._export_to_html(report)
            else:
                return f"Unsupported format: {format}"
                
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return f"Export failed: {e}"
    
    def _export_to_pdf(self, report: AnalyticsReport) -> str:
        """Export report to PDF"""
        # Placeholder implementation
        return "PDF export not implemented yet"
    
    def _export_to_excel(self, report: AnalyticsReport) -> str:
        """Export report to Excel"""
        # Placeholder implementation
        return "Excel export not implemented yet"
    
    def _export_to_html(self, report: AnalyticsReport) -> str:
        """Export report to HTML"""
        try:
            # Create HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AutoPPM Analytics Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #1f77b4; color: white; padding: 20px; text-align: center; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 3px; }}
                    .chart {{ text-align: center; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>AutoPPM Analytics Report</h1>
                    <p>Generated on {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Period: {report.period}</p>
                </div>
                
                <div class="section">
                    <h2>Performance Metrics</h2>
                    <div class="metric">
                        <strong>Total Return:</strong> {report.performance_metrics.total_return:.2%}
                    </div>
                    <div class="metric">
                        <strong>Sharpe Ratio:</strong> {report.performance_metrics.sharpe_ratio:.2f}
                    </div>
                    <div class="metric">
                        <strong>Max Drawdown:</strong> {report.performance_metrics.max_drawdown:.2%}
                    </div>
                    <div class="metric">
                        <strong>Win Rate:</strong> {report.performance_metrics.win_rate:.2%}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Risk Metrics</h2>
                    <div class="metric">
                        <strong>VaR (95%):</strong> {report.risk_metrics.var_95:.2%}
                    </div>
                    <div class="metric">
                        <strong>Beta:</strong> {report.risk_metrics.beta:.2f}
                    </div>
                    <div class="metric">
                        <strong>Volatility:</strong> {report.performance_metrics.volatility:.2%}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Charts</h2>
                    {''.join([f'<div class="chart"><img src="{chart_path}" alt="{chart_name}" style="max-width: 100%; height: auto;"></div>' for chart_name, chart_path in report.charts.items()])}
                </div>
            </body>
            </html>
            """
            
            # Save HTML file
            html_file = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            return str(html_file)
            
        except Exception as e:
            logger.error(f"Error exporting to HTML: {e}")
            return f"HTML export failed: {e}"


# Global instance
_advanced_analytics_engine: Optional[AdvancedAnalyticsEngine] = None


def get_advanced_analytics_engine() -> AdvancedAnalyticsEngine:
    """Get global advanced analytics engine instance"""
    global _advanced_analytics_engine
    if _advanced_analytics_engine is None:
        _advanced_analytics_engine = AdvancedAnalyticsEngine()
    return _advanced_analytics_engine

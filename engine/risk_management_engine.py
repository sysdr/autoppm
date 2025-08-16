"""
AutoPPM Risk Management Engine
Comprehensive risk management for trading strategies
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from models.strategy import StrategySignal
from models.market_data import MarketData, HistoricalData
from database.connection import get_database_session


@dataclass
class PositionRisk:
    """Risk metrics for a single position"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    risk_pct: float
    position_size_pct: float
    beta: float
    volatility: float
    var_95: float  # 95% Value at Risk


@dataclass
class PortfolioRisk:
    """Overall portfolio risk metrics"""
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    total_risk: float
    total_risk_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    var_95: float
    expected_shortfall: float
    sector_exposure: Dict[str, float]
    concentration_risk: float
    correlation_matrix: pd.DataFrame
    risk_metrics: Dict[str, float]


@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_position_size: float = 0.1  # 10% max position
    max_sector_exposure: float = 0.3  # 30% max sector exposure
    max_portfolio_risk: float = 0.02  # 2% max portfolio risk
    stop_loss_pct: float = 0.05  # 5% stop loss
    take_profit_pct: float = 0.15  # 15% take profit
    max_drawdown_limit: float = 0.15  # 15% max drawdown
    var_limit: float = 0.02  # 2% VaR limit
    position_sizing_method: str = "kelly"  # kelly, fixed, optimal
    risk_free_rate: float = 0.05  # 5% risk-free rate


class RiskManagementEngine:
    """Engine for managing trading risk"""
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.risk_alerts: List[Dict[str, Any]] = []
    
    async def calculate_position_size(self, signal: StrategySignal, portfolio_value: float, 
                                   risk_params: Dict[str, Any]) -> float:
        """Calculate optimal position size based on risk parameters"""
        try:
            if self.config.position_sizing_method == "kelly":
                return await self._kelly_position_sizing(signal, portfolio_value, risk_params)
            elif self.config.position_sizing_method == "optimal":
                return await self._optimal_position_sizing(signal, portfolio_value, risk_params)
            else:
                return await self._fixed_position_sizing(signal, portfolio_value, risk_params)
                
        except Exception as e:
            logger.error(f"Failed to calculate position size: {e}")
            return 0.0
    
    async def _kelly_position_sizing(self, signal: StrategySignal, portfolio_value: float, 
                                   risk_params: Dict[str, Any]) -> float:
        """Kelly Criterion position sizing"""
        try:
            # Get historical data for win rate and average win/loss
            win_rate = risk_params.get('win_rate', 0.5)
            avg_win = risk_params.get('avg_win', 0.1)
            avg_loss = risk_params.get('avg_loss', 0.05)
            
            if avg_loss <= 0:
                return 0.0
            
            # Kelly formula: f = (bp - q) / b
            # where b = odds received, p = probability of win, q = probability of loss
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # Apply constraints
            kelly_fraction = max(0, min(kelly_fraction, self.config.max_position_size))
            
            # Calculate position size
            position_value = portfolio_value * kelly_fraction
            position_size = position_value / signal.price
            
            logger.info(f"Kelly position size: {position_size:.2f} shares (fraction: {kelly_fraction:.4f})")
            return position_size
            
        except Exception as e:
            logger.error(f"Kelly position sizing failed: {e}")
            return 0.0
    
    async def _optimal_position_sizing(self, signal: StrategySignal, portfolio_value: float, 
                                     risk_params: Dict[str, Any]) -> float:
        """Optimal position sizing based on risk-return optimization"""
        try:
            # Get volatility and expected return
            volatility = risk_params.get('volatility', 0.2)
            expected_return = risk_params.get('expected_return', 0.1)
            risk_free_rate = self.config.risk_free_rate
            
            if volatility <= 0:
                return 0.0
            
            # Sharpe ratio optimization
            sharpe_ratio = (expected_return - risk_free_rate) / volatility
            
            # Position size based on Sharpe ratio and volatility
            optimal_fraction = min(
                sharpe_ratio / (2 * volatility),  # Optimal fraction
                self.config.max_position_size  # Max constraint
            )
            
            optimal_fraction = max(0, optimal_fraction)
            
            # Calculate position size
            position_value = portfolio_value * optimal_fraction
            position_size = position_value / signal.price
            
            logger.info(f"Optimal position size: {position_size:.2f} shares (fraction: {optimal_fraction:.4f})")
            return position_size
            
        except Exception as e:
            logger.error(f"Optimal position sizing failed: {e}")
            return 0.0
    
    async def _fixed_position_sizing(self, signal: StrategySignal, portfolio_value: float, 
                                   risk_params: Dict[str, Any]) -> float:
        """Fixed percentage position sizing"""
        try:
            # Use fixed percentage of portfolio
            position_fraction = risk_params.get('position_fraction', 0.02)  # 2% default
            
            # Apply max constraint
            position_fraction = min(position_fraction, self.config.max_position_size)
            
            # Calculate position size
            position_value = portfolio_value * position_fraction
            position_size = position_value / signal.price
            
            logger.info(f"Fixed position size: {position_size:.2f} shares (fraction: {position_fraction:.4f})")
            return position_size
            
        except Exception as e:
            logger.error(f"Fixed position sizing failed: {e}")
            return 0.0
    
    async def calculate_stop_loss(self, entry_price: float, signal: StrategySignal, 
                                risk_params: Dict[str, Any]) -> float:
        """Calculate dynamic stop-loss level"""
        try:
            # Get volatility-based stop loss
            volatility = risk_params.get('volatility', 0.2)
            atr_multiplier = risk_params.get('atr_multiplier', 2.0)
            
            # ATR-based stop loss (if available)
            if 'atr' in risk_params:
                atr = risk_params['atr']
                stop_loss = entry_price - (atr * atr_multiplier)
            else:
                # Volatility-based stop loss
                stop_loss = entry_price * (1 - volatility * atr_multiplier)
            
            # Apply percentage-based minimum
            min_stop_loss = entry_price * (1 - self.config.stop_loss_pct)
            stop_loss = max(stop_loss, min_stop_loss)
            
            logger.info(f"Stop loss calculated: {stop_loss:.2f} for entry {entry_price:.2f}")
            return stop_loss
            
        except Exception as e:
            logger.error(f"Stop loss calculation failed: {e}")
            return entry_price * (1 - self.config.stop_loss_pct)
    
    async def calculate_take_profit(self, entry_price: float, signal: StrategySignal, 
                                  risk_params: Dict[str, Any]) -> float:
        """Calculate take-profit level"""
        try:
            # Risk-reward ratio based take profit
            risk_reward_ratio = risk_params.get('risk_reward_ratio', 3.0)
            
            # Calculate risk amount
            stop_loss = await self.calculate_stop_loss(entry_price, signal, risk_params)
            risk_amount = entry_price - stop_loss
            
            # Calculate take profit
            take_profit = entry_price + (risk_amount * risk_reward_ratio)
            
            # Apply percentage-based maximum
            max_take_profit = entry_price * (1 + self.config.take_profit_pct)
            take_profit = min(take_profit, max_take_profit)
            
            logger.info(f"Take profit calculated: {take_profit:.2f} for entry {entry_price:.2f}")
            return take_profit
            
        except Exception as e:
            logger.error(f"Take profit calculation failed: {e}")
            return entry_price * (1 + self.config.take_profit_pct)
    
    async def calculate_position_risk(self, symbol: str, quantity: float, entry_price: float, 
                                    current_price: float, portfolio_value: float) -> PositionRisk:
        """Calculate risk metrics for a single position"""
        try:
            # Basic calculations
            market_value = quantity * current_price
            unrealized_pnl = (current_price - entry_price) * quantity
            unrealized_pnl_pct = (unrealized_pnl / (entry_price * quantity)) * 100
            position_size_pct = (market_value / portfolio_value) * 100
            
            # Risk amount
            risk_amount = abs(unrealized_pnl) if unrealized_pnl < 0 else 0
            risk_pct = (risk_amount / portfolio_value) * 100
            
            # Get volatility and beta
            volatility = await self._calculate_volatility(symbol)
            beta = await self._calculate_beta(symbol)
            
            # Calculate VaR
            var_95 = await self._calculate_var(symbol, market_value, volatility)
            
            # Stop loss and take profit
            stop_loss = entry_price * (1 - self.config.stop_loss_pct)
            take_profit = entry_price * (1 + self.config.take_profit_pct)
            
            return PositionRisk(
                symbol=symbol,
                quantity=quantity,
                entry_price=entry_price,
                current_price=current_price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                risk_pct=risk_pct,
                position_size_pct=position_size_pct,
                beta=beta,
                volatility=volatility,
                var_95=var_95
            )
            
        except Exception as e:
            logger.error(f"Position risk calculation failed for {symbol}: {e}")
            return None
    
    async def calculate_portfolio_risk(self, positions: List[PositionRisk], 
                                    portfolio_value: float) -> PortfolioRisk:
        """Calculate overall portfolio risk metrics"""
        try:
            if not positions:
                return PortfolioRisk(
                    total_value=portfolio_value,
                    total_pnl=0,
                    total_pnl_pct=0,
                    total_risk=0,
                    total_risk_pct=0,
                    max_drawdown=0,
                    max_drawdown_pct=0,
                    sharpe_ratio=0,
                    var_95=0,
                    expected_shortfall=0,
                    sector_exposure={},
                    concentration_risk=0,
                    correlation_matrix=pd.DataFrame(),
                    risk_metrics={}
                )
            
            # Calculate totals
            total_pnl = sum(pos.unrealized_pnl for pos in positions)
            total_pnl_pct = (total_pnl / portfolio_value) * 100
            total_risk = sum(pos.risk_amount for pos in positions)
            total_risk_pct = (total_risk / portfolio_value) * 100
            
            # Calculate sector exposure
            sector_exposure = await self._calculate_sector_exposure(positions)
            
            # Calculate concentration risk
            concentration_risk = await self._calculate_concentration_risk(positions, portfolio_value)
            
            # Calculate correlation matrix
            correlation_matrix = await self._calculate_correlation_matrix(positions)
            
            # Calculate VaR
            var_95 = await self._calculate_portfolio_var(positions, portfolio_value)
            
            # Calculate expected shortfall
            expected_shortfall = await self._calculate_expected_shortfall(positions, portfolio_value)
            
            # Calculate Sharpe ratio
            sharpe_ratio = await self._calculate_portfolio_sharpe(positions, portfolio_value)
            
            # Calculate max drawdown
            max_drawdown, max_drawdown_pct = await self._calculate_max_drawdown(positions, portfolio_value)
            
            # Additional risk metrics
            risk_metrics = {
                'sortino_ratio': await self._calculate_sortino_ratio(positions, portfolio_value),
                'calmar_ratio': await self._calculate_calmar_ratio(positions, portfolio_value),
                'information_ratio': await self._calculate_information_ratio(positions, portfolio_value),
                'treynor_ratio': await self._calculate_treynor_ratio(positions, portfolio_value)
            }
            
            return PortfolioRisk(
                total_value=portfolio_value,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                total_risk=total_risk,
                total_risk_pct=total_risk_pct,
                max_drawdown=max_drawdown,
                max_drawdown_pct=max_drawdown_pct,
                sharpe_ratio=sharpe_ratio,
                var_95=var_95,
                expected_shortfall=expected_shortfall,
                sector_exposure=sector_exposure,
                concentration_risk=concentration_risk,
                correlation_matrix=correlation_matrix,
                risk_metrics=risk_metrics
            )
            
        except Exception as e:
            logger.error(f"Portfolio risk calculation failed: {e}")
            return None
    
    async def check_risk_limits(self, portfolio_risk: PortfolioRisk) -> List[Dict[str, Any]]:
        """Check if portfolio violates risk limits"""
        alerts = []
        
        try:
            # Check position size limits
            if portfolio_risk.concentration_risk > self.config.max_position_size:
                alerts.append({
                    'type': 'concentration_risk',
                    'severity': 'high',
                    'message': f'Portfolio concentration risk {portfolio_risk.concentration_risk:.2%} exceeds limit {self.config.max_position_size:.2%}',
                    'timestamp': datetime.utcnow()
                })
            
            # Check VaR limits
            if portfolio_risk.var_95 > self.config.var_limit:
                alerts.append({
                    'type': 'var_limit',
                    'severity': 'high',
                    'message': f'Portfolio VaR {portfolio_risk.var_95:.2%} exceeds limit {self.config.var_limit:.2%}',
                    'timestamp': datetime.utcnow()
                })
            
            # Check drawdown limits
            if portfolio_risk.max_drawdown_pct > self.config.max_drawdown_limit:
                alerts.append({
                    'type': 'drawdown_limit',
                    'severity': 'critical',
                    'message': f'Portfolio drawdown {portfolio_risk.max_drawdown_pct:.2%} exceeds limit {self.config.max_drawdown_limit:.2%}',
                    'timestamp': datetime.utcnow()
                })
            
            # Check sector exposure limits
            for sector, exposure in portfolio_risk.sector_exposure.items():
                if exposure > self.config.max_sector_exposure:
                    alerts.append({
                        'type': 'sector_exposure',
                        'severity': 'medium',
                        'message': f'Sector {sector} exposure {exposure:.2%} exceeds limit {self.config.max_sector_exposure:.2%}',
                        'timestamp': datetime.utcnow()
                    })
            
            # Store alerts
            self.risk_alerts.extend(alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Risk limit check failed: {e}")
            return []
    
    async def _calculate_volatility(self, symbol: str, window: int = 252) -> float:
        """Calculate historical volatility for a symbol"""
        try:
            session = next(get_database_session())
            
            # Get historical data
            query = session.query(HistoricalData).filter(
                HistoricalData.symbol == symbol
            ).order_by(HistoricalData.date.desc()).limit(window)
            
            records = query.all()
            session.close()
            
            if len(records) < 2:
                return 0.2  # Default volatility
            
            # Calculate returns
            prices = [record.close_price for record in reversed(records)]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            
            # Calculate volatility (annualized)
            volatility = np.std(returns) * np.sqrt(252)
            return volatility
            
        except Exception as e:
            logger.error(f"Volatility calculation failed for {symbol}: {e}")
            return 0.2
    
    async def _calculate_beta(self, symbol: str, market_symbol: str = "NIFTY", window: int = 252) -> float:
        """Calculate beta relative to market index"""
        try:
            session = next(get_database_session())
            
            # Get symbol and market data
            symbol_query = session.query(HistoricalData).filter(
                HistoricalData.symbol == symbol
            ).order_by(HistoricalData.date.desc()).limit(window)
            
            market_query = session.query(HistoricalData).filter(
                HistoricalData.symbol == market_symbol
            ).order_by(HistoricalData.date.desc()).limit(window)
            
            symbol_records = symbol_query.all()
            market_records = market_query.all()
            session.close()
            
            if len(symbol_records) < 2 or len(market_records) < 2:
                return 1.0  # Default beta
            
            # Calculate returns
            symbol_prices = [record.close_price for record in reversed(symbol_records)]
            market_prices = [record.close_price for record in reversed(market_records)]
            
            symbol_returns = [(symbol_prices[i] - symbol_prices[i-1]) / symbol_prices[i-1] 
                            for i in range(1, len(symbol_prices))]
            market_returns = [(market_prices[i] - market_prices[i-1]) / market_prices[i-1] 
                            for i in range(1, len(market_prices))]
            
            # Calculate beta
            if len(symbol_returns) == len(market_returns) and len(symbol_returns) > 1:
                covariance = np.cov(symbol_returns, market_returns)[0, 1]
                market_variance = np.var(market_returns)
                beta = covariance / market_variance if market_variance > 0 else 1.0
                return beta
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Beta calculation failed for {symbol}: {e}")
            return 1.0
    
    async def _calculate_var(self, symbol: str, position_value: float, volatility: float, 
                           confidence: float = 0.95) -> float:
        """Calculate Value at Risk for a position"""
        try:
            # Parametric VaR calculation
            z_score = 1.645 if confidence == 0.95 else 2.326  # 95% or 99% confidence
            var = position_value * volatility * z_score / np.sqrt(252)
            return var
            
        except Exception as e:
            logger.error(f"VaR calculation failed for {symbol}: {e}")
            return position_value * 0.02  # 2% default
    
    async def _calculate_sector_exposure(self, positions: List[PositionRisk]) -> Dict[str, float]:
        """Calculate sector exposure for portfolio"""
        try:
            # This would integrate with actual sector data
            # For now, return placeholder
            return {"Technology": 0.3, "Finance": 0.25, "Healthcare": 0.2, "Others": 0.25}
            
        except Exception as e:
            logger.error(f"Sector exposure calculation failed: {e}")
            return {}
    
    async def _calculate_concentration_risk(self, positions: List[PositionRisk], 
                                          portfolio_value: float) -> float:
        """Calculate portfolio concentration risk"""
        try:
            if not positions:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index
            hhi = sum((pos.market_value / portfolio_value) ** 2 for pos in positions)
            
            # Normalize to 0-1 scale
            concentration_risk = (hhi - 1/len(positions)) / (1 - 1/len(positions)) if len(positions) > 1 else 0
            
            return concentration_risk
            
        except Exception as e:
            logger.error(f"Concentration risk calculation failed: {e}")
            return 0.0
    
    async def _calculate_correlation_matrix(self, positions: List[PositionRisk]) -> pd.DataFrame:
        """Calculate correlation matrix for portfolio positions"""
        try:
            if len(positions) < 2:
                return pd.DataFrame()
            
            # This would calculate actual correlations from historical data
            # For now, return identity matrix
            symbols = [pos.symbol for pos in positions]
            correlation_matrix = pd.DataFrame(
                np.eye(len(symbols)), 
                index=symbols, 
                columns=symbols
            )
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Correlation matrix calculation failed: {e}")
            return pd.DataFrame()
    
    async def _calculate_portfolio_var(self, positions: List[PositionRisk], 
                                     portfolio_value: float) -> float:
        """Calculate portfolio-level VaR"""
        try:
            if not positions:
                return 0.0
            
            # Simple sum of individual VaRs (would be more sophisticated in practice)
            portfolio_var = sum(pos.var_95 for pos in positions)
            
            return portfolio_var
            
        except Exception as e:
            logger.error(f"Portfolio VaR calculation failed: {e}")
            return 0.0
    
    async def _calculate_expected_shortfall(self, positions: List[PositionRisk], 
                                           portfolio_value: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        try:
            # Expected shortfall is typically 1.25-1.5x VaR
            portfolio_var = await self._calculate_portfolio_var(positions, portfolio_value)
            expected_shortfall = portfolio_var * 1.25
            
            return expected_shortfall
            
        except Exception as e:
            logger.error(f"Expected shortfall calculation failed: {e}")
            return 0.0
    
    async def _calculate_portfolio_sharpe(self, positions: List[PositionRisk], 
                                        portfolio_value: float) -> float:
        """Calculate portfolio Sharpe ratio"""
        try:
            if not positions:
                return 0.0
            
            # Calculate weighted average return and risk
            total_return = sum(pos.unrealized_pnl_pct * (pos.market_value / portfolio_value) 
                             for pos in positions)
            total_risk = sum(pos.volatility * (pos.market_value / portfolio_value) 
                           for pos in positions)
            
            if total_risk > 0:
                sharpe_ratio = (total_return - self.config.risk_free_rate) / total_risk
                return sharpe_ratio
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Portfolio Sharpe ratio calculation failed: {e}")
            return 0.0
    
    async def _calculate_max_drawdown(self, positions: List[PositionRisk], 
                                    portfolio_value: float) -> Tuple[float, float]:
        """Calculate maximum drawdown"""
        try:
            if not positions:
                return 0.0, 0.0
            
            # This would calculate actual drawdown from historical data
            # For now, return placeholder values
            max_drawdown = 0.05  # 5% placeholder
            max_drawdown_pct = 5.0
            
            return max_drawdown, max_drawdown_pct
            
        except Exception as e:
            logger.error(f"Max drawdown calculation failed: {e}")
            return 0.0, 0.0
    
    async def _calculate_sortino_ratio(self, positions: List[PositionRisk], 
                                     portfolio_value: float) -> float:
        """Calculate Sortino ratio"""
        try:
            # Similar to Sharpe but only considers downside risk
            return await self._calculate_portfolio_sharpe(positions, portfolio_value) * 0.8
            
        except Exception as e:
            logger.error(f"Sortino ratio calculation failed: {e}")
            return 0.0
    
    async def _calculate_calmar_ratio(self, positions: List[PositionRisk], 
                                    portfolio_value: float) -> float:
        """Calculate Calmar ratio"""
        try:
            max_drawdown, max_drawdown_pct = await self._calculate_max_drawdown(positions, portfolio_value)
            
            if max_drawdown_pct > 0:
                total_return = sum(pos.unrealized_pnl_pct * (pos.market_value / portfolio_value) 
                                 for pos in positions)
                calmar_ratio = total_return / max_drawdown_pct
                return calmar_ratio
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Calmar ratio calculation failed: {e}")
            return 0.0
    
    async def _calculate_information_ratio(self, positions: List[PositionRisk], 
                                         portfolio_value: float) -> float:
        """Calculate Information ratio"""
        try:
            # Information ratio = (Portfolio Return - Benchmark Return) / Tracking Error
            # For now, return placeholder
            return 0.5
            
        except Exception as e:
            logger.error(f"Information ratio calculation failed: {e}")
            return 0.0
    
    async def _calculate_treynor_ratio(self, positions: List[PositionRisk], 
                                     portfolio_value: float) -> float:
        """Calculate Treynor ratio"""
        try:
            # Treynor ratio = (Portfolio Return - Risk Free Rate) / Beta
            portfolio_return = sum(pos.unrealized_pnl_pct * (pos.market_value / portfolio_value) 
                                 for pos in positions)
            portfolio_beta = sum(pos.beta * (pos.market_value / portfolio_value) 
                               for pos in positions)
            
            if portfolio_beta > 0:
                treynor_ratio = (portfolio_return - self.config.risk_free_rate) / portfolio_beta
                return treynor_ratio
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Treynor ratio calculation failed: {e}")
            return 0.0
    
    def get_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get all risk alerts"""
        return self.risk_alerts.copy()
    
    def clear_risk_alerts(self):
        """Clear risk alerts"""
        self.risk_alerts.clear()


# Global risk management engine instance
risk_management_engine = RiskManagementEngine()


def get_risk_management_engine() -> RiskManagementEngine:
    """Get the global risk management engine instance"""
    return risk_management_engine

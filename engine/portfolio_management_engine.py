"""
AutoPPM Portfolio Management Engine
Comprehensive portfolio management and optimization system
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from models.market_data import MarketData, HistoricalData
from engine.risk_management_engine import PositionRisk, PortfolioRisk, get_risk_management_engine
from engine.order_management_engine import get_order_management_engine
from database.connection import get_database_session


class RebalancingType(Enum):
    """Rebalancing types"""
    TIME_BASED = "TIME_BASED"  # Daily, weekly, monthly
    THRESHOLD_BASED = "THRESHOLD_BASED"  # When deviation exceeds threshold
    RISK_BASED = "RISK_BASED"  # When risk metrics exceed limits
    PERFORMANCE_BASED = "PERFORMANCE_BASED"  # Based on performance


class OptimizationMethod(Enum):
    """Portfolio optimization methods"""
    EQUAL_WEIGHT = "EQUAL_WEIGHT"
    MARKET_CAP_WEIGHT = "MARKET_CAP_WEIGHT"
    RISK_PARITY = "RISK_PARITY"
    BLACK_LITTERMAN = "BLACK_LITTERMAN"
    MEAN_VARIANCE = "MEAN_VARIANCE"
    MAX_SHARPE = "MAX_SHARPE"
    MIN_VARIANCE = "MIN_VARIANCE"


@dataclass
class PortfolioPosition:
    """Portfolio position details"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    weight: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    sector: str
    beta: float
    volatility: float
    last_updated: datetime


@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot at a point in time"""
    timestamp: datetime
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    cash: float
    positions: List[PortfolioPosition]
    risk_metrics: PortfolioRisk
    performance_metrics: Dict[str, float]


@dataclass
class RebalancingTarget:
    """Target weights for rebalancing"""
    symbol: str
    target_weight: float
    current_weight: float
    deviation: float
    required_action: str  # BUY, SELL, HOLD
    quantity_change: float
    estimated_cost: float


@dataclass
class PortfolioConfig:
    """Portfolio configuration"""
    target_weights: Dict[str, float]
    rebalancing_frequency: str = "monthly"
    rebalancing_threshold: float = 0.05  # 5% deviation threshold
    max_position_size: float = 0.1  # 10% max position
    max_sector_exposure: float = 0.3  # 30% max sector
    cash_buffer: float = 0.05  # 5% cash buffer
    optimization_method: OptimizationMethod = OptimizationMethod.RISK_PARITY
    risk_free_rate: float = 0.05  # 5% risk-free rate


class PortfolioManagementEngine:
    """Engine for managing portfolio optimization and rebalancing"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig(target_weights={})
        self.risk_engine = get_risk_management_engine()
        self.order_engine = get_order_management_engine()
        self.portfolio_history: List[PortfolioSnapshot] = []
        self.last_rebalancing: Optional[datetime] = None
        self.is_auto_rebalancing = True
    
    async def get_current_portfolio(self) -> PortfolioSnapshot:
        """Get current portfolio snapshot"""
        try:
            # This would integrate with actual portfolio data
            # For now, return a placeholder snapshot
            
            positions = [
                PortfolioPosition(
                    symbol="RELIANCE",
                    quantity=100,
                    entry_price=2500.0,
                    current_price=2600.0,
                    market_value=260000.0,
                    weight=0.3,
                    unrealized_pnl=10000.0,
                    unrealized_pnl_pct=4.0,
                    sector="Energy",
                    beta=1.1,
                    volatility=0.25,
                    last_updated=datetime.utcnow()
                ),
                PortfolioPosition(
                    symbol="TCS",
                    quantity=200,
                    entry_price=3500.0,
                    current_price=3600.0,
                    market_value=720000.0,
                    weight=0.4,
                    unrealized_pnl=20000.0,
                    unrealized_pnl_pct=2.86,
                    sector="Technology",
                    beta=0.9,
                    volatility=0.22,
                    last_updated=datetime.utcnow()
                )
            ]
            
            total_value = sum(pos.market_value for pos in positions) + 100000  # Cash
            total_pnl = sum(pos.unrealized_pnl for pos in positions)
            total_pnl_pct = (total_pnl / (total_value - total_pnl)) * 100 if total_value > total_pnl else 0
            
            # Calculate risk metrics
            risk_metrics = await self.risk_engine.calculate_portfolio_risk(
                [await self._convert_to_position_risk(pos) for pos in positions],
                total_value
            )
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(positions, total_value)
            
            snapshot = PortfolioSnapshot(
                timestamp=datetime.utcnow(),
                total_value=total_value,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                cash=100000.0,
                positions=positions,
                risk_metrics=risk_metrics,
                performance_metrics=performance_metrics
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to get current portfolio: {e}")
            return None
    
    async def optimize_portfolio(self, method: OptimizationMethod = None, 
                               constraints: Dict[str, Any] = None) -> Dict[str, float]:
        """Optimize portfolio weights using specified method"""
        try:
            method = method or self.config.optimization_method
            constraints = constraints or {}
            
            if method == OptimizationMethod.EQUAL_WEIGHT:
                return await self._equal_weight_optimization()
            elif method == OptimizationMethod.RISK_PARITY:
                return await self._risk_parity_optimization()
            elif method == OptimizationMethod.MAX_SHARPE:
                return await self._max_sharpe_optimization()
            elif method == OptimizationMethod.MIN_VARIANCE:
                return await self._min_variance_optimization()
            else:
                logger.warning(f"Optimization method {method.value} not implemented, using equal weight")
                return await self._equal_weight_optimization()
                
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            return {}
    
    async def _equal_weight_optimization(self) -> Dict[str, float]:
        """Equal weight optimization"""
        try:
            current_portfolio = await self.get_current_portfolio()
            if not current_portfolio or not current_portfolio.positions:
                return {}
            
            # Equal weights for all positions
            num_positions = len(current_portfolio.positions)
            equal_weight = 1.0 / num_positions
            
            target_weights = {}
            for position in current_portfolio.positions:
                target_weights[position.symbol] = equal_weight
            
            return target_weights
            
        except Exception as e:
            logger.error(f"Equal weight optimization failed: {e}")
            return {}
    
    async def _risk_parity_optimization(self) -> Dict[str, float]:
        """Risk parity optimization"""
        try:
            current_portfolio = await self.get_current_portfolio()
            if not current_portfolio or not current_portfolio.positions:
                return {}
            
            # Calculate risk contribution for each position
            positions = current_portfolio.positions
            total_value = current_portfolio.total_value
            
            # Get correlation matrix
            correlation_matrix = current_portfolio.risk_metrics.correlation_matrix
            
            # Calculate risk contribution
            risk_contributions = {}
            for position in positions:
                # Simplified risk contribution calculation
                risk_contrib = position.volatility * position.weight
                risk_contributions[position.symbol] = risk_contrib
            
            # Target equal risk contribution
            target_risk_contrib = sum(risk_contributions.values()) / len(risk_contributions)
            
            # Calculate target weights
            target_weights = {}
            for position in positions:
                target_weight = target_risk_contrib / position.volatility
                target_weights[position.symbol] = min(target_weight, self.config.max_position_size)
            
            # Normalize weights
            total_weight = sum(target_weights.values())
            if total_weight > 0:
                for symbol in target_weights:
                    target_weights[symbol] /= total_weight
            
            return target_weights
            
        except Exception as e:
            logger.error(f"Risk parity optimization failed: {e}")
            return {}
    
    async def _max_sharpe_optimization(self) -> Dict[str, float]:
        """Maximum Sharpe ratio optimization"""
        try:
            current_portfolio = await self.get_current_portfolio()
            if not current_portfolio or not current_portfolio.positions:
                return {}
            
            # This would implement mean-variance optimization
            # For now, return equal weights
            return await self._equal_weight_optimization()
            
        except Exception as e:
            logger.error(f"Max Sharpe optimization failed: {e}")
            return {}
    
    async def _min_variance_optimization(self) -> Dict[str, float]:
        """Minimum variance optimization"""
        try:
            current_portfolio = await self.get_current_portfolio()
            if not current_portfolio or not current_portfolio.positions:
                return {}
            
            # This would implement minimum variance optimization
            # For now, return equal weights
            return await self._equal_weight_optimization()
            
        except Exception as e:
            logger.error(f"Min variance optimization failed: {e}")
            return {}
    
    async def check_rebalancing_needed(self, portfolio: PortfolioSnapshot) -> Tuple[bool, List[RebalancingTarget]]:
        """Check if portfolio rebalancing is needed"""
        try:
            rebalancing_targets = []
            rebalancing_needed = False
            
            # Get current weights
            current_weights = {pos.symbol: pos.weight for pos in portfolio.positions}
            
            # Check against target weights
            for symbol, target_weight in self.config.target_weights.items():
                current_weight = current_weights.get(symbol, 0.0)
                deviation = abs(target_weight - current_weight)
                
                if deviation > self.config.rebalancing_threshold:
                    rebalancing_needed = True
                    
                    # Calculate required action
                    if target_weight > current_weight:
                        action = "BUY"
                        quantity_change = (target_weight - current_weight) * portfolio.total_value / portfolio.positions[0].current_price
                    else:
                        action = "SELL"
                        quantity_change = (current_weight - target_weight) * portfolio.total_value / portfolio.positions[0].current_price
                    
                    # Find position for current price
                    position = next((pos for pos in portfolio.positions if pos.symbol == symbol), None)
                    current_price = position.current_price if position else 100.0
                    
                    rebalancing_target = RebalancingTarget(
                        symbol=symbol,
                        target_weight=target_weight,
                        current_weight=current_weight,
                        deviation=deviation,
                        required_action=action,
                        quantity_change=abs(quantity_change),
                        estimated_cost=abs(quantity_change) * current_price
                    )
                    
                    rebalancing_targets.append(rebalancing_target)
            
            # Check time-based rebalancing
            if self.config.rebalancing_frequency == "monthly":
                if not self.last_rebalancing or (datetime.utcnow() - self.last_rebalancing).days > 30:
                    rebalancing_needed = True
            
            return rebalancing_needed, rebalancing_targets
            
        except Exception as e:
            logger.error(f"Failed to check rebalancing needs: {e}")
            return False, []
    
    async def rebalance_portfolio(self, rebalancing_targets: List[RebalancingTarget]) -> bool:
        """Rebalance portfolio according to targets"""
        try:
            logger.info(f"Starting portfolio rebalancing with {len(rebalancing_targets)} targets")
            
            success_count = 0
            total_targets = len(rebalancing_targets)
            
            for target in rebalancing_targets:
                try:
                    # Execute rebalancing order
                    success = await self._execute_rebalancing_order(target)
                    if success:
                        success_count += 1
                        logger.info(f"Rebalancing order executed for {target.symbol}: {target.required_action}")
                    else:
                        logger.error(f"Rebalancing order failed for {target.symbol}")
                        
                except Exception as e:
                    logger.error(f"Failed to execute rebalancing for {target.symbol}: {e}")
            
            # Update last rebalancing time
            if success_count > 0:
                self.last_rebalancing = datetime.utcnow()
                logger.info(f"Portfolio rebalancing completed: {success_count}/{total_targets} successful")
                return True
            else:
                logger.warning("No rebalancing orders were successful")
                return False
                
        except Exception as e:
            logger.error(f"Portfolio rebalancing failed: {e}")
            return False
    
    async def _execute_rebalancing_order(self, target: RebalancingTarget) -> bool:
        """Execute a single rebalancing order"""
        try:
            # This would integrate with the order management engine
            # For now, return success
            logger.info(f"Executing rebalancing order: {target.required_action} {target.quantity_change} {target.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute rebalancing order: {e}")
            return False
    
    async def calculate_portfolio_performance(self, start_date: datetime, 
                                           end_date: datetime) -> Dict[str, Any]:
        """Calculate portfolio performance over a period"""
        try:
            # This would calculate actual performance from historical data
            # For now, return placeholder metrics
            
            performance_metrics = {
                'total_return': 0.15,  # 15%
                'annualized_return': 0.18,  # 18%
                'volatility': 0.22,  # 22%
                'sharpe_ratio': 0.82,
                'sortino_ratio': 1.2,
                'max_drawdown': 0.08,  # 8%
                'calmar_ratio': 2.25,
                'win_rate': 0.65,  # 65%
                'profit_factor': 1.8,
                'total_trades': 45,
                'avg_trade_duration': 5.2,  # days
                'best_trade': 0.12,  # 12%
                'worst_trade': -0.06,  # -6%
                'consecutive_wins': 8,
                'consecutive_losses': 3
            }
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio performance: {e}")
            return {}
    
    async def _calculate_performance_metrics(self, positions: List[PortfolioPosition], 
                                           total_value: float) -> Dict[str, float]:
        """Calculate basic performance metrics"""
        try:
            if not positions:
                return {}
            
            # Basic metrics
            total_pnl = sum(pos.unrealized_pnl for pos in positions)
            total_pnl_pct = (total_pnl / (total_value - total_pnl)) * 100 if total_value > total_pnl else 0
            
            # Weighted metrics
            weighted_return = sum(pos.unrealized_pnl_pct * pos.weight for pos in positions)
            weighted_volatility = sum(pos.volatility * pos.weight for pos in positions)
            weighted_beta = sum(pos.beta * pos.weight for pos in positions)
            
            # Sector diversification
            sector_weights = {}
            for pos in positions:
                if pos.sector not in sector_weights:
                    sector_weights[pos.sector] = 0
                sector_weights[pos.sector] += pos.weight
            
            sector_concentration = max(sector_weights.values()) if sector_weights else 0
            
            return {
                'total_return_pct': total_pnl_pct,
                'weighted_return': weighted_return,
                'weighted_volatility': weighted_volatility,
                'weighted_beta': weighted_beta,
                'sector_concentration': sector_concentration,
                'num_positions': len(positions),
                'avg_position_size': total_value / len(positions) if positions else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {}
    
    async def _convert_to_position_risk(self, position: PortfolioPosition) -> PositionRisk:
        """Convert portfolio position to position risk"""
        try:
            return PositionRisk(
                symbol=position.symbol,
                quantity=position.quantity,
                entry_price=position.entry_price,
                current_price=position.current_price,
                market_value=position.market_value,
                unrealized_pnl=position.unrealized_pnl,
                unrealized_pnl_pct=position.unrealized_pnl_pct,
                stop_loss=position.entry_price * 0.95,  # 5% stop loss
                take_profit=position.entry_price * 1.15,  # 15% take profit
                risk_amount=abs(position.unrealized_pnl) if position.unrealized_pnl < 0 else 0,
                risk_pct=abs(position.unrealized_pnl) / position.market_value * 100 if position.market_value > 0 else 0,
                position_size_pct=position.weight * 100,
                beta=position.beta,
                volatility=position.volatility,
                var_95=position.market_value * position.volatility * 1.645 / np.sqrt(252)
            )
            
        except Exception as e:
            logger.error(f"Failed to convert position to risk: {e}")
            return None
    
    async def get_portfolio_history(self, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> List[PortfolioSnapshot]:
        """Get portfolio history over a period"""
        try:
            filtered_history = self.portfolio_history
            
            if start_date:
                filtered_history = [snap for snap in filtered_history if snap.timestamp >= start_date]
            
            if end_date:
                filtered_history = [snap for snap in filtered_history if snap.timestamp <= end_date]
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"Failed to get portfolio history: {e}")
            return []
    
    async def add_portfolio_snapshot(self, snapshot: PortfolioSnapshot):
        """Add a portfolio snapshot to history"""
        try:
            self.portfolio_history.append(snapshot)
            
            # Keep only recent history (last 1000 snapshots)
            if len(self.portfolio_history) > 1000:
                self.portfolio_history = self.portfolio_history[-1000:]
            
            logger.info(f"Added portfolio snapshot: {snapshot.total_value:.2f} at {snapshot.timestamp}")
            
        except Exception as e:
            logger.error(f"Failed to add portfolio snapshot: {e}")
    
    def get_rebalancing_status(self) -> Dict[str, Any]:
        """Get rebalancing status"""
        return {
            'auto_rebalancing': self.is_auto_rebalancing,
            'last_rebalancing': self.last_rebalancing.isoformat() if self.last_rebalancing else None,
            'rebalancing_frequency': self.config.rebalancing_frequency,
            'rebalancing_threshold': self.config.rebalancing_threshold,
            'optimization_method': self.config.optimization_method.value
        }
    
    def set_auto_rebalancing(self, enabled: bool):
        """Enable/disable auto rebalancing"""
        self.is_auto_rebalancing = enabled
        logger.info(f"Auto rebalancing {'enabled' if enabled else 'disabled'}")
    
    def update_config(self, new_config: PortfolioConfig):
        """Update portfolio configuration"""
        self.config = new_config
        logger.info("Portfolio configuration updated")


# Global portfolio management engine instance
portfolio_management_engine = PortfolioManagementEngine()


def get_portfolio_management_engine() -> PortfolioManagementEngine:
    """Get the global portfolio management engine instance"""
    return portfolio_management_engine

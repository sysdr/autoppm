"""
AutoPPM Backtesting Engine
Comprehensive backtesting framework for trading strategies
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from models.strategy import Strategy, StrategyExecution, StrategySignal, StrategyPerformance
from models.market_data import HistoricalData
from database.connection import get_database_session


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    strategy_id: int
    execution_id: int
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    calmar_ratio: float
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]


@dataclass
class BacktestConfig:
    """Configuration for backtest runs"""
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0
    commission_rate: float = 0.0005  # 0.05% per trade
    slippage: float = 0.0001  # 0.01% slippage
    position_sizing: str = "fixed"  # fixed, kelly, optimal
    max_position_size: float = 0.1  # 10% max position
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    rebalance_frequency: str = "daily"  # daily, weekly, monthly


class BacktestingEngine:
    """Engine for running strategy backtests"""
    
    def __init__(self):
        self.results_cache: Dict[int, BacktestResult] = {}
    
    async def run_backtest(self, strategy_id: int, symbols: List[str], 
                          config: BacktestConfig) -> Optional[BacktestResult]:
        """Run a complete backtest for a strategy"""
        try:
            logger.info(f"Starting backtest for strategy {strategy_id}")
            
            # Get strategy details
            strategy = await self._get_strategy(strategy_id)
            if not strategy:
                logger.error(f"Strategy {strategy_id} not found")
                return None
            
            # Get historical data
            historical_data = await self._get_historical_data(symbols, config.start_date, config.end_date)
            if not historical_data:
                logger.error(f"No historical data available for symbols {symbols}")
                return None
            
            # Create execution context
            execution_id = await self._create_backtest_execution(strategy_id, symbols, config)
            
            # Run backtest simulation
            result = await self._simulate_backtest(strategy, symbols, historical_data, config, execution_id)
            
            # Store results
            self.results_cache[execution_id] = result
            
            # Save performance metrics
            await self._save_backtest_results(result)
            
            logger.info(f"Backtest completed for strategy {strategy_id}")
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed for strategy {strategy_id}: {e}")
            return None
    
    async def _get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        """Get strategy from database"""
        try:
            session = next(get_database_session())
            strategy = session.query(Strategy).filter(Strategy.id == strategy_id).first()
            return strategy
        except Exception as e:
            logger.error(f"Failed to get strategy {strategy_id}: {e}")
            return None
        finally:
            if session:
                session.close()
    
    async def _get_historical_data(self, symbols: List[str], start_date: datetime, 
                                  end_date: datetime) -> Optional[Dict[str, pd.DataFrame]]:
        """Get historical data for symbols"""
        try:
            session = next(get_database_session())
            
            data = {}
            for symbol in symbols:
                # Query historical data
                query = session.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.date >= start_date,
                    HistoricalData.date <= end_date
                ).order_by(HistoricalData.date)
                
                records = query.all()
                
                if records:
                    # Convert to DataFrame
                    df = pd.DataFrame([{
                        'date': record.date,
                        'open': record.open_price,
                        'high': record.high_price,
                        'low': record.low_price,
                        'close': record.close_price,
                        'volume': record.volume
                    } for record in records])
                    
                    df.set_index('date', inplace=True)
                    data[symbol] = df
                else:
                    logger.warning(f"No historical data for symbol {symbol}")
            
            session.close()
            return data if data else None
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return None
    
    async def _create_backtest_execution(self, strategy_id: int, symbols: List[str], 
                                       config: BacktestConfig) -> int:
        """Create a backtest execution record"""
        try:
            session = next(get_database_session())
            
            execution = StrategyExecution(
                strategy_id=strategy_id,
                user_id=1,  # System user for backtests
                execution_type="backtest",
                parameters={
                    "start_date": config.start_date.isoformat(),
                    "end_date": config.end_date.isoformat(),
                    "initial_capital": config.initial_capital,
                    "commission_rate": config.commission_rate,
                    "slippage": config.slippage,
                    "position_sizing": config.position_sizing,
                    "max_position_size": config.max_position_size
                },
                symbols=symbols,
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
            session.add(execution)
            session.commit()
            execution_id = execution.id
            
            session.close()
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to create backtest execution: {e}")
            return 0
    
    async def _simulate_backtest(self, strategy: Strategy, symbols: List[str], 
                                historical_data: Dict[str, pd.DataFrame], 
                                config: BacktestConfig, execution_id: int) -> BacktestResult:
        """Simulate the backtest"""
        try:
            # Initialize portfolio
            portfolio = {
                'cash': config.initial_capital,
                'positions': {symbol: 0 for symbol in symbols},
                'equity': config.initial_capital
            }
            
            # Initialize tracking
            trades = []
            equity_curve = []
            current_date = config.start_date
            
            # Get all trading dates (union of all symbol dates)
            all_dates = set()
            for symbol_data in historical_data.values():
                all_dates.update(symbol_data.index)
            all_dates = sorted(list(all_dates))
            
            # Filter dates within range
            trading_dates = [date for date in all_dates if config.start_date <= date <= config.end_date]
            
            # Run simulation day by day
            for date in trading_dates:
                current_date = date
                
                # Get market data for current date
                market_data = {}
                for symbol, symbol_data in historical_data.items():
                    if date in symbol_data.index:
                        row = symbol_data.loc[date]
                        market_data[symbol] = {
                            'price': row['close'],
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'volume': row['volume'],
                            'timestamp': date
                        }
                
                # Generate signals (simplified - would integrate with actual strategy)
                signals = await self._generate_backtest_signals(strategy, symbols, market_data, portfolio)
                
                # Execute signals
                for signal in signals:
                    trade_result = await self._execute_backtest_trade(signal, market_data, portfolio, config)
                    if trade_result:
                        trades.append(trade_result)
                
                # Update portfolio value
                portfolio['equity'] = portfolio['cash']
                for symbol, quantity in portfolio['positions'].items():
                    if symbol in market_data:
                        portfolio['equity'] += quantity * market_data[symbol]['price']
                
                # Record equity curve
                equity_curve.append({
                    'date': date,
                    'equity': portfolio['equity'],
                    'cash': portfolio['cash'],
                    'positions_value': portfolio['equity'] - portfolio['cash']
                })
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                config.initial_capital, portfolio['equity'], trades, equity_curve
            )
            
            # Create result
            result = BacktestResult(
                strategy_id=strategy.id,
                execution_id=execution_id,
                start_date=config.start_date,
                end_date=config.end_date,
                initial_capital=config.initial_capital,
                final_capital=portfolio['equity'],
                total_return=portfolio['equity'] - config.initial_capital,
                total_return_pct=(portfolio['equity'] - config.initial_capital) / config.initial_capital * 100,
                annualized_return=performance_metrics['annualized_return'],
                sharpe_ratio=performance_metrics['sharpe_ratio'],
                max_drawdown=performance_metrics['max_drawdown'],
                max_drawdown_pct=performance_metrics['max_drawdown_pct'],
                win_rate=performance_metrics['win_rate'],
                total_trades=performance_metrics['total_trades'],
                winning_trades=performance_metrics['winning_trades'],
                losing_trades=performance_metrics['losing_trades'],
                avg_win=performance_metrics['avg_win'],
                avg_loss=performance_metrics['avg_loss'],
                profit_factor=performance_metrics['profit_factor'],
                calmar_ratio=performance_metrics['calmar_ratio'],
                trades=trades,
                equity_curve=equity_curve,
                performance_metrics=performance_metrics
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest simulation failed: {e}")
            raise
    
    async def _generate_backtest_signals(self, strategy: Strategy, symbols: List[str], 
                                       market_data: Dict[str, Any], portfolio: Dict[str, Any]) -> List[StrategySignal]:
        """Generate signals for backtest (simplified)"""
        signals = []
        
        # This is a simplified signal generation for backtesting
        # In a real implementation, this would call the actual strategy logic
        
        for symbol in symbols:
            if symbol in market_data:
                # Simple momentum signal (example)
                price = market_data[symbol]['price']
                
                # Random signal generation for demonstration
                import random
                if random.random() < 0.1:  # 10% chance of signal
                    signal_type = "buy" if random.random() < 0.6 else "sell"
                    signal = StrategySignal(
                        strategy_id=strategy.id,
                        symbol=symbol,
                        signal_type=signal_type,
                        price=price,
                        quantity=100,  # Fixed quantity for demo
                        confidence=random.uniform(0.5, 0.9),
                        timestamp=market_data[symbol]['timestamp'],
                        metadata={"backtest": True}
                    )
                    signals.append(signal)
        
        return signals
    
    async def _execute_backtest_trade(self, signal: StrategySignal, market_data: Dict[str, Any], 
                                    portfolio: Dict[str, Any], config: BacktestConfig) -> Optional[Dict[str, Any]]:
        """Execute a trade in the backtest"""
        try:
            symbol = signal.symbol
            price = signal.price
            quantity = signal.quantity
            
            if signal.signal_type == "buy":
                # Check if we have enough cash
                cost = price * quantity * (1 + config.commission_rate + config.slippage)
                if portfolio['cash'] >= cost:
                    portfolio['cash'] -= cost
                    portfolio['positions'][symbol] += quantity
                    
                    return {
                        'timestamp': signal.timestamp,
                        'symbol': symbol,
                        'action': 'buy',
                        'quantity': quantity,
                        'price': price,
                        'cost': cost,
                        'commission': cost * config.commission_rate,
                        'slippage': cost * config.slippage
                    }
            
            elif signal.signal_type == "sell":
                # Check if we have enough shares
                if portfolio['positions'][symbol] >= quantity:
                    proceeds = price * quantity * (1 - config.commission_rate - config.slippage)
                    portfolio['cash'] += proceeds
                    portfolio['positions'][symbol] -= quantity
                    
                    return {
                        'timestamp': signal.timestamp,
                        'symbol': symbol,
                        'action': 'sell',
                        'quantity': quantity,
                        'price': price,
                        'proceeds': proceeds,
                        'commission': proceeds * config.commission_rate,
                        'slippage': proceeds * config.slippage
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to execute backtest trade: {e}")
            return None
    
    def _calculate_performance_metrics(self, initial_capital: float, final_capital: float, 
                                     trades: List[Dict[str, Any]], 
                                     equity_curve: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        try:
            # Basic metrics
            total_return = final_capital - initial_capital
            total_return_pct = (total_return / initial_capital) * 100
            
            # Calculate returns for each period
            returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]['equity']
                curr_equity = equity_curve[i]['equity']
                if prev_equity > 0:
                    returns.append((curr_equity - prev_equity) / prev_equity)
            
            # Annualized return
            if len(equity_curve) > 1:
                days = (equity_curve[-1]['date'] - equity_curve[0]['date']).days
                if days > 0:
                    annualized_return = ((final_capital / initial_capital) ** (365 / days) - 1) * 100
                else:
                    annualized_return = 0
            else:
                annualized_return = 0
            
            # Sharpe ratio (simplified)
            if returns and np.std(returns) > 0:
                sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252)  # Annualized
            else:
                sharpe_ratio = 0
            
            # Maximum drawdown
            peak = initial_capital
            max_drawdown = 0
            max_drawdown_pct = 0
            
            for point in equity_curve:
                equity = point['equity']
                if equity > peak:
                    peak = equity
                else:
                    drawdown = (peak - equity) / peak
                    if drawdown > max_drawdown_pct:
                        max_drawdown_pct = drawdown
                        max_drawdown = peak - equity
            
            # Trade analysis
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t.get('proceeds', 0) > t.get('cost', 0)])
            losing_trades = total_trades - winning_trades
            
            if winning_trades > 0:
                avg_win = np.mean([t.get('proceeds', 0) - t.get('cost', 0) 
                                 for t in trades if t.get('proceeds', 0) > t.get('cost', 0)])
            else:
                avg_win = 0
            
            if losing_trades > 0:
                avg_loss = np.mean([t.get('cost', 0) - t.get('proceeds', 0) 
                                  for t in trades if t.get('proceeds', 0) < t.get('cost', 0)])
            else:
                avg_loss = 0
            
            # Win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Profit factor
            total_wins = sum([t.get('proceeds', 0) - t.get('cost', 0) 
                            for t in trades if t.get('proceeds', 0) > t.get('cost', 0)])
            total_losses = sum([t.get('cost', 0) - t.get('proceeds', 0) 
                              for t in trades if t.get('proceeds', 0) < t.get('cost', 0)])
            
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            # Calmar ratio
            calmar_ratio = annualized_return / max_drawdown_pct if max_drawdown_pct > 0 else 0
            
            return {
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'annualized_return': annualized_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown_pct,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'calmar_ratio': calmar_ratio
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {}
    
    async def _save_backtest_results(self, result: BacktestResult):
        """Save backtest results to database"""
        try:
            session = next(get_database_session())
            
            # Update execution record
            execution = session.query(StrategyExecution).filter(
                StrategyExecution.id == result.execution_id
            ).first()
            
            if execution:
                execution.total_pnl = result.total_return
                execution.completed_at = datetime.utcnow()
                execution.status = "completed"
            
            # Create performance record
            performance = StrategyPerformance(
                strategy_id=result.strategy_id,
                execution_id=result.execution_id,
                total_return=result.total_return,
                total_return_pct=result.total_return_pct,
                annualized_return=result.annualized_return,
                sharpe_ratio=result.sharpe_ratio,
                max_drawdown=result.max_drawdown,
                max_drawdown_pct=result.max_drawdown_pct,
                win_rate=result.win_rate,
                total_trades=result.total_trades,
                winning_trades=result.winning_trades,
                losing_trades=result.losing_trades,
                avg_win=result.avg_win,
                avg_loss=result.avg_loss,
                profit_factor=result.profit_factor,
                calmar_ratio=result.calmar_ratio,
                metadata={
                    'backtest_start_date': result.start_date.isoformat(),
                    'backtest_end_date': result.end_date.isoformat(),
                    'initial_capital': result.initial_capital,
                    'final_capital': result.final_capital
                }
            )
            
            session.add(performance)
            session.commit()
            
            logger.info(f"Saved backtest results for execution {result.execution_id}")
            
        except Exception as e:
            logger.error(f"Failed to save backtest results: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    def get_backtest_result(self, execution_id: int) -> Optional[BacktestResult]:
        """Get cached backtest result"""
        return self.results_cache.get(execution_id)
    
    def clear_cache(self):
        """Clear results cache"""
        self.results_cache.clear()


# Global backtesting engine instance
backtesting_engine = BacktestingEngine()


def get_backtesting_engine() -> BacktestingEngine:
    """Get the global backtesting engine instance"""
    return backtesting_engine

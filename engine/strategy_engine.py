"""
AutoPPM Strategy Engine
Core engine for managing and executing trading strategies
"""

import asyncio
import importlib
import inspect
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass
from loguru import logger

from models.strategy import Strategy, StrategyExecution, StrategySignal, StrategyPerformance
from database.connection import get_database_session


@dataclass
class StrategyContext:
    """Context for strategy execution"""
    execution_id: int
    user_id: int
    symbols: List[str]
    parameters: Dict[str, Any]
    start_date: datetime
    current_date: datetime
    portfolio_value: float
    positions: Dict[str, float]  # symbol -> quantity


class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.strategy_type = "custom"
        self.category = "equity"
        self.risk_level = "moderate"
        self.default_parameters = {}
        self.required_parameters = []
    
    @abstractmethod
    async def initialize(self, context: StrategyContext) -> bool:
        """Initialize strategy with execution context"""
        pass
    
    @abstractmethod
    async def generate_signals(self, context: StrategyContext, market_data: Dict[str, Any]) -> List[StrategySignal]:
        """Generate trading signals based on market data"""
        pass
    
    @abstractmethod
    async def calculate_position_size(self, signal: StrategySignal, context: StrategyContext) -> float:
        """Calculate position size for a signal"""
        pass
    
    @abstractmethod
    async def should_exit(self, position: Dict[str, Any], context: StrategyContext) -> bool:
        """Determine if a position should be exited"""
        pass
    
    async def cleanup(self, context: StrategyContext) -> None:
        """Cleanup resources when strategy stops"""
        pass


class StrategyRegistry:
    """Registry for managing available strategies"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._instances: Dict[int, BaseStrategy] = {}
    
    def register_strategy(self, strategy_class: Type[BaseStrategy]) -> bool:
        """Register a strategy class"""
        try:
            strategy_name = strategy_class.__name__
            if strategy_name in self._strategies:
                logger.warning(f"Strategy {strategy_name} already registered, overwriting")
            
            self._strategies[strategy_name] = strategy_class
            logger.info(f"Strategy {strategy_name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register strategy {strategy_class.__name__}: {e}")
            return False
    
    def unregister_strategy(self, strategy_name: str) -> bool:
        """Unregister a strategy"""
        try:
            if strategy_name in self._strategies:
                del self._strategies[strategy_name]
                logger.info(f"Strategy {strategy_name} unregistered successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister strategy {strategy_name}: {e}")
            return False
    
    def get_strategy_class(self, strategy_name: str) -> Optional[Type[BaseStrategy]]:
        """Get strategy class by name"""
        return self._strategies.get(strategy_name)
    
    def list_strategies(self) -> List[str]:
        """List all registered strategy names"""
        return list(self._strategies.keys())
    
    def create_strategy_instance(self, strategy_name: str, **kwargs) -> Optional[BaseStrategy]:
        """Create a new instance of a strategy"""
        try:
            strategy_class = self.get_strategy_class(strategy_name)
            if strategy_class:
                instance = strategy_class(**kwargs)
                return instance
            return None
            
        except Exception as e:
            logger.error(f"Failed to create strategy instance {strategy_name}: {e}")
            return None


class StrategyExecutor:
    """Executes trading strategies"""
    
    def __init__(self, strategy_registry: StrategyRegistry):
        self.registry = strategy_registry
        self.running_executions: Dict[int, asyncio.Task] = {}
        self.execution_contexts: Dict[int, StrategyContext] = {}
    
    async def start_execution(self, execution_id: int, strategy_name: str, 
                            user_id: int, symbols: List[str], parameters: Dict[str, Any],
                            execution_type: str = "paper") -> bool:
        """Start strategy execution"""
        try:
            # Create strategy instance
            strategy = self.registry.create_strategy_instance(strategy_name, **parameters)
            if not strategy:
                logger.error(f"Failed to create strategy instance for {strategy_name}")
                return False
            
            # Create execution context
            context = StrategyContext(
                execution_id=execution_id,
                user_id=user_id,
                symbols=symbols,
                parameters=parameters,
                start_date=datetime.utcnow(),
                current_date=datetime.utcnow(),
                portfolio_value=100000.0,  # Default starting value
                positions={}
            )
            
            # Initialize strategy
            if not await strategy.initialize(context):
                logger.error(f"Strategy {strategy_name} failed to initialize")
                return False
            
            # Store context
            self.execution_contexts[execution_id] = context
            
            # Start execution task
            task = asyncio.create_task(self._run_strategy_execution(execution_id, strategy, context))
            self.running_executions[execution_id] = task
            
            logger.info(f"Started strategy execution {execution_id} for {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start strategy execution {execution_id}: {e}")
            return False
    
    async def stop_execution(self, execution_id: int) -> bool:
        """Stop strategy execution"""
        try:
            if execution_id in self.running_executions:
                task = self.running_executions[execution_id]
                task.cancel()
                
                # Cleanup
                if execution_id in self.execution_contexts:
                    context = self.execution_contexts[execution_id]
                    # Find strategy instance and cleanup
                    for strategy_name in self.registry.list_strategies():
                        strategy = self.registry.create_strategy_instance(strategy_name)
                        if strategy:
                            await strategy.cleanup(context)
                
                del self.running_executions[execution_id]
                if execution_id in self.execution_contexts:
                    del self.execution_contexts[execution_id]
                
                logger.info(f"Stopped strategy execution {execution_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop strategy execution {execution_id}: {e}")
            return False
    
    async def _run_strategy_execution(self, execution_id: int, strategy: BaseStrategy, context: StrategyContext):
        """Main execution loop for a strategy"""
        try:
            logger.info(f"Starting strategy execution loop for {execution_id}")
            
            while execution_id in self.running_executions:
                try:
                    # Update context
                    context.current_date = datetime.utcnow()
                    
                    # Get market data for symbols
                    market_data = await self._get_market_data(context.symbols)
                    
                    # Generate signals
                    signals = await strategy.generate_signals(context, market_data)
                    
                    # Process signals
                    for signal in signals:
                        await self._process_signal(signal, strategy, context)
                    
                    # Update performance
                    await self._update_performance(execution_id, context)
                    
                    # Wait for next iteration
                    await asyncio.sleep(60)  # Check every minute
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in strategy execution {execution_id}: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
            
            logger.info(f"Strategy execution {execution_id} completed")
            
        except Exception as e:
            logger.error(f"Fatal error in strategy execution {execution_id}: {e}")
        finally:
            # Cleanup
            if execution_id in self.execution_contexts:
                await strategy.cleanup(self.execution_contexts[execution_id])
    
    async def _get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market data for symbols (placeholder - would integrate with data service)"""
        # This would integrate with the data ingestion service
        market_data = {}
        for symbol in symbols:
            market_data[symbol] = {
                "price": 100.0,  # Placeholder
                "volume": 1000000,
                "timestamp": datetime.utcnow()
            }
        return market_data
    
    async def _process_signal(self, signal: StrategySignal, strategy: BaseStrategy, context: StrategyContext):
        """Process a trading signal"""
        try:
            # Calculate position size
            position_size = await strategy.calculate_position_size(signal, context)
            
            # Log signal
            logger.info(f"Signal generated: {signal.signal_type} {signal.symbol} "
                       f"at {signal.price} (confidence: {signal.confidence})")
            
            # Store signal in database
            await self._store_signal(signal)
            
            # Execute signal (placeholder - would integrate with order management)
            if signal.signal_type in ["buy", "sell"]:
                logger.info(f"Executing {signal.signal_type} order for {signal.symbol}")
                # This would integrate with the order management system
            
        except Exception as e:
            logger.error(f"Failed to process signal: {e}")
    
    async def _store_signal(self, signal: StrategySignal):
        """Store signal in database"""
        try:
            session = next(get_database_session())
            session.add(signal)
            session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store signal: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    async def _update_performance(self, execution_id: int, context: StrategyContext):
        """Update strategy performance metrics"""
        try:
            # This would calculate and store performance metrics
            # Placeholder for now
            pass
            
        except Exception as e:
            logger.error(f"Failed to update performance: {e}")
    
    def get_execution_status(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        if execution_id in self.running_executions:
            task = self.running_executions[execution_id]
            return {
                "status": "running" if not task.done() else "completed",
                "running": execution_id in self.running_executions
            }
        return None
    
    def list_running_executions(self) -> List[int]:
        """List all running execution IDs"""
        return list(self.running_executions.keys())


class StrategyEngine:
    """Main strategy engine orchestrator"""
    
    def __init__(self):
        self.registry = StrategyRegistry()
        self.executor = StrategyExecutor(self.registry)
        self.is_running = False
        
        # Register built-in strategies
        self._register_builtin_strategies()
    
    def _register_builtin_strategies(self):
        """Register built-in trading strategies"""
        try:
            # Import and register built-in strategies
            from strategies.momentum_strategy import MomentumStrategy
            from strategies.mean_reversion_strategy import MeanReversionStrategy
            from strategies.multi_factor_strategy import MultiFactorStrategy
            
            self.registry.register_strategy(MomentumStrategy)
            self.registry.register_strategy(MeanReversionStrategy)
            self.registry.register_strategy(MultiFactorStrategy)
            
            logger.info("Built-in strategies registered successfully")
            
        except ImportError as e:
            logger.warning(f"Some built-in strategies not available: {e}")
    
    async def start(self):
        """Start the strategy engine"""
        try:
            self.is_running = True
            logger.info("Strategy engine started")
            
        except Exception as e:
            logger.error(f"Failed to start strategy engine: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the strategy engine"""
        try:
            # Stop all running executions
            running_executions = self.executor.list_running_executions()
            for execution_id in running_executions:
                await self.executor.stop_execution(execution_id)
            
            self.is_running = False
            logger.info("Strategy engine stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop strategy engine: {e}")
            raise
    
    async def create_strategy(self, strategy_data: Dict[str, Any]) -> Optional[int]:
        """Create a new strategy"""
        try:
            session = next(get_database_session())
            
            strategy = Strategy(**strategy_data)
            session.add(strategy)
            session.commit()
            
            strategy_id = strategy.id
            logger.info(f"Created strategy {strategy_id}: {strategy.name}")
            
            return strategy_id
            
        except Exception as e:
            logger.error(f"Failed to create strategy: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    async def start_strategy_execution(self, strategy_id: int, user_id: int, 
                                     symbols: List[str], parameters: Dict[str, Any],
                                     execution_type: str = "paper") -> Optional[int]:
        """Start a strategy execution"""
        try:
            # Get strategy details
            session = next(get_database_session())
            strategy = session.query(Strategy).filter(Strategy.id == strategy_id).first()
            
            if not strategy:
                logger.error(f"Strategy {strategy_id} not found")
                return None
            
            # Create execution record
            execution = StrategyExecution(
                strategy_id=strategy_id,
                user_id=user_id,
                execution_type=execution_type,
                parameters=parameters,
                symbols=symbols,
                status="running"
            )
            
            session.add(execution)
            session.commit()
            execution_id = execution.id
            
            # Start execution
            success = await self.executor.start_execution(
                execution_id, strategy.name, user_id, symbols, parameters, execution_type
            )
            
            if not success:
                # Mark execution as failed
                execution.status = "error"
                session.commit()
                return None
            
            logger.info(f"Started strategy execution {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to start strategy execution: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    async def stop_strategy_execution(self, execution_id: int) -> bool:
        """Stop a strategy execution"""
        try:
            success = await self.executor.stop_execution(execution_id)
            
            if success:
                # Update execution status
                session = next(get_database_session())
                execution = session.query(StrategyExecution).filter(
                    StrategyExecution.id == execution_id
                ).first()
                
                if execution:
                    execution.status = "stopped"
                    execution.stopped_at = datetime.utcnow()
                    session.commit()
                
                session.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to stop strategy execution {execution_id}: {e}")
            return False
    
    def get_strategy_list(self) -> List[Dict[str, Any]]:
        """Get list of available strategies"""
        try:
            session = next(get_database_session())
            strategies = session.query(Strategy).filter(Strategy.is_active == True).all()
            
            strategy_list = []
            for strategy in strategies:
                strategy_list.append({
                    "id": strategy.id,
                    "name": strategy.name,
                    "description": strategy.description,
                    "version": strategy.version,
                    "strategy_type": strategy.strategy_type,
                    "category": strategy.category,
                    "risk_level": strategy.risk_level,
                    "is_active": strategy.is_active,
                    "is_backtest_only": strategy.is_backtest_only,
                    "total_return": strategy.total_return,
                    "sharpe_ratio": strategy.sharpe_ratio,
                    "max_drawdown": strategy.max_drawdown,
                    "win_rate": strategy.win_rate,
                    "created_at": strategy.created_at,
                    "last_executed": strategy.last_executed
                })
            
            return strategy_list
            
        except Exception as e:
            logger.error(f"Failed to get strategy list: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def get_execution_list(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of strategy executions"""
        try:
            session = next(get_database_session())
            query = session.query(StrategyExecution)
            
            if user_id:
                query = query.filter(StrategyExecution.user_id == user_id)
            
            executions = query.all()
            
            execution_list = []
            for execution in executions:
                status_info = self.executor.get_execution_status(execution.id)
                execution_list.append({
                    "id": execution.id,
                    "strategy_id": execution.strategy_id,
                    "user_id": execution.user_id,
                    "execution_type": execution.execution_type,
                    "status": execution.status,
                    "started_at": execution.started_at,
                    "total_pnl": execution.total_pnl,
                    "current_drawdown": execution.current_drawdown,
                    "running": status_info["running"] if status_info else False
                })
            
            return execution_list
            
        except Exception as e:
            logger.error(f"Failed to get execution list: {e}")
            return []
        finally:
            if session:
                session.close()


# Global strategy engine instance
strategy_engine = StrategyEngine()


def get_strategy_engine() -> StrategyEngine:
    """Get the global strategy engine instance"""
    return strategy_engine

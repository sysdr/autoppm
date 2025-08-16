"""
AutoPPM Main Orchestrator
Coordinates all trading engines and manages the overall system
"""

import asyncio
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from engine.strategy_engine import get_strategy_engine
from engine.backtesting_engine import get_backtesting_engine
from engine.risk_management_engine import get_risk_management_engine
from engine.order_management_engine import get_order_management_engine
from engine.portfolio_management_engine import get_portfolio_management_engine
from services.data_ingestion_service import get_data_ingestion_service


@dataclass
class SystemStatus:
    """System status information"""
    timestamp: datetime
    is_running: bool
    engines_status: Dict[str, bool]
    active_strategies: int
    active_orders: int
    portfolio_value: float
    total_pnl: float
    risk_alerts: int
    system_health: str  # healthy, warning, critical


class AutoPPMOrchestrator:
    """Main orchestrator for the AutoPPM system"""
    
    def __init__(self):
        # Initialize all engines
        self.strategy_engine = get_strategy_engine()
        self.backtesting_engine = get_backtesting_engine()
        self.risk_engine = get_risk_management_engine()
        self.order_engine = get_order_management_engine()
        self.portfolio_engine = get_portfolio_management_engine()
        self.data_service = get_data_ingestion_service()
        
        # System state
        self.is_running = False
        self.startup_time = None
        self.system_health = "healthy"
        self.health_check_interval = 60  # seconds
        self.performance_monitoring = True
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.performance_monitor_task: Optional[asyncio.Task] = None
        self.auto_rebalancing_task: Optional[asyncio.Task] = None
        
        # Signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.info("Signal handlers configured")
        except Exception as e:
            logger.warning(f"Failed to setup signal handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def start(self):
        """Start the AutoPPM system"""
        try:
            logger.info("Starting AutoPPM system...")
            
            # Start all engines
            await self._start_all_engines()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Mark system as running
            self.is_running = True
            self.startup_time = datetime.utcnow()
            
            logger.info("AutoPPM system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AutoPPM system: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """Shutdown the AutoPPM system gracefully"""
        try:
            logger.info("Shutting down AutoPPM system...")
            
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Stop all engines
            await self._stop_all_engines()
            
            # Mark system as stopped
            self.is_running = False
            
            logger.info("AutoPPM system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _start_all_engines(self):
        """Start all trading engines"""
        try:
            logger.info("Starting trading engines...")
            
            # Start strategy engine
            await self.strategy_engine.start()
            logger.info("Strategy engine started")
            
            # Start order management engine
            await self.order_engine.start()
            logger.info("Order management engine started")
            
            # Start data ingestion service
            await self.data_service.start()
            logger.info("Data ingestion service started")
            
            logger.info("All engines started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start engines: {e}")
            raise
    
    async def _stop_all_engines(self):
        """Stop all trading engines"""
        try:
            logger.info("Stopping trading engines...")
            
            # Stop strategy engine
            await self.strategy_engine.stop()
            logger.info("Strategy engine stopped")
            
            # Stop order management engine
            await self.order_engine.stop()
            logger.info("Order management engine stopped")
            
            # Stop data ingestion service
            await self.data_service.stop()
            logger.info("Data ingestion service stopped")
            
            logger.info("All engines stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop engines: {e}")
    
    async def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks"""
        try:
            logger.info("Starting background tasks...")
            
            # Health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # Performance monitoring task
            if self.performance_monitoring:
                self.performance_monitor_task = asyncio.create_task(self._performance_monitor_loop())
            
            # Auto rebalancing task
            self.auto_rebalancing_task = asyncio.create_task(self._auto_rebalancing_loop())
            
            logger.info("Background tasks started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
            raise
    
    async def _stop_background_tasks(self):
        """Stop background tasks"""
        try:
            logger.info("Stopping background tasks...")
            
            # Cancel health check task
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel performance monitor task
            if self.performance_monitor_task:
                self.performance_monitor_task.cancel()
                try:
                    await self.performance_monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel auto rebalancing task
            if self.auto_rebalancing_task:
                self.auto_rebalancing_task.cancel()
                try:
                    await self.auto_rebalancing_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Background tasks stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop background tasks: {e}")
    
    async def _health_check_loop(self):
        """Continuous health check loop"""
        try:
            logger.info("Health check loop started")
            
            while self.is_running:
                try:
                    # Perform health check
                    await self._perform_health_check()
                    
                    # Wait for next check
                    await asyncio.sleep(self.health_check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in health check loop: {e}")
                    await asyncio.sleep(10)  # Wait before retrying
            
            logger.info("Health check loop stopped")
            
        except Exception as e:
            logger.error(f"Fatal error in health check loop: {e}")
    
    async def _perform_health_check(self):
        """Perform system health check"""
        try:
            health_issues = []
            
            # Check engine status
            if not self.strategy_engine.is_running:
                health_issues.append("Strategy engine not running")
            
            if not self.order_engine.is_running:
                health_issues.append("Order management engine not running")
            
            # Check data service
            if not self.data_service.is_running:
                health_issues.append("Data ingestion service not running")
            
            # Check risk alerts
            risk_alerts = self.risk_engine.get_risk_alerts()
            if len(risk_alerts) > 5:  # More than 5 alerts
                health_issues.append(f"High number of risk alerts: {len(risk_alerts)}")
            
            # Update system health
            if health_issues:
                if len(health_issues) > 3:
                    self.system_health = "critical"
                else:
                    self.system_health = "warning"
                
                logger.warning(f"Health check issues: {health_issues}")
            else:
                self.system_health = "healthy"
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.system_health = "critical"
    
    async def _performance_monitor_loop(self):
        """Continuous performance monitoring loop"""
        try:
            logger.info("Performance monitoring loop started")
            
            while self.is_running:
                try:
                    # Monitor performance metrics
                    await self._monitor_performance()
                    
                    # Wait for next monitoring cycle
                    await asyncio.sleep(300)  # Every 5 minutes
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in performance monitoring loop: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
            
            logger.info("Performance monitoring loop stopped")
            
        except Exception as e:
            logger.error(f"Fatal error in performance monitoring loop: {e}")
    
    async def _monitor_performance(self):
        """Monitor system performance metrics"""
        try:
            # Get current portfolio
            portfolio = await self.portfolio_engine.get_current_portfolio()
            if not portfolio:
                return
            
            # Log performance metrics
            logger.info(f"Portfolio Value: ₹{portfolio.total_value:,.2f}")
            logger.info(f"Total P&L: ₹{portfolio.total_pnl:,.2f} ({portfolio.total_pnl_pct:.2f}%)")
            logger.info(f"Risk Level: {portfolio.risk_metrics.var_95:.2%}")
            
            # Check for performance alerts
            if portfolio.total_pnl_pct < -5:  # 5% loss
                logger.warning(f"Portfolio showing significant loss: {portfolio.total_pnl_pct:.2f}%")
            
            if portfolio.risk_metrics.var_95 > 0.03:  # 3% VaR
                logger.warning(f"Portfolio risk high: VaR {portfolio.risk_metrics.var_95:.2%}")
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
    
    async def _auto_rebalancing_loop(self):
        """Automatic portfolio rebalancing loop"""
        try:
            logger.info("Auto rebalancing loop started")
            
            while self.is_running:
                try:
                    # Check if rebalancing is needed
                    portfolio = await self.portfolio_engine.get_current_portfolio()
                    if portfolio:
                        rebalancing_needed, targets = await self.portfolio_engine.check_rebalancing_needed(portfolio)
                        
                        if rebalancing_needed:
                            logger.info(f"Auto rebalancing triggered with {len(targets)} targets")
                            success = await self.portfolio_engine.rebalance_portfolio(targets)
                            
                            if success:
                                logger.info("Auto rebalancing completed successfully")
                            else:
                                logger.warning("Auto rebalancing completed with issues")
                    
                    # Wait for next rebalancing check (daily)
                    await asyncio.sleep(86400)  # 24 hours
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in auto rebalancing loop: {e}")
                    await asyncio.sleep(3600)  # Wait 1 hour before retrying
            
            logger.info("Auto rebalancing loop stopped")
            
        except Exception as e:
            logger.error(f"Fatal error in auto rebalancing loop: {e}")
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        try:
            # Get portfolio information
            portfolio = await self.portfolio_engine.get_current_portfolio()
            portfolio_value = portfolio.total_value if portfolio else 0
            total_pnl = portfolio.total_pnl if portfolio else 0
            
            # Get engine status
            engines_status = {
                'strategy_engine': self.strategy_engine.is_running,
                'order_engine': self.order_engine.is_running,
                'data_service': self.data_service.is_running,
                'risk_engine': True,  # Always running
                'portfolio_engine': True,  # Always running
                'backtesting_engine': True  # Always running
            }
            
            # Get active counts
            active_strategies = len(self.strategy_engine.executor.list_running_executions())
            order_status = self.order_engine.get_order_queue_status()
            active_orders = order_status['total_orders']
            
            # Get risk alerts
            risk_alerts = len(self.risk_engine.get_risk_alerts())
            
            return SystemStatus(
                timestamp=datetime.utcnow(),
                is_running=self.is_running,
                engines_status=engines_status,
                active_strategies=active_strategies,
                active_orders=active_orders,
                portfolio_value=portfolio_value,
                total_pnl=total_pnl,
                risk_alerts=risk_alerts,
                system_health=self.system_health
            )
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return None
    
    async def run_backtest(self, strategy_id: int, symbols: List[str], 
                          start_date: datetime, end_date: datetime, 
                          initial_capital: float = 100000.0) -> Dict[str, Any]:
        """Run a strategy backtest"""
        try:
            logger.info(f"Starting backtest for strategy {strategy_id}")
            
            # Import backtest config
            from engine.backtesting_engine import BacktestConfig
            
            config = BacktestConfig(
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital
            )
            
            # Run backtest
            result = await self.backtesting_engine.run_backtest(strategy_id, symbols, config)
            
            if result:
                logger.info(f"Backtest completed successfully for strategy {strategy_id}")
                return {
                    'success': True,
                    'result': {
                        'total_return': result.total_return,
                        'total_return_pct': result.total_return_pct,
                        'sharpe_ratio': result.sharpe_ratio,
                        'max_drawdown': result.max_drawdown,
                        'win_rate': result.win_rate,
                        'total_trades': result.total_trades
                    }
                }
            else:
                logger.error(f"Backtest failed for strategy {strategy_id}")
                return {'success': False, 'message': 'Backtest execution failed'}
                
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}")
            return {'success': False, 'message': str(e)}
    
    async def start_strategy(self, strategy_id: int, user_id: int, symbols: List[str], 
                           parameters: Dict[str, Any], execution_type: str = "paper") -> Dict[str, Any]:
        """Start a strategy execution"""
        try:
            logger.info(f"Starting strategy {strategy_id} for user {user_id}")
            
            # Start strategy execution
            execution_id = await self.strategy_engine.start_strategy_execution(
                strategy_id, user_id, symbols, parameters, execution_type
            )
            
            if execution_id:
                logger.info(f"Strategy {strategy_id} started successfully with execution ID {execution_id}")
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'message': 'Strategy started successfully'
                }
            else:
                logger.error(f"Failed to start strategy {strategy_id}")
                return {
                    'success': False,
                    'message': 'Failed to start strategy'
                }
                
        except Exception as e:
            logger.error(f"Strategy start failed: {e}")
            return {'success': False, 'message': str(e)}
    
    async def stop_strategy(self, execution_id: int) -> Dict[str, Any]:
        """Stop a strategy execution"""
        try:
            logger.info(f"Stopping strategy execution {execution_id}")
            
            success = await self.strategy_engine.stop_strategy_execution(execution_id)
            
            if success:
                logger.info(f"Strategy execution {execution_id} stopped successfully")
                return {
                    'success': True,
                    'message': 'Strategy stopped successfully'
                }
            else:
                logger.error(f"Failed to stop strategy execution {execution_id}")
                return {
                    'success': False,
                    'message': 'Failed to stop strategy'
                }
                
        except Exception as e:
            logger.error(f"Strategy stop failed: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get list of available strategies"""
        try:
            return self.strategy_engine.get_strategy_list()
        except Exception as e:
            logger.error(f"Failed to get strategy list: {e}")
            return []
    
    def get_running_executions(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of running strategy executions"""
        try:
            return self.strategy_engine.get_execution_list(user_id)
        except Exception as e:
            logger.error(f"Failed to get execution list: {e}")
            return []
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        try:
            portfolio = await self.portfolio_engine.get_current_portfolio()
            if not portfolio:
                return {}
            
            return {
                'total_value': portfolio.total_value,
                'total_pnl': portfolio.total_pnl,
                'total_pnl_pct': portfolio.total_pnl_pct,
                'cash': portfolio.cash,
                'num_positions': len(portfolio.positions),
                'risk_level': portfolio.risk_metrics.var_95,
                'sharpe_ratio': portfolio.risk_metrics.sharpe_ratio,
                'max_drawdown': portfolio.risk_metrics.max_drawdown_pct
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}")
            return {}


# Global orchestrator instance
autoppm_orchestrator = AutoPPMOrchestrator()


def get_autoppm_orchestrator() -> AutoPPMOrchestrator:
    """Get the global AutoPPM orchestrator instance"""
    return autoppm_orchestrator

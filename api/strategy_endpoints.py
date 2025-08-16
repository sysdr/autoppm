"""
AutoPPM Strategy API Endpoints
Enhanced endpoints for strategy management, backtesting, and execution
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from loguru import logger

from engine.autoppm_orchestrator import get_autoppm_orchestrator
from engine.backtesting_engine import BacktestConfig
from engine.portfolio_management_engine import PortfolioConfig, OptimizationMethod
from models.strategy import Strategy, StrategyExecution, StrategySignal

router = APIRouter(prefix="/api/strategy", tags=["Strategy Management"])

# Get orchestrator
orchestrator = get_autoppm_orchestrator()


# Request/Response Models
class BacktestRequest(BaseModel):
    """Backtest request model"""
    strategy_id: int
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(default=100000.0, ge=1000.0)
    commission_rate: float = Field(default=0.0005, ge=0.0, le=0.01)
    slippage: float = Field(default=0.0001, ge=0.0, le=0.01)


class BacktestResponse(BaseModel):
    """Backtest response model"""
    success: bool
    execution_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class StrategyStartRequest(BaseModel):
    """Strategy start request model"""
    strategy_id: int
    user_id: int
    symbols: List[str]
    parameters: Dict[str, Any] = {}
    execution_type: str = Field(default="paper", regex="^(paper|live)$")


class StrategyStartResponse(BaseModel):
    """Strategy start response model"""
    success: bool
    execution_id: Optional[int] = None
    message: str


class PortfolioConfigRequest(BaseModel):
    """Portfolio configuration request model"""
    target_weights: Dict[str, float]
    rebalancing_frequency: str = Field(default="monthly", regex="^(daily|weekly|monthly)$")
    rebalancing_threshold: float = Field(default=0.05, ge=0.01, le=0.2)
    max_position_size: float = Field(default=0.1, ge=0.01, le=0.5)
    max_sector_exposure: float = Field(default=0.3, ge=0.1, le=0.8)
    cash_buffer: float = Field(default=0.05, ge=0.0, le=0.2)
    optimization_method: str = Field(default="RISK_PARITY")


class SystemStatusResponse(BaseModel):
    """System status response model"""
    timestamp: datetime
    is_running: bool
    engines_status: Dict[str, bool]
    active_strategies: int
    active_orders: int
    portfolio_value: float
    total_pnl: float
    risk_alerts: int
    system_health: str


class PortfolioSummaryResponse(BaseModel):
    """Portfolio summary response model"""
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    cash: float
    num_positions: int
    risk_level: float
    sharpe_ratio: float
    max_drawdown: float


# Strategy Management Endpoints
@router.get("/list", response_model=List[Dict[str, Any]])
async def get_strategies():
    """Get list of available strategies"""
    try:
        strategies = orchestrator.get_available_strategies()
        return strategies
    except Exception as e:
        logger.error(f"Failed to get strategies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve strategies")


@router.get("/executions", response_model=List[Dict[str, Any]])
async def get_executions(user_id: Optional[int] = Query(None, description="Filter by user ID")):
    """Get list of strategy executions"""
    try:
        executions = orchestrator.get_running_executions(user_id)
        return executions
    except Exception as e:
        logger.error(f"Failed to get executions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve executions")


@router.post("/start", response_model=StrategyStartResponse)
async def start_strategy(request: StrategyStartRequest):
    """Start a strategy execution"""
    try:
        result = await orchestrator.start_strategy(
            strategy_id=request.strategy_id,
            user_id=request.user_id,
            symbols=request.symbols,
            parameters=request.parameters,
            execution_type=request.execution_type
        )
        
        if result['success']:
            return StrategyStartResponse(
                success=True,
                execution_id=result['execution_id'],
                message=result['message']
            )
        else:
            return StrategyStartResponse(
                success=False,
                message=result['message']
            )
            
    except Exception as e:
        logger.error(f"Failed to start strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start strategy: {str(e)}")


@router.post("/stop/{execution_id}", response_model=Dict[str, Any])
async def stop_strategy(execution_id: int):
    """Stop a strategy execution"""
    try:
        result = await orchestrator.stop_strategy(execution_id)
        return result
    except Exception as e:
        logger.error(f"Failed to stop strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop strategy: {str(e)}")


# Backtesting Endpoints
@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """Run a strategy backtest"""
    try:
        result = await orchestrator.run_backtest(
            strategy_id=request.strategy_id,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
        
        if result['success']:
            return BacktestResponse(
                success=True,
                result=result['result'],
                message="Backtest completed successfully"
            )
        else:
            return BacktestResponse(
                success=False,
                message=result['message']
            )
            
    except Exception as e:
        logger.error(f"Failed to run backtest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run backtest: {str(e)}")


@router.get("/backtest/results/{execution_id}")
async def get_backtest_results(execution_id: int):
    """Get backtest results for an execution"""
    try:
        from engine.backtesting_engine import get_backtesting_engine
        backtest_engine = get_backtesting_engine()
        
        result = backtest_engine.get_backtest_result(execution_id)
        if result:
            return {
                'success': True,
                'result': {
                    'strategy_id': result.strategy_id,
                    'execution_id': result.execution_id,
                    'start_date': result.start_date,
                    'end_date': result.end_date,
                    'initial_capital': result.initial_capital,
                    'final_capital': result.final_capital,
                    'total_return': result.total_return,
                    'total_return_pct': result.total_return_pct,
                    'annualized_return': result.annualized_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_ddown,
                    'max_drawdown_pct': result.max_drawdown_pct,
                    'win_rate': result.win_rate,
                    'total_trades': result.total_trades,
                    'winning_trades': result.winning_trades,
                    'losing_trades': result.losing_trades,
                    'avg_win': result.avg_win,
                    'avg_loss': result.avg_loss,
                    'profit_factor': result.profit_factor,
                    'calmar_ratio': result.calmar_ratio
                }
            }
        else:
            return {'success': False, 'message': 'Backtest results not found'}
            
    except Exception as e:
        logger.error(f"Failed to get backtest results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get backtest results: {str(e)}")


# Portfolio Management Endpoints
@router.get("/portfolio/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        summary = await orchestrator.get_portfolio_summary()
        return PortfolioSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio summary: {str(e)}")


@router.post("/portfolio/optimize")
async def optimize_portfolio(method: str = Query("RISK_PARITY", description="Optimization method")):
    """Optimize portfolio weights"""
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine
        portfolio_engine = get_portfolio_management_engine()
        
        # Convert string to enum
        try:
            opt_method = OptimizationMethod(method)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid optimization method: {method}")
        
        # Run optimization
        target_weights = await portfolio_engine.optimize_portfolio(method=opt_method)
        
        return {
            'success': True,
            'optimization_method': method,
            'target_weights': target_weights
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize portfolio: {str(e)}")


@router.post("/portfolio/rebalance")
async def rebalance_portfolio():
    """Trigger portfolio rebalancing"""
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine
        portfolio_engine = get_portfolio_management_engine()
        
        # Get current portfolio
        portfolio = await portfolio_engine.get_current_portfolio()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Check if rebalancing is needed
        rebalancing_needed, targets = await portfolio_engine.check_rebalancing_needed(portfolio)
        
        if not rebalancing_needed:
            return {
                'success': True,
                'message': 'Portfolio is already balanced',
                'rebalancing_needed': False,
                'targets': []
            }
        
        # Execute rebalancing
        success = await portfolio_engine.rebalance_portfolio(targets)
        
        return {
            'success': success,
            'message': 'Portfolio rebalancing completed' if success else 'Portfolio rebalancing failed',
            'rebalancing_needed': True,
            'targets': [
                {
                    'symbol': target.symbol,
                    'action': target.required_action,
                    'quantity_change': target.quantity_change,
                    'estimated_cost': target.estimated_cost
                }
                for target in targets
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to rebalance portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebalance portfolio: {str(e)}")


@router.post("/portfolio/config")
async def update_portfolio_config(request: PortfolioConfigRequest):
    """Update portfolio configuration"""
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine, PortfolioConfig
        portfolio_engine = get_portfolio_management_engine()
        
        # Convert optimization method string to enum
        try:
            opt_method = OptimizationMethod(request.optimization_method)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid optimization method: {request.optimization_method}")
        
        # Create new config
        config = PortfolioConfig(
            target_weights=request.target_weights,
            rebalancing_frequency=request.rebalancing_frequency,
            rebalancing_threshold=request.rebalancing_threshold,
            max_position_size=request.max_position_size,
            max_sector_exposure=request.max_sector_exposure,
            cash_buffer=request.cash_buffer,
            optimization_method=opt_method
        )
        
        # Update configuration
        portfolio_engine.update_config(config)
        
        return {
            'success': True,
            'message': 'Portfolio configuration updated successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to update portfolio config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update portfolio config: {str(e)}")


@router.get("/portfolio/rebalancing/status")
async def get_rebalancing_status():
    """Get portfolio rebalancing status"""
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine
        portfolio_engine = get_portfolio_management_engine()
        
        status = portfolio_engine.get_rebalancing_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get rebalancing status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get rebalancing status: {str(e)}")


@router.post("/portfolio/rebalancing/auto/{enabled}")
async def set_auto_rebalancing(enabled: bool):
    """Enable/disable auto rebalancing"""
    try:
        from engine.portfolio_management_engine import get_portfolio_management_engine
        portfolio_engine = get_portfolio_management_engine()
        
        portfolio_engine.set_auto_rebalancing(enabled)
        
        return {
            'success': True,
            'message': f'Auto rebalancing {"enabled" if enabled else "disabled"} successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to set auto rebalancing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set auto rebalancing: {str(e)}")


# Risk Management Endpoints
@router.get("/risk/alerts")
async def get_risk_alerts():
    """Get current risk alerts"""
    try:
        from engine.risk_management_engine import get_risk_management_engine
        risk_engine = get_risk_management_engine()
        
        alerts = risk_engine.get_risk_alerts()
        return {
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get risk alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk alerts: {str(e)}")


@router.post("/risk/alerts/clear")
async def clear_risk_alerts():
    """Clear all risk alerts"""
    try:
        from engine.risk_management_engine import get_risk_management_engine
        risk_engine = get_risk_management_engine()
        
        risk_engine.clear_risk_alerts()
        
        return {
            'success': True,
            'message': 'Risk alerts cleared successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to clear risk alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear risk alerts: {str(e)}")


# System Management Endpoints
@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get system status"""
    try:
        status = await orchestrator.get_system_status()
        if status:
            return SystemStatusResponse(**status.__dict__)
        else:
            raise HTTPException(status_code=500, detail="Failed to get system status")
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.post("/system/start")
async def start_system():
    """Start the AutoPPM system"""
    try:
        await orchestrator.start()
        return {
            'success': True,
            'message': 'AutoPPM system started successfully'
        }
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start system: {str(e)}")


@router.post("/system/stop")
async def stop_system():
    """Stop the AutoPPM system"""
    try:
        await orchestrator.shutdown()
        return {
            'success': True,
            'message': 'AutoPPM system stopped successfully'
        }
    except Exception as e:
        logger.error(f"Failed to stop system: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop system: {str(e)}")


# Order Management Endpoints
@router.get("/orders/status")
async def get_order_status():
    """Get order management status"""
    try:
        from engine.order_management_engine import get_order_management_engine
        order_engine = get_order_management_engine()
        
        status = order_engine.get_order_queue_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get order status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get order status: {str(e)}")


@router.get("/orders/history")
async def get_order_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date")
):
    """Get order execution history"""
    try:
        from engine.order_management_engine import get_order_management_engine
        order_engine = get_order_management_engine()
        
        history = await order_engine.get_execution_history(symbol, start_date, end_date)
        
        return {
            'success': True,
            'history': [
                {
                    'order_id': ex.order_id,
                    'symbol': ex.symbol,
                    'side': ex.side.value,
                    'quantity': ex.quantity,
                    'price': ex.price,
                    'timestamp': ex.timestamp,
                    'trade_id': ex.trade_id,
                    'net_amount': ex.net_amount
                }
                for ex in history
            ],
            'count': len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get order history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get order history: {str(e)}")

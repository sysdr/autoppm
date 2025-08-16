"""
AutoPPM Order Management Engine
Comprehensive order management and execution system
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from models.strategy import StrategySignal
from services.zerodha_service import get_zerodha_service
from database.connection import get_database_session


class OrderType(Enum):
    """Order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"


class OrderStatus(Enum):
    """Order statuses"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"


class OrderSide(Enum):
    """Order sides"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class OrderRequest:
    """Order request structure"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    validity: str = "DAY"  # DAY, IOC, GTC
    disclosed_quantity: Optional[int] = None
    tag: Optional[str] = None
    strategy_id: Optional[int] = None
    signal_id: Optional[int] = None


@dataclass
class OrderResponse:
    """Order response structure"""
    order_id: str
    status: OrderStatus
    message: str
    kite_order_id: Optional[str] = None
    filled_quantity: int = 0
    average_price: Optional[float] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None


@dataclass
class OrderExecution:
    """Order execution details"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    trade_id: str
    brokerage: float
    taxes: float
    net_amount: float
    metadata: Dict[str, Any] = None


class OrderManagementEngine:
    """Engine for managing trading orders"""
    
    def __init__(self):
        self.zerodha_service = get_zerodha_service()
        self.pending_orders: Dict[str, OrderRequest] = {}
        self.order_status: Dict[str, OrderStatus] = {}
        self.execution_history: List[OrderExecution] = []
        self.order_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.execution_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the order management engine"""
        try:
            self.is_running = True
            self.execution_task = asyncio.create_task(self._order_execution_loop())
            logger.info("Order management engine started")
            
        except Exception as e:
            logger.error(f"Failed to start order management engine: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the order management engine"""
        try:
            self.is_running = False
            
            if self.execution_task:
                self.execution_task.cancel()
                try:
                    await self.execution_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Order management engine stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop order management engine: {e}")
            raise
    
    async def place_order(self, order_request: OrderRequest) -> OrderResponse:
        """Place a new order"""
        try:
            # Validate order request
            validation_result = await self._validate_order(order_request)
            if not validation_result['valid']:
                return OrderResponse(
                    order_id="",
                    status=OrderStatus.REJECTED,
                    message=validation_result['message']
                )
            
            # Generate order ID
            order_id = str(uuid.uuid4())
            
            # Store order request
            self.pending_orders[order_id] = order_request
            self.order_status[order_id] = OrderStatus.PENDING
            
            # Add to execution queue
            await self.order_queue.put((order_id, order_request))
            
            logger.info(f"Order {order_id} queued for execution: {order_request.side.value} "
                       f"{order_request.quantity} {order_request.symbol}")
            
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.PENDING,
                message="Order queued for execution",
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return OrderResponse(
                order_id="",
                status=OrderStatus.ERROR,
                message=f"Order placement failed: {str(e)}"
            )
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order"""
        try:
            if order_id not in self.pending_orders:
                logger.warning(f"Order {order_id} not found for cancellation")
                return False
            
            # Check if order can be cancelled
            status = self.order_status.get(order_id, OrderStatus.PENDING)
            if status in [OrderStatus.FILLED, OrderStatus.REJECTED, OrderStatus.CANCELLED]:
                logger.warning(f"Order {order_id} cannot be cancelled in status {status.value}")
                return False
            
            # Cancel order through Zerodha
            order_request = self.pending_orders[order_id]
            success = await self._cancel_zerodha_order(order_id, order_request)
            
            if success:
                self.order_status[order_id] = OrderStatus.CANCELLED
                logger.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                logger.error(f"Failed to cancel order {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order"""
        try:
            if order_id not in self.pending_orders:
                logger.warning(f"Order {order_id} not found for modification")
                return False
            
            # Check if order can be modified
            status = self.order_status.get(order_id, OrderStatus.PENDING)
            if status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                logger.warning(f"Order {order_id} cannot be modified in status {status.value}")
                return False
            
            # Modify order through Zerodha
            order_request = self.pending_orders[order_id]
            success = await self._modify_zerodha_order(order_id, order_request, modifications)
            
            if success:
                # Update order request
                for key, value in modifications.items():
                    if hasattr(order_request, key):
                        setattr(order_request, key, value)
                
                logger.info(f"Order {order_id} modified successfully")
                return True
            else:
                logger.error(f"Failed to modify order {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to modify order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an order"""
        try:
            if order_id not in self.pending_orders:
                return None
            
            order_request = self.pending_orders[order_id]
            status = self.order_status.get(order_id, OrderStatus.PENDING)
            
            # Get detailed status from Zerodha if available
            kite_status = await self._get_zerodha_order_status(order_id, order_request)
            
            return {
                'order_id': order_id,
                'symbol': order_request.symbol,
                'side': order_request.side.value,
                'order_type': order_request.order_type.value,
                'quantity': order_request.quantity,
                'price': order_request.price,
                'status': status.value,
                'kite_status': kite_status,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get order status for {order_id}: {e}")
            return None
    
    async def get_execution_history(self, symbol: Optional[str] = None, 
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> List[OrderExecution]:
        """Get order execution history"""
        try:
            filtered_executions = self.execution_history
            
            if symbol:
                filtered_executions = [ex for ex in filtered_executions if ex.symbol == symbol]
            
            if start_date:
                filtered_executions = [ex for ex in filtered_executions if ex.timestamp >= start_date]
            
            if end_date:
                filtered_executions = [ex for ex in filtered_executions if ex.timestamp <= end_date]
            
            return filtered_executions
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []
    
    async def _order_execution_loop(self):
        """Main order execution loop"""
        try:
            logger.info("Order execution loop started")
            
            while self.is_running:
                try:
                    # Wait for orders in queue
                    order_id, order_request = await asyncio.wait_for(
                        self.order_queue.get(), timeout=1.0
                    )
                    
                    # Execute order
                    await self._execute_order(order_id, order_request)
                    
                except asyncio.TimeoutError:
                    # No orders in queue, continue
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in order execution loop: {e}")
                    await asyncio.sleep(1)
            
            logger.info("Order execution loop stopped")
            
        except Exception as e:
            logger.error(f"Fatal error in order execution loop: {e}")
    
    async def _execute_order(self, order_id: str, order_request: OrderRequest):
        """Execute a single order"""
        try:
            logger.info(f"Executing order {order_id}: {order_request.side.value} "
                       f"{order_request.quantity} {order_request.symbol}")
            
            # Update status
            self.order_status[order_id] = OrderStatus.SUBMITTED
            
            # Execute through Zerodha
            execution_result = await self._execute_zerodha_order(order_request)
            
            if execution_result['success']:
                # Order executed successfully
                self.order_status[order_id] = OrderStatus.FILLED
                
                # Record execution
                execution = OrderExecution(
                    order_id=order_id,
                    symbol=order_request.symbol,
                    side=order_request.side,
                    quantity=order_request.quantity,
                    price=execution_result['price'],
                    timestamp=datetime.utcnow(),
                    trade_id=execution_result['trade_id'],
                    brokerage=execution_result['brokerage'],
                    taxes=execution_result['taxes'],
                    net_amount=execution_result['net_amount'],
                    metadata={
                        'strategy_id': order_request.strategy_id,
                        'signal_id': order_request.signal_id,
                        'order_type': order_request.order_type.value
                    }
                )
                
                self.execution_history.append(execution)
                
                logger.info(f"Order {order_id} executed successfully at {execution_result['price']}")
                
            else:
                # Order execution failed
                self.order_status[order_id] = OrderStatus.REJECTED
                logger.error(f"Order {order_id} execution failed: {execution_result['message']}")
                
        except Exception as e:
            logger.error(f"Failed to execute order {order_id}: {e}")
            self.order_status[order_id] = OrderStatus.ERROR
    
    async def _validate_order(self, order_request: OrderRequest) -> Dict[str, Any]:
        """Validate order request"""
        try:
            # Basic validation
            if not order_request.symbol or not order_request.side or not order_request.quantity:
                return {'valid': False, 'message': 'Missing required fields'}
            
            if order_request.quantity <= 0:
                return {'valid': False, 'message': 'Quantity must be positive'}
            
            if order_request.order_type == OrderType.LIMIT and not order_request.price:
                return {'valid': False, 'message': 'Price required for limit orders'}
            
            if order_request.order_type in [OrderType.STOP_LOSS, OrderType.STOP_LOSS_MARKET] and not order_request.trigger_price:
                return {'valid': False, 'message': 'Trigger price required for stop loss orders'}
            
            # Check if Zerodha service is available
            if not self.zerodha_service or not self.zerodha_service.is_connected():
                return {'valid': False, 'message': 'Zerodha service not connected'}
            
            # Additional validations can be added here
            # - Check symbol exists
            # - Check trading hours
            # - Check position limits
            # - Check risk limits
            
            return {'valid': True, 'message': 'Order validation successful'}
            
        except Exception as e:
            logger.error(f"Order validation failed: {e}")
            return {'valid': False, 'message': f'Validation error: {str(e)}'}
    
    async def _execute_zerodha_order(self, order_request: OrderRequest) -> Dict[str, Any]:
        """Execute order through Zerodha API"""
        try:
            # Prepare order parameters for Zerodha
            kite_order_params = {
                'symbol': order_request.symbol,
                'side': order_request.side.value.lower(),
                'order_type': order_request.order_type.value,
                'quantity': order_request.quantity,
                'validity': order_request.validity
            }
            
            if order_request.price:
                kite_order_params['price'] = order_request.price
            
            if order_request.trigger_price:
                kite_order_params['trigger_price'] = order_request.trigger_price
            
            if order_request.disclosed_quantity:
                kite_order_params['disclosed_quantity'] = order_request.disclosed_quantity
            
            if order_request.tag:
                kite_order_params['tag'] = order_request.tag
            
            # Execute order
            result = await self.zerodha_service.place_order(kite_order_params)
            
            if result['success']:
                return {
                    'success': True,
                    'price': result.get('average_price', order_request.price or 0),
                    'trade_id': result.get('order_id', ''),
                    'brokerage': result.get('brokerage', 0),
                    'taxes': result.get('taxes', 0),
                    'net_amount': result.get('net_amount', 0)
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Zerodha order execution failed: {e}")
            return {
                'success': False,
                'message': f'Execution error: {str(e)}'
            }
    
    async def _cancel_zerodha_order(self, order_id: str, order_request: OrderRequest) -> bool:
        """Cancel order through Zerodha API"""
        try:
            # This would integrate with Zerodha's cancel order API
            # For now, return success
            logger.info(f"Cancelling order {order_id} through Zerodha")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel Zerodha order {order_id}: {e}")
            return False
    
    async def _modify_zerodha_order(self, order_id: str, order_request: OrderRequest, 
                                  modifications: Dict[str, Any]) -> bool:
        """Modify order through Zerodha API"""
        try:
            # This would integrate with Zerodha's modify order API
            # For now, return success
            logger.info(f"Modifying order {order_id} through Zerodha: {modifications}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to modify Zerodha order {order_id}: {e}")
            return False
    
    async def _get_zerodha_order_status(self, order_id: str, order_request: OrderRequest) -> Dict[str, Any]:
        """Get order status from Zerodha API"""
        try:
            # This would integrate with Zerodha's order status API
            # For now, return placeholder
            return {
                'status': 'pending',
                'filled_quantity': 0,
                'average_price': None
            }
            
        except Exception as e:
            logger.error(f"Failed to get Zerodha order status for {order_id}: {e}")
            return {}
    
    async def execute_signal(self, signal: StrategySignal, portfolio_value: float, 
                           risk_params: Dict[str, Any]) -> Optional[str]:
        """Execute a trading signal"""
        try:
            # Determine order side
            if signal.signal_type == "buy":
                side = OrderSide.BUY
            elif signal.signal_type == "sell":
                side = OrderSide.SELL
            else:
                logger.warning(f"Unknown signal type: {signal.signal_type}")
                return None
            
            # Calculate position size
            from engine.risk_management_engine import get_risk_management_engine
            risk_engine = get_risk_management_engine()
            
            position_size = await risk_engine.calculate_position_size(signal, portfolio_value, risk_params)
            if position_size <= 0:
                logger.warning(f"Invalid position size calculated: {position_size}")
                return None
            
            # Create order request
            order_request = OrderRequest(
                symbol=signal.symbol,
                side=side,
                order_type=OrderType.MARKET,  # Default to market order
                quantity=int(position_size),
                price=signal.price,
                strategy_id=signal.strategy_id,
                signal_id=signal.id,
                tag=f"Strategy_{signal.strategy_id}"
            )
            
            # Place order
            order_response = await self.place_order(order_request)
            
            if order_response.status == OrderStatus.PENDING:
                logger.info(f"Signal executed: {signal.signal_type} {signal.symbol} "
                           f"Order ID: {order_response.order_id}")
                return order_response.order_id
            else:
                logger.error(f"Signal execution failed: {order_response.message}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to execute signal: {e}")
            return None
    
    def get_order_queue_status(self) -> Dict[str, Any]:
        """Get order queue status"""
        return {
            'queue_size': self.order_queue.qsize(),
            'pending_orders': len([o for o in self.order_status.values() if o == OrderStatus.PENDING]),
            'submitted_orders': len([o for o in self.order_status.values() if o == OrderStatus.SUBMITTED]),
            'total_orders': len(self.pending_orders),
            'total_executions': len(self.execution_history)
        }


# Global order management engine instance
order_management_engine = OrderManagementEngine()


def get_order_management_engine() -> OrderManagementEngine:
    """Get the global order management engine instance"""
    return order_management_engine

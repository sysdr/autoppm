"""
Multi-Broker Support Engine for AutoPPM
Provides additional broker integrations, smart order routing, best execution algorithms, and cost optimization
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
from abc import ABC, abstractmethod
import json
import hashlib

from models.market_data import MarketData, HistoricalData
from engine.order_management_engine import get_order_management_engine
from engine.risk_management_engine import get_risk_management_engine


@dataclass
class BrokerConfig:
    """Configuration for broker integration"""
    broker_id: str
    broker_name: str
    api_key: str
    api_secret: str
    is_active: bool = True
    priority: int = 1  # Lower number = higher priority
    max_order_size: float = 1000000.0
    min_order_size: float = 100.0
    commission_rate: float = 0.001  # 0.1%
    slippage_estimate: float = 0.0005  # 0.05%
    execution_speed_ms: int = 100
    reliability_score: float = 0.95


@dataclass
class OrderRoutingDecision:
    """Result of order routing decision"""
    broker_id: str
    broker_name: str
    routing_reason: str
    expected_cost: float
    expected_slippage: float
    confidence_score: float
    alternative_brokers: List[str]


@dataclass
class ExecutionQuality:
    """Execution quality metrics"""
    broker_id: str
    order_id: str
    execution_price: float
    expected_price: float
    slippage: float
    execution_time_ms: int
    fill_quality: str  # 'excellent', 'good', 'fair', 'poor'
    cost_savings: float


@dataclass
class BrokerPerformance:
    """Broker performance metrics"""
    broker_id: str
    total_orders: int
    successful_orders: int
    average_slippage: float
    average_execution_time: float
    total_commission_paid: float
    reliability_score: float
    last_updated: datetime


class BrokerInterface(ABC):
    """Abstract base class for broker interfaces"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from broker API"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        pass
    
    @abstractmethod
    async def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place order with broker"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get market data from broker"""
        pass


class ZerodhaBroker(BrokerInterface):
    """Zerodha broker implementation"""
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self.connected = False
        self.kite = None
        logger.info(f"Initialized Zerodha broker: {config.broker_name}")
    
    async def connect(self) -> bool:
        """Connect to Zerodha API"""
        try:
            # This would integrate with your existing Zerodha service
            # For now, simulate connection
            self.connected = True
            logger.info(f"Connected to Zerodha broker: {self.config.broker_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Zerodha: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Zerodha API"""
        self.connected = False
        logger.info(f"Disconnected from Zerodha broker: {self.config.broker_name}")
        return True
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        # Placeholder implementation
        return {
            'account_id': f"ZERODHA_{self.config.broker_id}",
            'balance': 100000.0,
            'buying_power': 100000.0,
            'positions': []
        }
    
    async def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place order with Zerodha"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        # Placeholder implementation
        order_id = f"ZERODHA_{hashlib.md5(str(order_request).encode()).hexdigest()[:8]}"
        
        return {
            'order_id': order_id,
            'status': 'submitted',
            'broker_id': self.config.broker_id,
            'timestamp': datetime.now().isoformat()
        }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        # Placeholder implementation
        return True
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        # Placeholder implementation
        return {
            'order_id': order_id,
            'status': 'filled',
            'filled_quantity': 100,
            'average_price': 100.0
        }
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get market data from Zerodha"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        # Placeholder implementation
        return MarketData(
            symbol=symbol,
            price=100.0,
            volume=1000000,
            timestamp=datetime.now()
        )


class ICICIBroker(BrokerInterface):
    """ICICI Direct broker implementation"""
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self.connected = False
        logger.info(f"Initialized ICICI broker: {config.broker_name}")
    
    async def connect(self) -> bool:
        """Connect to ICICI API"""
        try:
            # Placeholder implementation
            self.connected = True
            logger.info(f"Connected to ICICI broker: {self.config.broker_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ICICI: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from ICICI API"""
        self.connected = False
        logger.info(f"Disconnected from ICICI broker: {self.config.broker_name}")
        return True
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        return {
            'account_id': f"ICICI_{self.config.broker_id}",
            'balance': 150000.0,
            'buying_power': 150000.0,
            'positions': []
        }
    
    async def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place order with ICICI"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        order_id = f"ICICI_{hashlib.md5(str(order_request).encode()).hexdigest()[:8]}"
        
        return {
            'order_id': order_id,
            'status': 'submitted',
            'broker_id': self.config.broker_id,
            'timestamp': datetime.now().isoformat()
        }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        return True
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'filled_quantity': 100,
            'average_price': 100.0
        }
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get market data from ICICI"""
        if not self.connected:
            raise ConnectionError("Not connected to broker")
        
        return MarketData(
            symbol=symbol,
            price=100.0,
            volume=1000000,
            timestamp=datetime.now()
        )


class MultiBrokerEngine:
    """
    Multi-Broker Support Engine for AutoPPM
    
    Features:
    - Multiple broker integrations (Zerodha, ICICI, etc.)
    - Smart order routing based on cost and performance
    - Best execution algorithms
    - Cost optimization and analysis
    - Broker performance monitoring
    - Failover and redundancy
    """
    
    def __init__(self):
        self.brokers: Dict[str, BrokerInterface] = {}
        self.broker_configs: Dict[str, BrokerConfig] = {}
        self.broker_performance: Dict[str, BrokerPerformance] = {}
        self.order_routing_history: List[OrderRoutingDecision] = []
        self.execution_quality_history: List[ExecutionQuality] = []
        
        # Initialize sub-engines
        self.order_engine = get_order_management_engine()
        self.risk_engine = get_risk_management_engine()
        
        # Load default broker configurations
        self._load_default_brokers()
        
        logger.info("Multi-Broker Engine initialized successfully")
    
    def _load_default_brokers(self):
        """Load default broker configurations"""
        default_brokers = [
            BrokerConfig(
                broker_id="zerodha_primary",
                broker_name="Zerodha Primary",
                api_key="your_api_key",
                api_secret="your_api_secret",
                priority=1,
                commission_rate=0.0005,  # 0.05%
                slippage_estimate=0.0003,
                execution_speed_ms=80,
                reliability_score=0.98
            ),
            BrokerConfig(
                broker_id="icici_backup",
                broker_name="ICICI Direct Backup",
                api_key="your_api_key",
                api_secret="your_api_secret",
                priority=2,
                commission_rate=0.001,  # 0.1%
                slippage_estimate=0.0005,
                execution_speed_ms=120,
                reliability_score=0.95
            ),
            BrokerConfig(
                broker_id="upstox_alternative",
                broker_name="Upstox Alternative",
                api_key="your_api_key",
                api_secret="your_api_secret",
                priority=3,
                commission_rate=0.0008,  # 0.08%
                slippage_estimate=0.0004,
                execution_speed_ms=100,
                reliability_score=0.93
            )
        ]
        
        for config in default_brokers:
            self.add_broker(config)
    
    def add_broker(self, config: BrokerConfig) -> bool:
        """Add a new broker to the system"""
        try:
            # Create broker instance based on type
            if 'zerodha' in config.broker_name.lower():
                broker = ZerodhaBroker(config)
            elif 'icici' in config.broker_name.lower():
                broker = ICICIBroker(config)
            else:
                # Default to generic broker interface
                broker = ZerodhaBroker(config)  # Placeholder
            
            self.brokers[config.broker_id] = broker
            self.broker_configs[config.broker_id] = config
            
            # Initialize performance tracking
            self.broker_performance[config.broker_id] = BrokerPerformance(
                broker_id=config.broker_id,
                total_orders=0,
                successful_orders=0,
                average_slippage=0.0,
                average_execution_time=0.0,
                total_commission_paid=0.0,
                reliability_score=config.reliability_score,
                last_updated=datetime.now()
            )
            
            logger.info(f"Added broker: {config.broker_name} ({config.broker_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add broker {config.broker_name}: {e}")
            return False
    
    async def connect_all_brokers(self) -> Dict[str, bool]:
        """Connect to all active brokers"""
        connection_results = {}
        
        for broker_id, broker in self.brokers.items():
            config = self.broker_configs[broker_id]
            if config.is_active:
                try:
                    success = await broker.connect()
                    connection_results[broker_id] = success
                    if success:
                        logger.info(f"Connected to broker: {config.broker_name}")
                    else:
                        logger.warning(f"Failed to connect to broker: {config.broker_name}")
                except Exception as e:
                    logger.error(f"Error connecting to broker {config.broker_name}: {e}")
                    connection_results[broker_id] = False
        
        return connection_results
    
    async def disconnect_all_brokers(self) -> Dict[str, bool]:
        """Disconnect from all brokers"""
        disconnection_results = {}
        
        for broker_id, broker in self.brokers.items():
            try:
                success = await broker.disconnect()
                disconnection_results[broker_id] = success
                if success:
                    logger.info(f"Disconnected from broker: {self.broker_configs[broker_id].broker_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from broker {broker_id}: {e}")
                disconnection_results[broker_id] = False
        
        return disconnection_results
    
    async def route_order(
        self, 
        order_request: Dict[str, Any],
        routing_strategy: str = "cost_optimized"
    ) -> OrderRoutingDecision:
        """Route order to best broker based on strategy"""
        try:
            logger.info(f"Routing order using strategy: {routing_strategy}")
            
            # Get available brokers
            available_brokers = self._get_available_brokers()
            if not available_brokers:
                raise ValueError("No available brokers")
            
            # Apply routing strategy
            if routing_strategy == "cost_optimized":
                selected_broker = self._select_cost_optimized_broker(order_request, available_brokers)
            elif routing_strategy == "speed_optimized":
                selected_broker = self._select_speed_optimized_broker(order_request, available_brokers)
            elif routing_strategy == "reliability_optimized":
                selected_broker = self._select_reliability_optimized_broker(order_request, available_brokers)
            elif routing_strategy == "hybrid":
                selected_broker = self._select_hybrid_broker(order_request, available_brokers)
            else:
                selected_broker = self._select_default_broker(order_request, available_brokers)
            
            # Calculate expected costs and slippage
            expected_cost = self._calculate_expected_cost(order_request, selected_broker)
            expected_slippage = self._calculate_expected_slippage(order_request, selected_broker)
            
            # Get alternative brokers
            alternative_brokers = self._get_alternative_brokers(selected_broker, available_brokers)
            
            # Create routing decision
            routing_decision = OrderRoutingDecision(
                broker_id=selected_broker['broker_id'],
                broker_name=selected_broker['broker_name'],
                routing_reason=f"Selected based on {routing_strategy} strategy",
                expected_cost=expected_cost,
                expected_slippage=expected_slippage,
                confidence_score=selected_broker['confidence_score'],
                alternative_brokers=alternative_brokers
            )
            
            # Store routing decision
            self.order_routing_history.append(routing_decision)
            
            logger.info(f"Order routed to {selected_broker['broker_name']} (cost: {expected_cost:.4f})")
            return routing_decision
            
        except Exception as e:
            logger.error(f"Failed to route order: {e}")
            raise
    
    async def execute_order_with_routing(
        self, 
        order_request: Dict[str, Any],
        routing_strategy: str = "cost_optimized"
    ) -> Dict[str, Any]:
        """Execute order with smart routing"""
        try:
            # Route order to best broker
            routing_decision = await self.route_order(order_request, routing_strategy)
            
            # Get broker instance
            broker = self.brokers[routing_decision.broker_id]
            
            # Place order with selected broker
            order_result = await broker.place_order(order_request)
            
            # Track execution quality
            execution_quality = await self._track_execution_quality(
                order_result, routing_decision, order_request
            )
            
            # Update broker performance
            await self._update_broker_performance(
                routing_decision.broker_id, execution_quality
            )
            
            # Combine results
            result = {
                'order_result': order_result,
                'routing_decision': routing_decision,
                'execution_quality': execution_quality,
                'broker_used': routing_decision.broker_name
            }
            
            logger.info(f"Order executed successfully with {routing_decision.broker_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute order with routing: {e}")
            raise
    
    async def get_best_execution_analysis(
        self, 
        symbol: str, 
        quantity: int,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """Analyze best execution options across brokers"""
        try:
            logger.info(f"Analyzing best execution for {symbol} x {quantity}")
            
            analysis_results = {}
            
            for broker_id, broker in self.brokers.items():
                if not self.broker_configs[broker_id].is_active:
                    continue
                
                try:
                    # Get market data from broker
                    market_data = await broker.get_market_data(symbol)
                    
                    # Calculate execution metrics
                    execution_metrics = self._calculate_execution_metrics(
                        broker_id, symbol, quantity, order_type, market_data
                    )
                    
                    analysis_results[broker_id] = {
                        'broker_name': self.broker_configs[broker_id].broker_name,
                        'market_data': market_data,
                        'execution_metrics': execution_metrics,
                        'total_cost': execution_metrics['total_cost'],
                        'execution_score': execution_metrics['execution_score']
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze broker {broker_id}: {e}")
                    continue
            
            # Sort by execution score
            sorted_results = sorted(
                analysis_results.items(),
                key=lambda x: x[1]['execution_score'],
                reverse=True
            )
            
            # Calculate cost savings
            if len(sorted_results) > 1:
                best_cost = sorted_results[0][1]['total_cost']
                for broker_id, result in analysis_results.items():
                    cost_savings = (result['total_cost'] - best_cost) / best_cost * 100
                    result['cost_savings_vs_best'] = cost_savings
            
            logger.info(f"Best execution analysis completed for {len(analysis_results)} brokers")
            return {
                'symbol': symbol,
                'quantity': quantity,
                'order_type': order_type,
                'broker_analysis': analysis_results,
                'recommended_broker': sorted_results[0][0] if sorted_results else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze best execution: {e}")
            raise
    
    async def optimize_broker_allocation(
        self, 
        portfolio_value: float,
        target_orders_per_day: int = 10
    ) -> Dict[str, Any]:
        """Optimize broker allocation for portfolio"""
        try:
            logger.info("Optimizing broker allocation")
            
            # Get broker performance metrics
            performance_data = {}
            for broker_id, performance in self.broker_performance.items():
                if performance.total_orders > 0:
                    performance_data[broker_id] = {
                        'reliability': performance.reliability_score,
                        'cost_efficiency': 1 / (1 + performance.average_slippage),
                        'speed_efficiency': 1 / (1 + performance.average_execution_time / 1000),
                        'total_orders': performance.total_orders
                    }
            
            # Calculate optimal allocation weights
            allocation_weights = self._calculate_allocation_weights(performance_data)
            
            # Calculate expected portfolio costs
            expected_costs = self._calculate_expected_portfolio_costs(
                portfolio_value, target_orders_per_day, allocation_weights
            )
            
            # Generate recommendations
            recommendations = self._generate_broker_recommendations(
                performance_data, allocation_weights, expected_costs
            )
            
            optimization_result = {
                'allocation_weights': allocation_weights,
                'expected_costs': expected_costs,
                'recommendations': recommendations,
                'performance_summary': performance_data,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Broker allocation optimization completed")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Failed to optimize broker allocation: {e}")
            raise
    
    async def get_broker_performance_summary(self) -> Dict[str, BrokerPerformance]:
        """Get performance summary for all brokers"""
        return self.broker_performance
    
    async def get_order_routing_history(self) -> List[OrderRoutingDecision]:
        """Get history of order routing decisions"""
        return self.order_routing_history
    
    async def get_execution_quality_history(self) -> List[ExecutionQuality]:
        """Get history of execution quality metrics"""
        return self.execution_quality_history
    
    # Private helper methods
    
    def _get_available_brokers(self) -> List[Dict[str, Any]]:
        """Get list of available brokers with metrics"""
        available_brokers = []
        
        for broker_id, broker in self.brokers.items():
            config = self.broker_configs[broker_id]
            performance = self.broker_performance[broker_id]
            
            if config.is_active:
                broker_info = {
                    'broker_id': broker_id,
                    'broker_name': config.broker_name,
                    'priority': config.priority,
                    'commission_rate': config.commission_rate,
                    'slippage_estimate': config.slippage_estimate,
                    'execution_speed_ms': config.execution_speed_ms,
                    'reliability_score': performance.reliability_score,
                    'success_rate': performance.successful_orders / max(performance.total_orders, 1),
                    'average_slippage': performance.average_slippage,
                    'average_execution_time': performance.average_execution_time
                }
                available_brokers.append(broker_info)
        
        return available_brokers
    
    def _select_cost_optimized_broker(
        self, 
        order_request: Dict[str, Any], 
        available_brokers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select broker based on cost optimization"""
        best_broker = None
        best_cost = float('inf')
        
        for broker in available_brokers:
            # Calculate total cost (commission + slippage)
            order_value = order_request.get('quantity', 0) * order_request.get('price', 0)
            commission_cost = order_value * broker['commission_rate']
            slippage_cost = order_value * broker['slippage_estimate']
            total_cost = commission_cost + slippage_cost
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_broker = broker
        
        if best_broker:
            best_broker['confidence_score'] = 0.9
            best_broker['expected_cost'] = best_cost
        
        return best_broker or available_brokers[0]
    
    def _select_speed_optimized_broker(
        self, 
        order_request: Dict[str, Any], 
        available_brokers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select broker based on speed optimization"""
        best_broker = None
        best_speed = float('inf')
        
        for broker in available_brokers:
            if broker['execution_speed_ms'] < best_speed:
                best_speed = broker['execution_speed_ms']
                best_broker = broker
        
        if best_broker:
            best_broker['confidence_score'] = 0.85
            best_broker['expected_speed'] = best_speed
        
        return best_broker or available_brokers[0]
    
    def _select_reliability_optimized_broker(
        self, 
        order_request: Dict[str, Any], 
        available_brokers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select broker based on reliability optimization"""
        best_broker = None
        best_reliability = 0.0
        
        for broker in available_brokers:
            reliability_score = broker['reliability_score'] * broker['success_rate']
            if reliability_score > best_reliability:
                best_reliability = reliability_score
                best_broker = broker
        
        if best_broker:
            best_broker['confidence_score'] = 0.95
            best_broker['expected_reliability'] = best_reliability
        
        return best_broker or available_brokers[0]
    
    def _select_hybrid_broker(
        self, 
        order_request: Dict[str, Any], 
        available_brokers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select broker using hybrid scoring"""
        best_broker = None
        best_score = 0.0
        
        for broker in available_brokers:
            # Calculate hybrid score (cost + speed + reliability)
            cost_score = 1 / (1 + broker['commission_rate'] + broker['slippage_estimate'])
            speed_score = 1 / (1 + broker['execution_speed_ms'] / 1000)
            reliability_score = broker['reliability_score'] * broker['success_rate']
            
            hybrid_score = (cost_score * 0.4 + speed_score * 0.3 + reliability_score * 0.3)
            
            if hybrid_score > best_score:
                best_score = hybrid_score
                best_broker = broker
        
        if best_broker:
            best_broker['confidence_score'] = 0.88
            best_broker['hybrid_score'] = best_score
        
        return best_broker or available_brokers[0]
    
    def _select_default_broker(
        self, 
        order_request: Dict[str, Any], 
        available_brokers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select broker using default strategy (priority-based)"""
        # Sort by priority and select highest priority broker
        sorted_brokers = sorted(available_brokers, key=lambda x: x['priority'])
        selected_broker = sorted_brokers[0]
        selected_broker['confidence_score'] = 0.8
        return selected_broker
    
    def _calculate_expected_cost(self, order_request: Dict[str, Any], broker: Dict[str, Any]) -> float:
        """Calculate expected cost for order"""
        order_value = order_request.get('quantity', 0) * order_request.get('price', 0)
        commission_cost = order_value * broker['commission_rate']
        slippage_cost = order_value * broker['slippage_estimate']
        return commission_cost + slippage_cost
    
    def _calculate_expected_slippage(self, order_request: Dict[str, Any], broker: Dict[str, Any]) -> float:
        """Calculate expected slippage for order"""
        order_value = order_request.get('quantity', 0) * order_request.get('price', 0)
        return order_value * broker['slippage_estimate']
    
    def _get_alternative_brokers(self, selected_broker: Dict[str, Any], available_brokers: List[Dict[str, Any]]) -> List[str]:
        """Get alternative broker IDs"""
        return [b['broker_id'] for b in available_brokers if b['broker_id'] != selected_broker['broker_id']]
    
    async def _track_execution_quality(
        self, 
        order_result: Dict[str, Any], 
        routing_decision: OrderRoutingDecision,
        order_request: Dict[str, Any]
    ) -> ExecutionQuality:
        """Track execution quality metrics"""
        # Placeholder implementation
        # In production, this would track actual execution metrics
        
        execution_quality = ExecutionQuality(
            broker_id=routing_decision.broker_id,
            order_id=order_result.get('order_id', 'unknown'),
            execution_price=order_request.get('price', 0),
            expected_price=order_request.get('price', 0),
            slippage=0.0,  # Would be calculated from actual execution
            execution_time_ms=100,  # Would be measured
            fill_quality='good',  # Would be determined by analysis
            cost_savings=0.0  # Would be calculated vs. alternatives
        )
        
        self.execution_quality_history.append(execution_quality)
        return execution_quality
    
    async def _update_broker_performance(self, broker_id: str, execution_quality: ExecutionQuality):
        """Update broker performance metrics"""
        if broker_id in self.broker_performance:
            performance = self.broker_performance[broker_id]
            performance.total_orders += 1
            performance.successful_orders += 1
            performance.average_slippage = (
                (performance.average_slippage * (performance.total_orders - 1) + execution_quality.slippage) / 
                performance.total_orders
            )
            performance.average_execution_time = (
                (performance.average_execution_time * (performance.total_orders - 1) + execution_quality.execution_time_ms) / 
                performance.total_orders
            )
            performance.last_updated = datetime.now()
    
    def _calculate_execution_metrics(
        self, 
        broker_id: str, 
        symbol: str, 
        quantity: int, 
        order_type: str, 
        market_data: MarketData
    ) -> Dict[str, Any]:
        """Calculate execution metrics for broker"""
        config = self.broker_configs[broker_id]
        performance = self.broker_performance[broker_id]
        
        # Calculate costs
        order_value = quantity * market_data.price
        commission_cost = order_value * config.commission_rate
        slippage_cost = order_value * config.slippage_estimate
        total_cost = commission_cost + slippage_cost
        
        # Calculate execution score
        cost_score = 1 / (1 + total_cost / order_value)
        speed_score = 1 / (1 + config.execution_speed_ms / 1000)
        reliability_score = performance.reliability_score
        
        execution_score = (cost_score * 0.5 + speed_score * 0.3 + reliability_score * 0.2)
        
        return {
            'commission_cost': commission_cost,
            'slippage_cost': slippage_cost,
            'total_cost': total_cost,
            'execution_score': execution_score,
            'expected_execution_time': config.execution_speed_ms,
            'reliability': reliability_score
        }
    
    def _calculate_allocation_weights(self, performance_data: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Calculate optimal allocation weights for brokers"""
        if not performance_data:
            return {}
        
        # Calculate composite scores
        broker_scores = {}
        for broker_id, data in performance_data.items():
            composite_score = (
                data['reliability'] * 0.4 +
                data['cost_efficiency'] * 0.4 +
                data['speed_efficiency'] * 0.2
            )
            broker_scores[broker_id] = composite_score
        
        # Normalize to weights
        total_score = sum(broker_scores.values())
        if total_score > 0:
            allocation_weights = {
                broker_id: score / total_score 
                for broker_id, score in broker_scores.items()
            }
        else:
            # Equal allocation if no performance data
            num_brokers = len(performance_data)
            allocation_weights = {broker_id: 1.0 / num_brokers for broker_id in performance_data.keys()}
        
        return allocation_weights
    
    def _calculate_expected_portfolio_costs(
        self, 
        portfolio_value: float, 
        target_orders_per_day: int, 
        allocation_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate expected portfolio costs with allocation"""
        expected_costs = {}
        
        for broker_id, weight in allocation_weights.items():
            config = self.broker_configs[broker_id]
            
            # Daily trading volume
            daily_volume = portfolio_value * weight * 0.1  # Assume 10% daily turnover
            
            # Expected costs
            commission_cost = daily_volume * config.commission_rate
            slippage_cost = daily_volume * config.slippage_estimate
            total_cost = commission_cost + slippage_cost
            
            expected_costs[broker_id] = {
                'daily_commission': commission_cost,
                'daily_slippage': slippage_cost,
                'daily_total': total_cost,
                'annual_total': total_cost * 252
            }
        
        return expected_costs
    
    def _generate_broker_recommendations(
        self, 
        performance_data: Dict[str, Dict[str, Any]], 
        allocation_weights: Dict[str, float],
        expected_costs: Dict[str, Any]
    ) -> List[str]:
        """Generate broker optimization recommendations"""
        recommendations = []
        
        # Find best performing broker
        if performance_data:
            best_broker = max(performance_data.items(), key=lambda x: x[1]['reliability'])
            recommendations.append(f"Consider increasing allocation to {best_broker[0]} for better reliability")
        
        # Check for cost optimization opportunities
        if len(expected_costs) > 1:
            costs = [(broker_id, data['annual_total']) for broker_id, data in expected_costs.items()]
            costs.sort(key=lambda x: x[1])
            
            if costs[1][1] - costs[0][1] > 1000:  # $1000 difference
                recommendations.append(f"Significant cost savings possible by reallocating to {costs[0][0]}")
        
        # Check for performance issues
        for broker_id, performance in performance_data.items():
            if performance['reliability'] < 0.9:
                recommendations.append(f"Monitor {broker_id} for reliability issues")
        
        if not recommendations:
            recommendations.append("Current broker allocation appears optimal")
        
        return recommendations


# Global instance
_multi_broker_engine: Optional[MultiBrokerEngine] = None


def get_multi_broker_engine() -> MultiBrokerEngine:
    """Get global multi-broker engine instance"""
    global _multi_broker_engine
    if _multi_broker_engine is None:
        _multi_broker_engine = MultiBrokerEngine()
    return _multi_broker_engine

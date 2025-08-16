"""
AutoPPM Momentum Strategy
Momentum-based trading strategy following trends
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

from engine.strategy_engine import BaseStrategy, StrategyContext
from models.strategy import StrategySignal


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self):
        super().__init__(
            name="MomentumStrategy",
            description="Momentum-based strategy that follows trends using moving averages and RSI",
            strategy_type="momentum",
            category="equity",
            risk_level="moderate"
        )
        
        # Strategy parameters
        self.default_parameters = {
            "short_window": 20,      # Short-term moving average window
            "long_window": 50,       # Long-term moving average window
            "rsi_window": 14,        # RSI calculation window
            "rsi_overbought": 70,    # RSI overbought threshold
            "rsi_oversold": 30,      # RSI oversold threshold
            "momentum_threshold": 0.02,  # Minimum momentum threshold
            "position_size_pct": 0.1,    # Position size as % of portfolio
            "stop_loss_pct": 0.05,       # Stop loss percentage
            "take_profit_pct": 0.15      # Take profit percentage
        }
        
        self.required_parameters = [
            "short_window", "long_window", "rsi_window", 
            "rsi_overbought", "rsi_oversold", "momentum_threshold"
        ]
        
        # Strategy state
        self.positions = {}  # symbol -> position data
        self.price_history = {}  # symbol -> price history
        self.signals_generated = 0
    
    async def initialize(self, context: StrategyContext) -> bool:
        """Initialize strategy with execution context"""
        try:
            logger.info(f"Initializing MomentumStrategy for execution {context.execution_id}")
            
            # Initialize price history for all symbols
            for symbol in context.symbols:
                self.price_history[symbol] = []
                self.positions[symbol] = {
                    "quantity": 0,
                    "entry_price": 0.0,
                    "entry_time": None,
                    "stop_loss": 0.0,
                    "take_profit": 0.0
                }
            
            # Validate parameters
            for param in self.required_parameters:
                if param not in context.parameters:
                    logger.warning(f"Missing required parameter: {param}, using default")
                    context.parameters[param] = self.default_parameters[param]
            
            logger.info("MomentumStrategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MomentumStrategy: {e}")
            return False
    
    async def generate_signals(self, context: StrategyContext, market_data: Dict[str, Any]) -> List[StrategySignal]:
        """Generate trading signals based on market data"""
        signals = []
        
        try:
            for symbol in context.symbols:
                if symbol not in market_data:
                    continue
                
                # Update price history
                price_data = market_data[symbol]
                current_price = price_data["price"]
                self.price_history[symbol].append({
                    "price": current_price,
                    "timestamp": price_data["timestamp"]
                })
                
                # Keep only recent price history for calculations
                max_history = max(context.parameters["long_window"], context.parameters["rsi_window"]) * 2
                if len(self.price_history[symbol]) > max_history:
                    self.price_history[symbol] = self.price_history[symbol][-max_history:]
                
                # Generate signal if we have enough data
                if len(self.price_history[symbol]) >= context.parameters["long_window"]:
                    signal = await self._analyze_symbol(symbol, context, current_price)
                    if signal:
                        signals.append(signal)
                        self.signals_generated += 1
            
            logger.debug(f"Generated {len(signals)} signals for execution {context.execution_id}")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    async def _analyze_symbol(self, symbol: str, context: StrategyContext, current_price: float) -> Optional[StrategySignal]:
        """Analyze a single symbol and generate signal if needed"""
        try:
            prices = [p["price"] for p in self.price_history[symbol]]
            
            # Calculate moving averages
            short_ma = self._calculate_moving_average(prices, context.parameters["short_window"])
            long_ma = self._calculate_moving_average(prices, context.parameters["long_window"])
            
            # Calculate RSI
            rsi = self._calculate_rsi(prices, context.parameters["rsi_window"])
            
            # Calculate momentum
            momentum = self._calculate_momentum(prices, context.parameters["short_window"])
            
            # Get current position
            position = self.positions[symbol]
            
            # Generate signals based on strategy logic
            signal = None
            
            if position["quantity"] == 0:  # No position - look for entry
                signal = await self._generate_entry_signal(
                    symbol, current_price, short_ma, long_ma, rsi, momentum, context
                )
            else:  # Has position - check for exit
                signal = await self._generate_exit_signal(
                    symbol, current_price, position, short_ma, long_ma, rsi, context
                )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return None
    
    async def _generate_entry_signal(self, symbol: str, current_price: float, short_ma: float, 
                                   long_ma: float, rsi: float, momentum: float, 
                                   context: StrategyContext) -> Optional[StrategySignal]:
        """Generate entry signal based on momentum indicators"""
        try:
            # Entry conditions for momentum strategy
            bullish_momentum = (
                short_ma > long_ma and  # Golden cross
                momentum > context.parameters["momentum_threshold"] and  # Positive momentum
                rsi < context.parameters["rsi_overbought"] and  # Not overbought
                rsi > 40  # Some strength but not oversold
            )
            
            if bullish_momentum:
                # Calculate signal strength based on momentum and RSI
                momentum_strength = min(momentum / context.parameters["momentum_threshold"], 2.0)
                rsi_strength = (rsi - 40) / 30  # Normalize RSI strength
                signal_strength = (momentum_strength + rsi_strength) / 2
                
                # Calculate confidence based on trend strength
                trend_strength = abs(short_ma - long_ma) / long_ma
                confidence = min(trend_strength * 10, 0.9)  # Cap at 90%
                
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="buy",
                    signal_strength=signal_strength,
                    confidence=confidence,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason=f"Momentum buy: MA crossover, RSI={rsi:.1f}, Momentum={momentum:.3f}"
                )
                
                logger.info(f"Generated BUY signal for {symbol}: strength={signal_strength:.2f}, confidence={confidence:.2f}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating entry signal for {symbol}: {e}")
            return None
    
    async def _generate_exit_signal(self, symbol: str, current_price: float, position: Dict[str, Any],
                                  short_ma: float, long_ma: float, rsi: float, 
                                  context: StrategyContext) -> Optional[StrategySignal]:
        """Generate exit signal based on momentum indicators and position management"""
        try:
            # Check stop loss and take profit
            if current_price <= position["stop_loss"]:
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="sell",
                    signal_strength=1.0,
                    confidence=0.95,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason="Stop loss triggered"
                )
                logger.info(f"Stop loss triggered for {symbol} at {current_price}")
                return signal
            
            if current_price >= position["take_profit"]:
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="sell",
                    signal_strength=0.8,
                    confidence=0.85,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason="Take profit reached"
                )
                logger.info(f"Take profit reached for {symbol} at {current_price}")
                return signal
            
            # Check momentum reversal
            bearish_momentum = (
                short_ma < long_ma and  # Death cross
                rsi > context.parameters["rsi_overbought"]  # Overbought
            )
            
            if bearish_momentum:
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="sell",
                    signal_strength=0.7,
                    confidence=0.75,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason=f"Momentum reversal: MA crossover, RSI={rsi:.1f}"
                )
                logger.info(f"Momentum reversal signal for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating exit signal for {symbol}: {e}")
            return None
    
    async def calculate_position_size(self, signal: StrategySignal, context: StrategyContext) -> float:
        """Calculate position size for a signal"""
        try:
            if signal.signal_type == "buy":
                # Calculate position size based on portfolio percentage and signal strength
                position_pct = context.parameters.get("position_size_pct", 0.1)
                adjusted_pct = position_pct * signal.signal_strength
                
                position_value = context.portfolio_value * adjusted_pct
                position_size = position_value / signal.price
                
                logger.info(f"Calculated position size: {position_size:.2f} shares of {signal.symbol}")
                return position_size
            
            elif signal.signal_type == "sell":
                # For sell signals, return the current position size
                position = self.positions.get(signal.symbol, {"quantity": 0})
                return position["quantity"]
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def should_exit(self, position: Dict[str, Any], context: StrategyContext) -> bool:
        """Determine if a position should be exited"""
        try:
            # Check if position has exceeded time limits or other criteria
            if position["entry_time"]:
                time_in_position = datetime.utcnow() - position["entry_time"]
                max_hold_time = timedelta(days=30)  # Maximum hold time
                
                if time_in_position > max_hold_time:
                    logger.info(f"Position {position['symbol']} held too long, should exit")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking exit criteria: {e}")
            return False
    
    async def cleanup(self, context: StrategyContext) -> None:
        """Cleanup resources when strategy stops"""
        try:
            logger.info(f"Cleaning up MomentumStrategy for execution {context.execution_id}")
            
            # Log final statistics
            logger.info(f"Strategy execution summary:")
            logger.info(f"  - Symbols monitored: {len(context.symbols)}")
            logger.info(f"  - Signals generated: {self.signals_generated}")
            logger.info(f"  - Active positions: {len([p for p in self.positions.values() if p['quantity'] != 0])}")
            
            # Clear strategy state
            self.positions.clear()
            self.price_history.clear()
            self.signals_generated = 0
            
        except Exception as e:
            logger.error(f"Error during strategy cleanup: {e}")
    
    def _calculate_moving_average(self, prices: List[float], window: int) -> float:
        """Calculate simple moving average"""
        if len(prices) < window:
            return prices[-1] if prices else 0.0
        
        return sum(prices[-window:]) / window
    
    def _calculate_rsi(self, prices: List[float], window: int) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < window + 1:
            return 50.0  # Neutral RSI if not enough data
        
        try:
            # Calculate price changes
            changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            # Separate gains and losses
            gains = [change if change > 0 else 0 for change in changes]
            losses = [-change if change < 0 else 0 for change in changes]
            
            # Calculate average gains and losses
            avg_gain = sum(gains[-window:]) / window
            avg_loss = sum(losses[-window:]) / window
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
    
    def _calculate_momentum(self, prices: List[float], window: int) -> float:
        """Calculate price momentum"""
        if len(prices) < window:
            return 0.0
        
        try:
            current_price = prices[-1]
            past_price = prices[-window]
            momentum = (current_price - past_price) / past_price
            return momentum
            
        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return 0.0

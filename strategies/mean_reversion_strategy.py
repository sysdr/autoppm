"""
AutoPPM Mean Reversion Strategy
Mean reversion strategy identifying overbought/oversold conditions
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

from engine.strategy_engine import BaseStrategy, StrategyContext
from models.strategy import StrategySignal


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy"""
    
    def __init__(self):
        super().__init__(
            name="MeanReversionStrategy",
            description="Mean reversion strategy that identifies overbought/oversold conditions",
            strategy_type="mean_reversion",
            category="equity",
            risk_level="moderate"
        )
        
        # Strategy parameters
        self.default_parameters = {
            "bollinger_window": 20,      # Bollinger Bands calculation window
            "bollinger_std": 2.0,        # Standard deviation multiplier
            "rsi_window": 14,            # RSI calculation window
            "rsi_overbought": 70,        # RSI overbought threshold
            "rsi_oversold": 30,          # RSI oversold threshold
            "mean_reversion_threshold": 0.1,  # Minimum deviation from mean
            "position_size_pct": 0.08,       # Position size as % of portfolio
            "stop_loss_pct": 0.08,          # Stop loss percentage
            "take_profit_pct": 0.12,        # Take profit percentage
            "max_hold_days": 15             # Maximum position hold time
        }
        
        self.required_parameters = [
            "bollinger_window", "bollinger_std", "rsi_window", 
            "rsi_overbought", "rsi_oversold", "mean_reversion_threshold"
        ]
        
        # Strategy state
        self.positions = {}  # symbol -> position data
        self.price_history = {}  # symbol -> price history
        self.signals_generated = 0
    
    async def initialize(self, context: StrategyContext) -> bool:
        """Initialize strategy with execution context"""
        try:
            logger.info(f"Initializing MeanReversionStrategy for execution {context.execution_id}")
            
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
            
            logger.info("MeanReversionStrategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MeanReversionStrategy: {e}")
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
                max_history = context.parameters["bollinger_window"] * 3
                if len(self.price_history[symbol]) > max_history:
                    self.price_history[symbol] = self.price_history[symbol][-max_history:]
                
                # Generate signal if we have enough data
                if len(self.price_history[symbol]) >= context.parameters["bollinger_window"]:
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
            
            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                prices, context.parameters["bollinger_window"], context.parameters["bollinger_std"]
            )
            
            # Calculate RSI
            rsi = self._calculate_rsi(prices, context.parameters["rsi_window"])
            
            # Calculate mean reversion metrics
            mean_deviation = self._calculate_mean_deviation(current_price, bb_middle)
            
            # Get current position
            position = self.positions[symbol]
            
            # Generate signals based on strategy logic
            signal = None
            
            if position["quantity"] == 0:  # No position - look for entry
                signal = await self._generate_entry_signal(
                    symbol, current_price, bb_upper, bb_middle, bb_lower, rsi, mean_deviation, context
                )
            else:  # Has position - check for exit
                signal = await self._generate_exit_signal(
                    symbol, current_price, position, bb_upper, bb_middle, bb_lower, rsi, context
                )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return None
    
    async def _generate_entry_signal(self, symbol: str, current_price: float, bb_upper: float, 
                                   bb_middle: float, bb_lower: float, rsi: float, 
                                   mean_deviation: float, context: StrategyContext) -> Optional[StrategySignal]:
        """Generate entry signal based on mean reversion indicators"""
        try:
            # Entry conditions for mean reversion strategy
            oversold_condition = (
                current_price <= bb_lower and  # Price below lower Bollinger Band
                rsi < context.parameters["rsi_oversold"] and  # RSI oversold
                mean_deviation > context.parameters["mean_reversion_threshold"]  # Significant deviation
            )
            
            overbought_condition = (
                current_price >= bb_upper and  # Price above upper Bollinger Band
                rsi > context.parameters["rsi_overbought"] and  # RSI overbought
                mean_deviation > context.parameters["mean_reversion_threshold"]  # Significant deviation
            )
            
            if oversold_condition:
                # Calculate signal strength based on deviation and RSI
                deviation_strength = min(mean_deviation / context.parameters["mean_reversion_threshold"], 2.0)
                rsi_strength = (context.parameters["rsi_oversold"] - rsi) / context.parameters["rsi_oversold"]
                signal_strength = (deviation_strength + rsi_strength) / 2
                
                # Calculate confidence based on deviation strength
                confidence = min(deviation_strength * 0.4, 0.85)  # Cap at 85%
                
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="buy",
                    signal_strength=signal_strength,
                    confidence=confidence,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason=f"Mean reversion buy: Oversold (BB lower), RSI={rsi:.1f}, Deviation={mean_deviation:.3f}"
                )
                
                logger.info(f"Generated BUY signal for {symbol}: strength={signal_strength:.2f}, confidence={confidence:.2f}")
                return signal
            
            elif overbought_condition:
                # Calculate signal strength for short position
                deviation_strength = min(mean_deviation / context.parameters["mean_reversion_threshold"], 2.0)
                rsi_strength = (rsi - context.parameters["rsi_overbought"]) / (100 - context.parameters["rsi_overbought"])
                signal_strength = (deviation_strength + rsi_strength) / 2
                
                # Calculate confidence based on deviation strength
                confidence = min(deviation_strength * 0.4, 0.85)  # Cap at 85%
                
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="sell",
                    signal_strength=signal_strength,
                    confidence=confidence,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason=f"Mean reversion sell: Overbought (BB upper), RSI={rsi:.1f}, Deviation={mean_deviation:.3f}"
                )
                
                logger.info(f"Generated SELL signal for {symbol}: strength={signal_strength:.2f}, confidence={confidence:.2f}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating entry signal for {symbol}: {e}")
            return None
    
    async def _generate_exit_signal(self, symbol: str, current_price: float, position: Dict[str, Any],
                                  bb_upper: float, bb_middle: float, bb_lower: float, 
                                  rsi: float, context: StrategyContext) -> Optional[StrategySignal]:
        """Generate exit signal based on mean reversion indicators and position management"""
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
            
            # Check mean reversion exit conditions
            mean_reversion_exit = False
            exit_reason = ""
            
            if position["quantity"] > 0:  # Long position
                # Exit when price approaches mean or RSI becomes overbought
                if (current_price >= bb_middle * 0.98 or  # Price near middle band
                    rsi > context.parameters["rsi_overbought"]):  # RSI overbought
                    mean_reversion_exit = True
                    exit_reason = f"Mean reversion exit: Price near mean, RSI={rsi:.1f}"
            
            elif position["quantity"] < 0:  # Short position
                # Exit when price approaches mean or RSI becomes oversold
                if (current_price <= bb_middle * 1.02 or  # Price near middle band
                    rsi < context.parameters["rsi_oversold"]):  # RSI oversold
                    mean_reversion_exit = True
                    exit_reason = f"Mean reversion exit: Price near mean, RSI={rsi:.1f}"
            
            if mean_reversion_exit:
                signal = StrategySignal(
                    strategy_execution_id=context.execution_id,
                    symbol=symbol,
                    signal_type="sell" if position["quantity"] > 0 else "buy",
                    signal_strength=0.7,
                    confidence=0.75,
                    price=current_price,
                    timestamp=datetime.utcnow(),
                    reason=exit_reason
                )
                logger.info(f"Mean reversion exit signal for {symbol}")
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
                position_pct = context.parameters.get("position_size_pct", 0.08)
                adjusted_pct = position_pct * signal.signal_strength
                
                position_value = context.portfolio_value * adjusted_pct
                position_size = position_value / signal.price
                
                logger.info(f"Calculated position size: {position_size:.2f} shares of {signal.symbol}")
                return position_size
            
            elif signal.signal_type == "sell":
                # For sell signals, return the current position size
                position = self.positions.get(signal.symbol, {"quantity": 0})
                return abs(position["quantity"])  # Return absolute value for short positions
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def should_exit(self, position: Dict[str, Any], context: StrategyContext) -> bool:
        """Determine if a position should be exited"""
        try:
            # Check if position has exceeded time limits
            if position["entry_time"]:
                time_in_position = datetime.utcnow() - position["entry_time"]
                max_hold_time = timedelta(days=context.parameters.get("max_hold_days", 15))
                
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
            logger.info(f"Cleaning up MeanReversionStrategy for execution {context.execution_id}")
            
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
    
    def _calculate_bollinger_bands(self, prices: List[float], window: int, std_multiplier: float) -> tuple:
        """Calculate Bollinger Bands"""
        if len(prices) < window:
            current_price = prices[-1] if prices else 0.0
            return current_price, current_price, current_price
        
        try:
            # Calculate moving average
            ma = sum(prices[-window:]) / window
            
            # Calculate standard deviation
            variance = sum((price - ma) ** 2 for price in prices[-window:]) / window
            std = variance ** 0.5
            
            # Calculate bands
            upper_band = ma + (std * std_multiplier)
            lower_band = ma - (std * std_multiplier)
            
            return upper_band, ma, lower_band
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            current_price = prices[-1] if prices else 0.0
            return current_price, current_price, current_price
    
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
    
    def _calculate_mean_deviation(self, current_price: float, mean_price: float) -> float:
        """Calculate deviation from mean as percentage"""
        try:
            if mean_price == 0:
                return 0.0
            
            deviation = abs(current_price - mean_price) / mean_price
            return deviation
            
        except Exception as e:
            logger.error(f"Error calculating mean deviation: {e}")
            return 0.0

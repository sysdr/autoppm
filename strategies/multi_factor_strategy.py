"""
AutoPPM Multi-Factor Strategy
Multi-factor strategy combining technical and fundamental indicators
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

from engine.strategy_engine import BaseStrategy, StrategyContext
from models.strategy import StrategySignal


class MultiFactorStrategy(BaseStrategy):
    """Multi-factor trading strategy"""
    
    def __init__(self):
        super().__init__(
            name="MultiFactorStrategy",
            description="Multi-factor strategy combining technical and fundamental indicators",
            strategy_type="multi_factor",
            category="equity",
            risk_level="moderate"
        )
        
        # Strategy parameters
        self.default_parameters = {
            "ma_short_window": 20,        # Short-term moving average
            "ma_long_window": 50,         # Long-term moving average
            "rsi_window": 14,             # RSI calculation window
            "rsi_overbought": 70,         # RSI overbought threshold
            "rsi_oversold": 30,           # RSI oversold threshold
            "volume_ma_window": 20,       # Volume moving average window
            "volume_threshold": 1.5,      # Volume spike threshold
            "volatility_window": 20,      # Volatility calculation window
            "volatility_threshold": 0.02, # Minimum volatility threshold
            "momentum_window": 10,        # Momentum calculation window
            "momentum_threshold": 0.01,   # Minimum momentum threshold
            "position_size_pct": 0.06,    # Position size as % of portfolio
            "stop_loss_pct": 0.06,        # Stop loss percentage
            "take_profit_pct": 0.18,      # Take profit percentage
            "max_hold_days": 25           # Maximum position hold time
        }
        
        self.required_parameters = [
            "ma_short_window", "ma_long_window", "rsi_window", 
            "rsi_overbought", "rsi_oversold", "volume_threshold",
            "volatility_threshold", "momentum_threshold"
        ]
        
        # Strategy state
        self.positions = {}  # symbol -> position data
        self.price_history = {}  # symbol -> price history
        self.volume_history = {}  # symbol -> volume history
        self.signals_generated = 0
    
    async def initialize(self, context: StrategyContext) -> bool:
        """Initialize strategy with execution context"""
        try:
            logger.info(f"Initializing MultiFactorStrategy for execution {context.execution_id}")
            
            # Initialize history for all symbols
            for symbol in context.symbols:
                self.price_history[symbol] = []
                self.volume_history[symbol] = []
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
            
            logger.info("MultiFactorStrategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MultiFactorStrategy: {e}")
            return False
    
    async def generate_signals(self, context: StrategyContext, market_data: Dict[str, Any]) -> List[StrategySignal]:
        """Generate trading signals based on market data"""
        signals = []
        
        try:
            for symbol in context.symbols:
                if symbol not in market_data:
                    continue
                
                # Update price and volume history
                price_data = market_data[symbol]
                current_price = price_data["price"]
                current_volume = price_data.get("volume", 1000000)  # Default volume
                
                self.price_history[symbol].append({
                    "price": current_price,
                    "timestamp": price_data["timestamp"]
                })
                
                self.volume_history[symbol].append({
                    "volume": current_volume,
                    "timestamp": price_data["timestamp"]
                })
                
                # Keep only recent history for calculations
                max_history = max(
                    context.parameters["ma_long_window"],
                    context.parameters["volume_ma_window"],
                    context.parameters["volatility_window"]
                ) * 2
                
                if len(self.price_history[symbol]) > max_history:
                    self.price_history[symbol] = self.price_history[symbol][-max_history:]
                if len(self.volume_history[symbol]) > max_history:
                    self.volume_history[symbol] = self.volume_history[symbol][-max_history:]
                
                # Generate signal if we have enough data
                if len(self.price_history[symbol]) >= context.parameters["ma_long_window"]:
                    signal = await self._analyze_symbol(symbol, context, current_price, current_volume)
                    if signal:
                        signals.append(signal)
                        self.signals_generated += 1
            
            logger.debug(f"Generated {len(signals)} signals for execution {context.execution_id}")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    async def _analyze_symbol(self, symbol: str, context: StrategyContext, 
                            current_price: float, current_volume: float) -> Optional[StrategySignal]:
        """Analyze a single symbol and generate signal if needed"""
        try:
            prices = [p["price"] for p in self.price_history[symbol]]
            volumes = [v["volume"] for v in self.volume_history[symbol]]
            
            # Calculate all factors
            factors = await self._calculate_factors(prices, volumes, context.parameters)
            
            # Get current position
            position = self.positions[symbol]
            
            # Generate signals based on strategy logic
            signal = None
            
            if position["quantity"] == 0:  # No position - look for entry
                signal = await self._generate_entry_signal(
                    symbol, current_price, factors, context
                )
            else:  # Has position - check for exit
                signal = await self._generate_exit_signal(
                    symbol, current_price, position, factors, context
                )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return None
    
    async def _calculate_factors(self, prices: List[float], volumes: List[float], 
                               parameters: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all technical factors"""
        try:
            factors = {}
            
            # Moving averages
            factors["ma_short"] = self._calculate_moving_average(prices, parameters["ma_short_window"])
            factors["ma_long"] = self._calculate_moving_average(prices, parameters["ma_long_window"])
            
            # RSI
            factors["rsi"] = self._calculate_rsi(prices, parameters["rsi_window"])
            
            # Volume analysis
            factors["volume_ma"] = self._calculate_moving_average(volumes, parameters["volume_ma_window"])
            factors["volume_ratio"] = volumes[-1] / factors["volume_ma"] if factors["volume_ma"] > 0 else 1.0
            
            # Volatility
            factors["volatility"] = self._calculate_volatility(prices, parameters["volatility_window"])
            
            # Momentum
            factors["momentum"] = self._calculate_momentum(prices, parameters["momentum_window"])
            
            # Trend strength
            factors["trend_strength"] = abs(factors["ma_short"] - factors["ma_long"]) / factors["ma_long"] if factors["ma_long"] > 0 else 0.0
            
            # Price position relative to moving averages
            current_price = prices[-1]
            factors["price_vs_ma"] = (current_price - factors["ma_long"]) / factors["ma_long"] if factors["ma_long"] > 0 else 0.0
            
            return factors
            
        except Exception as e:
            logger.error(f"Error calculating factors: {e}")
            return {}
    
    async def _generate_entry_signal(self, symbol: str, current_price: float, 
                                   factors: Dict[str, float], context: StrategyContext) -> Optional[StrategySignal]:
        """Generate entry signal based on multiple factors"""
        try:
            # Multi-factor entry conditions
            bullish_conditions = (
                factors["ma_short"] > factors["ma_long"] and  # Golden cross
                factors["rsi"] < context.parameters["rsi_overbought"] and  # Not overbought
                factors["rsi"] > 35 and  # Some strength
                factors["volume_ratio"] > context.parameters["volume_threshold"] and  # Volume confirmation
                factors["volatility"] > context.parameters["volatility_threshold"] and  # Sufficient volatility
                factors["momentum"] > context.parameters["momentum_threshold"] and  # Positive momentum
                factors["trend_strength"] > 0.01  # Clear trend
            )
            
            bearish_conditions = (
                factors["ma_short"] < factors["ma_long"] and  # Death cross
                factors["rsi"] > context.parameters["rsi_oversold"] and  # Not oversold
                factors["rsi"] < 65 and  # Some weakness
                factors["volume_ratio"] > context.parameters["volume_threshold"] and  # Volume confirmation
                factors["volatility"] > context.parameters["volatility_threshold"] and  # Sufficient volatility
                factors["momentum"] < -context.parameters["momentum_threshold"] and  # Negative momentum
                factors["trend_strength"] > 0.01  # Clear trend
            )
            
            if bullish_conditions:
                signal = await self._create_buy_signal(symbol, current_price, factors, context)
                return signal
            
            elif bearish_conditions:
                signal = await self._create_sell_signal(symbol, current_price, factors, context)
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating entry signal for {symbol}: {e}")
            return None
    
    async def _create_buy_signal(self, symbol: str, current_price: float, 
                               factors: Dict[str, float], context: StrategyContext) -> StrategySignal:
        """Create a buy signal with calculated strength and confidence"""
        try:
            # Calculate signal strength based on multiple factors
            ma_strength = min(factors["trend_strength"] * 100, 1.0)
            rsi_strength = (factors["rsi"] - 35) / 35  # Normalize RSI strength
            volume_strength = min(factors["volume_ratio"] / context.parameters["volume_threshold"], 1.0)
            momentum_strength = min(factors["momentum"] / context.parameters["momentum_threshold"], 1.0)
            
            # Weighted average of all factors
            signal_strength = (
                ma_strength * 0.3 +
                rsi_strength * 0.2 +
                volume_strength * 0.25 +
                momentum_strength * 0.25
            )
            
            # Calculate confidence based on factor consistency
            factor_scores = [ma_strength, rsi_strength, volume_strength, momentum_strength]
            confidence = min(sum(factor_scores) / len(factor_scores), 0.9)
            
            signal = StrategySignal(
                strategy_execution_id=context.execution_id,
                symbol=symbol,
                signal_type="buy",
                signal_strength=signal_strength,
                confidence=confidence,
                price=current_price,
                timestamp=datetime.utcnow(),
                reason=f"Multi-factor buy: MA crossover, RSI={factors['rsi']:.1f}, "
                       f"Volume={factors['volume_ratio']:.2f}x, Momentum={factors['momentum']:.3f}"
            )
            
            logger.info(f"Generated BUY signal for {symbol}: strength={signal_strength:.2f}, confidence={confidence:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"Error creating buy signal for {symbol}: {e}")
            raise
    
    async def _create_sell_signal(self, symbol: str, current_price: float, 
                                factors: Dict[str, float], context: StrategyContext) -> StrategySignal:
        """Create a sell signal with calculated strength and confidence"""
        try:
            # Calculate signal strength based on multiple factors
            ma_strength = min(factors["trend_strength"] * 100, 1.0)
            rsi_strength = (65 - factors["rsi"]) / 35  # Normalize RSI weakness
            volume_strength = min(factors["volume_ratio"] / context.parameters["volume_threshold"], 1.0)
            momentum_strength = min(abs(factors["momentum"]) / context.parameters["momentum_threshold"], 1.0)
            
            # Weighted average of all factors
            signal_strength = (
                ma_strength * 0.3 +
                rsi_strength * 0.2 +
                volume_strength * 0.25 +
                momentum_strength * 0.25
            )
            
            # Calculate confidence based on factor consistency
            factor_scores = [ma_strength, rsi_strength, volume_strength, momentum_strength]
            confidence = min(sum(factor_scores) / len(factor_scores), 0.9)
            
            signal = StrategySignal(
                strategy_execution_id=context.execution_id,
                symbol=symbol,
                signal_type="sell",
                signal_strength=signal_strength,
                confidence=confidence,
                price=current_price,
                timestamp=datetime.utcnow(),
                reason=f"Multi-factor sell: MA crossover, RSI={factors['rsi']:.1f}, "
                       f"Volume={factors['volume_ratio']:.2f}x, Momentum={factors['momentum']:.3f}"
            )
            
            logger.info(f"Generated SELL signal for {symbol}: strength={signal_strength:.2f}, confidence={confidence:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"Error creating sell signal for {symbol}: {e}")
            raise
    
    async def _generate_exit_signal(self, symbol: str, current_price: float, position: Dict[str, Any],
                                  factors: Dict[str, Any], context: StrategyContext) -> Optional[StrategySignal]:
        """Generate exit signal based on multiple factors and position management"""
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
            
            # Check multi-factor exit conditions
            exit_signal = await self._check_factor_exit_conditions(symbol, current_price, position, factors, context)
            if exit_signal:
                return exit_signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating exit signal for {symbol}: {e}")
            return None
    
    async def _check_factor_exit_conditions(self, symbol: str, current_price: float, 
                                          position: Dict[str, Any], factors: Dict[str, float], 
                                          context: StrategyContext) -> Optional[StrategySignal]:
        """Check if exit conditions are met based on factor analysis"""
        try:
            if position["quantity"] > 0:  # Long position
                # Exit when factors turn bearish
                bearish_exit = (
                    factors["ma_short"] < factors["ma_long"] and  # Death cross
                    factors["rsi"] > context.parameters["rsi_overbought"] and  # Overbought
                    factors["momentum"] < 0  # Negative momentum
                )
                
                if bearish_exit:
                    signal = StrategySignal(
                        strategy_execution_id=context.execution_id,
                        symbol=symbol,
                        signal_type="sell",
                        signal_strength=0.7,
                        confidence=0.75,
                        price=current_price,
                        timestamp=datetime.utcnow(),
                        reason=f"Factor exit: MA crossover, RSI={factors['rsi']:.1f}, Momentum={factors['momentum']:.3f}"
                    )
                    logger.info(f"Factor exit signal for {symbol}")
                    return signal
            
            elif position["quantity"] < 0:  # Short position
                # Exit when factors turn bullish
                bullish_exit = (
                    factors["ma_short"] > factors["ma_long"] and  # Golden cross
                    factors["rsi"] < context.parameters["rsi_oversold"] and  # Oversold
                    factors["momentum"] > 0  # Positive momentum
                )
                
                if bullish_exit:
                    signal = StrategySignal(
                        strategy_execution_id=context.execution_id,
                        symbol=symbol,
                        signal_type="buy",
                        signal_strength=0.7,
                        confidence=0.75,
                        price=current_price,
                        timestamp=datetime.utcnow(),
                        reason=f"Factor exit: MA crossover, RSI={factors['rsi']:.1f}, Momentum={factors['momentum']:.3f}"
                    )
                    logger.info(f"Factor exit signal for {symbol}")
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking factor exit conditions: {e}")
            return None
    
    async def calculate_position_size(self, signal: StrategySignal, context: StrategyContext) -> float:
        """Calculate position size for a signal"""
        try:
            if signal.signal_type == "buy":
                # Calculate position size based on portfolio percentage and signal strength
                position_pct = context.parameters.get("position_size_pct", 0.06)
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
                max_hold_time = timedelta(days=context.parameters.get("max_hold_days", 25))
                
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
            logger.info(f"Cleaning up MultiFactorStrategy for execution {context.execution_id}")
            
            # Log final statistics
            logger.info(f"Strategy execution summary:")
            logger.info(f"  - Symbols monitored: {len(context.symbols)}")
            logger.info(f"  - Signals generated: {self.signals_generated}")
            logger.info(f"  - Active positions: {len([p for p in self.positions.values() if p['quantity'] != 0])}")
            
            # Clear strategy state
            self.positions.clear()
            self.price_history.clear()
            self.volume_history.clear()
            self.signals_generated = 0
            
        except Exception as e:
            logger.error(f"Error during strategy cleanup: {e}")
    
    def _calculate_moving_average(self, values: List[float], window: int) -> float:
        """Calculate simple moving average"""
        if len(values) < window:
            return values[-1] if values else 0.0
        
        return sum(values[-window:]) / window
    
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
    
    def _calculate_volatility(self, prices: List[float], window: int) -> float:
        """Calculate price volatility"""
        if len(prices) < window:
            return 0.0
        
        try:
            # Calculate returns
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] > 0:
                    returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return 0.0
            
            # Calculate standard deviation of returns
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = variance ** 0.5
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
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

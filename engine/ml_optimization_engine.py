"""
Machine Learning Optimization Engine for AutoPPM
Provides ML-powered strategy optimization, predictive analytics, and advanced risk modeling
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import joblib
import os
import json

from models.market_data import HistoricalData, MarketData
from models.strategy import Strategy, StrategyExecution, StrategyPerformance
from engine.risk_management_engine import get_risk_management_engine
from engine.backtesting_engine import get_backtesting_engine


@dataclass
class MLModelConfig:
    """Configuration for ML models"""
    model_type: str  # 'random_forest', 'gradient_boosting', 'linear', 'ridge'
    feature_columns: List[str]
    target_column: str
    prediction_horizon: int  # days ahead to predict
    retrain_frequency: int  # days between retraining
    validation_split: float = 0.2
    max_features: Optional[int] = None
    n_estimators: int = 100
    random_state: int = 42


@dataclass
class MLPrediction:
    """ML model prediction result"""
    timestamp: datetime
    predicted_value: float
    confidence: float
    model_type: str
    features_used: List[str]
    prediction_horizon: int


@dataclass
class StrategyOptimizationResult:
    """Result of ML-based strategy optimization"""
    strategy_name: str
    original_parameters: Dict[str, Any]
    optimized_parameters: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    optimization_method: str
    timestamp: datetime


@dataclass
class RiskModelCalibration:
    """ML-based risk model calibration result"""
    model_type: str
    original_parameters: Dict[str, Any]
    calibrated_parameters: Dict[str, Any]
    calibration_score: float
    validation_period: str
    timestamp: datetime


class MLOptimizationEngine:
    """
    Machine Learning Optimization Engine for AutoPPM
    
    Features:
    - Predictive analytics for market movements
    - Automated strategy parameter optimization
    - ML-based risk model calibration
    - Performance prediction models
    - Feature engineering and selection
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.feature_importance: Dict[str, Dict[str, float]] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.optimization_history: List[StrategyOptimizationResult] = []
        self.calibration_history: List[RiskModelCalibration] = []
        
        # Initialize sub-engines
        self.risk_engine = get_risk_management_engine()
        self.backtesting_engine = get_backtesting_engine()
        
        # Model storage directory
        self.model_dir = "models/ml_models"
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.info("ML Optimization Engine initialized successfully")
    
    async def create_market_prediction_model(
        self, 
        symbol: str, 
        config: MLModelConfig
    ) -> str:
        """Create and train a market prediction model"""
        try:
            logger.info(f"Creating market prediction model for {symbol}")
            
            # Fetch historical data
            historical_data = await self._fetch_historical_data(symbol, days=365)
            if historical_data.empty:
                raise ValueError(f"No historical data available for {symbol}")
            
            # Prepare features and target
            features, target = self._prepare_features_target(historical_data, config)
            
            # Split data for training/validation
            train_size = int(len(features) * (1 - config.validation_split))
            X_train, X_val = features[:train_size], features[train_size:]
            y_train, y_val = target[:train_size], target[train_size:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Create and train model
            model = self._create_model(config)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_val_scaled)
            performance = self._evaluate_model(y_val, y_pred)
            
            # Store model and scaler
            model_id = f"{symbol}_{config.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            self.scalers[model_id] = scaler
            self.model_performance[model_id] = performance
            
            # Save model to disk
            self._save_model(model_id, model, scaler, config)
            
            logger.info(f"Market prediction model {model_id} created successfully")
            return model_id
            
        except Exception as e:
            logger.error(f"Failed to create market prediction model: {e}")
            raise
    
    async def predict_market_movement(
        self, 
        model_id: str, 
        current_data: pd.DataFrame
    ) -> MLPrediction:
        """Predict market movement using trained ML model"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            model = self.models[model_id]
            scaler = self.scalers[model_id]
            
            # Prepare features
            features = self._extract_features(current_data)
            features_scaled = scaler.transform([features])
            
            # Make prediction
            prediction = model.predict(features_scaled)[0]
            
            # Calculate confidence (using model's feature importance or prediction variance)
            confidence = self._calculate_prediction_confidence(model_id, features_scaled)
            
            # Create prediction result
            result = MLPrediction(
                timestamp=datetime.now(),
                predicted_value=prediction,
                confidence=confidence,
                model_type=model_id.split('_')[1],
                features_used=self._get_model_features(model_id),
                prediction_horizon=1  # Default to 1 day ahead
            )
            
            logger.info(f"Market prediction made: {prediction:.4f} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict market movement: {e}")
            raise
    
    async def optimize_strategy_parameters(
        self, 
        strategy_name: str, 
        historical_data: pd.DataFrame,
        optimization_method: str = "bayesian"
    ) -> StrategyOptimizationResult:
        """Optimize strategy parameters using ML and backtesting"""
        try:
            logger.info(f"Optimizing parameters for strategy: {strategy_name}")
            
            # Get current strategy parameters
            current_params = await self._get_strategy_parameters(strategy_name)
            
            # Define parameter search space
            param_space = self._define_parameter_space(strategy_name)
            
            # Perform optimization
            if optimization_method == "bayesian":
                best_params = await self._bayesian_optimization(
                    strategy_name, param_space, historical_data
                )
            elif optimization_method == "genetic":
                best_params = await self._genetic_optimization(
                    strategy_name, param_space, historical_data
                )
            else:
                best_params = await self._grid_search_optimization(
                    strategy_name, param_space, historical_data
                )
            
            # Evaluate improvement
            improvement = await self._evaluate_parameter_improvement(
                strategy_name, current_params, best_params, historical_data
            )
            
            # Create optimization result
            result = StrategyOptimizationResult(
                strategy_name=strategy_name,
                original_parameters=current_params,
                optimized_parameters=best_params,
                expected_improvement=improvement,
                confidence_level=0.85,  # Default confidence
                optimization_method=optimization_method,
                timestamp=datetime.now()
            )
            
            # Store result
            self.optimization_history.append(result)
            
            logger.info(f"Strategy optimization completed. Expected improvement: {improvement:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize strategy parameters: {e}")
            raise
    
    async def calibrate_risk_model(
        self, 
        model_type: str, 
        historical_data: pd.DataFrame
    ) -> RiskModelCalibration:
        """Calibrate risk model parameters using ML"""
        try:
            logger.info(f"Calibrating risk model: {model_type}")
            
            # Get current risk model parameters
            current_params = self._get_risk_model_parameters(model_type)
            
            # Prepare calibration data
            calibration_data = self._prepare_risk_calibration_data(historical_data)
            
            # Perform calibration
            calibrated_params = await self._calibrate_risk_parameters(
                model_type, calibration_data
            )
            
            # Validate calibration
            calibration_score = await self._validate_risk_calibration(
                model_type, calibrated_params, historical_data
            )
            
            # Create calibration result
            result = RiskModelCalibration(
                model_type=model_type,
                original_parameters=current_params,
                calibrated_parameters=calibrated_params,
                calibration_score=calibration_score,
                validation_period="1Y",
                timestamp=datetime.now()
            )
            
            # Store result
            self.calibration_history.append(result)
            
            # Apply calibrated parameters
            await self._apply_risk_calibration(model_type, calibrated_params)
            
            logger.info(f"Risk model calibration completed. Score: {calibration_score:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calibrate risk model: {e}")
            raise
    
    async def generate_ml_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Generate advanced ML features from market data"""
        try:
            features = market_data.copy()
            
            # Technical indicators
            features = self._add_technical_indicators(features)
            
            # Statistical features
            features = self._add_statistical_features(features)
            
            # Market microstructure features
            features = self._add_microstructure_features(features)
            
            # Sentiment features (placeholder for future integration)
            features = self._add_sentiment_features(features)
            
            # Clean and normalize features
            features = self._clean_features(features)
            
            logger.info(f"Generated {len(features.columns)} ML features")
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate ML features: {e}")
            raise
    
    async def get_model_performance(self, model_id: str) -> Dict[str, float]:
        """Get performance metrics for a specific model"""
        if model_id not in self.model_performance:
            raise ValueError(f"Model {model_id} not found")
        return self.model_performance[model_id]
    
    async def get_optimization_history(self) -> List[StrategyOptimizationResult]:
        """Get history of strategy optimizations"""
        return self.optimization_history
    
    async def get_calibration_history(self) -> List[RiskModelCalibration]:
        """Get history of risk model calibrations"""
        return self.calibration_history
    
    async def retrain_model(self, model_id: str) -> bool:
        """Retrain a specific model with new data"""
        try:
            logger.info(f"Retraining model: {model_id}")
            
            # Get model configuration
            config = self._get_model_config(model_id)
            
            # Fetch latest data
            symbol = model_id.split('_')[0]
            historical_data = await self._fetch_historical_data(symbol, days=365)
            
            # Retrain model
            await self.create_market_prediction_model(symbol, config)
            
            logger.info(f"Model {model_id} retrained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retrain model {model_id}: {e}")
            return False
    
    # Private helper methods
    
    async def _fetch_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical data for ML training"""
        # This would integrate with your data service
        # For now, return mock data
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(days).cumsum() + 100,
            'high': np.random.randn(days).cumsum() + 102,
            'low': np.random.randn(days).cumsum() + 98,
            'close': np.random.randn(days).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, days)
        })
        return data
    
    def _prepare_features_target(self, data: pd.DataFrame, config: MLModelConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for ML training"""
        # Generate features
        features_df = self._generate_basic_features(data)
        
        # Select specified features
        features = features_df[config.feature_columns].values
        
        # Create target (next day's return)
        target = (data['close'].shift(-1) / data['close'] - 1).dropna().values
        
        # Align features and target
        features = features[:-1]  # Remove last row (no target)
        
        return features, target
    
    def _generate_basic_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate basic technical features"""
        features = data.copy()
        
        # Price-based features
        features['returns'] = data['close'].pct_change()
        features['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        features['price_change'] = data['close'] - data['close'].shift(1)
        
        # Moving averages
        features['ma_5'] = data['close'].rolling(5).mean()
        features['ma_20'] = data['close'].rolling(20).mean()
        features['ma_50'] = data['close'].rolling(50).mean()
        
        # Volatility
        features['volatility_5'] = features['returns'].rolling(5).std()
        features['volatility_20'] = features['returns'].rolling(20).std()
        
        # Volume features
        features['volume_ma_5'] = data['volume'].rolling(5).mean()
        features['volume_ratio'] = data['volume'] / features['volume_ma_5']
        
        # Drop NaN values
        features = features.dropna()
        
        return features
    
    def _create_model(self, config: MLModelConfig) -> Any:
        """Create ML model based on configuration"""
        if config.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=config.n_estimators,
                max_features=config.max_features,
                random_state=config.random_state
            )
        elif config.model_type == 'gradient_boosting':
            return GradientBoostingRegressor(
                n_estimators=config.n_estimators,
                random_state=config.random_state
            )
        elif config.model_type == 'linear':
            return LinearRegression()
        elif config.model_type == 'ridge':
            return Ridge(random_state=config.random_state)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")
    
    def _evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Evaluate ML model performance"""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
        }
    
    def _save_model(self, model_id: str, model: Any, scaler: Any, config: MLModelConfig):
        """Save model and scaler to disk"""
        model_path = os.path.join(self.model_dir, f"{model_id}_model.pkl")
        scaler_path = os.path.join(self.model_dir, f"{model_id}_scaler.pkl")
        config_path = os.path.join(self.model_dir, f"{model_id}_config.json")
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save scaler
        joblib.dump(scaler, scaler_path)
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump({
                'model_type': config.model_type,
                'feature_columns': config.feature_columns,
                'target_column': config.target_column,
                'prediction_horizon': config.prediction_horizon,
                'retrain_frequency': config.retrain_frequency
            }, f)
    
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extract features from current market data"""
        # This would extract the same features used in training
        features_df = self._generate_basic_features(data)
        return features_df.iloc[-1].values
    
    def _calculate_prediction_confidence(self, model_id: str, features: np.ndarray) -> float:
        """Calculate confidence level for prediction"""
        # Simple confidence calculation based on feature values
        # In production, this could use model uncertainty estimation
        return 0.8  # Placeholder
    
    def _get_model_features(self, model_id: str) -> List[str]:
        """Get list of features used by a model"""
        # This would read from saved config
        return ['returns', 'ma_5', 'ma_20', 'volatility_5', 'volume_ratio']
    
    async def _get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get current parameters for a strategy"""
        # This would integrate with your strategy engine
        return {'lookback_period': 20, 'threshold': 0.02}
    
    def _define_parameter_space(self, strategy_name: str) -> Dict[str, List]:
        """Define parameter search space for optimization"""
        if 'momentum' in strategy_name.lower():
            return {
                'lookback_period': [10, 15, 20, 25, 30],
                'threshold': [0.01, 0.015, 0.02, 0.025, 0.03]
            }
        elif 'mean_reversion' in strategy_name.lower():
            return {
                'lookback_period': [20, 30, 40, 50],
                'std_dev': [1.5, 2.0, 2.5, 3.0]
            }
        else:
            return {
                'lookback_period': [15, 20, 25],
                'threshold': [0.02, 0.025, 0.03]
            }
    
    async def _bayesian_optimization(self, strategy_name: str, param_space: Dict, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform Bayesian optimization for strategy parameters"""
        # Placeholder implementation
        # In production, this would use libraries like scikit-optimize
        return {'lookback_period': 20, 'threshold': 0.02}
    
    async def _genetic_optimization(self, strategy_name: str, param_space: Dict, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform genetic algorithm optimization"""
        # Placeholder implementation
        return {'lookback_period': 25, 'threshold': 0.025}
    
    async def _grid_search_optimization(self, strategy_name: str, param_space: Dict, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform grid search optimization"""
        # Placeholder implementation
        return {'lookback_period': 22, 'threshold': 0.022}
    
    async def _evaluate_parameter_improvement(self, strategy_name: str, current_params: Dict, new_params: Dict, data: pd.DataFrame) -> float:
        """Evaluate expected improvement from parameter changes"""
        # Placeholder implementation
        return 5.2  # 5.2% expected improvement
    
    def _get_risk_model_parameters(self, model_type: str) -> Dict[str, Any]:
        """Get current parameters for risk model"""
        # This would integrate with your risk engine
        return {'confidence_level': 0.95, 'lookback_period': 252}
    
    def _prepare_risk_calibration_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for risk model calibration"""
        return data
    
    async def _calibrate_risk_parameters(self, model_type: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Calibrate risk model parameters"""
        # Placeholder implementation
        return {'confidence_level': 0.97, 'lookback_period': 300}
    
    async def _validate_risk_calibration(self, model_type: str, params: Dict[str, Any], data: pd.DataFrame) -> float:
        """Validate risk model calibration"""
        # Placeholder implementation
        return 0.92
    
    async def _apply_risk_calibration(self, model_type: str, params: Dict[str, Any]):
        """Apply calibrated parameters to risk model"""
        # This would update the risk engine
        logger.info(f"Applied calibrated parameters for {model_type}")
    
    def _get_model_config(self, model_id: str) -> MLModelConfig:
        """Get configuration for a specific model"""
        # This would read from saved config
        return MLModelConfig(
            model_type='random_forest',
            feature_columns=['returns', 'ma_5', 'ma_20', 'volatility_5', 'volume_ratio'],
            target_column='returns',
            prediction_horizon=1,
            retrain_frequency=30
        )
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators as features"""
        # RSI
        data['rsi'] = self._calculate_rsi(data['close'])
        
        # MACD
        data['macd'], data['macd_signal'] = self._calculate_macd(data['close'])
        
        # Bollinger Bands
        data['bb_upper'], data['bb_lower'] = self._calculate_bollinger_bands(data['close'])
        
        return data
    
    def _add_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features"""
        # Rolling statistics
        data['returns_skew'] = data['returns'].rolling(20).skew()
        data['returns_kurtosis'] = data['returns'].rolling(20).kurt()
        
        # Z-score
        data['price_zscore'] = (data['close'] - data['close'].rolling(20).mean()) / data['close'].rolling(20).std()
        
        return data
    
    def _add_microstructure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        # Price impact
        data['price_impact'] = data['volume'] * data['returns'].abs()
        
        # Volume-price relationship
        data['volume_price_corr'] = data['volume'].rolling(10).corr(data['close'])
        
        return data
    
    def _add_sentiment_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add sentiment features (placeholder)"""
        # In production, this would integrate with news/social media APIs
        data['sentiment_score'] = 0.0  # Neutral sentiment
        return data
    
    def _clean_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize features"""
        # Remove infinite values
        data = data.replace([np.inf, -np.inf], np.nan)
        
        # Forward fill NaN values
        data = data.fillna(method='ffill')
        
        # Drop remaining NaN rows
        data = data.dropna()
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, lower


# Global instance
_ml_optimization_engine: Optional[MLOptimizationEngine] = None


def get_ml_optimization_engine() -> MLOptimizationEngine:
    """Get global ML optimization engine instance"""
    global _ml_optimization_engine
    if _ml_optimization_engine is None:
        _ml_optimization_engine = MLOptimizationEngine()
    return _ml_optimization_engine

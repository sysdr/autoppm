"""
Strategy Marketplace Engine for AutoPPM
Provides third-party strategy integration, discovery, and marketplace management
"""

import asyncio
import json
import hashlib
import requests
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import yaml
from pathlib import Path
import importlib.util
import inspect
import zipfile
import tempfile
import shutil

from engine.autoppm_orchestrator import get_autoppm_orchestrator
from engine.ml_optimization_engine import get_ml_optimization_engine
from engine.backtesting_engine import get_backtesting_engine


@dataclass
class StrategyMetadata:
    """Strategy metadata for marketplace"""
    id: str
    name: str
    description: str
    author: str
    version: str
    category: str  # 'momentum', 'mean_reversion', 'arbitrage', 'ml', 'custom'
    tags: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    min_capital: float
    max_capital: float
    expected_return: float
    max_drawdown: float
    sharpe_ratio: float
    strategy_file: str
    config_file: str
    documentation: str
    license: str
    price: float  # 0.0 for free strategies
    rating: float
    downloads: int
    last_updated: datetime
    is_verified: bool = False
    is_active: bool = True


@dataclass
class StrategyReview:
    """Strategy review and rating"""
    id: str
    strategy_id: str
    user_id: str
    rating: int  # 1-5 stars
    comment: str
    timestamp: datetime
    helpful_votes: int = 0


@dataclass
class StrategyDownload:
    """Strategy download record"""
    id: str
    strategy_id: str
    user_id: str
    timestamp: datetime
    version: str
    ip_address: Optional[str] = None


@dataclass
class MarketplaceConfig:
    """Marketplace configuration"""
    name: str
    description: str
    api_endpoint: str
    rate_limit: int  # requests per minute
    max_file_size: int  # bytes
    allowed_file_types: List[str]
    api_key: Optional[str] = None
    verification_required: bool = True
    auto_update: bool = True


class StrategyMarketplaceEngine:
    """
    Strategy Marketplace Engine for AutoPPM
    
    Features:
    - Third-party strategy discovery and integration
    - Strategy marketplace management
    - Strategy validation and verification
    - Rating and review system
    - Automated strategy testing
    - Strategy version management
    """
    
    def __init__(self):
        self.orchestrator = get_autoppm_orchestrator()
        self.ml_engine = get_ml_optimization_engine()
        self.backtesting_engine = get_backtesting_engine()
        
        # Configuration
        self.config = self._load_config()
        self.marketplace_url = self.config.get('marketplace_url', 'https://marketplace.autoppm.com')
        self.api_key = self.config.get('api_key')
        
        # Local storage
        self.strategies_dir = Path("strategies/marketplace")
        self.strategies_dir.mkdir(parents=True, exist_ok=True)
        
        # Marketplace state
        self.available_strategies: Dict[str, StrategyMetadata] = {}
        self.downloaded_strategies: Dict[str, StrategyMetadata] = {}
        self.strategy_reviews: Dict[str, List[StrategyReview]] = {}
        self.download_history: List[StrategyDownload] = []
        
        # Initialize marketplace
        self._initialize_marketplace()
        
        logger.info("Strategy Marketplace Engine initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load marketplace configuration"""
        config_path = Path("config/marketplace_config.yaml")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load marketplace config: {e}")
        
        # Default configuration
        return {
            'marketplace_url': 'https://marketplace.autoppm.com',
            'api_key': None,
            'auto_update': True,
            'verification_required': True,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'allowed_file_types': ['.py', '.zip', '.tar.gz'],
            'rate_limit': 60,  # requests per minute
            'cache_duration_hours': 24
        }
    
    def _initialize_marketplace(self):
        """Initialize marketplace connection and load strategies"""
        try:
            # Load downloaded strategies
            self._load_downloaded_strategies()
            
            # Connect to marketplace
            if self.config.get('auto_update', True):
                self._update_available_strategies()
            
            logger.info("Marketplace initialization completed")
            
        except Exception as e:
            logger.error(f"Error initializing marketplace: {e}")
    
    def _load_downloaded_strategies(self):
        """Load already downloaded strategies"""
        try:
            for strategy_dir in self.strategies_dir.iterdir():
                if strategy_dir.is_dir():
                    metadata_file = strategy_dir / "metadata.yaml"
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = yaml.safe_load(f)
                            strategy_id = metadata.get('id')
                            if strategy_id:
                                self.downloaded_strategies[strategy_id] = StrategyMetadata(**metadata)
            
            logger.info(f"Loaded {len(self.downloaded_strategies)} downloaded strategies")
            
        except Exception as e:
            logger.error(f"Error loading downloaded strategies: {e}")
    
    def _update_available_strategies(self):
        """Update list of available strategies from marketplace"""
        try:
            # In production, this would make an API call to the marketplace
            # For now, we'll use mock data
            self.available_strategies = self._get_mock_strategies()
            
            logger.info(f"Updated available strategies: {len(self.available_strategies)} strategies")
            
        except Exception as e:
            logger.error(f"Error updating available strategies: {e}")
    
    def _get_mock_strategies(self) -> Dict[str, StrategyMetadata]:
        """Get mock strategies for development"""
        strategies = {
            'strategy_001': StrategyMetadata(
                id='strategy_001',
                name='Advanced Momentum Pro',
                description='Professional momentum strategy with ML optimization',
                author='QuantPro Solutions',
                version='2.1.0',
                category='momentum',
                tags=['ml', 'momentum', 'professional'],
                risk_level='medium',
                min_capital=100000,
                max_capital=10000000,
                expected_return=18.5,
                max_drawdown=12.0,
                sharpe_ratio=1.85,
                strategy_file='advanced_momentum_pro.py',
                config_file='config.yaml',
                documentation='https://docs.quantpro.com/advanced-momentum',
                license='commercial',
                price=299.99,
                rating=4.8,
                downloads=1250,
                last_updated=datetime.now() - timedelta(days=15),
                is_verified=True
            ),
            'strategy_002': StrategyMetadata(
                id='strategy_002',
                name='Mean Reversion Master',
                description='Advanced mean reversion with statistical arbitrage',
                author='StatArb Labs',
                version='1.5.2',
                category='mean_reversion',
                tags=['statistical', 'arbitrage', 'mean_reversion'],
                risk_level='low',
                min_capital=50000,
                max_capital=5000000,
                expected_return=15.2,
                max_drawdown=8.5,
                sharpe_ratio=2.15,
                strategy_file='mean_reversion_master.py',
                config_file='config.yaml',
                documentation='https://docs.statarblabs.com/mean-reversion',
                license='commercial',
                price=199.99,
                rating=4.6,
                downloads=890,
                last_updated=datetime.now() - timedelta(days=8),
                is_verified=True
            ),
            'strategy_003': StrategyMetadata(
                id='strategy_003',
                name='ML Sentiment Trader',
                description='AI-powered sentiment analysis trading strategy',
                author='AI Trading Systems',
                version='3.0.1',
                category='ml',
                tags=['ai', 'sentiment', 'nlp', 'ml'],
                risk_level='high',
                min_capital=200000,
                max_capital=20000000,
                expected_return=25.0,
                max_drawdown=18.0,
                sharpe_ratio=1.95,
                strategy_file='ml_sentiment_trader.py',
                config_file='config.yaml',
                documentation='https://docs.aitrading.com/sentiment-trader',
                license='commercial',
                price=499.99,
                rating=4.9,
                downloads=2100,
                last_updated=datetime.now() - timedelta(days=3),
                is_verified=True
            ),
            'strategy_004': StrategyMetadata(
                id='strategy_004',
                name='Free Momentum Starter',
                description='Free momentum strategy for beginners',
                author='AutoPPM Team',
                version='1.0.0',
                category='momentum',
                tags=['free', 'beginner', 'momentum'],
                risk_level='medium',
                min_capital=10000,
                max_capital=1000000,
                expected_return=12.0,
                max_drawdown=15.0,
                sharpe_ratio=1.25,
                strategy_file='free_momentum_starter.py',
                config_file='config.yaml',
                documentation='https://docs.autoppm.com/free-strategies',
                license='mit',
                price=0.0,
                rating=4.2,
                downloads=5000,
                last_updated=datetime.now() - timedelta(days=30),
                is_verified=True
            )
        }
        
        return strategies
    
    def search_strategies(self, 
                         query: Optional[str] = None,
                         category: Optional[str] = None,
                         risk_level: Optional[str] = None,
                         min_rating: Optional[float] = None,
                         max_price: Optional[float] = None,
                         tags: Optional[List[str]] = None) -> List[StrategyMetadata]:
        """Search for strategies based on criteria"""
        try:
            results = []
            
            for strategy in self.available_strategies.values():
                # Apply filters
                if not self._matches_search_criteria(strategy, query, category, risk_level, min_rating, max_price, tags):
                    continue
                
                results.append(strategy)
            
            # Sort by rating (descending)
            results.sort(key=lambda x: x.rating, reverse=True)
            
            logger.info(f"Search returned {len(results)} strategies")
            return results
            
        except Exception as e:
            logger.error(f"Error searching strategies: {e}")
            return []
    
    def _matches_search_criteria(self, 
                               strategy: StrategyMetadata,
                               query: Optional[str] = None,
                               category: Optional[str] = None,
                               risk_level: Optional[str] = None,
                               min_rating: Optional[float] = None,
                               max_price: Optional[float] = None,
                               tags: Optional[List[str]] = None) -> bool:
        """Check if strategy matches search criteria"""
        try:
            # Query filter
            if query:
                query_lower = query.lower()
                if (query_lower not in strategy.name.lower() and 
                    query_lower not in strategy.description.lower() and
                    not any(query_lower in tag.lower() for tag in strategy.tags)):
                    return False
            
            # Category filter
            if category and strategy.category != category:
                return False
            
            # Risk level filter
            if risk_level and strategy.risk_level != risk_level:
                return False
            
            # Rating filter
            if min_rating and strategy.rating < min_rating:
                return False
            
            # Price filter
            if max_price is not None and strategy.price > max_price:
                return False
            
            # Tags filter
            if tags:
                if not any(tag.lower() in [t.lower() for t in strategy.tags] for tag in tags):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking search criteria: {e}")
            return False
    
    def get_strategy_details(self, strategy_id: str) -> Optional[StrategyMetadata]:
        """Get detailed information about a strategy"""
        try:
            # Check available strategies
            if strategy_id in self.available_strategies:
                strategy = self.available_strategies[strategy_id]
                
                # Add reviews if available
                if strategy_id in self.strategy_reviews:
                    strategy.reviews = self.strategy_reviews[strategy_id]
                
                return strategy
            
            # Check downloaded strategies
            if strategy_id in self.downloaded_strategies:
                return self.downloaded_strategies[strategy_id]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting strategy details: {e}")
            return None
    
    def download_strategy(self, strategy_id: str, user_id: str = "default") -> Dict[str, Any]:
        """Download a strategy from the marketplace"""
        try:
            # Check if strategy exists
            if strategy_id not in self.available_strategies:
                return {'success': False, 'error': 'Strategy not found'}
            
            strategy = self.available_strategies[strategy_id]
            
            # Check if already downloaded
            if strategy_id in self.downloaded_strategies:
                return {'success': False, 'error': 'Strategy already downloaded'}
            
            # Create strategy directory
            strategy_dir = self.strategies_dir / strategy_id
            strategy_dir.mkdir(exist_ok=True)
            
            # Download strategy files (mock implementation)
            download_success = self._download_strategy_files(strategy, strategy_dir)
            
            if not download_success:
                return {'success': False, 'error': 'Failed to download strategy files'}
            
            # Validate strategy
            validation_result = self._validate_strategy(strategy_dir, strategy)
            
            if not validation_result['valid']:
                # Cleanup failed download
                shutil.rmtree(strategy_dir)
                return {'success': False, 'error': f'Strategy validation failed: {validation_result["error"]}'}
            
            # Add to downloaded strategies
            self.downloaded_strategies[strategy_id] = strategy
            
            # Record download
            download_record = StrategyDownload(
                id=f"download_{int(datetime.now().timestamp())}",
                strategy_id=strategy_id,
                user_id=user_id,
                timestamp=datetime.now(),
                version=strategy.version
            )
            self.download_history.append(download_record)
            
            # Update download count
            strategy.downloads += 1
            
            logger.info(f"Strategy downloaded successfully: {strategy.name}")
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'download_path': str(strategy_dir),
                'validation_result': validation_result
            }
            
        except Exception as e:
            logger.error(f"Error downloading strategy: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_strategy_files(self, strategy: StrategyMetadata, strategy_dir: Path) -> bool:
        """Download strategy files (mock implementation)"""
        try:
            # In production, this would download from the marketplace
            # For now, we'll create mock files
            
            # Create strategy file
            strategy_file = strategy_dir / strategy.strategy_file
            with open(strategy_file, 'w') as f:
                f.write(self._generate_mock_strategy_code(strategy))
            
            # Create config file
            config_file = strategy_dir / strategy.config_file
            with open(config_file, 'w') as f:
                yaml.dump(self._generate_mock_config(strategy), f)
            
            # Create metadata file
            metadata_file = strategy_dir / "metadata.yaml"
            with open(metadata_file, 'w') as f:
                yaml.dump(asdict(strategy), f)
            
            # Create documentation file
            doc_file = strategy_dir / "README.md"
            with open(doc_file, 'w') as f:
                f.write(self._generate_mock_documentation(strategy))
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading strategy files: {e}")
            return False
    
    def _generate_mock_strategy_code(self, strategy: StrategyMetadata) -> str:
        """Generate mock strategy code"""
        if strategy.category == 'momentum':
            return f'''
"""
{strategy.name} - {strategy.description}
Author: {strategy.author}
Version: {strategy.version}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from loguru import logger

class {strategy.name.replace(" ", "").replace("-", "")}Strategy:
    """{strategy.description}"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lookback_period = config.get('lookback_period', 20)
        self.momentum_threshold = config.get('momentum_threshold', 0.02)
        self.position_size = config.get('position_size', 0.1)
        
        logger.info(f"{strategy.name} strategy initialized")
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        try:
            # Calculate momentum indicators
            market_data['returns'] = market_data['close'].pct_change()
            market_data['momentum'] = market_data['returns'].rolling(self.lookback_period).mean()
            
            # Generate signals
            market_data['signal'] = 0
            market_data.loc[market_data['momentum'] > self.momentum_threshold, 'signal'] = 1
            market_data.loc[market_data['momentum'] < -self.momentum_threshold, 'signal'] = -1
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error generating signals: {{e}}")
            return market_data
    
    def calculate_position_size(self, signal: float, portfolio_value: float) -> float:
        """Calculate position size"""
        return signal * self.position_size * portfolio_value
    
    def should_exit(self, current_position: float, market_data: pd.DataFrame) -> bool:
        """Check if position should be exited"""
        # Simple exit logic
        return abs(current_position) < 0.01
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info(f"{strategy.name} strategy cleanup completed")
'''
        else:
            return f'''
"""
{strategy.name} - {strategy.description}
Author: {strategy.author}
Version: {strategy.version}
"""

# Strategy implementation would go here
# This is a placeholder for the actual strategy code
'''
    
    def _generate_mock_config(self, strategy: StrategyMetadata) -> Dict[str, Any]:
        """Generate mock configuration file"""
        return {
            'strategy_name': strategy.name,
            'version': strategy.version,
            'author': strategy.author,
            'category': strategy.category,
            'risk_level': strategy.risk_level,
            'parameters': {
                'lookback_period': 20,
                'momentum_threshold': 0.02,
                'position_size': 0.1,
                'stop_loss': 0.05,
                'take_profit': 0.10
            },
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            },
            'risk_limits': {
                'max_position_size': 0.2,
                'max_daily_loss': 0.05,
                'max_drawdown': 0.15
            }
        }
    
    def _generate_mock_documentation(self, strategy: StrategyMetadata) -> str:
        """Generate mock documentation"""
        return f"""# {strategy.name}

## Overview

{strategy.description}

## Author

{strategy.author}

## Version

{strategy.version}

## Category

{strategy.category}

## Risk Level

{strategy.risk_level}

## Expected Performance

- Expected Return: {strategy.expected_return}%
- Max Drawdown: {strategy.max_drawdown}%
- Sharpe Ratio: {strategy.sharpe_ratio}

## Installation

1. Download the strategy files
2. Place in your strategies directory
3. Configure the parameters
4. Test with backtesting

## Configuration

See `config.yaml` for detailed configuration options.

## Usage

This strategy can be used with the AutoPPM system.

## License

{strategy.license}

## Support

For support, contact the strategy author.
"""
    
    def _validate_strategy(self, strategy_dir: Path, strategy: StrategyMetadata) -> Dict[str, Any]:
        """Validate downloaded strategy"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'checks_passed': []
            }
            
            # Check required files
            required_files = [strategy.strategy_file, strategy.config_file, "metadata.yaml"]
            for file_name in required_files:
                file_path = strategy_dir / file_name
                if not file_path.exists():
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Required file missing: {file_name}")
                else:
                    validation_result['checks_passed'].append(f"File exists: {file_name}")
            
            # Check file sizes
            for file_name in required_files:
                file_path = strategy_dir / file_name
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    if file_size > self.config['max_file_size']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(f"File too large: {file_name} ({file_size} bytes)")
                    else:
                        validation_result['checks_passed'].append(f"File size OK: {file_name}")
            
            # Validate Python syntax (if it's a Python file)
            if strategy.strategy_file.endswith('.py'):
                syntax_valid = self._validate_python_syntax(strategy_dir / strategy.strategy_file)
                if not syntax_valid:
                    validation_result['valid'] = False
                    validation_result['errors'].append("Python syntax validation failed")
                else:
                    validation_result['checks_passed'].append("Python syntax validation passed")
            
            # Validate configuration
            config_valid = self._validate_config_file(strategy_dir / strategy.config_file)
            if not config_valid:
                validation_result['valid'] = False
                validation_result['errors'].append("Configuration validation failed")
            else:
                validation_result['checks_passed'].append("Configuration validation passed")
            
            # Check for malicious code (basic checks)
            security_check = self._security_check(strategy_dir)
            if not security_check['safe']:
                validation_result['valid'] = False
                validation_result['errors'].extend(security_check['issues'])
            else:
                validation_result['checks_passed'].append("Security check passed")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating strategy: {e}")
            return {
                'valid': False,
                'error': str(e),
                'errors': [str(e)],
                'warnings': [],
                'checks_passed': []
            }
    
    def _validate_python_syntax(self, python_file: Path) -> bool:
        """Validate Python file syntax"""
        try:
            with open(python_file, 'r') as f:
                code = f.read()
            
            # Basic syntax check
            compile(code, python_file.name, 'exec')
            return True
            
        except SyntaxError as e:
            logger.error(f"Python syntax error in {python_file}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking Python syntax: {e}")
            return False
    
    def _validate_config_file(self, config_file: Path) -> bool:
        """Validate configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ['strategy_name', 'version', 'author', 'category']
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required field in config: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating config file: {e}")
            return False
    
    def _security_check(self, strategy_dir: Path) -> Dict[str, Any]:
        """Basic security check for strategy files"""
        try:
            security_result = {
                'safe': True,
                'issues': []
            }
            
            # Check for suspicious imports
            suspicious_imports = [
                'os', 'subprocess', 'sys', 'shutil', 'tempfile',
                'urllib', 'requests', 'socket', 'multiprocessing'
            ]
            
            for file_path in strategy_dir.rglob('*.py'):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for suspicious_import in suspicious_imports:
                    if f'import {suspicious_import}' in content or f'from {suspicious_import}' in content:
                        security_result['issues'].append(f"Suspicious import found: {suspicious_import} in {file_path.name}")
                        security_result['safe'] = False
            
            # Check for eval/exec usage
            for file_path in strategy_dir.rglob('*.py'):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if 'eval(' in content or 'exec(' in content:
                    security_result['issues'].append(f"Dangerous function usage found: eval/exec in {file_path.name}")
                    security_result['safe'] = False
            
            return security_result
            
        except Exception as e:
            logger.error(f"Error during security check: {e}")
            return {
                'safe': False,
                'issues': [f"Security check error: {e}"]
            }
    
    def install_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Install a downloaded strategy into the AutoPPM system"""
        try:
            # Check if strategy is downloaded
            if strategy_id not in self.downloaded_strategies:
                return {'success': False, 'error': 'Strategy not downloaded'}
            
            strategy = self.downloaded_strategies[strategy_id]
            strategy_dir = self.strategies_dir / strategy_id
            
            # Load strategy module
            strategy_module = self._load_strategy_module(strategy_dir, strategy)
            
            if not strategy_module:
                return {'success': False, 'error': 'Failed to load strategy module'}
            
            # Register strategy with AutoPPM
            registration_success = self._register_strategy_with_autoppm(strategy, strategy_module)
            
            if not registration_success:
                return {'success': False, 'error': 'Failed to register strategy with AutoPPM'}
            
            logger.info(f"Strategy installed successfully: {strategy.name}")
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'message': 'Strategy installed and ready for use'
            }
            
        except Exception as e:
            logger.error(f"Error installing strategy: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_strategy_module(self, strategy_dir: Path, strategy: StrategyMetadata):
        """Load strategy module from file"""
        try:
            strategy_file = strategy_dir / strategy.strategy_file
            
            if not strategy_file.exists():
                logger.error(f"Strategy file not found: {strategy_file}")
                return None
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"marketplace_strategy_{strategy.id}",
                strategy_file
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"Failed to create module spec for {strategy_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logger.error(f"Error loading strategy module: {e}")
            return None
    
    def _register_strategy_with_autoppm(self, strategy: StrategyMetadata, strategy_module) -> bool:
        """Register strategy with AutoPPM system"""
        try:
            # Find strategy class in module
            strategy_class = None
            for name, obj in inspect.getmembers(strategy_module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, 'generate_signals') and
                    hasattr(obj, 'calculate_position_size')):
                    strategy_class = obj
                    break
            
            if not strategy_class:
                logger.error(f"No valid strategy class found in {strategy.name}")
                return False
            
            # Register with AutoPPM (placeholder)
            # In production, this would register with the strategy engine
            logger.info(f"Strategy class found: {strategy_class.__name__}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering strategy with AutoPPM: {e}")
            return False
    
    def test_strategy(self, strategy_id: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a strategy with backtesting"""
        try:
            # Check if strategy is downloaded
            if strategy_id not in self.downloaded_strategies:
                return {'success': False, 'error': 'Strategy not downloaded'}
            
            strategy = self.downloaded_strategies[strategy_id]
            
            # Run backtest
            backtest_result = self.backtesting_engine.run_backtest(
                strategy_name=strategy.name,
                start_date=test_config.get('start_date', '2023-01-01'),
                end_date=test_config.get('end_date', '2023-12-31'),
                initial_capital=test_config.get('initial_capital', 100000),
                symbols=test_config.get('symbols', ['RELIANCE', 'TCS', 'HDFC'])
            )
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'backtest_result': backtest_result
            }
            
        except Exception as e:
            logger.error(f"Error testing strategy: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_strategy_review(self, strategy_id: str, user_id: str, rating: int, comment: str) -> Dict[str, Any]:
        """Add a review for a strategy"""
        try:
            # Validate rating
            if not 1 <= rating <= 5:
                return {'success': False, 'error': 'Rating must be between 1 and 5'}
            
            # Create review
            review = StrategyReview(
                id=f"review_{int(datetime.now().timestamp())}",
                strategy_id=strategy_id,
                user_id=user_id,
                rating=rating,
                comment=comment,
                timestamp=datetime.now()
            )
            
            # Add to reviews
            if strategy_id not in self.strategy_reviews:
                self.strategy_reviews[strategy_id] = []
            
            self.strategy_reviews[strategy_id].append(review)
            
            # Update strategy rating
            if strategy_id in self.available_strategies:
                strategy = self.available_strategies[strategy_id]
                all_ratings = [r.rating for r in self.strategy_reviews[strategy_id]]
                strategy.rating = sum(all_ratings) / len(all_ratings)
            
            logger.info(f"Review added for strategy {strategy_id}")
            
            return {
                'success': True,
                'review_id': review.id,
                'message': 'Review added successfully'
            }
            
        except Exception as e:
            logger.error(f"Error adding review: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_strategy_reviews(self, strategy_id: str) -> List[StrategyReview]:
        """Get reviews for a strategy"""
        return self.strategy_reviews.get(strategy_id, [])
    
    def get_download_history(self, user_id: Optional[str] = None) -> List[StrategyDownload]:
        """Get download history"""
        if user_id:
            return [d for d in self.download_history if d.user_id == user_id]
        return self.download_history
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            total_strategies = len(self.available_strategies)
            total_downloads = sum(s.downloads for s in self.available_strategies.values())
            total_reviews = sum(len(reviews) for reviews in self.strategy_reviews.values())
            
            # Category breakdown
            categories = {}
            for strategy in self.available_strategies.values():
                category = strategy.category
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            # Price breakdown
            free_strategies = len([s for s in self.available_strategies.values() if s.price == 0])
            paid_strategies = total_strategies - free_strategies
            
            return {
                'total_strategies': total_strategies,
                'total_downloads': total_downloads,
                'total_reviews': total_reviews,
                'categories': categories,
                'free_strategies': free_strategies,
                'paid_strategies': paid_strategies,
                'average_rating': sum(s.rating for s in self.available_strategies.values()) / total_strategies if total_strategies > 0 else 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting marketplace stats: {e}")
            return {'error': str(e)}
    
    def update_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Update a strategy to the latest version"""
        try:
            # Check if strategy is downloaded
            if strategy_id not in self.downloaded_strategies:
                return {'success': False, 'error': 'Strategy not downloaded'}
            
            # Check if update is available
            if strategy_id not in self.available_strategies:
                return {'success': False, 'error': 'Strategy not available in marketplace'}
            
            downloaded_strategy = self.downloaded_strategies[strategy_id]
            available_strategy = self.available_strategies[strategy_id]
            
            if downloaded_strategy.version == available_strategy.version:
                return {'success': False, 'error': 'Strategy is already up to date'}
            
            # Download new version
            download_result = self.download_strategy(strategy_id)
            
            if not download_result['success']:
                return download_result
            
            logger.info(f"Strategy updated successfully: {available_strategy.name}")
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'strategy_name': available_strategy.name,
                'old_version': downloaded_strategy.version,
                'new_version': available_strategy.version,
                'message': 'Strategy updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Remove a downloaded strategy"""
        try:
            # Check if strategy is downloaded
            if strategy_id not in self.downloaded_strategies:
                return {'success': False, 'error': 'Strategy not downloaded'}
            
            strategy = self.downloaded_strategies[strategy_id]
            strategy_dir = self.strategies_dir / strategy_id
            
            # Remove strategy directory
            if strategy_dir.exists():
                shutil.rmtree(strategy_dir)
            
            # Remove from downloaded strategies
            del self.downloaded_strategies[strategy_id]
            
            logger.info(f"Strategy removed successfully: {strategy.name}")
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'message': 'Strategy removed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error removing strategy: {e}")
            return {'success': False, 'error': str(e)}


# Global instance
_strategy_marketplace_engine: Optional[StrategyMarketplaceEngine] = None


def get_strategy_marketplace_engine() -> StrategyMarketplaceEngine:
    """Get global strategy marketplace engine instance"""
    global _strategy_marketplace_engine
    if _strategy_marketplace_engine is None:
        _strategy_marketplace_engine = StrategyMarketplaceEngine()
    return _strategy_marketplace_engine

# AutoPPM Portfolio Dashboard

## Overview

The AutoPPM Portfolio Dashboard is a comprehensive web-based interface that provides real-time portfolio monitoring, strategy management, risk analytics, and trading controls. Built with Streamlit, it offers an intuitive and powerful way to manage your automated trading system.

## Features

### 📊 Portfolio Overview
- Real-time portfolio value and performance tracking
- Daily P&L and YTD returns
- Risk level indicators
- Active strategy status

### 💼 Portfolio Management
- Asset allocation visualization
- Sector exposure analysis
- Current holdings table
- Performance metrics (Sharpe ratio, max drawdown, volatility, beta)

### 🎯 Strategy Management
- Strategy performance comparison charts
- Start/stop strategy controls
- Backtest results display
- ML-powered strategy optimization

### ⚠️ Risk Management
- Current risk metrics (VaR, Expected Shortfall)
- Risk limits monitoring
- Real-time risk alerts
- Monte Carlo simulations
- Stress testing scenarios
- Comprehensive scenario analysis

### 📈 Trading & Execution
- Order placement forms
- Order status tracking
- Execution quality metrics
- Broker performance monitoring
- Smart order routing

### 📊 Advanced Analytics
- Machine learning insights
- Market predictions
- Strategy optimization results
- Returns analysis
- Risk analysis
- Correlation analysis

### ⚙️ System Settings
- Portfolio configuration
- Strategy parameters
- Risk management settings
- Alert preferences
- Broker configurations

## Installation

1. Install the UI requirements:
```bash
pip install -r requirements_ui.txt
```

2. Ensure all AutoPPM engines are properly installed and configured.

## Usage

### Quick Start

1. Launch the dashboard:
```bash
python run_dashboard.py
```

2. The dashboard will open in your default web browser at `http://localhost:8501`

3. Navigate through the different sections using the sidebar

### Manual Launch

1. Navigate to the UI directory:
```bash
cd ui
```

2. Run the Streamlit app:
```bash
streamlit run portfolio_dashboard.py
```

## Architecture

The dashboard integrates with all AutoPPM engines:

- **AutoPPM Orchestrator**: Core system management
- **ML Optimization Engine**: AI-powered insights and optimization
- **Advanced Risk Engine**: Risk modeling and analysis
- **Multi-Broker Engine**: Trading execution and monitoring

## Customization

### Adding New Pages

1. Create a new page method in the `PortfolioDashboard` class
2. Add the page to the sidebar navigation
3. Update the main content routing

### Custom Metrics

1. Modify the helper methods to return your custom data
2. Update the visualization components
3. Add new metric cards as needed

### Styling

1. Modify the CSS in the `run()` method
2. Update color schemes and layouts
3. Add custom components as needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all AutoPPM engines are properly installed
2. **Port Conflicts**: Change the port in `run_dashboard.py` if 8501 is occupied
3. **Data Loading**: Check that your data sources are accessible

### Performance

1. **Large Datasets**: Use data sampling for real-time updates
2. **Complex Calculations**: Implement caching for expensive operations
3. **Memory Usage**: Monitor memory consumption with large portfolios

## Development

### Adding New Features

1. **Data Sources**: Extend the helper methods to connect to your data
2. **Real-time Updates**: Implement Streamlit's session state for live data
3. **External APIs**: Add API integrations for market data and news

### Testing

1. **Unit Tests**: Test individual dashboard components
2. **Integration Tests**: Test dashboard-engine interactions
3. **UI Tests**: Test user interactions and workflows

## Security

- **Local Access**: Dashboard runs on localhost by default
- **Authentication**: Add user authentication for production use
- **Data Privacy**: Ensure sensitive portfolio data is protected

## Production Deployment

1. **Web Server**: Deploy behind a reverse proxy (nginx, Apache)
2. **SSL**: Enable HTTPS for secure access
3. **Monitoring**: Add logging and performance monitoring
4. **Scaling**: Use multiple Streamlit instances for high traffic

## Support

For issues and questions:
1. Check the AutoPPM main documentation
2. Review the engine integration points
3. Test with sample data first
4. Verify all dependencies are installed

## License

This dashboard is part of the AutoPPM automated trading system.

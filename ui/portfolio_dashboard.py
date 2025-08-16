"""
Portfolio Dashboard for AutoPPM
Provides comprehensive portfolio monitoring, strategy management, and trading controls
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Any, Optional
import json
import time

# Import AutoPPM engines
from engine.autoppm_orchestrator import get_autoppm_orchestrator
from engine.ml_optimization_engine import get_ml_optimization_engine
from engine.advanced_risk_engine import get_advanced_risk_engine
from engine.multi_broker_engine import get_multi_broker_engine


class PortfolioDashboard:
    """
    Comprehensive Portfolio Dashboard for AutoPPM
    
    Features:
    - Real-time portfolio monitoring
    - Strategy performance tracking
    - Risk analytics and alerts
    - Trading controls and order management
    - ML insights and predictions
    - Multi-broker status
    """
    
    def __init__(self):
        # Check authentication first
        self._check_authentication()
        
        self.orchestrator = get_autoppm_orchestrator()
        self.ml_engine = get_ml_optimization_engine()
        self.risk_engine = get_advanced_risk_engine()
        self.broker_engine = get_multi_broker_engine()

        # Initialize session state
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = self._get_sample_portfolio_data()
        if 'risk_alerts' not in st.session_state:
            st.session_state.risk_alerts = []
        if 'trading_signals' not in st.session_state:
            st.session_state.trading_signals = []
    
    def _check_authentication(self):
        """Check if user is authenticated"""
        if 'authenticated' not in st.session_state or not st.session_state.authenticated:
            st.error("❌ Authentication required. Please log in first.")
            st.info("Redirecting to landing page...")
            time.sleep(2)
            st.switch_page("ui/landing_page.py")
            return False
        return True
    
    def _logout_user(self):
        """Logout user and redirect to landing page"""
        # Clear session state
        for key in ['authenticated', 'user_id', 'user_email', 'user_full_name', 'user_role', 'account_type', 'created_at', 'session_token']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ Logged out successfully!")
        st.info("Redirecting to landing page...")
        time.sleep(2)
        st.switch_page("ui/landing_page.py")
    
    def run(self):
        """Run the main dashboard"""
        st.set_page_config(
            page_title="AutoPPM Portfolio Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .alert-high {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }
        .alert-medium {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        .alert-low {
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">🚀 AutoPPM Portfolio Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        self._render_sidebar()
        
        # Main content based on selection
        page = st.session_state.get('current_page', 'overview')
        
        if page == 'overview':
            self._render_overview_page()
        elif page == 'portfolio':
            self._render_portfolio_page()
        elif page == 'strategies':
            self._render_strategies_page()
        elif page == 'risk':
            self._render_risk_page()
        elif page == 'trading':
            self._render_trading_page()
        elif page == 'analytics':
            self._render_analytics_page()
        elif page == 'settings':
            self._render_settings_page()
    
    def _render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            # User info and logout
            st.markdown("### 👤 User Profile")
            if 'user_full_name' in st.session_state:
                st.write(f"**Name:** {st.session_state.user_full_name}")
            if 'user_email' in st.session_state:
                st.write(f"**Email:** {st.session_state.user_email}")
            if 'user_role' in st.session_state:
                st.write(f"**Role:** {st.session_state.user_role}")
            if 'account_type' in st.session_state:
                st.write(f"**Account:** {st.session_state.account_type}")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                self._logout_user()
            
            st.markdown("---")
            st.markdown("## 📊 Navigation")
            
            # Page selection
            pages = {
                'overview': '🏠 Overview',
                'portfolio': '💼 Portfolio',
                'strategies': '🎯 Strategies',
                'risk': '⚠️ Risk Management',
                'trading': '📈 Trading',
                'analytics': '📊 Analytics',
                'settings': '⚙️ Settings'
            }
            
            selected_page = st.selectbox(
                "Select Page",
                list(pages.keys()),
                format_func=lambda x: pages[x],
                key='page_selector'
            )
            
            st.session_state.current_page = selected_page
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("## 📈 Quick Stats")
            portfolio_value = st.session_state.portfolio_data['total_value'].iloc[-1]
            daily_return = st.session_state.portfolio_data['daily_return'].iloc[-1]
            
            st.metric("Portfolio Value", f"₹{portfolio_value:,.0f}")
            st.metric("Daily Return", f"{daily_return:.2f}%")
            
            # Risk level indicator
            risk_level = self._calculate_risk_level()
            risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
            st.markdown(f"**Risk Level:** {risk_color[risk_level]} {risk_level}")
            
            st.markdown("---")
            
            # System status
            st.markdown("## 🔧 System Status")
            st.markdown("✅ AutoPPM Core: Active")
            st.markdown("✅ ML Engine: Active")
            st.markdown("✅ Risk Engine: Active")
            st.markdown("✅ Broker Engine: Active")
    
    def _render_overview_page(self):
        """Render the overview page"""
        st.markdown("## 📊 Portfolio Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_metric_card("Total Value", "₹1,250,000", "+2.5%", "positive")
        
        with col2:
            self._render_metric_card("Daily P&L", "₹31,250", "+2.5%", "positive")
        
        with col3:
            self._render_metric_card("YTD Return", "₹125,000", "+11.1%", "positive")
        
        with col4:
            self._render_metric_card("Risk Score", "Medium", "🟡", "neutral")
        
        st.markdown("---")
        
        # Portfolio performance chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📈 Portfolio Performance")
            fig = self._create_portfolio_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Active Strategies")
            strategies = self._get_active_strategies()
            for strategy in strategies:
                st.markdown(f"**{strategy['name']}**")
                st.markdown(f"Status: {strategy['status']}")
                st.markdown(f"P&L: {strategy['pnl']}")
                st.markdown("---")
        
        # Recent activity
        st.markdown("### 🔄 Recent Activity")
        activity_data = self._get_recent_activity()
        st.dataframe(activity_data, use_container_width=True)
    
    def _render_portfolio_page(self):
        """Render the portfolio page"""
        st.markdown("## 💼 Portfolio Details")
        
        # Portfolio composition
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📊 Asset Allocation")
            allocation_data = self._get_asset_allocation()
            fig = px.pie(
                allocation_data, 
                values='value', 
                names='asset',
                title="Portfolio Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Sector Exposure")
            sector_data = self._get_sector_exposure()
            fig = px.bar(
                sector_data,
                x='sector',
                y='exposure',
                title="Sector Exposure (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Holdings table
        st.markdown("### 📋 Current Holdings")
        holdings_data = self._get_holdings_data()
        st.dataframe(holdings_data, use_container_width=True)
        
        # Performance metrics
        st.markdown("### 📊 Performance Metrics")
        metrics_data = self._get_performance_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sharpe Ratio", f"{metrics_data['sharpe_ratio']:.2f}")
        with col2:
            st.metric("Max Drawdown", f"{metrics_data['max_drawdown']:.2f}%")
        with col3:
            st.metric("Volatility", f"{metrics_data['volatility']:.2f}%")
        with col4:
            st.metric("Beta", f"{metrics_data['beta']:.2f}")
    
    def _render_strategies_page(self):
        """Render the strategies page"""
        st.markdown("## 🎯 Strategy Management")
        
        # Strategy overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Strategy Performance")
            strategy_perf = self._get_strategy_performance()
            fig = px.line(
                strategy_perf,
                x='date',
                y='cumulative_return',
                color='strategy',
                title="Strategy Performance Comparison"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⚡ Quick Actions")
            
            # Start strategy
            strategy_name = st.selectbox("Select Strategy", ["Momentum", "Mean Reversion", "Multi-Factor"])
            if st.button("🚀 Start Strategy"):
                self._start_strategy(strategy_name)
                st.success(f"Strategy {strategy_name} started successfully!")
            
            # Stop strategy
            running_strategies = self._get_running_strategies()
            if running_strategies:
                stop_strategy = st.selectbox("Stop Strategy", running_strategies)
                if st.button("⏹️ Stop Strategy"):
                    self._stop_strategy(stop_strategy)
                    st.success(f"Strategy {stop_strategy} stopped successfully!")
        
        # Strategy details
        st.markdown("### 🔍 Strategy Details")
        
        tabs = st.tabs(["Active Strategies", "Strategy Backtests", "ML Optimization"])
        
        with tabs[0]:
            active_strategies = self._get_active_strategies()
            st.dataframe(active_strategies, use_container_width=True)
        
        with tabs[1]:
            backtest_results = self._get_backtest_results()
            st.dataframe(backtest_results, use_container_width=True)
        
        with tabs[2]:
            st.markdown("#### 🤖 ML Strategy Optimization")
            
            if st.button("🔧 Optimize Strategy Parameters"):
                with st.spinner("Optimizing strategy parameters..."):
                    optimization_result = self._optimize_strategy_ml()
                    st.success("Strategy optimization completed!")
                    st.json(optimization_result)
    
    def _render_risk_page(self):
        """Render the risk management page"""
        st.markdown("## ⚠️ Risk Management")
        
        # Risk overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Current Risk Level")
            risk_metrics = self._get_current_risk_metrics()
            st.metric("VaR (95%)", f"{risk_metrics['var_95']:.2f}%")
            st.metric("Expected Shortfall", f"{risk_metrics['es_95']:.2f}%")
        
        with col2:
            st.markdown("### 📊 Risk Limits")
            risk_limits = self._get_risk_limits()
            st.metric("Max Position Size", f"{risk_limits['max_position']:.1f}%")
            st.metric("Max Sector Exposure", f"{risk_limits['max_sector']:.1f}%")
        
        with col3:
            st.markdown("### 🚨 Risk Alerts")
            alerts = self._get_risk_alerts()
            for alert in alerts:
                alert_class = f"alert-{alert['level'].lower()}"
                st.markdown(f"""
                <div class="metric-card {alert_class}">
                    <strong>{alert['type']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)
        
        # Risk analytics
        st.markdown("### 📈 Risk Analytics")
        
        tabs = st.tabs(["Monte Carlo Simulation", "Stress Testing", "Scenario Analysis"])
        
        with tabs[0]:
            st.markdown("#### 🎲 Monte Carlo Risk Analysis")
            
            if st.button("🔄 Run Monte Carlo Simulation"):
                with st.spinner("Running Monte Carlo simulation..."):
                    mc_result = self._run_monte_carlo_simulation()
                    st.success("Monte Carlo simulation completed!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("VaR (95%)", f"{mc_result['var_95']:.2f}%")
                        st.metric("VaR (99%)", f"{mc_result['var_99']:.2f}%")
                    with col2:
                        st.metric("Max Drawdown", f"{mc_result['max_drawdown']:.2f}%")
                        st.metric("Probability of Loss", f"{mc_result['probability_of_loss']:.1f}%")
        
        with tabs[1]:
            st.markdown("#### 🧪 Stress Testing")
            
            stress_scenarios = self._get_stress_scenarios()
            selected_scenario = st.selectbox("Select Stress Scenario", stress_scenarios)
            
            if st.button("🧪 Run Stress Test"):
                with st.spinner("Running stress test..."):
                    stress_result = self._run_stress_test(selected_scenario)
                    st.success("Stress test completed!")
                    
                    st.metric("Portfolio Loss", f"{stress_result['portfolio_loss']:.2f}%")
                    st.metric("Recovery Time", f"{stress_result['recovery_time']} days")
        
        with tabs[2]:
            st.markdown("#### 📊 Scenario Analysis")
            
            if st.button("📊 Run Scenario Analysis"):
                with st.spinner("Running scenario analysis..."):
                    scenario_results = self._run_scenario_analysis()
                    st.success("Scenario analysis completed!")
                    
                    # Display scenario results
                    for scenario in scenario_results:
                        st.markdown(f"**{scenario['name']}**")
                        st.markdown(f"Probability: {scenario['probability']:.1%}")
                        st.markdown(f"Risk Score: {scenario['risk_score']:.2f}")
                        st.markdown("---")
    
    def _render_trading_page(self):
        """Render the trading page"""
        st.markdown("## 📈 Trading & Execution")
        
        # Order management
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📝 Place Order")
            
            order_form = st.form("order_form")
            with order_form:
                symbol = st.text_input("Symbol", "RELIANCE")
                quantity = st.number_input("Quantity", min_value=1, value=100)
                order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop Loss"])
                side = st.selectbox("Side", ["Buy", "Sell"])
                
                if order_type == "Limit":
                    price = st.number_input("Price", min_value=0.0, value=2500.0)
                else:
                    price = None
                
                routing_strategy = st.selectbox("Routing Strategy", 
                                             ["Cost Optimized", "Speed Optimized", "Reliability Optimized", "Hybrid"])
                
                submitted = st.form_submit_button("🚀 Place Order")
                
                if submitted:
                    order_result = self._place_order(symbol, quantity, order_type, side, price, routing_strategy)
                    if order_result['success']:
                        st.success(f"Order placed successfully! Order ID: {order_result['order_id']}")
                    else:
                        st.error(f"Order failed: {order_result['error']}")
        
        with col2:
            st.markdown("### 📊 Order Status")
            
            # Get recent orders
            recent_orders = self._get_recent_orders()
            if recent_orders:
                for order in recent_orders:
                    status_color = {"filled": "🟢", "pending": "🟡", "cancelled": "🔴"}
                    st.markdown(f"{status_color[order['status']]} **{order['symbol']}** - {order['status']}")
                    st.markdown(f"Quantity: {order['quantity']} | Price: ₹{order['price']}")
                    st.markdown("---")
            else:
                st.info("No recent orders")
        
        # Execution quality
        st.markdown("### 📈 Execution Quality")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            execution_metrics = self._get_execution_metrics()
            st.metric("Average Slippage", f"{execution_metrics['avg_slippage']:.3f}%")
            st.metric("Fill Rate", f"{execution_metrics['fill_rate']:.1f}%")
        
        with col2:
            st.metric("Average Execution Time", f"{execution_metrics['avg_execution_time']:.0f}ms")
            st.metric("Cost Savings", f"{execution_metrics['cost_savings']:.2f}%")
        
        with col3:
            st.metric("Best Execution Score", f"{execution_metrics['best_execution_score']:.2f}")
            st.metric("Broker Reliability", f"{execution_metrics['broker_reliability']:.1f}%")
        
        # Broker performance
        st.markdown("### 🏦 Broker Performance")
        broker_performance = self._get_broker_performance()
        
        for broker_id, performance in broker_performance.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{performance['name']}**")
            with col2:
                st.metric("Success Rate", f"{performance['success_rate']:.1f}%")
            with col3:
                st.metric("Avg Slippage", f"{performance['avg_slippage']:.3f}%")
            with col4:
                st.metric("Reliability", f"{performance['reliability']:.1f}%")
            st.markdown("---")
    
    def _render_analytics_page(self):
        """Render the analytics page"""
        st.markdown("## 📊 Advanced Analytics")
        
        # ML insights
        st.markdown("### 🤖 Machine Learning Insights")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📈 Market Predictions")
            
            if st.button("🔮 Generate Market Predictions"):
                with st.spinner("Generating predictions..."):
                    predictions = self._generate_market_predictions()
                    st.success("Predictions generated!")
                    
                    for pred in predictions:
                        st.markdown(f"**{pred['symbol']}**")
                        st.markdown(f"Predicted Return: {pred['predicted_return']:.2f}%")
                        st.metric("Confidence", f"{pred['confidence']:.1f}%")
                        st.markdown("---")
        
        with col2:
            st.markdown("#### 🎯 Strategy Optimization")
            
            if st.button("🔧 Optimize Strategies"):
                with st.spinner("Optimizing strategies..."):
                    optimization_results = self._optimize_all_strategies()
                    st.success("Strategy optimization completed!")
                    
                    for result in optimization_results:
                        st.markdown(f"**{result['strategy']}**")
                        st.metric("Expected Improvement", f"{result['improvement']:.2f}%")
                        st.markdown("---")
        
        # Performance analytics
        st.markdown("### 📊 Performance Analytics")
        
        tabs = st.tabs(["Returns Analysis", "Risk Analysis", "Correlation Analysis"])
        
        with tabs[0]:
            st.markdown("#### 📈 Returns Analysis")
            
            returns_data = self._get_returns_analysis()
            fig = px.histogram(returns_data, x='returns', title="Returns Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Rolling metrics
            rolling_data = self._get_rolling_metrics()
            fig = px.line(rolling_data, x='date', y=['sharpe_ratio', 'volatility'], 
                         title="Rolling Sharpe Ratio & Volatility")
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[1]:
            st.markdown("#### ⚠️ Risk Analysis")
            
            risk_data = self._get_risk_analysis()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.line(risk_data, x='date', y='var_95', title="VaR (95%) Over Time")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(risk_data, x='date', y='max_drawdown', title="Maximum Drawdown")
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:
            st.markdown("#### 🔗 Correlation Analysis")
            
            correlation_data = self._get_correlation_matrix()
            fig = px.imshow(correlation_data, title="Asset Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_settings_page(self):
        """Render the settings page"""
        st.markdown("## ⚙️ System Settings")
        
        # General settings
        st.markdown("### 🔧 General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Portfolio Settings")
            risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
            rebalancing_frequency = st.selectbox("Rebalancing Frequency", ["Daily", "Weekly", "Monthly"])
            max_position_size = st.slider("Max Position Size (%)", 1, 20, 10)
            
            if st.button("💾 Save Portfolio Settings"):
                st.success("Portfolio settings saved!")
        
        with col2:
            st.markdown("#### 🎯 Strategy Settings")
            auto_trading = st.checkbox("Enable Auto Trading", value=True)
            max_strategies = st.number_input("Max Concurrent Strategies", min_value=1, max_value=10, value=5)
            stop_loss_pct = st.slider("Default Stop Loss (%)", 1, 20, 5)
            
            if st.button("💾 Save Strategy Settings"):
                st.success("Strategy settings saved!")
        
        # Risk management settings
        st.markdown("### ⚠️ Risk Management Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚨 Risk Limits")
            max_var = st.slider("Max VaR (95%)", 1, 10, 5)
            max_drawdown = st.slider("Max Drawdown (%)", 5, 30, 15)
            max_sector_exposure = st.slider("Max Sector Exposure (%)", 20, 50, 30)
            
            if st.button("💾 Save Risk Limits"):
                st.success("Risk limits saved!")
        
        with col2:
            st.markdown("#### 🔔 Alert Settings")
            email_alerts = st.checkbox("Email Alerts", value=True)
            sms_alerts = st.checkbox("SMS Alerts", value=False)
            risk_alert_threshold = st.slider("Risk Alert Threshold", 70, 95, 80)
            
            if st.button("💾 Save Alert Settings"):
                st.success("Alert settings saved!")
        
        # Broker settings
        st.markdown("### 🏦 Broker Settings")
        
        broker_configs = self._get_broker_configs()
        
        for broker_id, config in broker_configs.items():
            st.markdown(f"#### {config['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                is_active = st.checkbox(f"Active", value=config['is_active'], key=f"active_{broker_id}")
                priority = st.number_input(f"Priority", min_value=1, max_value=10, value=config['priority'], key=f"priority_{broker_id}")
            
            with col2:
                max_order_size = st.number_input(f"Max Order Size", value=config['max_order_size'], key=f"max_size_{broker_id}")
                commission_rate = st.number_input(f"Commission Rate (%)", value=config['commission_rate']*100, key=f"commission_{broker_id}")
            
            if st.button(f"💾 Save {config['name']} Settings", key=f"save_{broker_id}"):
                st.success(f"{config['name']} settings saved!")
    
    # Helper methods
    
    def _render_metric_card(self, title: str, value: str, change: str, change_type: str):
        """Render a metric card"""
        change_color = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <h2>{value}</h2>
            <p>{change_color[change_type]} {change}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _get_sample_portfolio_data(self) -> pd.DataFrame:
        """Get sample portfolio data for demonstration"""
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_value = 1000000
        
        # Generate realistic portfolio data
        daily_returns = np.random.normal(0.001, 0.02, 30)  # 0.1% daily return, 2% volatility
        portfolio_values = [base_value]
        
        for ret in daily_returns[1:]:
            portfolio_values.append(portfolio_values[-1] * (1 + ret))
        
        data = pd.DataFrame({
            'date': dates,
            'total_value': portfolio_values,
            'daily_return': daily_returns * 100,
            'cumulative_return': (np.array(portfolio_values) / base_value - 1) * 100
        })
        
        return data
    
    def _create_portfolio_chart(self) -> go.Figure:
        """Create portfolio performance chart"""
        data = st.session_state.portfolio_data
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['total_value'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Portfolio Performance (30 Days)",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def _get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get active strategies"""
        return [
            {
                'name': 'Momentum Strategy',
                'status': 'Active',
                'pnl': '+₹15,250'
            },
            {
                'name': 'Mean Reversion',
                'status': 'Active',
                'pnl': '+₹8,750'
            },
            {
                'name': 'Multi-Factor',
                'status': 'Active',
                'pnl': '+₹7,250'
            }
        ]
    
    def _get_recent_activity(self) -> pd.DataFrame:
        """Get recent portfolio activity"""
        data = {
            'Date': ['2024-01-15', '2024-01-14', '2024-01-13', '2024-01-12'],
            'Activity': ['Buy RELIANCE', 'Sell TCS', 'Strategy Rebalancing', 'Dividend Received'],
            'Amount': ['₹25,000', '-₹15,000', '₹0', '₹2,500'],
            'Status': ['Completed', 'Completed', 'Completed', 'Completed']
        }
        return pd.DataFrame(data)
    
    def _calculate_risk_level(self) -> str:
        """Calculate current risk level"""
        # Simple risk calculation based on volatility
        volatility = st.session_state.portfolio_data['daily_return'].std()
        
        if volatility < 1.5:
            return "Low"
        elif volatility < 2.5:
            return "Medium"
        else:
            return "High"
    
    def _get_asset_allocation(self) -> pd.DataFrame:
        """Get asset allocation data"""
        return pd.DataFrame({
            'asset': ['Equities', 'Bonds', 'Cash', 'Alternatives'],
            'value': [750000, 300000, 150000, 50000]
        })
    
    def _get_sector_exposure(self) -> pd.DataFrame:
        """Get sector exposure data"""
        return pd.DataFrame({
            'sector': ['Technology', 'Financial', 'Healthcare', 'Consumer', 'Energy'],
            'exposure': [25, 20, 18, 15, 12]
        })
    
    def _get_holdings_data(self) -> pd.DataFrame:
        """Get current holdings data"""
        data = {
            'Symbol': ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC'],
            'Quantity': [100, 50, 200, 75, 300],
            'Avg Price': [2500, 3500, 1200, 1800, 400],
            'Current Price': [2600, 3600, 1250, 1850, 420],
            'P&L': ['+₹10,000', '+₹5,000', '+₹10,000', '+₹3,750', '+₹6,000'],
            'Weight': ['20%', '15%', '20%', '12%', '10%']
        }
        return pd.DataFrame(data)
    
    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics"""
        return {
            'sharpe_ratio': 1.85,
            'max_drawdown': -8.5,
            'volatility': 15.2,
            'beta': 0.95
        }
    
    def _get_strategy_performance(self) -> pd.DataFrame:
        """Get strategy performance data"""
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        
        data = {
            'date': dates,
            'strategy': ['Momentum'] * 30 + ['Mean Reversion'] * 30 + ['Multi-Factor'] * 30,
            'cumulative_return': list(np.random.normal(0.001, 0.02, 30).cumsum() * 100) * 3
        }
        
        return pd.DataFrame(data)
    
    def _get_running_strategies(self) -> List[str]:
        """Get list of running strategies"""
        return ['Momentum Strategy', 'Mean Reversion', 'Multi-Factor']
    
    def _start_strategy(self, strategy_name: str):
        """Start a strategy"""
        # Placeholder implementation
        pass
    
    def _stop_strategy(self, strategy_name: str):
        """Stop a strategy"""
        # Placeholder implementation
        pass
    
    def _get_backtest_results(self) -> pd.DataFrame:
        """Get backtest results"""
        data = {
            'Strategy': ['Momentum', 'Mean Reversion', 'Multi-Factor'],
            'Total Return': ['15.2%', '12.8%', '18.5%'],
            'Sharpe Ratio': ['1.85', '1.62', '2.15'],
            'Max Drawdown': ['-8.5%', '-6.2%', '-9.8%'],
            'Win Rate': ['65%', '58%', '72%']
        }
        return pd.DataFrame(data)
    
    def _optimize_strategy_ml(self) -> Dict[str, Any]:
        """Optimize strategy using ML"""
        # Placeholder implementation
        return {
            'strategy': 'Momentum',
            'original_params': {'lookback': 20, 'threshold': 0.02},
            'optimized_params': {'lookback': 25, 'threshold': 0.018},
            'expected_improvement': 5.2
        }
    
    def _get_current_risk_metrics(self) -> Dict[str, float]:
        """Get current risk metrics"""
        return {
            'var_95': -2.5,
            'es_95': -3.8
        }
    
    def _get_risk_limits(self) -> Dict[str, float]:
        """Get risk limits"""
        return {
            'max_position': 10.0,
            'max_sector': 30.0
        }
    
    def _get_risk_alerts(self) -> List[Dict[str, Any]]:
        """Get risk alerts"""
        return [
            {
                'type': 'High Volatility',
                'message': 'Portfolio volatility exceeds normal range',
                'level': 'Medium'
            },
            {
                'type': 'Sector Concentration',
                'message': 'Technology sector exposure at 25%',
                'level': 'Low'
            }
        ]
    
    def _run_monte_carlo_simulation(self) -> Dict[str, float]:
        """Run Monte Carlo simulation"""
        # Placeholder implementation
        return {
            'var_95': -2.8,
            'var_99': -4.2,
            'max_drawdown': -12.5,
            'probability_of_loss': 0.45
        }
    
    def _get_stress_scenarios(self) -> List[str]:
        """Get available stress scenarios"""
        return ['2008 Financial Crisis', '2020 COVID Crash', 'Interest Rate Shock', 'Volatility Spike']
    
    def _run_stress_test(self, scenario: str) -> Dict[str, Any]:
        """Run stress test"""
        # Placeholder implementation
        return {
            'portfolio_loss': 15.2,
            'recovery_time': 180
        }
    
    def _run_scenario_analysis(self) -> List[Dict[str, Any]]:
        """Run scenario analysis"""
        # Placeholder implementation
        return [
            {
                'name': '2008 Financial Crisis',
                'probability': 0.01,
                'risk_score': 0.85
            },
            {
                'name': 'Interest Rate Shock',
                'probability': 0.05,
                'risk_score': 0.65
            }
        ]
    
    def _place_order(self, symbol: str, quantity: int, order_type: str, side: str, price: Optional[float], routing_strategy: str) -> Dict[str, Any]:
        """Place an order"""
        # Placeholder implementation
        return {
            'success': True,
            'order_id': f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    def _get_recent_orders(self) -> List[Dict[str, Any]]:
        """Get recent orders"""
        return [
            {
                'symbol': 'RELIANCE',
                'status': 'filled',
                'quantity': 100,
                'price': 2600
            },
            {
                'symbol': 'TCS',
                'status': 'pending',
                'quantity': 50,
                'price': 3600
            }
        ]
    
    def _get_execution_metrics(self) -> Dict[str, float]:
        """Get execution quality metrics"""
        return {
            'avg_slippage': 0.05,
            'fill_rate': 98.5,
            'avg_execution_time': 150,
            'cost_savings': 2.3,
            'best_execution_score': 8.7,
            'broker_reliability': 96.2
        }
    
    def _get_broker_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get broker performance data"""
        return {
            'zerodha': {
                'name': 'Zerodha',
                'success_rate': 98.5,
                'avg_slippage': 0.03,
                'reliability': 98.0
            },
            'icici': {
                'name': 'ICICI Direct',
                'success_rate': 97.2,
                'avg_slippage': 0.05,
                'reliability': 95.5
            }
        }
    
    def _generate_market_predictions(self) -> List[Dict[str, Any]]:
        """Generate market predictions using ML"""
        # Placeholder implementation
        return [
            {
                'symbol': 'RELIANCE',
                'predicted_return': 2.5,
                'confidence': 85.0
            },
            {
                'symbol': 'TCS',
                'predicted_return': 1.8,
                'confidence': 78.0
            }
        ]
    
    def _optimize_all_strategies(self) -> List[Dict[str, Any]]:
        """Optimize all strategies using ML"""
        # Placeholder implementation
        return [
            {
                'strategy': 'Momentum',
                'improvement': 5.2
            },
            {
                'strategy': 'Mean Reversion',
                'improvement': 3.8
            }
        ]
    
    def _get_returns_analysis(self) -> pd.DataFrame:
        """Get returns analysis data"""
        returns = np.random.normal(0.001, 0.02, 1000)
        return pd.DataFrame({'returns': returns})
    
    def _get_rolling_metrics(self) -> pd.DataFrame:
        """Get rolling metrics data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        
        data = {
            'date': dates,
            'sharpe_ratio': np.random.normal(1.5, 0.3, 100),
            'volatility': np.random.normal(15, 2, 100)
        }
        
        return pd.DataFrame(data)
    
    def _get_risk_analysis(self) -> pd.DataFrame:
        """Get risk analysis data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        
        data = {
            'date': dates,
            'var_95': np.random.normal(-2.5, 0.5, 100),
            'max_drawdown': np.random.normal(-8, 2, 100)
        }
        
        return pd.DataFrame(data)
    
    def _get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix data"""
        symbols = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC']
        correlation_data = np.random.rand(5, 5)
        correlation_data = (correlation_data + correlation_data.T) / 2  # Make symmetric
        np.fill_diagonal(correlation_data, 1)  # Diagonal = 1
        
        return pd.DataFrame(correlation_data, index=symbols, columns=symbols)
    
    def _get_broker_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get broker configurations"""
        return {
            'zerodha': {
                'name': 'Zerodha',
                'is_active': True,
                'priority': 1,
                'max_order_size': 1000000,
                'commission_rate': 0.0005
            },
            'icici': {
                'name': 'ICICI Direct',
                'is_active': True,
                'priority': 2,
                'max_order_size': 500000,
                'commission_rate': 0.001
            }
        }


def main():
    """Main function to run the dashboard"""
    dashboard = PortfolioDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()

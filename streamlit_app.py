"""
AutoPPM - Professional Automated Trading Platform
Main Streamlit application with modern, responsive UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="AutoPPM - Professional Trading Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional styling
st.markdown("""
<style>
    /* Modern color scheme and typography */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #d62728;
        --info-color: #17a2b8;
        --dark-bg: #0e1117;
        --card-bg: #262730;
        --text-color: #fafafa;
    }
    
    /* Professional header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: white;
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.9;
    }
    
    /* Modern card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Dashboard grid layout */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Responsive grid */
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    # Check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        show_professional_dashboard()
    else:
        show_modern_landing_page()

def show_modern_landing_page():
    """Show modern, professional landing page"""
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AutoPPM</h1>
        <p>Professional Automated Trading Platform</p>
        <p>AI-Powered Portfolio Management • Advanced Risk Analytics • Multi-Broker Integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
            <h3 style="color: #1f77b4;">🤖 AI-Powered Trading</h3>
            <ul style="color: #666;">
                <li>Machine learning algorithms</li>
                <li>Predictive analytics</li>
                <li>Automated decision making</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
            <h3 style="color: #1f77b4;">📊 Professional Analytics</h3>
            <ul style="color: #666;">
                <li>Real-time portfolio tracking</li>
                <li>Advanced risk metrics</li>
                <li>Performance attribution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
            <h3 style="color: #1f77b4;">🛡️ Risk Management</h3>
            <ul style="color: #666;">
                <li>Portfolio optimization</li>
                <li>Risk monitoring</li>
                <li>Compliance tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Authentication Section
    st.markdown("## 🔐 Get Started")
    
    tab1, tab2, tab3 = st.tabs(["📝 Sign Up", "🔑 Login", "🎬 Demo"])
    
    with tab1:
        show_signup_form()
    
    with tab2:
        show_login_form()
    
    with tab3:
        show_demo_section()

def show_professional_dashboard():
    """Show comprehensive, professional dashboard with all functionality"""
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 0.5rem; color: white; text-align: center; margin-bottom: 1rem;">
            <h3>🚀 AutoPPM</h3>
            <p style="font-size: 0.9rem; opacity: 0.9;">Professional Trading Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile
        st.markdown("### 👤 User Profile")
        st.info(f"**{st.session_state.get('user_full_name', 'Demo User')}**")
        st.caption(f"Email: {st.session_state.get('user_email', 'demo@example.com')}")
        st.caption(f"Role: {st.session_state.get('user_role', 'Trader')}")
        st.caption(f"Account: {st.session_state.get('account_type', 'Standard')}")
        
        st.markdown("---")
        
        # Main Navigation
        st.markdown("### 🧭 Navigation")
        page = st.selectbox(
            "Select Dashboard",
            ["🏠 Dashboard Home", "📊 Portfolio Management", "🔗 Broker Integration", "🤖 Strategy Management", "🛡️ Risk Analytics", "📈 Performance Reports", "⚙️ Settings & Configuration"]
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.success("Data refreshed!")
        
        if st.button("📊 Export Report", use_container_width=True):
            st.info("Report exported successfully!")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_full_name = None
            st.session_state.user_role = None
            st.session_state.account_type = None
            st.session_state.created_at = None
            st.rerun()
    
    # Main Dashboard Content
    if page == "🏠 Dashboard Home":
        show_dashboard_home()
    elif page == "📊 Portfolio Management":
        show_portfolio_management()
    elif page == "🔗 Broker Integration":
        show_broker_integration()
    elif page == "🤖 Strategy Management":
        show_strategy_management()
    elif page == "🛡️ Risk Analytics":
        show_risk_analytics()
    elif page == "📈 Performance Reports":
        show_performance_reports()
    elif page == "⚙️ Settings & Configuration":
        show_settings_configuration()

def show_dashboard_home():
    """Show comprehensive dashboard home with all key metrics and workflows"""
    st.title("🏠 Dashboard Home")
    st.markdown("Welcome to your AutoPPM Professional Trading Dashboard")
    
    # Key Metrics Row
    st.markdown("### 📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value="$1,247,893",
            delta="+$12,847 (+1.04%)"
        )
    
    with col2:
        st.metric(
            label="Daily P&L",
            value="$8,234",
            delta="+$1,234 (+17.6%)"
        )
    
    with col3:
        st.metric(
            label="YTD Return",
            value="24.7%",
            delta="+2.3%"
        )
    
    with col4:
        st.metric(
            label="Risk Level",
            value="Moderate",
            delta="-0.2%"
        )
    
    # Quick Access Workflows
    st.markdown("### 🚀 Quick Access Workflows")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">🔗 Connect Broker</h4>
            <p style="color: #666; font-size: 0.9rem;">Integrate your trading account</p>
            <button style="background: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Connect Now</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">🤖 Create Strategy</h4>
            <p style="color: #666; font-size: 0.9rem;">Build automated trading strategies</p>
            <button style="background: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Create Strategy</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">📊 View Reports</h4>
            <p style="color: #666; font-size: 0.9rem;">Access performance analytics</p>
            <button style="background: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">View Reports</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Portfolio Overview Chart
    st.markdown("### 📈 Portfolio Performance Overview")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
    
    fig = px.line(
        x=dates,
        y=portfolio_values,
        title="Portfolio Value Over Time",
        labels={'x': 'Date', 'y': 'Portfolio Value ($)'}
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.markdown("### 📋 Recent Activity")
    
    activities = [
        {"Time": "2 minutes ago", "Action": "Strategy 'Tech Momentum' executed", "Status": "✅ Success"},
        {"Time": "15 minutes ago", "Action": "Portfolio rebalancing completed", "Status": "✅ Success"},
        {"Time": "1 hour ago", "Action": "Risk alert: High volatility detected", "Status": "⚠️ Warning"},
        {"Time": "2 hours ago", "Action": "New broker connection established", "Status": "✅ Success"}
    ]
    
    for activity in activities:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.caption(activity["Time"])
        with col2:
            st.write(activity["Action"])
        with col3:
            st.write(activity["Status"])

def show_portfolio_management():
    """Show comprehensive portfolio management"""
    st.title("📊 Portfolio Management")
    
    # Portfolio Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Value", "$1,247,893", "+1.04%")
    with col2:
        st.metric("Cash", "$45,230", "+2.1%")
    with col3:
        st.metric("Invested", "$1,202,663", "+0.98%")
    with col4:
        st.metric("Unrealized P&L", "$12,847", "+1.04%")
    
    # Asset Allocation
    st.markdown("### 🎯 Asset Allocation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        assets = ['US Stocks', 'International Stocks', 'Bonds', 'Real Estate', 'Cash', 'Commodities']
        allocations = [45, 25, 15, 10, 3, 2]
        
        fig_pie = px.pie(
            values=allocations,
            names=assets,
            title="Current Asset Allocation"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### Top Holdings")
        holdings = [
            {"Symbol": "AAPL", "Name": "Apple Inc.", "Value": "$125,430", "Return": "+8.7%"},
            {"Symbol": "MSFT", "Name": "Microsoft Corp.", "Value": "$98,234", "Return": "+12.3%"},
            {"Symbol": "GOOGL", "Name": "Alphabet Inc.", "Value": "$87,654", "Return": "+5.4%"},
            {"Symbol": "AMZN", "Name": "Amazon.com Inc.", "Value": "$76,543", "Return": "+15.2%"},
            {"Symbol": "TSLA", "Name": "Tesla Inc.", "Value": "$65,432", "Return": "+3.8%"}
        ]
        
        for holding in holdings:
            st.markdown(f"""
            **{holding['Symbol']}** - {holding['Name']}
            - Value: {holding['Value']}
            - Return: {holding['Return']}
            ---
            """)
    
    # Portfolio Actions
    st.markdown("### ⚡ Portfolio Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Rebalance Portfolio", use_container_width=True):
            st.success("Portfolio rebalancing initiated!")
    
    with col2:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Portfolio report generated!")
    
    with col3:
        if st.button("💾 Export Data", use_container_width=True):
            st.success("Portfolio data exported!")

def show_broker_integration():
    """Show broker integration and management"""
    st.title("🔗 Broker Integration")
    
    # Connected Brokers
    st.markdown("### 🔌 Connected Brokers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">📈 Zerodha</h4>
            <p style="color: #2ca02c;">✅ Connected</p>
            <p style="color: #666; font-size: 0.9rem;">Account: XXXX1234</p>
            <p style="color: #666; font-size: 0.9rem;">Balance: ₹2,45,000</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">🏦 ICICI Direct</h4>
            <p style="color: #2ca02c;">✅ Connected</p>
            <p style="color: #666; font-size: 0.9rem;">Account: XXXX5678</p>
            <p style="color: #666; font-size: 0.9rem;">Balance: ₹1,85,000</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">➕ Add New</h4>
            <p style="color: #666; font-size: 0.9rem;">Connect additional broker</p>
            <button style="background: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Connect</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Add New Broker
    st.markdown("### 🔌 Connect New Broker")
    
    with st.form("broker_connection"):
        col1, col2 = st.columns(2)
        
        with col1:
            broker_name = st.selectbox("Select Broker", ["Zerodha", "ICICI Direct", "HDFC Securities", "Kotak Securities", "Angel One", "Upstox"])
            account_type = st.selectbox("Account Type", ["Demat + Trading", "Trading Only", "Demat Only"])
        
        with col2:
            api_key = st.text_input("API Key", type="password")
            api_secret = st.text_input("API Secret", type="password")
        
        if st.form_submit_button("🔗 Connect Broker"):
            st.success(f"Successfully connected to {broker_name}!")
    
    # Broker Status
    st.markdown("### 📊 Connection Status")
    
    status_data = {
        "Broker": ["Zerodha", "ICICI Direct"],
        "Status": ["🟢 Connected", "🟢 Connected"],
        "Last Sync": ["2 min ago", "5 min ago"],
        "Balance": ["₹2,45,000", "₹1,85,000"],
        "Actions": ["🔄 Sync", "🔄 Sync"]
    }
    
    st.dataframe(pd.DataFrame(status_data), use_container_width=True)

def show_strategy_management():
    """Show strategy management and creation"""
    st.title("🤖 Strategy Management")
    
    # Active Strategies
    st.markdown("### 🚀 Active Strategies")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">Tech Momentum</h4>
            <p style="color: #2ca02c;">🟢 Active</p>
            <p style="color: #666; font-size: 0.9rem;">Return: +18.7%</p>
            <p style="color: #666; font-size: 0.9rem;">Risk: Medium</p>
            <button style="background: #d62728; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Pause</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">Value Rotation</h4>
            <p style="color: #2ca02c;">🟢 Active</p>
            <p style="color: #666; font-size: 0.9rem;">Return: +12.3%</p>
            <p style="color: #666; font-size: 0.9rem;">Risk: Low</p>
            <button style="background: #d62728; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Pause</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1); text-align: center;">
            <h4 style="color: #1f77b4;">➕ Create New</h4>
            <p style="color: #666; font-size: 0.9rem;">Build new strategy</p>
            <button style="background: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">Create</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Create New Strategy
    st.markdown("### 🎯 Create New Strategy")
    
    with st.form("strategy_creation"):
        col1, col2 = st.columns(2)
        
        with col1:
            strategy_name = st.text_input("Strategy Name")
            strategy_type = st.selectbox("Strategy Type", ["Momentum", "Mean Reversion", "Arbitrage", "Statistical Arbitrage", "Trend Following"])
            time_horizon = st.selectbox("Time Horizon", ["Intraday", "Daily", "Weekly", "Monthly"])
            risk_level = st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"])
        
        with col2:
            max_position_size = st.number_input("Max Position Size (%)", min_value=1, max_value=100, value=10)
            stop_loss = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=5.0)
            take_profit = st.number_input("Take Profit (%)", min_value=0.1, max_value=100.0, value=15.0)
            rebalance_frequency = st.selectbox("Rebalance Frequency", ["Daily", "Weekly", "Monthly"])
        
        if st.form_submit_button("🚀 Create Strategy"):
            st.success(f"Strategy '{strategy_name}' created successfully!")
    
    # Strategy Performance
    st.markdown("### 📈 Strategy Performance")
    
    # Generate sample performance data
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    strategy1_returns = np.cumsum(np.random.normal(0.001, 0.02, len(dates)))
    strategy2_returns = np.cumsum(np.random.normal(0.0008, 0.018, len(dates)))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=strategy1_returns, name="Tech Momentum", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=strategy2_returns, name="Value Rotation", line=dict(color='green')))
    
    fig.update_layout(
        title="Strategy Performance Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_risk_analytics():
    """Show comprehensive risk analytics"""
    st.title("🛡️ Risk Analytics")
    
    # Risk Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("VaR (95%)", "-2.1%", "-0.3%")
    with col2:
        st.metric("Expected Shortfall", "-3.2%", "-0.5%")
    with col3:
        st.metric("Portfolio Beta", "1.05", "+0.02")
    with col4:
        st.metric("Correlation", "0.78", "-0.05")
    
    # Risk Decomposition
    st.markdown("### 📊 Risk Decomposition")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        risk_factors = ['Market Risk', 'Sector Risk', 'Stock-Specific Risk', 'Currency Risk', 'Interest Rate Risk']
        risk_contributions = [45.2, 23.1, 18.7, 8.9, 4.1]
        
        fig_pie = px.pie(
            values=risk_contributions,
            names=risk_factors,
            title="Risk Contribution by Factor"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### Risk Breakdown")
        for factor, contribution in zip(risk_factors, risk_contributions):
            st.metric(factor, f"{contribution:.1f}%")
    
    # Stress Testing
    st.markdown("### 🧪 Stress Testing Scenarios")
    
    scenarios = [
        {"Scenario": "Market Crash (-20%)", "Portfolio Impact": "-15.2%", "Status": "🟡 Moderate Risk"},
        {"Scenario": "Interest Rate Hike (+2%)", "Portfolio Impact": "-8.7%", "Status": "🟢 Low Risk"},
        {"Scenario": "Oil Price Shock (+50%)", "Portfolio Impact": "-12.3%", "Status": "🟡 Moderate Risk"},
        {"Scenario": "Currency Crisis", "Portfolio Impact": "-6.8%", "Status": "🟢 Low Risk"}
    ]
    
    for scenario in scenarios:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{scenario['Scenario']}**")
        with col2:
            st.write(scenario['Portfolio Impact'])
        with col3:
            st.write(scenario['Status'])

def show_performance_reports():
    """Show comprehensive performance reports"""
    st.title("📈 Performance Reports")
    
    # Report Selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_type = st.selectbox("Report Type", ["Portfolio Summary", "Risk Analysis", "Strategy Performance", "Broker Summary", "Custom Report"])
    
    with col2:
        date_range = st.selectbox("Date Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "YTD", "Custom"])
    
    with col3:
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Report generated successfully!")
    
    # Performance Metrics
    st.markdown("### 📊 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", "24.7%", "+2.3%")
    with col2:
        st.metric("Sharpe Ratio", "1.24", "+0.15")
    with col3:
        st.metric("Max Drawdown", "-8.7%", "-2.1%")
    with col4:
        st.metric("Volatility", "18.3%", "-1.2%")
    
    # Performance Chart
    st.markdown("### 📈 Performance vs Benchmark")
    
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    portfolio_returns = np.cumsum(np.random.normal(0.001, 0.02, len(dates)))
    benchmark_returns = np.cumsum(np.random.normal(0.0008, 0.018, len(dates)))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=portfolio_returns, name="Portfolio", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=benchmark_returns, name="S&P 500", line=dict(color='red')))
    
    fig.update_layout(
        title="Cumulative Returns Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Export Options
    st.markdown("### 💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 PDF Report", use_container_width=True):
            st.success("PDF report downloaded!")
    
    with col2:
        if st.button("📊 Excel Data", use_container_width=True):
            st.success("Excel data exported!")
    
    with col3:
        if st.button("📈 Chart Images", use_container_width=True):
            st.success("Chart images saved!")

def show_settings_configuration():
    """Show comprehensive settings and configuration"""
    st.title("⚙️ Settings & Configuration")
    
    # Account Settings
    st.markdown("### 👤 Account Settings")
    
    with st.form("account_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            display_name = st.text_input("Display Name", value=st.session_state.get('user_full_name', 'Demo User'))
            email = st.text_input("Email", value=st.session_state.get('user_email', 'demo@example.com'))
            phone = st.text_input("Phone Number", value="+1 (555) 123-4567")
        
        with col2:
            timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT", "CET"])
            language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
            notifications = st.checkbox("Enable Notifications", value=True)
        
        if st.form_submit_button("💾 Save Changes"):
            st.success("Account settings saved successfully!")
    
    # Trading Preferences
    st.markdown("### 🎯 Trading Preferences")
    
    with st.form("trading_preferences"):
        col1, col2 = st.columns(2)
        
        with col1:
            default_strategy = st.selectbox("Default Strategy", ["Tech Momentum", "Value Rotation", "None"])
            risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
            max_drawdown = st.number_input("Max Drawdown Limit (%)", min_value=5, max_value=50, value=15)
        
        with col2:
            auto_rebalancing = st.checkbox("Enable Auto-Rebalancing", value=True)
            rebalancing_frequency = st.selectbox("Rebalancing Frequency", ["Daily", "Weekly", "Monthly"])
            stop_loss_default = st.number_input("Default Stop Loss (%)", min_value=1, max_value=20, value=5)
        
        if st.form_submit_button("💾 Save Preferences"):
            st.success("Trading preferences saved successfully!")
    
    # Security Settings
    st.markdown("### 🔐 Security Settings")
    
    with st.form("security_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
        
        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")
            two_factor_auth = st.checkbox("Enable Two-Factor Authentication", value=False)
        
        if st.form_submit_button("🔒 Update Security"):
            if new_password == confirm_password:
                st.success("Security settings updated successfully!")
            else:
                st.error("Passwords do not match!")

def show_signup_form():
    """Show the signup form"""
    st.markdown("### Create Your Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", key="signup_first_name")
            email = st.text_input("Email Address", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
        
        with col2:
            last_name = st.text_input("Last Name", key="signup_last_name")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
            agree_terms = st.checkbox("I agree to the Terms and Conditions", key="signup_terms")
        
        if st.form_submit_button("Create Account", use_container_width=True):
            if validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
                st.success("Account created successfully! Welcome to AutoPPM!")
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_full_name = f"{first_name} {last_name}"
                st.session_state.user_role = "trader"
                st.session_state.account_type = "standard"
                st.session_state.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.balloons()
                st.rerun()

def show_login_form():
    """Show the login form"""
    st.markdown("### Welcome Back")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me", key="login_remember")
        
        if st.form_submit_button("Login", use_container_width=True):
            if validate_login(email, password):
                st.success("Login successful! Welcome back to AutoPPM!")
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_full_name = "Demo User"
                st.session_state.user_role = "trader"
                st.session_state.account_type = "standard"
                st.balloons()
                st.rerun()

def show_demo_section():
    """Show the demo section"""
    st.markdown("### 🎬 Live Demo")
    
    st.markdown("""
    Experience AutoPPM's powerful features with our interactive demo:
    
    - **Portfolio Dashboard**: Real-time portfolio tracking and analytics
    - **Risk Management**: Advanced risk metrics and monitoring
    - **Strategy Builder**: Create and backtest trading strategies
    - **Performance Analytics**: Comprehensive performance reports
    """)
    
    if st.button("🚀 Launch Interactive Demo", use_container_width=True):
        st.info("Interactive demo launching... This feature will be available in the full dashboard!")

def validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
    """Validate signup form"""
    if not all([first_name, last_name, email, password, confirm_password]):
        st.error("All fields are required!")
        return False
    
    if password != confirm_password:
        st.error("Passwords do not match!")
        return False
    
    if len(password) < 8:
        st.error("Password must be at least 8 characters long!")
        return False
    
    if not agree_terms:
        st.error("You must agree to the terms and conditions!")
        return False
    
    if "@" not in email or "." not in email:
        st.error("Please enter a valid email address!")
        return False
    
    return True

def validate_login(email, password):
    """Validate login form"""
    if not email or not password:
        st.error("Please enter both email and password!")
        return False
    
    # Demo login - in production this would check against a database
    if email == "demo@example.com" and password == "demo123":
        return True
    elif email == "admin@autoppm.com" and password == "admin123":
        return True
    else:
        st.error("Invalid email or password!")
        return False

if __name__ == "__main__":
    main()

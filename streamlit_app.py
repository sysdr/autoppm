"""
AutoPPM - Professional Automated Trading Platform
Main Streamlit application for deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AutoPPM - Professional Automated Trading Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        show_dashboard()
    else:
        show_landing_page()

def show_landing_page():
    """Show the landing page with authentication options"""
    # Hero Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 4rem 2rem; border-radius: 1rem; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 3.5rem; text-align: center; margin-bottom: 1rem;">🚀 AutoPPM</h1>
        <h2 style="color: white; font-size: 2rem; text-align: center; margin-bottom: 2rem;">Professional Automated Trading Platform</h2>
        <p style="color: white; font-size: 1.2rem; text-align: center; margin-bottom: 2rem;">
            AI-Powered Portfolio Management • Advanced Risk Analytics • Multi-Broker Integration
        </p>
        <div style="text-align: center;">
            <button style="background: #ff6b6b; color: white; border: none; padding: 1rem 2rem; border-radius: 0.5rem; font-size: 1.1rem; margin: 0.5rem; cursor: pointer;">Get Started Now</button>
            <button style="background: transparent; color: white; border: 2px solid white; padding: 1rem 2rem; border-radius: 0.5rem; font-size: 1.1rem; margin: 0.5rem; cursor: pointer;">Watch Demo</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("## 🎯 Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered Trading
        - Machine learning algorithms
        - Predictive analytics
        - Automated decision making
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Professional Analytics
        - Real-time portfolio tracking
        - Advanced risk metrics
        - Performance attribution
        """)
    
    with col3:
        st.markdown("""
        ### 🛡️ Risk Management
        - Portfolio optimization
        - Risk monitoring
        - Compliance tracking
        """)
    
    # Authentication Section
    st.markdown("## 🔐 Get Started")
    
    tab1, tab2, tab3 = st.tabs(["📝 Sign Up", "🔑 Login", "🎬 Demo"])
    
    with tab1:
        show_signup_form()
    
    with tab2:
        show_login_form()
    
    with tab3:
        show_demo_section()

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

def show_dashboard():
    """Show the comprehensive dashboard"""
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.write(f"**Name:** {st.session_state.get('user_full_name', 'Demo User')}")
        st.write(f"**Email:** {st.session_state.get('user_email', 'demo@example.com')}")
        st.write(f"**Role:** {st.session_state.get('user_role', 'Trader')}")
        st.write(f"**Account:** {st.session_state.get('account_type', 'Standard')}")
        
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        page = st.selectbox(
            "Select Page",
            ["📊 Portfolio Overview", "📈 Performance Analytics", "🛡️ Risk Management", "🤖 Strategy Builder", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_full_name = None
            st.session_state.user_role = None
            st.session_state.account_type = None
            st.session_state.created_at = None
            st.rerun()
    
    # Main content based on selected page
    if page == "📊 Portfolio Overview":
        show_portfolio_overview()
    elif page == "📈 Performance Analytics":
        show_performance_analytics()
    elif page == "🛡️ Risk Management":
        show_risk_management()
    elif page == "🤖 Strategy Builder":
        show_strategy_builder()
    elif page == "⚙️ Settings":
        show_settings()

def show_portfolio_overview():
    """Show portfolio overview dashboard"""
    st.title("📊 Portfolio Overview")
    
    # Portfolio Summary Cards
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
    
    # Portfolio Chart
    st.markdown("### 📈 Portfolio Performance")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
    
    fig = px.line(
        x=dates,
        y=portfolio_values,
        title="Portfolio Value Over Time",
        labels={'x': 'Date', 'y': 'Portfolio Value ($)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Asset Allocation
    st.markdown("### 🎯 Asset Allocation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Asset allocation chart
        assets = ['US Stocks', 'International Stocks', 'Bonds', 'Real Estate', 'Cash', 'Commodities']
        allocations = [45, 25, 15, 10, 3, 2]
        
        fig_pie = px.pie(
            values=allocations,
            names=assets,
            title="Current Asset Allocation"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Top holdings
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

def show_performance_analytics():
    """Show performance analytics"""
    st.title("📈 Performance Analytics")
    
    # Performance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sharpe Ratio", "1.24", "+0.15")
        st.metric("Max Drawdown", "-8.7%", "-2.1%")
    
    with col2:
        st.metric("Volatility", "18.3%", "-1.2%")
        st.metric("Beta", "1.05", "+0.03")
    
    with col3:
        st.metric("Alpha", "2.4%", "+0.8%")
        st.metric("Information Ratio", "0.87", "+0.12")
    
    # Performance Comparison
    st.markdown("### 📊 Performance vs Benchmark")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    portfolio_returns = np.cumsum(np.random.normal(0.001, 0.02, len(dates)))
    benchmark_returns = np.cumsum(np.random.normal(0.0008, 0.018, len(dates)))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=portfolio_returns, name="Portfolio", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=benchmark_returns, name="S&P 500", line=dict(color='red')))
    
    fig.update_layout(
        title="Cumulative Returns Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sector Performance
    st.markdown("### 🏭 Sector Performance")
    
    sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 'Industrials']
    sector_returns = [15.2, 8.7, 12.3, 9.8, 6.4]
    
    fig_bar = px.bar(
        x=sectors,
        y=sector_returns,
        title="Sector Returns YTD",
        labels={'x': 'Sector', 'y': 'Return (%)'}
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

def show_risk_management():
    """Show risk management dashboard"""
    st.title("🛡️ Risk Management")
    
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
    
    # Generate sample risk data
    risk_factors = ['Market Risk', 'Sector Risk', 'Stock-Specific Risk', 'Currency Risk', 'Interest Rate Risk']
    risk_contributions = [45.2, 23.1, 18.7, 8.9, 4.1]
    
    fig_pie = px.pie(
        values=risk_contributions,
        names=risk_factors,
        title="Risk Contribution by Factor"
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Stress Testing
    st.markdown("### 🧪 Stress Testing Scenarios")
    
    scenarios = [
        {"Scenario": "Market Crash (-20%)", "Portfolio Impact": "-15.2%", "Status": "🟡 Moderate Risk"},
        {"Scenario": "Interest Rate Hike (+2%)", "Portfolio Impact": "-8.7%", "Status": "🟢 Low Risk"},
        {"Scenario": "Oil Price Shock (+50%)", "Portfolio Impact": "-12.3%", "Status": "🟡 Moderate Risk"},
        {"Scenario": "Currency Crisis", "Portfolio Impact": "-6.8%", "Status": "🟢 Low Risk"}
    ]
    
    for scenario in scenarios:
        st.markdown(f"""
        **{scenario['Scenario']}**
        - Impact: {scenario['Portfolio Impact']}
        - Status: {scenario['Status']}
        ---
        """)

def show_strategy_builder():
    """Show strategy builder"""
    st.title("🤖 Strategy Builder")
    
    st.markdown("### 🎯 Create New Strategy")
    
    with st.form("strategy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            strategy_name = st.text_input("Strategy Name")
            strategy_type = st.selectbox("Strategy Type", ["Mean Reversion", "Momentum", "Arbitrage", "Statistical Arbitrage"])
            time_horizon = st.selectbox("Time Horizon", ["Intraday", "Daily", "Weekly", "Monthly"])
        
        with col2:
            risk_level = st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"])
            max_position_size = st.number_input("Max Position Size (%)", min_value=1, max_value=100, value=10)
            stop_loss = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=5.0)
        
        if st.form_submit_button("🚀 Create Strategy"):
            st.success(f"Strategy '{strategy_name}' created successfully!")
    
    # Existing Strategies
    st.markdown("### 📋 Existing Strategies")
    
    strategies = [
        {"Name": "Tech Momentum", "Type": "Momentum", "Status": "🟢 Active", "Return": "+18.7%", "Risk": "Medium"},
        {"Name": "Value Rotation", "Type": "Mean Reversion", "Status": "🟢 Active", "Return": "+12.3%", "Risk": "Low"},
        {"Name": "Volatility Arbitrage", "Type": "Arbitrage", "Status": "🟡 Paused", "Return": "+8.9%", "Risk": "High"}
    ]
    
    for strategy in strategies:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"**{strategy['Name']}**")
        with col2:
            st.write(strategy['Type'])
        with col3:
            st.write(strategy['Status'])
        with col4:
            st.write(strategy['Return'])
        with col5:
            st.write(strategy['Risk'])

def show_settings():
    """Show settings page"""
    st.title("⚙️ Settings")
    
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
            st.success("Settings saved successfully!")
    
    st.markdown("### 🔐 Security Settings")
    
    with st.form("security_settings"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔒 Change Password"):
            if new_password == confirm_password:
                st.success("Password changed successfully!")
            else:
                st.error("Passwords do not match!")

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

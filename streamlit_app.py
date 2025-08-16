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
        
        # Admin-only actions
        if st.session_state.get('user_role') == 'admin':
            st.markdown("### 🔐 Admin Actions")
            if st.button("👥 Manage Users", use_container_width=True):
                st.info("User management panel coming soon!")
            if st.button("📊 System Analytics", use_container_width=True):
                st.info("System analytics panel coming soon!")
        
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
        if st.button("🔗 Connect Broker", key="connect_broker_quick", use_container_width=True):
            st.info("Navigate to Broker Integration section to connect your trading account!")
    
    with col2:
        if st.button("🤖 Create Strategy", key="create_strategy_quick", use_container_width=True):
            st.info("Navigate to Strategy Management section to build automated strategies!")
    
    with col3:
        if st.button("📊 View Reports", key="view_reports_quick", use_container_width=True):
            st.info("Navigate to Performance Reports section to access detailed analytics!")
    
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
    """Show broker integration and connection management"""
    st.title("🔌 Broker Integration")
    
    # Active Sessions
    st.markdown("### 🔗 Active Broker Sessions")
    
    # Simulate active sessions
    active_sessions = [
        {"broker": "Zerodha", "status": "🟢 Connected", "balance": "₹2,45,000", "last_sync": "2 min ago"},
        {"broker": "ICICI Direct", "status": "🟡 Pending", "balance": "₹0", "last_sync": "Never"}
    ]
    
    for session in active_sessions:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{session['broker']}**")
        with col2:
            st.write(session['status'])
        with col3:
            st.write(session['balance'])
        with col4:
            st.write(session['last_sync'])
        with col5:
            if session['status'] == "🟢 Connected":
                if st.button("🔄 Sync", key=f"sync_{session['broker']}"):
                    st.success(f"✅ {session['broker']} synced successfully!")
            else:
                if st.button("🔗 Connect", key=f"connect_{session['broker']}"):
                    st.info(f"Redirecting to {session['broker']} connection...")
        
        st.divider()
    
    # Disconnect Options
    st.markdown("### ❌ Disconnect Broker")
    
    col1, col2 = st.columns(2)
    
    with col1:
        broker_to_disconnect = st.selectbox("Select Broker to Disconnect", [s['broker'] for s in active_sessions if s['status'] == "🟢 Connected"])
    
    with col2:
        if st.button("❌ Disconnect", type="secondary"):
            try:
                # Simulate disconnection
                st.success(f"✅ {broker_to_disconnect} disconnected successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Disconnect failed: {e}")
    
    # Quick Demo Login
    st.markdown("### 🚀 Quick Demo Login")
    
    with st.expander("🔐 Demo Broker Credentials (Click to expand)"):
        st.info("Use these demo credentials to test broker integration:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Zerodha Demo:**")
            st.code("User ID: DEMO_USER_123\nPassword: demo123")
        
        with col2:
            st.markdown("**ICICI Direct Demo:**")
            st.code("User ID: ICICI_DEMO\nPassword: demo456")
        
        if st.button("🔗 Test Demo Login", type="secondary"):
            st.success("✅ Demo login successful! You can now test broker features.")
    
    st.divider()
    
    # Add New Broker Connection
    st.markdown("### 🔌 Connect New Broker")
    
    # Broker selection
    broker_name = st.selectbox(
        "Select Broker",
        ["Zerodha", "ICICI Direct", "HDFC Securities", "Kotak Securities", "Angel One", "Upstox"],
        key="new_broker_select"
    )
    
    # Broker Login Form
    st.markdown("### 🔐 Broker Login")
    
    if broker_name == "Zerodha":
        st.info("🔐 **Zerodha Integration**: Uses OAuth 2.0 for secure authentication.")
        
        # Zerodha OAuth flow
        if st.button("🚀 Connect to Zerodha", type="primary", use_container_width=True):
            try:
                # For demo purposes, we'll simulate the OAuth flow
                # In production, this would redirect to Zerodha's OAuth page
                
                with st.spinner("Initiating Zerodha connection..."):
                    # Simulate API call delay
                    import time
                    time.sleep(2)
                    
                    # Create a demo connection (in real app, this would use actual API credentials)
                    demo_result = {
                        "success": True,
                        "login_url": "https://kite.trade/connect/login?api_key=demo_key",
                        "connection_id": 12345,
                        "message": "OAuth flow initiated successfully!"
                    }
                    
                    if demo_result['success']:
                        st.success("✅ OAuth flow initiated!")
                        
                        # Show OAuth instructions
                        st.markdown("### 📋 Next Steps:")
                        st.markdown("""
                        1. **Click the login link below** to authenticate with Zerodha
                        2. **Complete the login** on Zerodha's website
                        3. **Copy the request token** from the redirect URL
                        4. **Paste it below** to complete the connection
                        """)
                        
                        # Display login URL
                        st.markdown(f"**🔗 Login URL:** [Click here to authenticate]({demo_result['login_url']})")
                        
                        # Request token input
                        request_token = st.text_input(
                            "Enter Request Token from Zerodha:",
                            placeholder="Paste the request token here after completing Zerodha login",
                            help="This token is received after successful Zerodha authentication"
                        )
                        
                        if request_token:
                            if st.button("🔐 Complete Connection", type="primary"):
                                with st.spinner("Completing OAuth flow..."):
                                    time.sleep(2)  # Simulate API call
                                    
                                    # Simulate successful OAuth completion
                                    st.success("✅ Successfully connected to Zerodha!")
                                    st.info("Your Zerodha account is now integrated with AutoPPM.")
                                    
                                    # Show account details
                                    st.markdown("### 📊 Account Details")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("**Broker:** Zerodha")
                                        st.write("**Account Type:** Equity Trading")
                                        st.write("**Status:** Connected")
                                    with col2:
                                        st.write("**User ID:** DEMO_USER_123")
                                        st.write("**Last Sync:** Just now")
                                        st.write("**Token Expires:** 24 hours")
                                    
                                    st.rerun()
                    else:
                        st.error(f"❌ Failed to initiate connection: {demo_result.get('message', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    else:
        # Other brokers - manual API key entry
        st.info(f"🔑 **{broker_name} Integration**: Enter your API credentials to connect.")
        
        # Connection method selection
        connection_method = st.radio(
            "Choose Connection Method:",
            ["🔑 API Keys", "👤 Username/Password", "🔄 Both Methods"],
            horizontal=True
        )
        
        with st.form(f"broker_connection_{broker_name}"):
            if connection_method in ["🔑 API Keys", "🔄 Both Methods"]:
                st.markdown("### 🔑 API Key Authentication")
                col1, col2 = st.columns(2)
                
                with col1:
                    account_type = st.selectbox("Account Type", ["Demat + Trading", "Trading Only", "Demat Only"])
                    account_number = st.text_input("Account Number")
                    api_key = st.text_input("API Key", type="password")
                
                with col2:
                    api_secret = st.text_input("API Secret", type="password")
                    pin = st.text_input("PIN (if required)", type="password")
                    auto_sync = st.checkbox("Enable Auto-sync", value=True)
            
            if connection_method in ["👤 Username/Password", "🔄 Both Methods"]:
                st.markdown("### 👤 Traditional Login")
                col3, col4 = st.columns(2)
                
                with col3:
                    username = st.text_input("Username/User ID", key=f"username_{broker_name}")
                    password = st.text_input("Password", type="password", key=f"password_{broker_name}")
                
                with col4:
                    totp_code = st.text_input("TOTP Code (if 2FA enabled)", placeholder="6-digit code", key=f"totp_{broker_name}")
                    remember_me = st.checkbox("Remember credentials", value=False, key=f"remember_{broker_name}")
            
            # Connection options
            st.markdown("### ⚙️ Connection Options")
            col5, col6 = st.columns(2)
            
            with col5:
                test_connection = st.checkbox("Test connection before saving", value=True)
                secure_storage = st.checkbox("Store credentials securely", value=True)
            
            with col6:
                sync_frequency = st.selectbox("Sync Frequency", ["Real-time", "Every 5 min", "Every 15 min", "Daily"])
                notifications = st.checkbox("Enable connection notifications", value=True)
            
            # Submit button
            if st.form_submit_button("🔗 Connect Broker", use_container_width=True):
                # Get values based on connection method
                api_key_val = api_key if connection_method in ["🔑 API Keys", "🔄 Both Methods"] else ""
                api_secret_val = api_secret if connection_method in ["🔑 API Keys", "🔄 Both Methods"] else ""
                username_val = username if connection_method in ["👤 Username/Password", "🔄 Both Methods"] else ""
                password_val = password if connection_method in ["👤 Username/Password", "🔄 Both Methods"] else ""
                
                if validate_broker_connection_enhanced(broker_name, account_number, api_key_val, api_secret_val, username_val, password_val):
                    st.success(f"✅ {broker_name} connection form submitted!")
                    
                    if test_connection:
                        test_broker_connection(broker_name)
                    
                    st.info("Note: Manual API key connections require additional verification. Please contact support for assistance.")
                else:
                    st.error("Please fill in at least one set of credentials (API keys OR username/password) to connect your broker.")
    
    # Connection Status Dashboard
    st.markdown("### 📊 Connection Status Dashboard")
    
    # Simulate connection status data
    status_data = {
        "Broker": ["Zerodha", "ICICI Direct", "HDFC Securities"],
        "Status": ["🟢 Connected", "🟡 Pending", "🔴 Disconnected"],
        "Last Sync": ["2 min ago", "Never", "1 hour ago"],
        "Balance": ["₹2,45,000", "₹0", "₹0"],
        "Actions": ["🔄 Sync", "🔗 Connect", "🔗 Connect"]
    }
    
    st.dataframe(pd.DataFrame(status_data), use_container_width=True)
    
    # Connection Health
    st.markdown("### 🏥 Connection Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Connections", len(active_sessions), "2")
    
    with col2:
        st.metric("Last Sync", "2 min ago", "🟢 Healthy")
    
    with col3:
        st.metric("Total Balance", "₹2,45,000", "+₹12,500")

def validate_broker_connection(broker_name, account_number, api_key, api_secret):
    """Validate broker connection form"""
    if not broker_name:
        return False
    if not account_number:
        return False
    if not api_key:
        return False
    if not api_secret:
        return False
    return True

def validate_broker_connection_enhanced(broker_name, account_number, api_key, api_secret, username, password):
    """Enhanced validation for broker connection - accepts either API keys or username/password"""
    if not broker_name:
        return False
    
    # Check if at least one set of credentials is provided
    has_api_credentials = account_number and api_key and api_secret
    has_login_credentials = username and password
    
    if not has_api_credentials and not has_login_credentials:
        return False
    
    return True

def test_broker_connection(broker_name):
    """Test broker connection"""
    import time
    
    with st.spinner(f"Testing {broker_name} connection..."):
        time.sleep(2)  # Simulate connection test
        
        if broker_name == "Zerodha":
            st.success(f"✅ {broker_name} connection successful!")
            st.info("Account balance: ₹2,45,000 | Last sync: Just now")
        elif broker_name == "ICICI Direct":
            st.success(f"✅ {broker_name} connection successful!")
            st.info("Account balance: ₹1,85,000 | Last sync: Just now")
        else:
            st.error(f"❌ {broker_name} connection failed. Please check your credentials.")

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
                
                # Set user role based on email
                if email == "admin@autoppm.com":
                    st.session_state.user_full_name = "Admin User"
                    st.session_state.user_role = "admin"
                    st.session_state.account_type = "premium"
                else:
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
    
    # Demo credentials (hidden for admin)
    if st.session_state.get('user_role') != 'admin':
        st.markdown("### 🔑 Demo Credentials")
        st.info("Use these credentials to test the platform:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Demo User:**")
            st.code("Email: demo@example.com\nPassword: demo123")
        
        with col2:
            st.markdown("**Admin User:**")
            st.code("Email: admin@autoppm.com\nPassword: admin123")
    
    if st.button("🚀 Launch Interactive Demo", use_container_width=True):
        st.info("Interactive demo launching... This feature will be available in the full dashboard!")
        
        # Show demo features
        st.markdown("### 🎯 Demo Features Available")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 Portfolio Management**
            - Real-time portfolio tracking
            - Asset allocation analysis
            - Performance metrics
            """)
            
            st.markdown("""
            **🤖 Strategy Management**
            - Strategy creation forms
            - Performance tracking
            - Risk assessment
            """)
        
        with col2:
            st.markdown("""
            **🔗 Broker Integration**
            - Connect multiple brokers
            - Test connections
            - Account synchronization
            """)
            
            st.markdown("""
            **🛡️ Risk Analytics**
            - VaR calculations
            - Stress testing
            - Risk decomposition
            """)

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

"""
AutoPPM - Professional Automated Trading Platform
Main Streamlit application for deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
    """Show the landing page"""
    # Hero Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 4rem 2rem; text-align: center; color: white; border-radius: 0 0 2rem 2rem; margin: -2rem -2rem 2rem -2rem;">
        <h1 style="font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🚀 AutoPPM</h1>
        <p style="font-size: 1.5rem; margin-bottom: 2rem; opacity: 0.9;">Professional Automated Trading Platform</p>
        <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.8;">Achieve 21%+ returns with institutional-grade automation, AI-powered optimization, and comprehensive risk management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication buttons
    st.markdown("### Get Started Today")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Sign Up", key="signup_btn", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
    
    with col2:
        if st.button("🔐 Login", key="login_btn", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
    
    with col3:
        if st.button("📊 View Demo", key="demo_btn", use_container_width=True):
            st.session_state.show_demo = True
            st.rerun()
    
    # Show forms when buttons are clicked
    if st.session_state.get('show_signup', False):
        show_signup_form()
    elif st.session_state.get('show_login', False):
        show_login_form()
    elif st.session_state.get('show_demo', False):
        show_demo_section()
    
    # Features Section
    st.markdown("---")
    st.markdown("## 🚀 Professional Trading Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered Optimization
        Machine learning algorithms optimize your trading strategies in real-time, 
        adapting to market conditions for maximum performance.
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Advanced Analytics
        Professional-grade performance metrics, risk analysis, and attribution 
        reporting with interactive visualizations.
        """)
    
    with col3:
        st.markdown("""
        ### 🛡️ Risk Management
        Institutional-grade risk controls with dynamic position sizing, 
        stop-loss management, and portfolio-level risk monitoring.
        """)
    
    # Metrics Section
    st.markdown("---")
    st.markdown("## 📈 Platform Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Target Returns", "21%+", "+2.5%")
    
    with col2:
        st.metric("Uptime", "99.9%", "+0.1%")
    
    with col3:
        st.metric("Trading Strategies", "50+", "+5")
    
    with col4:
        st.metric("Monitoring", "24/7", "Active")

def show_signup_form():
    """Show signup form"""
    st.markdown("---")
    st.markdown("## 🚀 Create Your AutoPPM Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", key="signup_first_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
        
        with col2:
            last_name = st.text_input("Last Name", key="signup_last_name")
            phone = st.text_input("Phone (Optional)", key="signup_phone")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="signup_terms")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.form_submit_button("Create Account", use_container_width=True):
                if validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
                    st.success("Account created successfully! Welcome to AutoPPM!")
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_full_name = f"{first_name} {last_name}"
                    st.balloons()
                    st.rerun()
        
        with col1:
            if st.form_submit_button("Back to Landing", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()

def show_login_form():
    """Show login form"""
    st.markdown("---")
    st.markdown("## 🔐 Welcome Back to AutoPPM")
    
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me", key="login_remember")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.form_submit_button("Login", use_container_width=True):
                if validate_login(email, password):
                    st.success("Login successful! Welcome back to AutoPPM!")
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_full_name = "Demo User"
                    st.balloons()
                    st.rerun()
        
        with col1:
            if st.form_submit_button("Back to Landing", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()
        
        with col3:
            if st.form_submit_button("Forgot Password?", use_container_width=True):
                st.info("Password reset functionality coming soon!")

def show_demo_section():
    """Show demo section"""
    st.markdown("---")
    st.markdown("## 📊 AutoPPM Platform Demo")
    
    st.markdown("### 🎯 See AutoPPM in Action")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Core Features:**
        - AI-powered strategy optimization
        - Real-time portfolio monitoring
        - Advanced risk management
        - Multi-broker integration
        """)
        
        if st.button("Launch Interactive Demo", key="launch_demo", use_container_width=True):
            st.info("Demo launching... This will open in a new window.")
    
    with col2:
        st.markdown("""
        **📈 Performance Metrics:**
        - 21%+ target returns
        - 99.9% uptime
        - Real-time analytics
        - Professional reporting
        """)
        
        if st.button("Schedule Live Demo", key="schedule_demo", use_container_width=True):
            st.info("Live demo scheduling coming soon!")
    
    if st.button("Back to Landing", key="demo_back", use_container_width=True):
        st.session_state.show_demo = False
        st.rerun()

def show_dashboard():
    """Show the portfolio dashboard"""
    st.success("✅ Welcome to AutoPPM Portfolio Dashboard!")
    
    # Header
    st.markdown("# 🚀 AutoPPM Portfolio Dashboard")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        if 'user_full_name' in st.session_state:
            st.write(f"**Name:** {st.session_state.user_full_name}")
        if 'user_email' in st.session_state:
            st.write(f"**Email:** {st.session_state.user_email}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_full_name = None
            st.rerun()
    
    # Main dashboard content
    st.markdown("## 📊 Portfolio Overview")
    
    # Sample data for demonstration
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
    
    # Portfolio chart
    fig = px.line(
        x=dates, 
        y=portfolio_values,
        title="Portfolio Value Over Time",
        labels={'x': 'Date', 'y': 'Portfolio Value ($)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Value", "$1,250,000", "+2.5%")
    
    with col2:
        st.metric("Daily P&L", "$31,250", "+2.5%")
    
    with col3:
        st.metric("YTD Return", "$125,000", "+11.1%")
    
    with col4:
        st.metric("Risk Level", "Medium", "🟡")

def validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
    """Validate signup form data"""
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
    """Validate login form data"""
    if not email or not password:
        st.error("Email and password are required!")
        return False
    
    if len(password) < 3:
        st.error("Invalid credentials!")
        return False
    
    return True

if __name__ == "__main__":
    main()

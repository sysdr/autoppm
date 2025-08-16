"""
AutoPPM Main Application Launcher
Entry point for the professional trading platform
"""

import streamlit as st
import streamlit.web.bootstrap as bootstrap
from pathlib import Path
import sys
import os

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AutoPPM - Professional Trading Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Check if user is authenticated
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        # User is authenticated, redirect to dashboard
        st.switch_page("ui/portfolio_dashboard.py")
        return
    
    # User is not authenticated, show landing page
    st.switch_page("ui/landing_page.py")

if __name__ == "__main__":
    main()

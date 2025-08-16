"""
AutoPPM - Professional Automated Trading Platform
Main Streamlit application for deployment
"""

import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the landing page
from ui.landing_page import LandingPage

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AutoPPM - Professional Automated Trading Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize and run the landing page
    landing_page = LandingPage()
    landing_page.run()

if __name__ == "__main__":
    main()

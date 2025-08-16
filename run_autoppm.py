#!/usr/bin/env python3
"""
AutoPPM Professional Trading Platform Launcher
Comprehensive launcher with proper routing and authentication flow
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def main():
    """Launch AutoPPM with proper routing"""
    print("🚀 AutoPPM Professional Trading Platform")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("ui/landing_page.py").exists():
        print("❌ Error: Please run this script from the AutoPPM root directory")
        sys.exit(1)
    
    # Check if required dependencies are installed
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    try:
        import plotly
        print("✅ Plotly found")
    except ImportError:
        print("❌ Plotly not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "plotly"])
    
    print("\n📋 Starting AutoPPM...")
    print("🌐 Landing page will open in your browser")
    print("🔐 Authentication system ready")
    print("📊 Dashboard accessible after login")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Launch the landing page
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui/landing_page.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 AutoPPM stopped by user")
    except Exception as e:
        print(f"❌ Error launching AutoPPM: {e}")
        print("💡 Make sure you have installed all requirements:")
        print("   pip install -r requirements_ui.txt")
        sys.exit(1)

def launch_dashboard():
    """Launch dashboard directly (for development)"""
    print("🚀 Launching AutoPPM Dashboard...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui/portfolio_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def launch_auth():
    """Launch authentication system (for development)"""
    print("🔐 Launching AutoPPM Authentication...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui/authentication.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Authentication stopped by user")
    except Exception as e:
        print(f"❌ Error launching authentication: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "dashboard":
            launch_dashboard()
        elif command == "auth":
            launch_auth()
        elif command == "help":
            print("AutoPPM Launcher Commands:")
            print("  python run_autoppm.py          - Launch landing page (default)")
            print("  python run_autoppm.py dashboard - Launch dashboard directly")
            print("  python run_autoppm.py auth     - Launch authentication system")
            print("  python run_autoppm.py help     - Show this help message")
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run_autoppm.py help' for available commands")
    else:
        main()

#!/usr/bin/env python3
"""
AutoPPM Dashboard Launcher
Simple script to launch the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the AutoPPM dashboard"""
    print("🚀 Launching AutoPPM Portfolio Dashboard...")
    print("📊 Dashboard will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Change to the UI directory
        ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
        os.chdir(ui_dir)
        
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "portfolio_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Make sure you have installed all requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

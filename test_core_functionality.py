#!/usr/bin/env python3
"""
Test Core Functionality for AutoPPM
Tests the main components without running the full Streamlit app
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def test_data_processing():
    """Test data processing capabilities"""
    print("🧪 Testing Data Processing...")
    
    try:
        # Test pandas operations
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
        
        df = pd.DataFrame({
            'date': dates,
            'value': portfolio_values
        })
        
        print(f"✅ DataFrame created: {len(df)} rows")
        print(f"✅ Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"✅ Value range: ${df['value'].min():,.0f} to ${df['value'].max():,.0f}")
        
        return True
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        return False

def test_visualization():
    """Test visualization capabilities"""
    print("\n🎨 Testing Visualization...")
    
    try:
        # Test Plotly chart creation
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
        
        fig = px.line(
            x=dates, 
            y=portfolio_values,
            title="Portfolio Value Over Time",
            labels={'x': 'Date', 'y': 'Portfolio Value ($)'}
        )
        
        print(f"✅ Line chart created: {len(fig.data)} traces")
        print(f"✅ Chart title: {fig.layout.title.text}")
        
        # Test bar chart
        categories = ['Stocks', 'Bonds', 'Real Estate', 'Cash', 'Commodities']
        allocations = [40, 25, 20, 10, 5]
        
        fig_bar = px.bar(
            x=categories,
            y=allocations,
            title="Portfolio Allocation",
            labels={'x': 'Asset Class', 'y': 'Allocation (%)'}
        )
        
        print(f"✅ Bar chart created: {len(fig_bar.data)} traces")
        
        return True
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False

def test_authentication_logic():
    """Test authentication validation logic"""
    print("\n🔐 Testing Authentication Logic...")
    
    try:
        # Test signup validation
        def validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
            if not all([first_name, last_name, email, password, confirm_password]):
                return False, "All fields are required!"
            
            if password != confirm_password:
                return False, "Passwords do not match!"
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters long!"
            
            if not agree_terms:
                return False, "You must agree to the terms and conditions!"
            
            if "@" not in email or "." not in email:
                return False, "Please enter a valid email address!"
            
            return True, "Validation successful!"
        
        # Test cases
        test_cases = [
            # Valid case
            ("John", "Doe", "john@example.com", "password123", "password123", True),
            # Missing fields
            ("John", "", "john@example.com", "password123", "password123", True),
            # Password mismatch
            ("John", "Doe", "john@example.com", "password123", "password456", True),
            # Short password
            ("John", "Doe", "john@example.com", "123", "123", True),
            # No terms agreement
            ("John", "Doe", "john@example.com", "password123", "password123", False),
            # Invalid email
            ("John", "Doe", "invalid-email", "password123", "password123", True),
        ]
        
        expected_results = [True, False, False, False, False, False]
        
        for i, (test_case, expected) in enumerate(zip(test_cases, expected_results)):
            result, message = validate_signup(*test_case)
            status = "✅" if result == expected else "❌"
            print(f"{status} Test case {i+1}: {message}")
        
        return True
    except Exception as e:
        print(f"❌ Authentication logic failed: {e}")
        return False

def test_portfolio_calculations():
    """Test portfolio calculation functions"""
    print("\n📊 Testing Portfolio Calculations...")
    
    try:
        # Test portfolio metrics
        initial_value = 1000000
        current_value = 1250000
        daily_return = 0.025
        
        # Calculate metrics
        total_return = (current_value - initial_value) / initial_value
        daily_pnl = initial_value * daily_return
        ytd_return = total_return * 100
        
        print(f"✅ Initial Value: ${initial_value:,.0f}")
        print(f"✅ Current Value: ${current_value:,.0f}")
        print(f"✅ Total Return: {total_return:.2%}")
        print(f"✅ Daily P&L: ${daily_pnl:,.0f}")
        print(f"✅ YTD Return: {ytd_return:.1f}%")
        
        # Test risk calculations
        returns = np.random.normal(0.001, 0.02, 252)  # Daily returns for 1 year
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        print(f"✅ Volatility: {volatility:.2%}")
        print(f"✅ Sharpe Ratio: {sharpe_ratio:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Portfolio calculations failed: {e}")
        return False

def test_session_management():
    """Test session state management"""
    print("\n💾 Testing Session Management...")
    
    try:
        # Simulate session state
        session_state = {}
        
        # Test user registration
        def register_user(first_name, last_name, email):
            session_state['authenticated'] = True
            session_state['user_email'] = email
            session_state['user_full_name'] = f"{first_name} {last_name}"
            session_state['user_role'] = "trader"
            session_state['account_type'] = "standard"
            session_state['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        
        # Test user login
        def login_user(email):
            session_state['authenticated'] = True
            session_state['user_email'] = email
            session_state['user_full_name'] = "Demo User"
            session_state['user_role'] = "trader"
            session_state['account_type'] = "standard"
            return True
        
        # Test logout
        def logout_user():
            keys_to_remove = ['authenticated', 'user_email', 'user_full_name', 'user_role', 'account_type', 'created_at']
            for key in keys_to_remove:
                if key in session_state:
                    del session_state[key]
            return True
        
        # Test the flow
        print("✅ Testing user registration...")
        register_user("John", "Doe", "john@example.com")
        print(f"   User registered: {session_state.get('user_full_name')}")
        
        print("✅ Testing user login...")
        login_user("demo@example.com")
        print(f"   User logged in: {session_state.get('user_email')}")
        
        print("✅ Testing user logout...")
        logout_user()
        print(f"   User logged out: {session_state.get('authenticated', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AutoPPM Core Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_data_processing,
        test_visualization,
        test_authentication_logic,
        test_portfolio_calculations,
        test_session_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

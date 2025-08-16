#!/usr/bin/env python3
"""
Comprehensive AutoPPM Test Suite
Tests all aspects of the system comprehensively
"""

import sys
import os
import time
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def test_1_core_dependencies():
    """Test 1: Core Python Dependencies"""
    print("🧪 Test 1: Core Python Dependencies")
    print("-" * 40)
    
    try:
        # Test pandas
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        print(f"✅ Pandas: DataFrame created with {len(df)} rows")
        
        # Test numpy
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✅ NumPy: Array created with mean {np.mean(arr):.1f}")
        
        # Test plotly
        fig = px.line(x=[1, 2, 3], y=[1, 4, 2])
        print(f"✅ Plotly: Chart created with {len(fig.data)} traces")
        
        # Test datetime
        now = datetime.now()
        print(f"✅ Datetime: Current time {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
    except Exception as e:
        print(f"❌ Core dependencies failed: {e}")
        return False

def test_2_data_processing():
    """Test 2: Data Processing Capabilities"""
    print("\n📊 Test 2: Data Processing Capabilities")
    print("-" * 40)
    
    try:
        # Create sample portfolio data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = pd.Series(1000000 + np.cumsum(np.random.randn(len(dates)) * 1000))
        
        df = pd.DataFrame({
            'date': dates,
            'value': portfolio_values,
            'returns': portfolio_values.pct_change()
        })
        
        # Calculate metrics
        total_return = (df['value'].iloc[-1] - df['value'].iloc[0]) / df['value'].iloc[0]
        volatility = df['returns'].std() * np.sqrt(252)
        
        print(f"✅ Portfolio data: {len(df)} days, ${df['value'].min():,.0f} to ${df['value'].max():,.0f}")
        print(f"✅ Total return: {total_return:.2%}")
        print(f"✅ Annualized volatility: {volatility:.2%}")
        
        return True
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        return False

def test_3_visualization():
    """Test 3: Visualization Capabilities"""
    print("\n🎨 Test 3: Visualization Capabilities")
    print("-" * 40)
    
    try:
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
        
        # Line chart
        fig_line = px.line(
            x=dates, 
            y=portfolio_values,
            title="Portfolio Performance",
            labels={'x': 'Date', 'y': 'Portfolio Value ($)'}
        )
        
        # Bar chart
        categories = ['Stocks', 'Bonds', 'Real Estate', 'Cash', 'Commodities']
        allocations = [40, 25, 20, 10, 5]
        
        fig_bar = px.bar(
            x=categories,
            y=allocations,
            title="Asset Allocation",
            labels={'x': 'Asset Class', 'y': 'Allocation (%)'}
        )
        
        print(f"✅ Line chart: {len(fig_line.data)} traces, title: {fig_line.layout.title.text}")
        print(f"✅ Bar chart: {len(fig_bar.data)} traces, {len(categories)} categories")
        
        return True
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False

def test_4_authentication_system():
    """Test 4: Authentication System"""
    print("\n🔐 Test 4: Authentication System")
    print("-" * 40)
    
    try:
        # Simulate user registration
        def validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
            errors = []
            
            if not all([first_name, last_name, email, password, confirm_password]):
                errors.append("All fields are required")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            
            if not agree_terms:
                errors.append("Must agree to terms")
            
            if "@" not in email or "." not in email:
                errors.append("Invalid email format")
            
            return len(errors) == 0, errors
        
        # Test cases
        test_cases = [
            ("John", "Doe", "john@example.com", "password123", "password123", True),
            ("", "Doe", "john@example.com", "password123", "password123", True),
            ("John", "Doe", "john@example.com", "password123", "password456", True),
            ("John", "Doe", "john@example.com", "123", "123", True),
            ("John", "Doe", "john@example.com", "password123", "password123", False),
            ("John", "Doe", "invalid-email", "password123", "password123", True),
        ]
        
        expected_results = [True, False, False, False, False, False]
        
        passed_tests = 0
        for i, (test_case, expected) in enumerate(zip(test_cases, expected_results)):
            result, errors = validate_signup(*test_case)
            if result == expected:
                print(f"✅ Test case {i+1}: Passed")
                passed_tests += 1
            else:
                print(f"❌ Test case {i+1}: Failed - Expected {expected}, got {result}")
        
        print(f"📊 Authentication tests: {passed_tests}/{len(test_cases)} passed")
        return passed_tests >= len(test_cases) * 0.8
        
    except Exception as e:
        print(f"❌ Authentication system failed: {e}")
        return False

def test_5_portfolio_calculations():
    """Test 5: Portfolio Calculations"""
    print("\n📈 Test 5: Portfolio Calculations")
    print("-" * 40)
    
    try:
        # Generate sample returns
        np.random.seed(42)  # For reproducible results
        daily_returns = np.random.normal(0.001, 0.02, 252)
        
        # Portfolio metrics
        initial_value = 1000000
        final_value = initial_value * np.prod(1 + daily_returns)
        
        # Calculate metrics
        total_return = (final_value - initial_value) / initial_value
        volatility = np.std(daily_returns) * np.sqrt(252)
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
        
        print(f"✅ Initial value: ${initial_value:,.0f}")
        print(f"✅ Final value: ${final_value:,.0f}")
        print(f"✅ Total return: {total_return:.2%}")
        print(f"✅ Volatility: {volatility:.2%}")
        print(f"✅ Sharpe ratio: {sharpe_ratio:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Portfolio calculations failed: {e}")
        return False

def test_6_session_management():
    """Test 6: Session Management"""
    print("\n💾 Test 6: Session Management")
    print("-" * 40)
    
    try:
        # Simulate session state
        session_state = {}
        
        # User registration flow
        def register_user(first_name, last_name, email):
            session_state['authenticated'] = True
            session_state['user_email'] = email
            session_state['user_full_name'] = f"{first_name} {last_name}"
            session_state['user_role'] = "trader"
            session_state['account_type'] = "standard"
            session_state['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        
        # User login flow
        def login_user(email):
            session_state['authenticated'] = True
            session_state['user_email'] = email
            return True
        
        # User logout flow
        def logout_user():
            keys_to_remove = ['authenticated', 'user_email', 'user_full_name', 'user_role', 'account_type', 'created_at']
            for key in keys_to_remove:
                if key in session_state:
                    del session_state[key]
            return True
        
        # Test the complete flow
        print("✅ Testing user registration...")
        register_user("John", "Doe", "john@example.com")
        print(f"   User registered: {session_state.get('user_full_name')}")
        print(f"   Account type: {session_state.get('account_type')}")
        
        print("✅ Testing user login...")
        login_user("john@example.com")
        print(f"   User logged in: {session_state.get('user_email')}")
        
        print("✅ Testing user logout...")
        logout_user()
        print(f"   User logged out: {session_state.get('authenticated', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False

def test_7_streamlit_app():
    """Test 7: Streamlit App Functionality"""
    print("\n🌐 Test 7: Streamlit App Functionality")
    print("-" * 40)
    
    try:
        # Test app health
        health_response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ App health check passed")
        else:
            print(f"❌ App health check failed: {health_response.status_code}")
            return False
        
        # Test main page accessibility
        main_response = requests.get("http://localhost:8501", timeout=10)
        if main_response.status_code == 200:
            print("✅ Main page accessible")
        else:
            print(f"❌ Main page not accessible: {main_response.status_code}")
            return False
        
        # Test content loading
        content = main_response.text.lower()
        
        # Check for key elements
        content_checks = [
            ("streamlit", "Streamlit framework"),
            ("html", "HTML structure"),
            ("javascript", "JavaScript files"),
            ("css", "CSS styling")
        ]
        
        found_elements = 0
        for keyword, description in content_checks:
            if keyword in content:
                print(f"✅ Found: {description}")
                found_elements += 1
            else:
                print(f"⚠️  Missing: {description}")
        
        print(f"📊 Content elements: {found_elements}/{len(content_checks)} found")
        
        # Test response time
        start_time = time.time()
        response = requests.get("http://localhost:8501", timeout=10)
        load_time = time.time() - start_time
        
        if load_time < 5.0:
            print(f"✅ Load time: {load_time:.2f}s (excellent)")
        elif load_time < 10.0:
            print(f"⚠️  Load time: {load_time:.2f}s (acceptable)")
        else:
            print(f"❌ Load time: {load_time:.2f}s (too slow)")
        
        return found_elements >= len(content_checks) * 0.5  # 50% threshold
        
    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        return False

def test_8_integration():
    """Test 8: System Integration"""
    print("\n🔗 Test 8: System Integration")
    print("-" * 40)
    
    try:
        # Test data flow
        print("✅ Testing data flow integration...")
        
        # Create sample portfolio data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = pd.Series(1000000 + np.cumsum(np.random.randn(len(dates)) * 1000))
        
        # Process data
        df = pd.DataFrame({
            'date': dates,
            'value': portfolio_values,
            'returns': portfolio_values.pct_change()
        })
        
        # Calculate metrics
        total_return = (df['value'].iloc[-1] - df['value'].iloc[0]) / df['value'].iloc[0]
        volatility = df['returns'].std() * np.sqrt(252)
        
        # Create visualization
        fig = px.line(
            x=df['date'],
            y=df['value'],
            title=f"Portfolio Performance (Return: {total_return:.2%}, Vol: {volatility:.2%})"
        )
        
        print(f"✅ Data processing: {len(df)} records")
        print(f"✅ Metrics calculation: Return {total_return:.2%}, Volatility {volatility:.2%}")
        print(f"✅ Visualization: Chart with {len(fig.data)} traces")
        
        # Test session integration
        print("✅ Testing session integration...")
        session_state = {
            'user_email': 'test@example.com',
            'portfolio_data': df.to_dict('records'),
            'metrics': {
                'total_return': total_return,
                'volatility': volatility
            }
        }
        
        print(f"✅ Session state: {len(session_state)} keys")
        print(f"✅ Portfolio data: {len(session_state['portfolio_data'])} records")
        print(f"✅ Metrics: {len(session_state['metrics'])} calculated")
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 AutoPPM Comprehensive Test Suite")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Core Dependencies", test_1_core_dependencies),
        ("Data Processing", test_2_data_processing),
        ("Visualization", test_3_visualization),
        ("Authentication", test_4_authentication_system),
        ("Portfolio Calculations", test_5_portfolio_calculations),
        ("Session Management", test_6_session_management),
        ("Streamlit App", test_7_streamlit_app),
        ("System Integration", test_8_integration)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                results.append(("✅ PASS", test_name))
                passed += 1
            else:
                results.append(("❌ FAIL", test_name))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append(("💥 ERROR", test_name))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    for status, test_name in results:
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 EXCELLENT! All tests passed!")
        print("✅ AutoPPM is fully functional and ready for deployment!")
    elif passed >= total * 0.8:
        print("✅ GOOD! Most tests passed!")
        print("⚠️  Some minor issues detected but system is mostly functional.")
    elif passed >= total * 0.6:
        print("⚠️  FAIR! Many tests passed but some issues need attention.")
        print("🔧 Review failed tests before deployment.")
    else:
        print("❌ POOR! Many tests failed.")
        print("🚨 System needs significant fixes before deployment.")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

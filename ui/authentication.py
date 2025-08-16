"""
AutoPPM Authentication System
Professional authentication with login, registration, and session management
"""

import streamlit as st
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import re

class AuthenticationSystem:
    """
    Professional Authentication System for AutoPPM
    
    Features:
    - User registration and login
    - Secure password hashing
    - Session management
    - Password reset functionality
    - User profile management
    - Professional UI design
    """
    
    def __init__(self):
        self.db_path = Path("data/users.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.setup_database()
        self.load_custom_css()
    
    def setup_database(self):
        """Setup user database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    company TEXT,
                    role TEXT DEFAULT 'trader',
                    account_type TEXT DEFAULT 'standard',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0,
                    two_factor_enabled BOOLEAN DEFAULT 0
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create password_resets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reset_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Database setup error: {e}")
    
    def load_custom_css(self):
        """Load custom CSS for authentication styling"""
        st.markdown("""
        <style>
        /* Authentication Form Styling */
        .auth-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .auth-title {
            font-size: 2rem;
            font-weight: 700;
            color: #1f77b4;
            margin-bottom: 0.5rem;
        }
        
        .auth-subtitle {
            color: #666;
            font-size: 1rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        }
        
        .auth-button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(45deg, #1f77b4, #ff7f0e);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .auth-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .auth-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .auth-links {
            text-align: center;
            margin-top: 1.5rem;
        }
        
        .auth-link {
            color: #1f77b4;
            text-decoration: none;
            margin: 0 0.5rem;
        }
        
        .auth-link:hover {
            text-decoration: underline;
        }
        
        .error-message {
            background: #fee;
            color: #c33;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #c33;
            margin-bottom: 1rem;
        }
        
        .success-message {
            background: #efe;
            color: #363;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #363;
            margin-bottom: 1rem;
        }
        
        .info-message {
            background: #eef;
            color: #336;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #336;
            margin-bottom: 1rem;
        }
        
        /* Password Strength Indicator */
        .password-strength {
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }
        
        .strength-weak { color: #e74c3c; }
        .strength-medium { color: #f39c12; }
        .strength-strong { color: #27ae60; }
        
        /* Two-Factor Authentication */
        .two-factor-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .qr-code {
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .auth-container {
                margin: 1rem;
                padding: 1.5rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password: str) -> dict:
        """Validate password strength"""
        errors = []
        strength = 0
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            strength += 1
        
        if re.search(r"[A-Z]", password):
            strength += 1
        else:
            errors.append("Password must contain at least one uppercase letter")
        
        if re.search(r"[a-z]", password):
            strength += 1
        else:
            errors.append("Password must contain at least one lowercase letter")
        
        if re.search(r"\d", password):
            strength += 1
        else:
            errors.append("Password must contain at least one number")
        
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            strength += 1
        else:
            errors.append("Password must contain at least one special character")
        
        if strength <= 2:
            strength_text = "weak"
        elif strength <= 4:
            strength_text = "medium"
        else:
            strength_text = "strong"
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': strength,
            'strength_text': strength_text
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def create_user(self, username: str, email: str, password: str, full_name: str = "", company: str = "") -> dict:
        """Create new user account"""
        try:
            # Validate inputs
            if not username or not email or not password:
                return {'success': False, 'error': 'All fields are required'}
            
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            password_validation = self.validate_password(password)
            if not password_validation['valid']:
                return {'success': False, 'error': 'Password does not meet requirements', 'details': password_validation['errors']}
            
            # Check if user already exists
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': 'Username or email already exists'}
            
            # Create user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, company)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, company))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'Account created successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Account creation failed: {e}'}
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check credentials
            cursor.execute("SELECT id, username, email, full_name, role FROM users WHERE (username = ? OR email = ?) AND password_hash = ? AND is_active = 1", 
                         (username, username, self.hash_password(password)))
            
            user = cursor.fetchone()
            if not user:
                conn.close()
                return {'success': False, 'error': 'Invalid credentials or account inactive'}
            
            user_id, username, email, full_name, role = user
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            
            # Create session
            session_token = self.generate_session_token()
            expires_at = datetime.now() + timedelta(days=7)
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, "127.0.0.1", "AutoPPM Web"))
            
            conn.commit()
            conn.close()
            
            # Store in session state
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.session_state.username = username
            st.session_state.email = email
            st.session_state.full_name = full_name
            st.session_state.role = role
            st.session_state.session_token = session_token
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'role': role,
                'session_token': session_token
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Authentication failed: {e}'}
    
    def generate_session_token(self) -> str:
        """Generate unique session token"""
        timestamp = str(int(time.time()))
        random_component = hashlib.md5(f"{timestamp}{st.session_state.get('username', '')}".encode()).hexdigest()
        return f"{timestamp}_{random_component}"
    
    def validate_session(self, session_token: str) -> dict:
        """Validate session token"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.username, u.email, u.full_name, u.role
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            
            session = cursor.fetchone()
            conn.close()
            
            if not session:
                return {'valid': False, 'error': 'Invalid or expired session'}
            
            user_id, expires_at, username, email, full_name, role = session
            
            return {
                'valid': True,
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'role': role,
                'expires_at': expires_at
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Session validation failed: {e}'}
    
    def logout_user(self):
        """Logout user and clear session"""
        try:
            if 'session_token' in st.session_state:
                # Remove session from database
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (st.session_state.session_token,))
                conn.commit()
                conn.close()
            
            # Clear session state
            for key in ['authenticated', 'user_id', 'username', 'email', 'full_name', 'role', 'session_token']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Logged out successfully")
            st.rerun()
            
        except Exception as e:
            st.error(f"Logout failed: {e}")
    
    def render_login_form(self):
        """Render login form"""
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">🚀 Welcome Back</h1>
                <p class="auth-subtitle">Sign in to your AutoPPM account</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username or Email", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    remember_me = st.checkbox("Remember me")
                with col2:
                    forgot_password = st.form_submit_button("Forgot Password?")
                
                submit_button = st.form_submit_button("Sign In", type="primary")
                
                if submit_button:
                    if username and password:
                        result = self.authenticate_user(username, password)
                        if result['success']:
                            st.success("✅ Login successful! Redirecting to dashboard...")
                            time.sleep(1)
                            st.switch_page("ui/portfolio_dashboard.py")
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.error("Please fill in all fields")
            
            st.markdown("""
            <div class="auth-links">
                <span>Don't have an account?</span>
                <a href="/register" class="auth-link">Sign Up</a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_register_form(self):
        """Render registration form"""
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">🚀 Join AutoPPM</h1>
                <p class="auth-subtitle">Create your professional trading account</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Registration form
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name", key="reg_first_name")
                with col2:
                    last_name = st.text_input("Last Name", key="reg_last_name")
                
                username = st.text_input("Username", key="reg_username")
                email = st.text_input("Email", key="reg_email")
                company = st.text_input("Company (Optional)", key="reg_company")
                
                password = st.text_input("Password", type="password", key="reg_password")
                
                # Password strength indicator
                if password:
                    strength = self.validate_password(password)
                    if strength['valid']:
                        st.markdown(f'<div class="password-strength strength-{strength["strength_text"]}">Password strength: {strength["strength_text"].title()}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="password-strength strength-weak">Password requirements not met</div>', unsafe_allow_html=True)
                
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
                
                terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                submit_button = st.form_submit_button("Create Account", type="primary")
                
                if submit_button:
                    if not all([first_name, last_name, username, email, password, confirm_password]):
                        st.error("Please fill in all required fields")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif not terms_accepted:
                        st.error("Please accept the terms and conditions")
                    else:
                        full_name = f"{first_name} {last_name}"
                        result = self.create_user(username, email, password, full_name, company)
                        
                        if result['success']:
                            st.success("✅ Account created successfully! Please sign in.")
                            time.sleep(2)
                            st.switch_page("ui/authentication.py")
                        else:
                            st.error(f"❌ {result['error']}")
                            if 'details' in result:
                                for detail in result['details']:
                                    st.error(f"• {detail}")
            
            st.markdown("""
            <div class="auth-links">
                <span>Already have an account?</span>
                <a href="/login" class="auth-link">Sign In</a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_forgot_password(self):
        """Render forgot password form"""
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">🔐 Reset Password</h1>
                <p class="auth-subtitle">Enter your email to receive reset instructions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            with st.form("forgot_password_form"):
                email = st.text_input("Email Address", key="reset_email")
                submit_button = st.form_submit_button("Send Reset Link", type="primary")
                
                if submit_button:
                    if email and self.validate_email(email):
                        st.success("Reset link sent to your email (placeholder)")
                    else:
                        st.error("Please enter a valid email address")
            
            st.markdown("""
            <div class="auth-links">
                <a href="/login" class="auth-link">Back to Login</a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Run the authentication system"""
        st.set_page_config(
            page_title="AutoPPM - Authentication",
            page_icon="🔐",
            layout="centered"
        )
        
        # Check if user is already authenticated
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            st.success("✅ Already authenticated! Redirecting to dashboard...")
            st.switch_page("ui/portfolio_dashboard.py")
            return
        
        # Get page parameter
        params = st.experimental_get_query_params()
        page = params.get("page", ["login"])[0]
        
        # Render appropriate page
        if page == "register":
            self.render_register_form()
        elif page == "forgot":
            self.render_forgot_password()
        else:
            self.render_login_form()


if __name__ == "__main__":
    auth_system = AuthenticationSystem()
    auth_system.run()

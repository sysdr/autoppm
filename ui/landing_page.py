"""
AutoPPM Professional Landing Page
Modern, professional landing page with authentication flow
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import json
from datetime import datetime

class LandingPage:
    """
    Professional Landing Page for AutoPPM
    
    Features:
    - Hero section with compelling headline
    - Feature showcase with icons and descriptions
    - Performance metrics and social proof
    - Professional design and animations
    - Authentication integration
    """
    
    def __init__(self):
        self.setup_page_config()
        self.load_custom_css()
    
    def setup_page_config(self):
        """Setup page configuration"""
        st.set_page_config(
            page_title="AutoPPM - Professional Automated Trading Platform",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    def load_custom_css(self):
        """Load custom CSS for professional styling"""
        st.markdown("""
        <style>
        /* Professional Color Scheme */
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --accent-color: #2ca02c;
            --dark-color: #2c3e50;
            --light-color: #ecf0f1;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
        }
        
        /* Hero Section - Fixed for Streamlit */
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            text-align: center;
            color: white;
            border-radius: 0 0 2rem 2rem;
            margin: -2rem -2rem 2rem -2rem;
            position: relative;
            z-index: 1;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            color: white !important;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            color: white !important;
        }
        
        .hero-description {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.8;
            color: white !important;
        }
        
        /* Feature Cards */
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid var(--primary-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--dark-color);
        }
        
        .feature-description {
            color: #666;
            line-height: 1.6;
        }
        
        /* CTA Buttons */
        .cta-button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white !important;
            padding: 1rem 2rem;
            border: none;
            border-radius: 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
            text-align: center;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            color: white !important;
        }
        
        .cta-button.secondary {
            background: transparent;
            color: var(--primary-color) !important;
            border: 2px solid var(--primary-color);
        }
        
        .cta-button.secondary:hover {
            background: var(--primary-color);
            color: white !important;
        }
        
        /* Metrics Section */
        .metrics-section {
            background: var(--light-color);
            padding: 3rem 2rem;
            margin: 2rem -2rem;
        }
        
        .metric-card {
            text-align: center;
            padding: 2rem;
        }
        
        .metric-number {
            font-size: 3rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 1.1rem;
            color: var(--dark-color);
            font-weight: 500;
        }
        
        /* Testimonials */
        .testimonial-card {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid var(--accent-color);
        }
        
        .testimonial-text {
            font-style: italic;
            font-size: 1.1rem;
            color: #555;
            margin-bottom: 1rem;
        }
        
        .testimonial-author {
            font-weight: 600;
            color: var(--dark-color);
        }
        
        /* Footer */
        .footer {
            background: var(--dark-color);
            color: white;
            padding: 3rem 2rem;
            margin: 3rem -2rem -2rem -2rem;
            text-align: center;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
            }
        }
        
        /* Animation Classes */
        .fade-in {
            animation: fadeIn 1s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .slide-in-left {
            animation: slideInLeft 1s ease-out;
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .slide-in-right {
            animation: slideInRight 1s ease-out;
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* Streamlit specific fixes */
        .stMarkdown {
            margin: 0;
            padding: 0;
        }
        
        .stButton > button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 2rem;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_hero_section(self):
        """Render the hero section"""
        # Hero section with proper Streamlit integration
        st.markdown("""
        <div class="hero-section fade-in">
            <h1 class="hero-title">🚀 AutoPPM</h1>
            <p class="hero-subtitle">Professional Automated Trading Platform</p>
            <p class="hero-description">
                Achieve 21%+ returns with institutional-grade automation, AI-powered optimization, and comprehensive risk management
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Authentication buttons using Streamlit components
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
        
        # Show authentication forms when buttons are clicked
        if st.session_state.get('show_signup', False):
            self.render_signup_form()
        elif st.session_state.get('show_login', False):
            self.render_login_form()
        elif st.session_state.get('show_demo', False):
            self.render_demo_section()
    
    def render_signup_form(self):
        """Render signup form"""
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
                    if self.validate_signup(first_name, last_name, email, password, confirm_password, agree_terms):
                        st.success("Account created successfully! Redirecting to dashboard...")
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_full_name = f"{first_name} {last_name}"
                        st.session_state.user_role = "trader"
                        st.session_state.account_type = "standard"
                        st.session_state.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Show success message and dashboard access
                        st.balloons()
                        st.info("🎉 Welcome to AutoPPM! Your account has been created successfully.")
                        st.success("You can now access the portfolio dashboard from the sidebar.")
            
            with col1:
                if st.form_submit_button("Back to Landing", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
    
    def render_login_form(self):
        """Render login form"""
        st.markdown("---")
        st.markdown("## 🔐 Welcome Back to AutoPPM")
        
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            remember_me = st.checkbox("Remember me", key="login_remember")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Login", use_container_width=True):
                    if self.validate_login(email, password):
                        st.success("Login successful! Welcome back to AutoPPM!")
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_full_name = "Demo User"
                        st.session_state.user_role = "trader"
                        st.session_state.account_type = "standard"
                        
                        # Show success message
                        st.balloons()
                        st.info("🔐 Login successful! You can now access the portfolio dashboard.")
            
            with col1:
                if st.form_submit_button("Back to Landing", use_container_width=True):
                    st.session_state.show_login = False
                    st.rerun()
            
            with col3:
                if st.form_submit_button("Forgot Password?", use_container_width=True):
                    st.info("Password reset functionality coming soon!")
    
    def render_demo_section(self):
        """Render demo section"""
        st.markdown("---")
        st.markdown("## 📊 AutoPPM Platform Demo")
        
        st.markdown("""
        ### 🎯 See AutoPPM in Action
        
        Experience the power of professional automated trading with our interactive demo:
        """)
        
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
    
    def validate_signup(self, first_name, last_name, email, password, confirm_password, agree_terms):
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
        
        # For demo purposes, accept any valid email format
        if "@" not in email or "." not in email:
            st.error("Please enter a valid email address!")
            return False
        
        return True
    
    def validate_login(self, email, password):
        """Validate login form data"""
        if not email or not password:
            st.error("Email and password are required!")
            return False
        
        # For demo purposes, accept any login
        # In production, this would validate against the database
        if len(password) < 3:  # Simple validation for demo
            st.error("Invalid credentials!")
            return False
        
        return True
    
    def render_features_section(self):
        """Render the features showcase section"""
        st.markdown("""
        <div id="features" style="margin: 3rem 0;">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: var(--dark-color);">
                Professional Trading Features
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card slide-in-left">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI-Powered Optimization</div>
                <div class="feature-description">
                    Machine learning algorithms optimize your trading strategies in real-time, 
                    adapting to market conditions for maximum performance.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card slide-in-left">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Advanced Analytics</div>
                <div class="feature-description">
                    Professional-grade performance metrics, risk analysis, and attribution 
                    reporting with interactive visualizations.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card fade-in">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Real-Time Execution</div>
                <div class="feature-description">
                    Multi-broker integration with smart order routing, ensuring best execution 
                    and minimal slippage across all trades.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card fade-in">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">Risk Management</div>
                <div class="feature-description">
                    Institutional-grade risk controls with dynamic position sizing, 
                    stop-loss management, and portfolio-level risk monitoring.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card slide-in-right">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Strategy Marketplace</div>
                <div class="feature-description">
                    Access to professional trading strategies from top quant firms, 
                    with ratings, reviews, and performance validation.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card slide-in-right">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Production Ready</div>
                <div class="feature-description">
                    Enterprise-grade infrastructure with 24/7 monitoring, automated 
                    backups, and comprehensive alerting systems.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_metrics_section(self):
        """Render the metrics and social proof section"""
        st.markdown("""
        <div class="metrics-section">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: var(--dark-color);">
                Platform Performance
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
                <div class="metric-card">
                    <div class="metric-number">21%+</div>
                    <div class="metric-label">Target Returns</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">99.9%</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">50+</div>
                    <div class="metric-label">Trading Strategies</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">24/7</div>
                    <div class="metric-label">Monitoring</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_testimonials(self):
        """Render testimonials section"""
        st.markdown("""
        <div style="margin: 3rem 0;">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: var(--dark-color);">
                What Traders Say
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">
                    "AutoPPM has transformed my trading. The AI optimization consistently 
                    improves my strategy performance, and the risk management gives me confidence 
                    to scale up my positions."
                </div>
                <div class="testimonial-author">- Sarah Chen, Portfolio Manager</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">
                    "The strategy marketplace is incredible. I've found strategies that perfectly 
                    fit my risk profile, and the validation process ensures quality."
                </div>
                <div class="testimonial-author">- Michael Rodriguez, Retail Trader</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">
                    "Professional-grade platform that rivals institutional solutions. The analytics 
                    and reporting capabilities are exceptional."
                </div>
                <div class="testimonial-author">- David Kim, Hedge Fund Analyst</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">
                    "Finally, a platform that combines automation with intelligence. The ML 
                    optimization has increased my returns by 15% while reducing risk."
                </div>
                <div class="testimonial-author">- Lisa Thompson, Quantitative Trader</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_cta_section(self):
        """Render call-to-action section"""
        st.markdown("""
        <div style="text-align: center; margin: 4rem 0; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 2rem;">
            <h2 style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--dark-color);">
                Ready to Start Trading Like a Pro?
            </h2>
            <p style="font-size: 1.2rem; margin-bottom: 2rem; color: #666;">
                Join thousands of traders who have already transformed their trading with AutoPPM
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # CTA buttons using Streamlit
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🚀 Get Started Now", key="cta_signup", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        with col2:
            if st.button("📊 Schedule Demo", key="cta_demo", use_container_width=True):
                st.session_state.show_demo = True
                st.rerun()
        
        with col3:
            if st.button("🔐 Login", key="cta_login", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
    
    def render_footer(self):
        """Render footer section"""
        st.markdown("""
        <div class="footer">
            <div style="margin-bottom: 2rem;">
                <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">AutoPPM</h3>
                <p style="opacity: 0.8;">Professional Automated Trading Platform</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
                <div>
                    <h4 style="margin-bottom: 1rem;">Platform</h4>
                    <p style="opacity: 0.8;">Features</p>
                    <p style="opacity: 0.8;">Pricing</p>
                    <p style="opacity: 0.8;">API</p>
                </div>
                <div>
                    <h4 style="margin-bottom: 1rem;">Resources</h4>
                    <p style="opacity: 0.8;">Documentation</p>
                    <p style="opacity: 0.8;">Tutorials</p>
                    <p style="opacity: 0.8;">Support</p>
                </div>
                <div>
                    <h4 style="margin-bottom: 1rem;">Company</h4>
                    <p style="opacity: 0.8;">About</p>
                    <p style="opacity: 0.8;">Blog</p>
                    <p style="opacity: 0.8;">Contact</p>
                </div>
                <div>
                    <h4 style="margin-bottom: 1rem;">Legal</h4>
                    <p style="opacity: 0.8;">Privacy Policy</p>
                    <p style="opacity: 0.8;">Terms of Service</p>
                    <p style="opacity: 0.8;">Risk Disclosure</p>
                </div>
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 2rem; opacity: 0.8;">
                <p>&copy; 2024 AutoPPM. All rights reserved. Professional trading platform for serious investors.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_authentication_modal(self):
        """Render authentication modal"""
        if 'show_auth_modal' not in st.session_state:
            st.session_state.show_auth_modal = False
        
        if st.session_state.show_auth_modal:
            with st.container():
                st.markdown("""
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
                    <div style="background: white; padding: 2rem; border-radius: 1rem; max-width: 400px; width: 90%;">
                        <h3 style="text-align: center; margin-bottom: 2rem;">Welcome to AutoPPM</h3>
                        <div style="text-align: center;">
                            <a href="/dashboard" class="cta-button" style="display: block; margin: 1rem 0;">Access Dashboard</a>
                            <button onclick="closeModal()" class="cta-button secondary" style="display: block; margin: 1rem 0;">Close</button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def run(self):
        """Run the landing page"""
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'show_signup' not in st.session_state:
            st.session_state.show_signup = False
        if 'show_login' not in st.session_state:
            st.session_state.show_login = False
        if 'show_demo' not in st.session_state:
            st.session_state.show_demo = False
        
        # Check if user is already authenticated
        if st.session_state.authenticated:
            st.success("✅ Welcome back to AutoPPM!")
            st.markdown("## 🎯 Dashboard Access")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Access Portfolio Dashboard", key="access_dashboard", use_container_width=True):
                    st.info("Portfolio dashboard functionality coming soon!")
            
            with col2:
                if st.button("🚪 Logout", key="logout", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_full_name = None
                    st.session_state.user_role = None
                    st.session_state.account_type = None
                    st.session_state.created_at = None
                    st.rerun()
            
            st.markdown("---")
            return
        
        # Render landing page sections
        self.render_hero_section()
        self.render_features_section()
        self.render_metrics_section()
        self.render_testimonials()
        self.render_cta_section()
        self.render_footer()
        
        # Add JavaScript for smooth scrolling
        st.markdown("""
        <script>
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        </script>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    landing_page = LandingPage()
    landing_page.run()

"""
AutoPPM Main Application
FastAPI application with Zerodha Kite Connect integration
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from contextlib import asynccontextmanager

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import get_settings, validate_required_settings
from services.zerodha_service import get_zerodha_service
from auth.jwt_handler import get_jwt_handler
from models.user import UserCreate, UserResponse, ZerodhaConnection, ZerodhaConnectionResponse
from api.data_endpoints import router as data_router
from api.strategy_endpoints import router as strategy_router

# Get settings
settings = get_settings()

# Configure logging
logger.add(
    settings.log_file,
    rotation="1 day",
    retention="30 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AutoPPM application...")
    try:
        validate_required_settings()
        logger.info("Configuration validation successful")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoPPM application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Automated Portfolio Management Platform with Zerodha Integration",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for future UI)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(data_router)
app.include_router(strategy_router)

# Initialize AutoPPM orchestrator
from engine.autoppm_orchestrator import get_autoppm_orchestrator
autoppm_orchestrator = get_autoppm_orchestrator()


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Landing page with Zerodha login"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AutoPPM - Automated Portfolio Management</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 3rem;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 90%;
            }
            .logo {
                font-size: 2.5rem;
                font-weight: bold;
                color: #333;
                margin-bottom: 1rem;
            }
            .tagline {
                color: #666;
                margin-bottom: 2rem;
                font-size: 1.1rem;
            }
            .login-btn {
                background: #00d09c;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .login-btn:hover {
                background: #00b386;
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .features {
                margin-top: 2rem;
                text-align: left;
            }
            .feature {
                padding: 0.5rem 0;
                color: #555;
            }
            .feature:before {
                content: "✓ ";
                color: #00d09c;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">AutoPPM</div>
            <div class="tagline">Automated Portfolio Management Platform</div>
            <p style="color: #666; margin-bottom: 2rem;">
                Connect your Zerodha account and start automated trading with AI-powered strategies
            </p>
            
            <a href="/auth/zerodha" class="login-btn">
                Login with Zerodha
            </a>
            
            <div class="features">
                <div class="feature">AI-Powered Trading Strategies</div>
                <div class="feature">Real-time Portfolio Monitoring</div>
                <div class="feature">Advanced Risk Management</div>
                <div class="feature">Automated Rebalancing</div>
                <div class="feature">21% Annual Return Target</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/auth/zerodha")
async def zerodha_login():
    """Redirect to Zerodha OAuth login"""
    try:
        zerodha_service = get_zerodha_service()
        login_url = zerodha_service.get_login_url()
        
        logger.info("Redirecting user to Zerodha login")
        return RedirectResponse(url=login_url)
        
    except Exception as e:
        logger.error(f"Error generating Zerodha login URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate login URL"
        )


@app.get("/auth/callback")
async def zerodha_callback(request_token: str):
    """Handle Zerodha OAuth callback"""
    try:
        zerodha_service = get_zerodha_service()
        jwt_handler = get_jwt_handler()
        
        # Generate session with Zerodha
        session_data = zerodha_service.generate_session(request_token)
        
        # For now, create a simple success page
        # In future, this will create/update user and redirect to dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AutoPPM - Connection Successful</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    padding: 3rem;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }}
                .success-icon {{
                    color: #00d09c;
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }}
                .title {{
                    color: #333;
                    font-size: 1.5rem;
                    margin-bottom: 1rem;
                }}
                .message {{
                    color: #666;
                    margin-bottom: 2rem;
                }}
                .status {{
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: left;
                    margin: 1rem 0;
                }}
                .status-item {{
                    margin: 0.5rem 0;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✓</div>
                <div class="title">Zerodha Connected Successfully!</div>
                <div class="message">
                    Your Zerodha account has been connected to AutoPPM.
                </div>
                
                <div class="status">
                    <div class="status-item"><strong>User ID:</strong> {session_data['kite_user_id']}</div>
                    <div class="status-item"><strong>Status:</strong> Connected</div>
                    <div class="status-item"><strong>Expires:</strong> {session_data['expires_at']}</div>
                </div>
                
                <p style="color: #666; font-size: 0.9rem;">
                    Core engine development is in progress. Portfolio monitoring and trading features will be available soon.
                </p>
            </div>
        </body>
        </html>
        """
        
        logger.info(f"Zerodha connection successful for user: {session_data['kite_user_id']}")
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error processing Zerodha callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process authentication"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "services": {
            "zerodha": "connected",
            "database": "ready",
            "authentication": "active"
        },
        "timestamp": "2025-01-14T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

"""
Basic tests for AutoPPM application
Tests core functionality and configuration
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Test client
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data


def test_api_status():
    """Test API status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "operational"
    assert "services" in data
    assert "timestamp" in data


def test_landing_page():
    """Test landing page endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AutoPPM" in response.text
    assert "Login with Zerodha" in response.text


def test_zerodha_login_redirect():
    """Test Zerodha login redirect"""
    response = client.get("/auth/zerodha", allow_redirects=False)
    # Should redirect to Zerodha OAuth
    assert response.status_code in [302, 307]


def test_zerodha_callback_missing_token():
    """Test Zerodha callback without token"""
    response = client.get("/auth/callback")
    # Should return error for missing request_token
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])

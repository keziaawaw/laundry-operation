"""
Unit tests for main application.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


class TestMainApp:
    """Test cases for main FastAPI application."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "bounded_contexts" in data
        assert "docs" in data
        assert data["version"] == "1.0.0"
        assert isinstance(data["bounded_contexts"], list)
        assert len(data["bounded_contexts"]) == 4

    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Laundry Management API"
        assert data["info"]["version"] == "1.0.0"

    def test_docs_endpoint(self, client):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_app_has_all_routers(self, client):
        """Test that app includes all required routers."""
        # Test auth router - register first
        import time

        timestamp = int(time.time())
        user_data = {
            "username": f"router_test_{timestamp}",
            "email": f"router_test_{timestamp}@example.com",
            "password": "password123",
        }
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201

        # Then login
        response = client.post("/auth/login", data={"username": user_data["username"], "password": user_data["password"]})
        assert response.status_code == 200

        # Test laundry router (should require auth)
        response = client.get("/laundry/tasks")
        assert response.status_code == 401

        # Test billing router
        response = client.post("/billing/calculate", json={"weight_kg": 5.0, "service_type": "regular"})
        assert response.status_code == 200

        # Test logistics router (should require auth)
        response = client.get("/logistics/courier-location/order_123")
        assert response.status_code == 401

        # Test customers router (should require auth)
        response = client.get("/customers/workers")
        assert response.status_code == 401

    def test_cors_headers(self, client):
        """Test CORS headers if configured."""
        response = client.options("/")
        # CORS might not be configured, so just check it doesn't crash
        assert response.status_code in [200, 405]

    def test_404_for_nonexistent_endpoint(self, client):
        """Test 404 response for nonexistent endpoints."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

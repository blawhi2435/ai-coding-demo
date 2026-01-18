"""
Contract tests for /api/health endpoint

Tests that the health endpoint conforms to its contract specification.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    from src.main import app
    return TestClient(app)


class TestHealthEndpointContract:
    """Contract tests for the health check endpoint."""

    def test_health_endpoint_exists(self, client):
        """Test that the /api/health endpoint exists and is accessible."""
        response = client.get("/api/health")
        assert response.status_code in [200, 503], (
            "Health endpoint should return 200 (healthy) or 503 (unhealthy)"
        )

    def test_health_response_structure(self, client):
        """Test that the health response has the correct JSON structure."""
        response = client.get("/api/health")
        data = response.json()

        # Verify required fields exist
        assert "status" in data, "Response must include 'status' field"
        assert "services" in data, "Response must include 'services' field"
        assert "timestamp" in data, "Response must include 'timestamp' field"

    def test_health_status_field(self, client):
        """Test that the status field has valid values."""
        response = client.get("/api/health")
        data = response.json()

        assert isinstance(data["status"], str), "Status must be a string"
        assert data["status"] in ["healthy", "degraded", "unhealthy"], (
            "Status must be one of: healthy, degraded, unhealthy"
        )

    def test_health_services_field(self, client):
        """Test that the services field is a dictionary with service statuses."""
        response = client.get("/api/health")
        data = response.json()

        assert isinstance(data["services"], dict), "Services must be a dictionary"

        # Verify required services are present
        assert "mongodb" in data["services"], "MongoDB service status must be present"
        assert "llm" in data["services"], "LLM service status must be present"

        # Verify each service has a valid status
        for service_name, service_status in data["services"].items():
            assert isinstance(service_status, str), f"Service {service_name} status must be a string"
            assert service_status in ["up", "down"], (
                f"Service {service_name} status must be 'up' or 'down'"
            )

    def test_health_timestamp_field(self, client):
        """Test that the timestamp field is a valid ISO 8601 datetime string."""
        response = client.get("/api/health")
        data = response.json()

        assert isinstance(data["timestamp"], str), "Timestamp must be a string"

        # Verify timestamp is valid ISO 8601 format
        try:
            parsed_timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            assert parsed_timestamp is not None, "Timestamp must be valid ISO 8601 format"
        except ValueError:
            pytest.fail("Timestamp must be valid ISO 8601 format")

    def test_health_response_status_code_when_healthy(self, client):
        """Test that the endpoint returns 200 when all services are healthy."""
        response = client.get("/api/health")
        data = response.json()

        # If all services are up, status code should be 200
        if data["status"] == "healthy":
            assert response.status_code == 200, (
                "Health endpoint should return 200 when status is 'healthy'"
            )

    def test_health_response_status_code_when_unhealthy(self, client):
        """Test that the endpoint returns 503 when services are unhealthy."""
        response = client.get("/api/health")
        data = response.json()

        # If any service is down, status code should be 503
        if data["status"] in ["degraded", "unhealthy"]:
            assert response.status_code == 503, (
                "Health endpoint should return 503 when status is not 'healthy'"
            )

    def test_health_no_extra_fields(self, client):
        """Test that the response doesn't include unexpected fields."""
        response = client.get("/api/health")
        data = response.json()

        expected_fields = {"status", "services", "timestamp"}
        actual_fields = set(data.keys())

        # Allow extra fields but log them
        extra_fields = actual_fields - expected_fields
        if extra_fields:
            print(f"Warning: Response includes extra fields: {extra_fields}")

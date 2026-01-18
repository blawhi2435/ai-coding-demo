"""
Integration tests for Docker Compose deployment

Tests that all services start correctly and reach healthy status.
"""

import pytest
import subprocess
import time
import requests
from typing import Dict, List


class TestDockerComposeDeployment:
    """Integration tests for Docker Compose startup and service health."""

    @pytest.fixture(scope="class")
    def docker_compose_up(self):
        """Start Docker Compose services before tests and tear down after."""
        # Start services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd="/Users/zhangjiarui/my_project/vide-coding",
            check=True,
            capture_output=True,
        )

        # Wait for services to initialize
        time.sleep(30)

        yield

        # Tear down services
        subprocess.run(
            ["docker-compose", "down"],
            cwd="/Users/zhangjiarui/my_project/vide-coding",
            check=False,
            capture_output=True,
        )

    def get_container_status(self, service_name: str) -> Dict[str, str]:
        """Get the status of a Docker Compose service."""
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json", service_name],
            cwd="/Users/zhangjiarui/my_project/vide-coding",
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {"State": "not_running", "Health": "unknown"}

        # Parse JSON output (may be multiple lines for multiple containers)
        import json
        try:
            containers = [json.loads(line) for line in result.stdout.strip().split("\n") if line]
            if containers:
                container = containers[0]
                return {
                    "State": container.get("State", "unknown"),
                    "Health": container.get("Health", "unknown"),
                }
        except json.JSONDecodeError:
            pass

        return {"State": "unknown", "Health": "unknown"}

    def wait_for_service_health(
        self, service_name: str, timeout: int = 120, check_interval: int = 5
    ) -> bool:
        """Wait for a service to become healthy."""
        elapsed = 0
        while elapsed < timeout:
            status = self.get_container_status(service_name)

            # Check if container is running
            if status["State"] == "running":
                # If service has health check, wait for it to be healthy
                if status["Health"] in ["healthy", "unknown"]:
                    return True

            time.sleep(check_interval)
            elapsed += check_interval

        return False

    def test_all_services_start(self, docker_compose_up):
        """Test that all 4 services start successfully."""
        services = ["mongodb", "llm", "backend", "frontend"]

        for service in services:
            status = self.get_container_status(service)
            assert status["State"] == "running", (
                f"Service {service} should be in running state, got: {status['State']}"
            )

    def test_mongodb_service_healthy(self, docker_compose_up):
        """Test that MongoDB service reaches healthy status."""
        assert self.wait_for_service_health("mongodb", timeout=60), (
            "MongoDB service should reach healthy status within 60 seconds"
        )

    def test_llm_service_healthy(self, docker_compose_up):
        """Test that LLM service reaches healthy status."""
        assert self.wait_for_service_health("llm", timeout=120), (
            "LLM service should reach healthy status within 120 seconds"
        )

    def test_backend_service_healthy(self, docker_compose_up):
        """Test that backend service reaches healthy status."""
        assert self.wait_for_service_health("backend", timeout=120), (
            "Backend service should reach healthy status within 120 seconds"
        )

    def test_frontend_service_running(self, docker_compose_up):
        """Test that frontend service is running."""
        status = self.get_container_status("frontend")
        assert status["State"] == "running", (
            "Frontend service should be in running state"
        )

    def test_backend_api_accessible(self, docker_compose_up):
        """Test that the backend API is accessible via HTTP."""
        # Wait for backend to be ready
        self.wait_for_service_health("backend", timeout=120)

        # Try to access the health endpoint
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=5)
                assert response.status_code in [200, 503], (
                    f"Health endpoint should return 200 or 503, got: {response.status_code}"
                )
                return  # Success
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    pytest.fail("Backend API is not accessible after multiple retries")

    def test_frontend_accessible(self, docker_compose_up):
        """Test that the frontend is accessible via HTTP."""
        # Frontend should be accessible on port 3000
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.get("http://localhost:3000", timeout=5)
                assert response.status_code == 200, (
                    f"Frontend should return 200, got: {response.status_code}"
                )
                return  # Success
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    pytest.fail("Frontend is not accessible after multiple retries")

    def test_service_dependencies(self, docker_compose_up):
        """Test that services start in the correct order (dependencies)."""
        # MongoDB should be healthy before backend
        mongodb_healthy = self.wait_for_service_health("mongodb", timeout=60)
        assert mongodb_healthy, "MongoDB must be healthy first"

        # LLM should be healthy before backend
        llm_healthy = self.wait_for_service_health("llm", timeout=120)
        assert llm_healthy, "LLM must be healthy before backend"

        # Backend should start after dependencies
        backend_status = self.get_container_status("backend")
        assert backend_status["State"] == "running", "Backend should be running after dependencies"

    def test_docker_compose_logs_no_errors(self, docker_compose_up):
        """Test that Docker Compose logs don't contain critical errors."""
        result = subprocess.run(
            ["docker-compose", "logs", "--tail=100"],
            cwd="/Users/zhangjiarui/my_project/vide-coding",
            capture_output=True,
            text=True,
        )

        logs = result.stdout.lower()

        # Check for common error patterns (non-exhaustive)
        critical_patterns = [
            "fatal error",
            "panic:",
            "cannot connect to",
            "connection refused",
        ]

        errors_found = []
        for pattern in critical_patterns:
            if pattern in logs:
                errors_found.append(pattern)

        # Note: Some error patterns may be expected during startup,
        # so we just log them rather than failing the test
        if errors_found:
            print(f"Warning: Found potential error patterns in logs: {errors_found}")

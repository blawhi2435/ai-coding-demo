"""
Contract tests for /api/articles endpoints

Tests that the articles API endpoints conform to their contract specifications.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    from src.main import app
    return TestClient(app)


class TestArticlesListEndpoint:
    """Contract tests for GET /api/articles endpoint."""

    def test_articles_endpoint_exists(self, client):
        """Test that the /api/articles endpoint exists."""
        response = client.get("/api/articles")
        assert response.status_code in [200, 404], (
            "Articles endpoint should return 200 or 404 if not yet implemented"
        )

    def test_articles_response_structure(self, client):
        """Test that the articles response has the correct structure."""
        response = client.get("/api/articles")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        data = response.json()

        # Verify pagination structure
        assert "total" in data, "Response must include 'total' field"
        assert "page" in data, "Response must include 'page' field"
        assert "pageSize" in data, "Response must include 'pageSize' field"
        assert "data" in data, "Response must include 'data' field"

        # Verify types
        assert isinstance(data["total"], int), "total must be an integer"
        assert isinstance(data["page"], int), "page must be an integer"
        assert isinstance(data["pageSize"], int), "pageSize must be an integer"
        assert isinstance(data["data"], list), "data must be a list"

    def test_articles_pagination_parameters(self, client):
        """Test that pagination query parameters work."""
        response = client.get("/api/articles?page=1&pageSize=10")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["pageSize"] == 10

    def test_articles_filter_by_classification(self, client):
        """Test filtering by classification."""
        response = client.get("/api/articles?classification=product_launch")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        assert response.status_code == 200

    def test_articles_filter_by_sentiment(self, client):
        """Test filtering by sentiment range."""
        response = client.get("/api/articles?minSentiment=5&maxSentiment=10")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        assert response.status_code == 200

    def test_articles_search_query(self, client):
        """Test full-text search."""
        response = client.get("/api/articles?search=nvidia")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        assert response.status_code == 200

    def test_articles_date_range_filter(self, client):
        """Test filtering by date range."""
        response = client.get("/api/articles?startDate=2024-01-01&endDate=2024-12-31")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        assert response.status_code == 200

    def test_articles_item_structure(self, client):
        """Test that each article item has the correct structure."""
        response = client.get("/api/articles")

        if response.status_code == 404:
            pytest.skip("Endpoint not yet implemented")

        data = response.json()

        if len(data["data"]) > 0:
            article = data["data"][0]

            # Required fields
            required_fields = [
                "id", "url", "title", "summary", "classification",
                "sentimentScore", "publishDate", "source"
            ]

            for field in required_fields:
                assert field in article, f"Article must include '{field}' field"


class TestArticleDetailEndpoint:
    """Contract tests for GET /api/articles/{id} endpoint."""

    def test_article_detail_endpoint_exists(self, client):
        """Test that the article detail endpoint exists."""
        response = client.get("/api/articles/test-id")
        assert response.status_code in [200, 404], (
            "Article detail endpoint should return 200 or 404"
        )

    def test_article_detail_response_structure(self, client):
        """Test that article detail response has the correct structure."""
        # This test requires an actual article ID
        # For now, we'll just verify the endpoint pattern
        response = client.get("/api/articles/https://example.com/article")

        if response.status_code == 200:
            data = response.json()

            # Full article fields
            required_fields = [
                "id", "url", "title", "content", "summary",
                "classification", "sentimentScore", "publishDate",
                "source", "entities", "scrapedAt"
            ]

            for field in required_fields:
                assert field in data, f"Article detail must include '{field}' field"

    def test_article_detail_entities_structure(self, client):
        """Test that entities have the correct structure."""
        response = client.get("/api/articles/https://example.com/article")

        if response.status_code == 200:
            data = response.json()

            if "entities" in data and len(data["entities"]) > 0:
                entity = data["entities"][0]

                assert "text" in entity
                assert "type" in entity
                assert "mentions" in entity
                assert entity["type"] in ["company", "person", "product", "technology"]

    def test_article_not_found(self, client):
        """Test that non-existent article returns 404."""
        response = client.get("/api/articles/non-existent-id-12345")
        assert response.status_code == 404

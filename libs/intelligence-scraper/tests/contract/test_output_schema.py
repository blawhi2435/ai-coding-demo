"""
Contract tests for scraper output schema

Verifies that the scraper output conforms to the expected schema.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


class TestScraperOutputSchema:
    """Contract tests for ScrapedArticle model output."""

    def test_scraper_model_exists(self):
        """Test that the ScrapedArticle model can be imported."""
        try:
            from intelligence_scraper.models import ScrapedArticle
            assert ScrapedArticle is not None
        except ImportError:
            pytest.fail("ScrapedArticle model should be importable from intelligence_scraper.models")

    def test_scraper_output_required_fields(self):
        """Test that ScrapedArticle requires all mandatory fields."""
        from intelligence_scraper.models import ScrapedArticle

        # Valid article with all required fields
        valid_article = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        article = ScrapedArticle(**valid_article)
        assert article.url == "https://example.com/article"
        assert article.title == "Test Article"
        assert article.content == "This is test content."
        assert article.source == "Example News"

    def test_scraper_output_missing_required_field(self):
        """Test that ScrapedArticle raises error when required fields are missing."""
        from intelligence_scraper.models import ScrapedArticle

        # Missing required field 'title'
        invalid_article = {
            "url": "https://example.com/article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        with pytest.raises(ValidationError) as exc_info:
            ScrapedArticle(**invalid_article)

        assert "title" in str(exc_info.value).lower()

    def test_scraper_output_url_validation(self):
        """Test that ScrapedArticle validates URL format."""
        from intelligence_scraper.models import ScrapedArticle

        # Invalid URL format
        invalid_article = {
            "url": "not-a-valid-url",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        with pytest.raises(ValidationError) as exc_info:
            ScrapedArticle(**invalid_article)

        assert "url" in str(exc_info.value).lower()

    def test_scraper_output_publish_date_format(self):
        """Test that ScrapedArticle accepts ISO 8601 datetime format."""
        from intelligence_scraper.models import ScrapedArticle

        valid_article = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        article = ScrapedArticle(**valid_article)
        assert isinstance(article.publishDate, datetime)

    def test_scraper_output_empty_content_validation(self):
        """Test that ScrapedArticle rejects empty content."""
        from intelligence_scraper.models import ScrapedArticle

        # Empty content string
        invalid_article = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        with pytest.raises(ValidationError) as exc_info:
            ScrapedArticle(**invalid_article)

        assert "content" in str(exc_info.value).lower()

    def test_scraper_output_metadata_field(self):
        """Test that ScrapedArticle includes optional metadata field."""
        from intelligence_scraper.models import ScrapedArticle

        article_with_metadata = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
            "metadata": {
                "scraperMethod": "trafilatura",
                "contentTruncated": False,
            },
        }

        article = ScrapedArticle(**article_with_metadata)
        assert article.metadata is not None
        assert article.metadata["scraperMethod"] == "trafilatura"
        assert article.metadata["contentTruncated"] is False

    def test_scraper_output_json_serialization(self):
        """Test that ScrapedArticle can be serialized to JSON."""
        from intelligence_scraper.models import ScrapedArticle

        valid_article = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        article = ScrapedArticle(**valid_article)
        json_output = article.model_dump_json()

        assert isinstance(json_output, str)
        assert "https://example.com/article" in json_output
        assert "Test Article" in json_output

    def test_scraper_output_title_min_length(self):
        """Test that ScrapedArticle enforces minimum title length."""
        from intelligence_scraper.models import ScrapedArticle

        # Very short title
        invalid_article = {
            "url": "https://example.com/article",
            "title": "T",
            "content": "This is test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example News",
        }

        with pytest.raises(ValidationError) as exc_info:
            ScrapedArticle(**invalid_article)

        assert "title" in str(exc_info.value).lower()

    def test_scraper_output_multiple_articles_list(self):
        """Test that multiple ScrapedArticle instances can be created and stored in a list."""
        from intelligence_scraper.models import ScrapedArticle

        articles_data = [
            {
                "url": "https://example.com/article1",
                "title": "First Article",
                "content": "Content of first article.",
                "publishDate": "2024-01-15T10:00:00Z",
                "source": "Example News",
            },
            {
                "url": "https://example.com/article2",
                "title": "Second Article",
                "content": "Content of second article.",
                "publishDate": "2024-01-16T10:00:00Z",
                "source": "Example News",
            },
        ]

        articles = [ScrapedArticle(**data) for data in articles_data]

        assert len(articles) == 2
        assert articles[0].title == "First Article"
        assert articles[1].title == "Second Article"

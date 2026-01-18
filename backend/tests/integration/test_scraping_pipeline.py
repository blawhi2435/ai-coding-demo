"""
Integration tests for scraper → MongoDB pipeline

Tests the integration between the scraper library and MongoDB storage.
"""

import pytest
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


class TestScrapingPipeline:
    """Integration tests for scraper to MongoDB pipeline."""

    @pytest.fixture(scope="class")
    async def mongodb_connection(self):
        """Setup MongoDB connection for tests."""
        client = AsyncIOMotorClient("mongodb://mongodb:27017")
        db = client["intelligence_test"]
        yield db
        # Cleanup: drop test database after tests
        await client.drop_database("intelligence_test")
        client.close()

    @pytest.fixture
    async def clean_articles_collection(self, mongodb_connection):
        """Clean articles collection before each test."""
        await mongodb_connection.articles.delete_many({})
        yield
        await mongodb_connection.articles.delete_many({})

    @pytest.mark.asyncio
    async def test_scraper_library_can_be_imported(self):
        """Test that the scraper library can be imported."""
        try:
            from intelligence_scraper.models import ScrapedArticle
            from intelligence_scraper.extractors.base import BaseScraper
            assert ScrapedArticle is not None
            assert BaseScraper is not None
        except ImportError as e:
            pytest.fail(f"Failed to import scraper library: {e}")

    @pytest.mark.asyncio
    async def test_scraped_article_can_be_stored_in_mongodb(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that a scraped article can be stored in MongoDB."""
        from intelligence_scraper.models import ScrapedArticle

        # Create a scraped article
        article_data = {
            "url": "https://example.com/test-article",
            "title": "Test Article for MongoDB Storage",
            "content": "This is test content that should be stored in MongoDB.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Test Source",
            "metadata": {
                "scraperMethod": "trafilatura",
                "contentTruncated": False,
            },
        }

        article = ScrapedArticle(**article_data)

        # Store in MongoDB
        article_dict = article.model_dump()
        article_dict["_id"] = article_dict["url"]  # Use URL as unique ID
        article_dict["scrapedAt"] = datetime.utcnow()
        article_dict["status"] = "pending"  # Pending analysis

        result = await mongodb_connection.articles.insert_one(article_dict)
        assert result.inserted_id is not None

        # Verify article was stored
        stored_article = await mongodb_connection.articles.find_one({"_id": article_dict["url"]})
        assert stored_article is not None
        assert stored_article["title"] == "Test Article for MongoDB Storage"
        assert stored_article["status"] == "pending"

    @pytest.mark.asyncio
    async def test_multiple_scraped_articles_can_be_stored(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that multiple scraped articles can be stored in MongoDB."""
        from intelligence_scraper.models import ScrapedArticle

        articles_data = [
            {
                "url": f"https://example.com/article-{i}",
                "title": f"Test Article {i}",
                "content": f"Content for article {i}.",
                "publishDate": "2024-01-15T10:00:00Z",
                "source": "Test Source",
            }
            for i in range(5)
        ]

        articles = [ScrapedArticle(**data) for data in articles_data]

        # Store all articles
        for article in articles:
            article_dict = article.model_dump()
            article_dict["_id"] = article_dict["url"]
            article_dict["scrapedAt"] = datetime.utcnow()
            article_dict["status"] = "pending"
            await mongodb_connection.articles.insert_one(article_dict)

        # Verify all articles were stored
        count = await mongodb_connection.articles.count_documents({})
        assert count == 5

        # Verify each article exists
        for i in range(5):
            article = await mongodb_connection.articles.find_one(
                {"_id": f"https://example.com/article-{i}"}
            )
            assert article is not None
            assert article["title"] == f"Test Article {i}"

    @pytest.mark.asyncio
    async def test_duplicate_url_handling(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that duplicate URLs are handled correctly (update vs insert)."""
        from intelligence_scraper.models import ScrapedArticle

        article_data = {
            "url": "https://example.com/duplicate-test",
            "title": "Original Title",
            "content": "Original content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Test Source",
        }

        # Insert first article
        article1 = ScrapedArticle(**article_data)
        article_dict1 = article1.model_dump()
        article_dict1["_id"] = article_dict1["url"]
        article_dict1["scrapedAt"] = datetime.utcnow()
        article_dict1["status"] = "pending"

        await mongodb_connection.articles.insert_one(article_dict1)

        # Try to insert duplicate (same URL)
        article_data["title"] = "Updated Title"
        article2 = ScrapedArticle(**article_data)
        article_dict2 = article2.model_dump()
        article_dict2["_id"] = article_dict2["url"]
        article_dict2["scrapedAt"] = datetime.utcnow()
        article_dict2["status"] = "pending"

        # Should fail due to duplicate _id
        with pytest.raises(Exception):  # DuplicateKeyError
            await mongodb_connection.articles.insert_one(article_dict2)

        # Should succeed with upsert
        await mongodb_connection.articles.replace_one(
            {"_id": article_dict2["url"]}, article_dict2, upsert=True
        )

        # Verify only one document exists with updated title
        count = await mongodb_connection.articles.count_documents({})
        assert count == 1

        article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/duplicate-test"}
        )
        assert article["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_scraping_pipeline_with_status_flags(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that articles can be stored with different status flags."""
        from intelligence_scraper.models import ScrapedArticle

        statuses = ["pending", "complete", "failed"]

        for i, status in enumerate(statuses):
            article_data = {
                "url": f"https://example.com/status-{status}",
                "title": f"Article with {status} status",
                "content": "Test content.",
                "publishDate": "2024-01-15T10:00:00Z",
                "source": "Test Source",
            }

            article = ScrapedArticle(**article_data)
            article_dict = article.model_dump()
            article_dict["_id"] = article_dict["url"]
            article_dict["scrapedAt"] = datetime.utcnow()
            article_dict["status"] = status

            await mongodb_connection.articles.insert_one(article_dict)

        # Verify status filtering works
        pending_count = await mongodb_connection.articles.count_documents({"status": "pending"})
        complete_count = await mongodb_connection.articles.count_documents({"status": "complete"})
        failed_count = await mongodb_connection.articles.count_documents({"status": "failed"})

        assert pending_count == 1
        assert complete_count == 1
        assert failed_count == 1

    @pytest.mark.asyncio
    async def test_scraping_pipeline_metadata_storage(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that scraper metadata is properly stored."""
        from intelligence_scraper.models import ScrapedArticle

        article_data = {
            "url": "https://example.com/metadata-test",
            "title": "Article with Metadata",
            "content": "Test content.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Test Source",
            "metadata": {
                "scraperMethod": "playwright",
                "contentTruncated": True,
                "processingTime": 2.5,
            },
        }

        article = ScrapedArticle(**article_data)
        article_dict = article.model_dump()
        article_dict["_id"] = article_dict["url"]
        article_dict["scrapedAt"] = datetime.utcnow()
        article_dict["status"] = "pending"

        await mongodb_connection.articles.insert_one(article_dict)

        # Verify metadata was stored correctly
        stored_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/metadata-test"}
        )

        assert stored_article["metadata"]["scraperMethod"] == "playwright"
        assert stored_article["metadata"]["contentTruncated"] is True
        assert stored_article["metadata"]["processingTime"] == 2.5

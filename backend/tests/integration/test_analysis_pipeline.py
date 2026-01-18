"""
Integration tests for analyzer → MongoDB pipeline

Tests the integration between the analyzer library and MongoDB storage.
"""

import pytest
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


class TestAnalysisPipeline:
    """Integration tests for analyzer to MongoDB pipeline."""

    @pytest.fixture(scope="class")
    async def mongodb_connection(self):
        """Setup MongoDB connection for tests."""
        client = AsyncIOMotorClient("mongodb://mongodb:27017")
        db = client["intelligence_test"]
        yield db
        # Cleanup
        await client.drop_database("intelligence_test")
        client.close()

    @pytest.fixture
    async def clean_articles_collection(self, mongodb_connection):
        """Clean articles collection before each test."""
        await mongodb_connection.articles.delete_many({})
        yield
        await mongodb_connection.articles.delete_many({})

    @pytest.mark.asyncio
    async def test_analyzer_library_can_be_imported(self):
        """Test that the analyzer library can be imported."""
        try:
            from intelligence_analyzer.models import AnalysisInput, AnalysisResult
            assert AnalysisInput is not None
            assert AnalysisResult is not None
        except ImportError as e:
            pytest.fail(f"Failed to import analyzer library: {e}")

    @pytest.mark.asyncio
    async def test_analysis_result_can_update_article_in_mongodb(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that analysis results can update an existing article in MongoDB."""
        from intelligence_analyzer.models import AnalysisResult

        # First, insert a pending article
        pending_article = {
            "_id": "https://example.com/test-article",
            "url": "https://example.com/test-article",
            "title": "Test Article",
            "content": "This is test content.",
            "publishDate": datetime(2024, 1, 15, 10, 0, 0),
            "source": "Test Source",
            "scrapedAt": datetime.utcnow(),
            "status": "pending",
        }

        await mongodb_connection.articles.insert_one(pending_article)

        # Create analysis result
        analysis_data = {
            "summary": "This article discusses NVIDIA's latest innovations in AI and GPU technology.",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 5},
                {"text": "Jensen Huang", "type": "person", "mentions": 2},
            ],
            "classification": "product_launch",
            "sentimentScore": 8,
        }

        analysis_result = AnalysisResult(**analysis_data)

        # Update article with analysis results
        update_data = {
            "summary": analysis_result.summary,
            "entities": [entity.model_dump() for entity in analysis_result.entities],
            "classification": analysis_result.classification,
            "sentimentScore": analysis_result.sentimentScore,
            "analyzedAt": datetime.utcnow(),
            "status": "complete",
        }

        await mongodb_connection.articles.update_one(
            {"_id": "https://example.com/test-article"}, {"$set": update_data}
        )

        # Verify article was updated
        updated_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/test-article"}
        )

        assert updated_article["status"] == "complete"
        assert updated_article["summary"] == analysis_data["summary"]
        assert len(updated_article["entities"]) == 2
        assert updated_article["classification"] == "product_launch"
        assert updated_article["sentimentScore"] == 8
        assert updated_article["analyzedAt"] is not None

    @pytest.mark.asyncio
    async def test_analysis_result_entities_stored_correctly(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that entity information is stored correctly in MongoDB."""
        from intelligence_analyzer.models import AnalysisResult

        # Insert pending article
        pending_article = {
            "_id": "https://example.com/entity-test",
            "url": "https://example.com/entity-test",
            "title": "Entity Test Article",
            "content": "Content",
            "publishDate": datetime(2024, 1, 15, 10, 0, 0),
            "source": "Test Source",
            "scrapedAt": datetime.utcnow(),
            "status": "pending",
        }

        await mongodb_connection.articles.insert_one(pending_article)

        # Create analysis with multiple entities
        analysis_data = {
            "summary": "Article summary with multiple entities.",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 10},
                {"text": "Jensen Huang", "type": "person", "mentions": 3},
                {"text": "H100", "type": "product", "mentions": 7},
                {"text": "AI", "type": "technology", "mentions": 15},
            ],
            "classification": "competitive_news",
            "sentimentScore": 7,
        }

        analysis_result = AnalysisResult(**analysis_data)

        # Update article
        update_data = {
            "summary": analysis_result.summary,
            "entities": [entity.model_dump() for entity in analysis_result.entities],
            "classification": analysis_result.classification,
            "sentimentScore": analysis_result.sentimentScore,
            "analyzedAt": datetime.utcnow(),
            "status": "complete",
        }

        await mongodb_connection.articles.update_one(
            {"_id": "https://example.com/entity-test"}, {"$set": update_data}
        )

        # Verify entities were stored with correct structure
        updated_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/entity-test"}
        )

        assert len(updated_article["entities"]) == 4

        # Verify each entity has correct structure
        nvidia_entity = next(e for e in updated_article["entities"] if e["text"] == "NVIDIA")
        assert nvidia_entity["type"] == "company"
        assert nvidia_entity["mentions"] == 10

        ai_entity = next(e for e in updated_article["entities"] if e["text"] == "AI")
        assert ai_entity["type"] == "technology"
        assert ai_entity["mentions"] == 15

    @pytest.mark.asyncio
    async def test_analysis_failure_updates_status(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that failed analysis updates article status to 'failed'."""
        # Insert pending article
        pending_article = {
            "_id": "https://example.com/failed-analysis",
            "url": "https://example.com/failed-analysis",
            "title": "Failed Analysis Test",
            "content": "Content",
            "publishDate": datetime(2024, 1, 15, 10, 0, 0),
            "source": "Test Source",
            "scrapedAt": datetime.utcnow(),
            "status": "pending",
        }

        await mongodb_connection.articles.insert_one(pending_article)

        # Simulate failed analysis by updating status
        await mongodb_connection.articles.update_one(
            {"_id": "https://example.com/failed-analysis"},
            {
                "$set": {
                    "status": "failed",
                    "metadata": {"error": "Analysis timeout", "failedAt": datetime.utcnow()},
                }
            },
        )

        # Verify article status was updated to failed
        failed_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/failed-analysis"}
        )

        assert failed_article["status"] == "failed"
        assert "error" in failed_article["metadata"]
        assert failed_article["metadata"]["error"] == "Analysis timeout"

    @pytest.mark.asyncio
    async def test_classification_values_stored_correctly(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that all classification types can be stored correctly."""
        from intelligence_analyzer.models import AnalysisResult

        classifications = [
            "competitive_news",
            "personnel_change",
            "product_launch",
            "market_trend",
        ]

        for i, classification in enumerate(classifications):
            # Insert pending article
            article_id = f"https://example.com/classification-{classification}"
            pending_article = {
                "_id": article_id,
                "url": article_id,
                "title": f"Test {classification}",
                "content": "Content",
                "publishDate": datetime(2024, 1, 15, 10, 0, 0),
                "source": "Test Source",
                "scrapedAt": datetime.utcnow(),
                "status": "pending",
            }

            await mongodb_connection.articles.insert_one(pending_article)

            # Create analysis with specific classification
            analysis_data = {
                "summary": f"Summary for {classification} article.",
                "entities": [],
                "classification": classification,
                "sentimentScore": 5,
            }

            analysis_result = AnalysisResult(**analysis_data)

            # Update article
            await mongodb_connection.articles.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "summary": analysis_result.summary,
                        "entities": [],
                        "classification": analysis_result.classification,
                        "sentimentScore": analysis_result.sentimentScore,
                        "analyzedAt": datetime.utcnow(),
                        "status": "complete",
                    }
                },
            )

        # Verify all classifications were stored
        for classification in classifications:
            article_id = f"https://example.com/classification-{classification}"
            article = await mongodb_connection.articles.find_one({"_id": article_id})
            assert article["classification"] == classification
            assert article["status"] == "complete"

    @pytest.mark.asyncio
    async def test_sentiment_scores_stored_correctly(
        self, mongodb_connection, clean_articles_collection
    ):
        """Test that sentiment scores in range 1-10 are stored correctly."""
        from intelligence_analyzer.models import AnalysisResult

        sentiment_scores = [1, 3, 5, 7, 10]

        for score in sentiment_scores:
            article_id = f"https://example.com/sentiment-{score}"
            pending_article = {
                "_id": article_id,
                "url": article_id,
                "title": f"Sentiment {score} Test",
                "content": "Content",
                "publishDate": datetime(2024, 1, 15, 10, 0, 0),
                "source": "Test Source",
                "scrapedAt": datetime.utcnow(),
                "status": "pending",
            }

            await mongodb_connection.articles.insert_one(pending_article)

            analysis_data = {
                "summary": f"Summary with sentiment score {score}.",
                "entities": [],
                "classification": "market_trend",
                "sentimentScore": score,
            }

            analysis_result = AnalysisResult(**analysis_data)

            await mongodb_connection.articles.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "summary": analysis_result.summary,
                        "entities": [],
                        "classification": analysis_result.classification,
                        "sentimentScore": analysis_result.sentimentScore,
                        "analyzedAt": datetime.utcnow(),
                        "status": "complete",
                    }
                },
            )

        # Verify all sentiment scores were stored correctly
        for score in sentiment_scores:
            article_id = f"https://example.com/sentiment-{score}"
            article = await mongodb_connection.articles.find_one({"_id": article_id})
            assert article["sentimentScore"] == score

"""
End-to-end tests for full scraping and analysis workflow

Tests the complete pipeline from scraping to analysis to storage.
"""

import pytest
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


class TestFullPipeline:
    """E2E tests for complete scraping and analysis workflow."""

    @pytest.fixture(scope="class")
    async def mongodb_connection(self):
        """Setup MongoDB connection for tests."""
        client = AsyncIOMotorClient("mongodb://mongodb:27017")
        db = client["intelligence_test"]
        yield db
        await client.drop_database("intelligence_test")
        client.close()

    @pytest.fixture
    async def clean_database(self, mongodb_connection):
        """Clean database before each test."""
        await mongodb_connection.articles.delete_many({})
        yield
        await mongodb_connection.articles.delete_many({})

    @pytest.mark.asyncio
    async def test_full_pipeline_scrape_to_storage(
        self, mongodb_connection, clean_database
    ):
        """Test full pipeline: scrape → store → verify."""
        from intelligence_scraper.models import ScrapedArticle

        # Step 1: Simulate scraping
        scraped_data = {
            "url": "https://example.com/full-pipeline-test",
            "title": "Full Pipeline Test Article",
            "content": "This is content that will go through the full pipeline from scraping to analysis.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Example Source",
            "metadata": {"scraperMethod": "trafilatura"},
        }

        article = ScrapedArticle(**scraped_data)

        # Step 2: Store in MongoDB
        article_dict = article.model_dump()
        article_dict["_id"] = article_dict["url"]
        article_dict["scrapedAt"] = datetime.utcnow()
        article_dict["status"] = "pending"

        await mongodb_connection.articles.insert_one(article_dict)

        # Step 3: Verify article is stored with pending status
        stored_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/full-pipeline-test"}
        )

        assert stored_article is not None
        assert stored_article["status"] == "pending"
        assert stored_article["title"] == "Full Pipeline Test Article"
        assert "scrapedAt" in stored_article

    @pytest.mark.asyncio
    async def test_full_pipeline_scrape_analyze_update(
        self, mongodb_connection, clean_database
    ):
        """Test full pipeline: scrape → store → analyze → update."""
        from intelligence_scraper.models import ScrapedArticle
        from intelligence_analyzer.models import AnalysisResult

        # Step 1: Scrape and store
        scraped_data = {
            "url": "https://example.com/full-cycle-test",
            "title": "NVIDIA Announces New AI Chip",
            "content": "NVIDIA CEO Jensen Huang announced a groundbreaking new AI chip today. The H100 GPU represents a major leap forward in AI processing capabilities.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Tech News",
        }

        article = ScrapedArticle(**scraped_data)
        article_dict = article.model_dump()
        article_dict["_id"] = article_dict["url"]
        article_dict["scrapedAt"] = datetime.utcnow()
        article_dict["status"] = "pending"

        await mongodb_connection.articles.insert_one(article_dict)

        # Step 2: Simulate analysis
        analysis_data = {
            "summary": "NVIDIA unveils new H100 AI GPU with CEO Jensen Huang announcing major advancements in AI processing.",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 2},
                {"text": "Jensen Huang", "type": "person", "mentions": 1},
                {"text": "H100", "type": "product", "mentions": 1},
            ],
            "classification": "product_launch",
            "sentimentScore": 9,
        }

        analysis_result = AnalysisResult(**analysis_data)

        # Step 3: Update article with analysis results
        update_data = {
            "summary": analysis_result.summary,
            "entities": [entity.model_dump() for entity in analysis_result.entities],
            "classification": analysis_result.classification,
            "sentimentScore": analysis_result.sentimentScore,
            "analyzedAt": datetime.utcnow(),
            "status": "complete",
        }

        await mongodb_connection.articles.update_one(
            {"_id": "https://example.com/full-cycle-test"}, {"$set": update_data}
        )

        # Step 4: Verify complete pipeline
        final_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/full-cycle-test"}
        )

        # Verify article has both scraped and analyzed data
        assert final_article["status"] == "complete"
        assert final_article["title"] == "NVIDIA Announces New AI Chip"
        assert final_article["content"].startswith("NVIDIA CEO Jensen Huang")
        assert final_article["summary"] is not None
        assert len(final_article["entities"]) == 3
        assert final_article["classification"] == "product_launch"
        assert final_article["sentimentScore"] == 9
        assert "scrapedAt" in final_article
        assert "analyzedAt" in final_article

    @pytest.mark.asyncio
    async def test_full_pipeline_multiple_articles(
        self, mongodb_connection, clean_database
    ):
        """Test full pipeline with multiple articles processed in batch."""
        from intelligence_scraper.models import ScrapedArticle
        from intelligence_analyzer.models import AnalysisResult

        # Step 1: Scrape and store multiple articles
        articles_data = [
            {
                "url": f"https://example.com/batch-{i}",
                "title": f"Article {i}",
                "content": f"Content for article {i} about technology.",
                "publishDate": "2024-01-15T10:00:00Z",
                "source": "Tech News",
            }
            for i in range(3)
        ]

        for data in articles_data:
            article = ScrapedArticle(**data)
            article_dict = article.model_dump()
            article_dict["_id"] = article_dict["url"]
            article_dict["scrapedAt"] = datetime.utcnow()
            article_dict["status"] = "pending"
            await mongodb_connection.articles.insert_one(article_dict)

        # Verify all articles are pending
        pending_count = await mongodb_connection.articles.count_documents({"status": "pending"})
        assert pending_count == 3

        # Step 2: Analyze each article
        for i in range(3):
            analysis_data = {
                "summary": f"Summary for article {i}.",
                "entities": [{"text": f"Entity{i}", "type": "technology", "mentions": 1}],
                "classification": "market_trend",
                "sentimentScore": 5 + i,
            }

            analysis_result = AnalysisResult(**analysis_data)

            update_data = {
                "summary": analysis_result.summary,
                "entities": [entity.model_dump() for entity in analysis_result.entities],
                "classification": analysis_result.classification,
                "sentimentScore": analysis_result.sentimentScore,
                "analyzedAt": datetime.utcnow(),
                "status": "complete",
            }

            await mongodb_connection.articles.update_one(
                {"_id": f"https://example.com/batch-{i}"}, {"$set": update_data}
            )

        # Step 3: Verify all articles are complete
        complete_count = await mongodb_connection.articles.count_documents({"status": "complete"})
        assert complete_count == 3

        # Verify each article has analysis results
        for i in range(3):
            article = await mongodb_connection.articles.find_one(
                {"_id": f"https://example.com/batch-{i}"}
            )
            assert article["status"] == "complete"
            assert article["summary"] is not None
            assert len(article["entities"]) >= 1
            assert article["sentimentScore"] == 5 + i

    @pytest.mark.asyncio
    async def test_full_pipeline_with_failed_analysis(
        self, mongodb_connection, clean_database
    ):
        """Test full pipeline where some analyses fail."""
        from intelligence_scraper.models import ScrapedArticle

        # Step 1: Scrape and store article
        scraped_data = {
            "url": "https://example.com/failure-test",
            "title": "Article That Will Fail Analysis",
            "content": "Content that causes analysis failure.",
            "publishDate": "2024-01-15T10:00:00Z",
            "source": "Test Source",
        }

        article = ScrapedArticle(**scraped_data)
        article_dict = article.model_dump()
        article_dict["_id"] = article_dict["url"]
        article_dict["scrapedAt"] = datetime.utcnow()
        article_dict["status"] = "pending"

        await mongodb_connection.articles.insert_one(article_dict)

        # Step 2: Simulate failed analysis
        await mongodb_connection.articles.update_one(
            {"_id": "https://example.com/failure-test"},
            {
                "$set": {
                    "status": "failed",
                    "metadata": {
                        "error": "LLM timeout",
                        "failedAt": datetime.utcnow(),
                    },
                }
            },
        )

        # Step 3: Verify article is marked as failed
        failed_article = await mongodb_connection.articles.find_one(
            {"_id": "https://example.com/failure-test"}
        )

        assert failed_article["status"] == "failed"
        assert "error" in failed_article["metadata"]
        assert failed_article["metadata"]["error"] == "LLM timeout"
        # Article should still have original scraped content
        assert failed_article["title"] == "Article That Will Fail Analysis"
        assert failed_article["content"] == "Content that causes analysis failure."

    @pytest.mark.asyncio
    async def test_full_pipeline_query_analyzed_articles(
        self, mongodb_connection, clean_database
    ):
        """Test querying analyzed articles by various criteria."""
        from intelligence_scraper.models import ScrapedArticle
        from intelligence_analyzer.models import AnalysisResult

        # Create and analyze multiple articles with different classifications
        test_cases = [
            {
                "url": "https://example.com/query-1",
                "title": "Product Launch Article",
                "classification": "product_launch",
                "sentiment": 9,
            },
            {
                "url": "https://example.com/query-2",
                "title": "Market Trend Article",
                "classification": "market_trend",
                "sentiment": 6,
            },
            {
                "url": "https://example.com/query-3",
                "title": "Another Product Launch",
                "classification": "product_launch",
                "sentiment": 8,
            },
        ]

        for case in test_cases:
            # Scrape and store
            article = ScrapedArticle(
                url=case["url"],
                title=case["title"],
                content="Test content.",
                publishDate="2024-01-15T10:00:00Z",
                source="Test",
            )

            article_dict = article.model_dump()
            article_dict["_id"] = article_dict["url"]
            article_dict["scrapedAt"] = datetime.utcnow()
            article_dict["status"] = "pending"
            await mongodb_connection.articles.insert_one(article_dict)

            # Analyze
            analysis = AnalysisResult(
                summary="Summary",
                entities=[],
                classification=case["classification"],
                sentimentScore=case["sentiment"],
            )

            await mongodb_connection.articles.update_one(
                {"_id": case["url"]},
                {
                    "$set": {
                        "summary": analysis.summary,
                        "entities": [],
                        "classification": analysis.classification,
                        "sentimentScore": analysis.sentimentScore,
                        "analyzedAt": datetime.utcnow(),
                        "status": "complete",
                    }
                },
            )

        # Test queries
        # Query by classification
        product_launches = await mongodb_connection.articles.count_documents(
            {"classification": "product_launch"}
        )
        assert product_launches == 2

        # Query by sentiment range
        high_sentiment = await mongodb_connection.articles.count_documents(
            {"sentimentScore": {"$gte": 8}}
        )
        assert high_sentiment == 2

        # Query by status
        complete_articles = await mongodb_connection.articles.count_documents(
            {"status": "complete"}
        )
        assert complete_articles == 3

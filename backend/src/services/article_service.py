"""
Article storage service

Handles MongoDB operations for articles.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from src.utils.logger import logger


class ArticleService:
    """Service for managing articles in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize article service.

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db.articles

    async def upsert_scraped_article(self, article_data: Dict[str, Any]) -> str:
        """
        Insert or update a scraped article.

        Args:
            article_data: Article data from scraper

        Returns:
            str: Article ID (URL)
        """
        article_id = article_data["url"]

        # Prepare document
        doc = {
            "_id": article_id,
            **article_data,
            "scrapedAt": datetime.utcnow(),
            "status": "pending",  # Pending analysis
        }

        try:
            # Try to insert
            await self.collection.insert_one(doc)
            logger.info(
                f"Inserted new article",
                extra={"url": article_id, "title": article_data.get("title")},
            )
        except DuplicateKeyError:
            # Article already exists, update it
            await self.collection.replace_one({"_id": article_id}, doc)
            logger.info(
                f"Updated existing article",
                extra={"url": article_id, "title": article_data.get("title")},
            )

        return article_id

    async def update_with_analysis(
        self, article_id: str, analysis_data: Dict[str, Any]
    ) -> bool:
        """
        Update an article with analysis results.

        Args:
            article_id: Article ID (URL)
            analysis_data: Analysis results

        Returns:
            bool: True if successful
        """
        update = {
            "$set": {
                "summary": analysis_data["summary"],
                "entities": analysis_data["entities"],
                "classification": analysis_data["classification"],
                "sentimentScore": analysis_data["sentimentScore"],
                "analyzedAt": datetime.utcnow(),
                "status": "complete",
            }
        }

        result = await self.collection.update_one({"_id": article_id}, update)

        if result.modified_count > 0:
            logger.info(
                f"Updated article with analysis results",
                extra={"url": article_id, "classification": analysis_data["classification"]},
            )
            return True
        else:
            logger.warning(f"Article not found for analysis update", extra={"url": article_id})
            return False

    async def mark_as_failed(self, article_id: str, error: str) -> bool:
        """
        Mark an article as failed.

        Args:
            article_id: Article ID (URL)
            error: Error message

        Returns:
            bool: True if successful
        """
        update = {
            "$set": {
                "status": "failed",
                "metadata.error": error,
                "metadata.failedAt": datetime.utcnow(),
            }
        }

        result = await self.collection.update_one({"_id": article_id}, update)

        if result.modified_count > 0:
            logger.warning(
                f"Marked article as failed",
                extra={"url": article_id, "error": error},
            )
            return True
        else:
            return False

    async def get_pending_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get articles pending analysis.

        Args:
            limit: Maximum number of articles to return

        Returns:
            List[Dict]: List of pending articles
        """
        cursor = self.collection.find({"status": "pending"}).limit(limit)
        articles = await cursor.to_list(length=limit)
        return articles

    async def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get article by ID.

        Args:
            article_id: Article ID (URL)

        Returns:
            Optional[Dict]: Article data or None
        """
        article = await self.collection.find_one({"_id": article_id})
        return article

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get article statistics.

        Returns:
            Dict: Statistics (total, pending, complete, failed)
        """
        total = await self.collection.count_documents({})
        pending = await self.collection.count_documents({"status": "pending"})
        complete = await self.collection.count_documents({"status": "complete"})
        failed = await self.collection.count_documents({"status": "failed"})

        return {
            "total": total,
            "pending": pending,
            "complete": complete,
            "failed": failed,
        }

"""
Articles API routes

Provides endpoints for retrieving and filtering articles.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.db.mongo import get_database
from src.utils.logger import logger

router = APIRouter()


# Response models
class EntityResponse(BaseModel):
    """Entity response model."""
    text: str
    type: str
    mentions: int


class ArticleListItem(BaseModel):
    """Article list item model."""
    id: str
    url: str
    title: str
    summary: str
    classification: str
    sentimentScore: int
    publishDate: str
    source: str
    topEntities: List[str] = Field(default_factory=list)


class ArticleDetail(BaseModel):
    """Full article detail model."""
    id: str
    url: str
    title: str
    content: str
    summary: str
    classification: str
    sentimentScore: int
    publishDate: str
    source: str
    entities: List[EntityResponse]
    scrapedAt: str
    analyzedAt: Optional[str] = None
    status: str


class PaginatedArticles(BaseModel):
    """Paginated articles response."""
    total: int
    page: int
    pageSize: int
    data: List[ArticleListItem]


@router.get("/articles", response_model=PaginatedArticles)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(20, ge=1, le=100, description="Items per page"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    minSentiment: Optional[int] = Query(None, ge=1, le=10, description="Minimum sentiment score"),
    maxSentiment: Optional[int] = Query(None, ge=1, le=10, description="Maximum sentiment score"),
    startDate: Optional[str] = Query(None, description="Start date (ISO 8601)"),
    endDate: Optional[str] = Query(None, description="End date (ISO 8601)"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """
    Get paginated list of articles with optional filters.

    Query Parameters:
    - page: Page number (default: 1)
    - pageSize: Items per page (default: 20, max: 100)
    - classification: Filter by classification type
    - minSentiment: Minimum sentiment score (1-10)
    - maxSentiment: Maximum sentiment score (1-10)
    - startDate: Filter articles after this date
    - endDate: Filter articles before this date
    - search: Full-text search query

    Returns:
        PaginatedArticles: Paginated list of articles
    """
    logger.info(
        "Fetching articles",
        extra={
            "page": page,
            "pageSize": pageSize,
            "classification": classification,
            "minSentiment": minSentiment,
            "maxSentiment": maxSentiment,
            "search": search,
        },
    )

    try:
        # Build query filter
        query = {"status": "complete"}  # Only return completed articles

        # Classification filter
        if classification:
            query["classification"] = classification

        # Sentiment filter
        if minSentiment is not None or maxSentiment is not None:
            sentiment_query = {}
            if minSentiment is not None:
                sentiment_query["$gte"] = minSentiment
            if maxSentiment is not None:
                sentiment_query["$lte"] = maxSentiment
            query["sentimentScore"] = sentiment_query

        # Date range filter
        if startDate or endDate:
            date_query = {}
            if startDate:
                try:
                    start_dt = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
                    date_query["$gte"] = start_dt
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid startDate format")
            if endDate:
                try:
                    end_dt = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
                    date_query["$lte"] = end_dt
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid endDate format")
            query["publishDate"] = date_query

        # Full-text search
        if search:
            query["$text"] = {"$search": search}

        # Calculate pagination
        skip = (page - 1) * pageSize

        # Get database instance
        db = get_database()

        # Get total count
        total = await db.articles.count_documents(query)

        # Get articles with pagination
        cursor = db.articles.find(query).sort("publishDate", -1).skip(skip).limit(pageSize)
        articles = await cursor.to_list(length=pageSize)

        # Transform to response model
        article_items = []
        for article in articles:
            # Extract top 3 entities
            entities = article.get("entities", [])
            top_entities = [e["text"] for e in sorted(entities, key=lambda x: x.get("mentions", 0), reverse=True)[:3]]

            # Handle both string and datetime publishDate
            publish_date = article["publishDate"]
            if isinstance(publish_date, str):
                publish_date_str = publish_date if publish_date.endswith("Z") else publish_date + "Z"
            else:
                publish_date_str = publish_date.isoformat() + "Z"

            article_items.append(
                ArticleListItem(
                    id=article["_id"],
                    url=article["url"],
                    title=article["title"],
                    summary=article.get("summary", ""),
                    classification=article.get("classification", ""),
                    sentimentScore=article.get("sentimentScore", 5),
                    publishDate=publish_date_str,
                    source=article["source"],
                    topEntities=top_entities,
                )
            )

        logger.info(
            f"Returned {len(article_items)} articles",
            extra={"total": total, "page": page, "returned": len(article_items)},
        )

        return PaginatedArticles(
            total=total,
            page=page,
            pageSize=pageSize,
            data=article_items,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch articles: {e}", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch articles")


@router.get("/articles/{article_id:path}", response_model=ArticleDetail)
async def get_article_by_id(article_id: str):
    """
    Get full article details by ID.

    Args:
        article_id: Article ID (URL)

    Returns:
        ArticleDetail: Full article details

    Raises:
        HTTPException: 404 if article not found
    """
    logger.info(f"Fetching article detail", extra={"article_id": article_id})

    try:
        db = get_database()
        article = await db.articles.find_one({"_id": article_id})

        if not article:
            logger.warning(f"Article not found", extra={"article_id": article_id})
            raise HTTPException(status_code=404, detail="Article not found")

        # Transform entities
        entities = [
            EntityResponse(
                text=e["text"],
                type=e["type"],
                mentions=e["mentions"],
            )
            for e in article.get("entities", [])
        ]

        # Handle both string and datetime formats
        def format_date(date_field):
            if isinstance(date_field, str):
                return date_field if date_field.endswith("Z") else date_field + "Z"
            return date_field.isoformat() + "Z" if date_field else None

        article_detail = ArticleDetail(
            id=article["_id"],
            url=article["url"],
            title=article["title"],
            content=article["content"],
            summary=article.get("summary", ""),
            classification=article.get("classification", ""),
            sentimentScore=article.get("sentimentScore", 5),
            publishDate=format_date(article["publishDate"]),
            source=article["source"],
            entities=entities,
            scrapedAt=format_date(article["scrapedAt"]),
            analyzedAt=format_date(article.get("analyzedAt")),
            status=article.get("status", "pending"),
        )

        logger.info(f"Returned article detail", extra={"article_id": article_id})

        return article_detail

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to fetch article detail: {e}",
            extra={"article_id": article_id, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Failed to fetch article")

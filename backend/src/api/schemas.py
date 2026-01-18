"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field, HttpUrl


class EntitySummary(BaseModel):
    """Aggregated entity information across articles."""

    text: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type")
    totalMentions: int = Field(..., ge=1, description="Total mentions across all articles")
    articleCount: int = Field(..., ge=1, description="Number of articles mentioning this entity")
    articleIds: List[str] = Field(..., description="List of article IDs containing this entity")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "NVIDIA",
                "type": "company",
                "totalMentions": 127,
                "articleCount": 45,
                "articleIds": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
            }
        }


class ArticleListItem(BaseModel):
    """Lightweight article representation for list views."""

    id: str = Field(alias="_id", description="MongoDB ObjectId")
    url: HttpUrl = Field(..., description="Source URL")
    title: str = Field(..., description="Article title")
    summary: str = Field(..., description="Generated summary")
    classification: str = Field(..., description="Article classification")
    sentimentScore: int = Field(..., ge=1, le=10, description="Sentiment score")
    publishDate: datetime = Field(..., description="Publication date")
    source: str = Field(..., description="Source website")
    topEntities: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Top 3 entity names for preview",
    )

    class Config:
        populate_by_name = True


class PaginatedArticles(BaseModel):
    """Paginated article list response."""

    total: int = Field(..., ge=0, description="Total articles matching filters")
    page: int = Field(..., ge=1, description="Current page number")
    pageSize: int = Field(..., ge=1, le=100, description="Items per page")
    data: List[ArticleListItem] = Field(..., description="Article list items")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "pageSize": 20,
                "data": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "title": "NVIDIA Announces New AI Supercomputer",
                        "summary": "NVIDIA launched DGX H200...",
                        "classification": "product_launch",
                        "sentimentScore": 9,
                        "publishDate": "2026-01-15T10:00:00Z",
                        "source": "NVIDIA Newsroom",
                        "topEntities": ["NVIDIA", "DGX H200", "Jensen Huang"],
                    }
                ],
            }
        }


class AggregatedStats(BaseModel):
    """Dashboard statistics for aggregated data."""

    totalArticles: int = Field(..., ge=0, description="Total articles analyzed")
    classificationBreakdown: Dict[str, int] = Field(
        ..., description="Count per classification"
    )
    avgSentiment: float = Field(..., ge=1.0, le=10.0, description="Average sentiment score")
    lastUpdated: datetime = Field(..., description="Last article analysis timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "totalArticles": 150,
                "classificationBreakdown": {
                    "product_launch": 45,
                    "competitive_news": 38,
                    "market_trend": 42,
                    "personnel_change": 25,
                },
                "avgSentiment": 6.8,
                "lastUpdated": "2026-01-17T10:30:00Z",
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Overall service status")
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check time")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {"mongodb": "connected", "llm": "available"},
                "timestamp": "2026-01-17T10:30:00Z",
            }
        }

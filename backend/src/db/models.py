"""Pydantic models for MongoDB documents."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Entity(BaseModel):
    """Named entity extracted from article."""

    text: str = Field(..., min_length=1, description="Entity text")
    type: str = Field(..., description="Entity type: company, person, product, technology")
    mentions: int = Field(default=1, ge=1, description="Number of mentions in article")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "NVIDIA",
                "type": "company",
                "mentions": 5,
            }
        }


class Article(BaseModel):
    """Complete article document stored in MongoDB."""

    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId as string")
    url: HttpUrl = Field(..., description="Source article URL (unique)")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Full article text")
    publishDate: datetime = Field(..., description="Publication date")
    source: str = Field(..., description="Source website")
    summary: str = Field(default="", description="Generated summary")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    classification: str = Field(
        default="",
        description="Article classification: competitive_news, personnel_change, product_launch, market_trend",
    )
    sentimentScore: int = Field(default=5, ge=1, le=10, description="Sentiment score (1-10)")
    scrapedAt: datetime = Field(
        default_factory=datetime.utcnow, description="Scraping timestamp"
    )
    analyzedAt: Optional[datetime] = Field(default=None, description="Analysis timestamp")
    status: str = Field(
        default="pending",
        description="Processing status: complete, pending, failed",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional technical metadata"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
                "title": "NVIDIA Announces New AI Supercomputer",
                "content": "NVIDIA today unveiled...",
                "publishDate": "2026-01-15T10:00:00Z",
                "source": "NVIDIA Newsroom",
                "summary": "NVIDIA launched DGX H200...",
                "entities": [{"text": "NVIDIA", "type": "company", "mentions": 5}],
                "classification": "product_launch",
                "sentimentScore": 9,
                "scrapedAt": "2026-01-17T08:30:00Z",
                "analyzedAt": "2026-01-17T08:35:00Z",
                "status": "complete",
                "metadata": {
                    "scraperMethod": "trafilatura",
                    "contentTruncated": False,
                    "processingTime": 4.2,
                },
            }
        }

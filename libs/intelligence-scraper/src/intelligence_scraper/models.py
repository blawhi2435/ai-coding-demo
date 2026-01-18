"""
Pydantic models for scraper library

Defines the data structures for scraped articles.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator


class ScrapedArticle(BaseModel):
    """
    Model representing a scraped article.

    This model defines the structure of data extracted by scrapers.
    """

    url: HttpUrl = Field(..., description="Article URL")
    title: str = Field(..., min_length=3, description="Article title")
    content: str = Field(..., min_length=10, description="Article content")
    publishDate: datetime = Field(..., description="Publication date (ISO 8601)")
    source: str = Field(..., description="Source name (e.g., 'NVIDIA Newsroom')")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (scraperMethod, contentTruncated, etc.)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://nvidianews.nvidia.com/news/example",
                "title": "NVIDIA Announces New GPU Architecture",
                "content": "NVIDIA today announced...",
                "publishDate": "2024-01-15T10:00:00Z",
                "source": "NVIDIA Newsroom",
                "metadata": {
                    "scraperMethod": "trafilatura",
                    "contentTruncated": False,
                },
            }
        }
    }

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

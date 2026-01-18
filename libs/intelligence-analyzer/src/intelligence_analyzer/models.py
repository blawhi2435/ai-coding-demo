"""
Pydantic models for analyzer library

Defines input and output data structures for analysis.
"""

from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, HttpUrl, Field


class Entity(BaseModel):
    """Entity extracted from article content."""

    text: str = Field(..., min_length=1, description="Entity text")
    type: Literal["company", "person", "product", "technology"] = Field(
        ..., description="Entity type"
    )
    mentions: int = Field(..., ge=1, description="Number of mentions in the article")


class AnalysisInput(BaseModel):
    """Input data for analysis."""

    url: HttpUrl = Field(..., description="Article URL")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    publishDate: datetime = Field(..., description="Publication date")


class AnalysisResult(BaseModel):
    """Result of article analysis."""

    summary: str = Field(..., min_length=20, description="Article summary")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    classification: Literal[
        "competitive_news", "personnel_change", "product_launch", "market_trend"
    ] = Field(..., description="Article classification")
    sentimentScore: int = Field(..., ge=1, le=10, description="Sentiment score (1-10)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "summary": "NVIDIA announces breakthrough AI chip with CEO Jensen Huang unveiling the H100 GPU.",
                "entities": [
                    {"text": "NVIDIA", "type": "company", "mentions": 5},
                    {"text": "Jensen Huang", "type": "person", "mentions": 2},
                    {"text": "H100", "type": "product", "mentions": 3},
                ],
                "classification": "product_launch",
                "sentimentScore": 9,
            }
        }
    }

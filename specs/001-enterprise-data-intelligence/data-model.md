# Data Model: Enterprise Data Intelligence Assistant

**Feature**: 001-enterprise-data-intelligence
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines all data models, entities, and their relationships for the Enterprise Data Intelligence Assistant. Models are organized by layer (library, service, database) to support the library-first architecture.

---

## 1. Scraper Library Models

### 1.1 ScrapedArticle (Output Contract)

**Purpose**: Standard output format from scraper library CLI

**Schema**:
```python
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List

class ScrapedArticle(BaseModel):
    """Output contract for intelligence-scraper library"""

    url: HttpUrl = Field(..., description="Source article URL")
    title: str = Field(..., min_length=1, description="Article title")
    content: str = Field(..., min_length=50, description="Clean article text (HTML stripped)")
    publishDate: datetime = Field(..., description="Publication date from article metadata")
    source: str = Field(..., description="Source website name (e.g., 'NVIDIA Newsroom')")
    keywords: Optional[List[str]] = Field(default=[], description="Extracted keywords if available")

    # Metadata
    scrapedAt: datetime = Field(default_factory=datetime.utcnow, description="Scraping timestamp")
    scraperMethod: str = Field(..., description="Extraction method: 'trafilatura' or 'playwright'")
    contentTruncated: bool = Field(default=False, description="True if content exceeded max length")
    errorLog: Optional[str] = Field(default=None, description="Error details if scraping partially failed")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
                "title": "NVIDIA Announces New AI Supercomputer",
                "content": "NVIDIA today unveiled its latest DGX system...",
                "publishDate": "2026-01-15T10:00:00Z",
                "source": "NVIDIA Newsroom",
                "keywords": ["AI", "supercomputer", "DGX"],
                "scrapedAt": "2026-01-17T08:30:00Z",
                "scraperMethod": "trafilatura",
                "contentTruncated": False,
                "errorLog": None
            }
        }
```

**Validation Rules**:
- `url` must be valid HTTP/HTTPS URL
- `title` cannot be empty
- `content` must have at least 50 characters (indicates successful extraction)
- `publishDate` cannot be in the future
- `scraperMethod` must be one of: "trafilatura", "playwright"

**CLI Output Format** (JSON to stdout):
```bash
$ intelligence-scraper scrape nvidia output.json
# Writes ScrapedArticle JSON array to output.json
# Logs to stderr with structured JSON logging
```

---

## 2. Analyzer Library Models

### 2.1 AnalysisInput (Input Contract)

**Purpose**: Standard input format for analyzer library CLI

**Schema**:
```python
class AnalysisInput(BaseModel):
    """Input contract for intelligence-analyzer library"""

    url: HttpUrl = Field(..., description="Article URL (for reference)")
    title: str = Field(..., description="Article title")
    content: str = Field(..., max_length=10000, description="Article text to analyze")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
                "title": "NVIDIA Announces New AI Supercomputer",
                "content": "NVIDIA today unveiled its latest DGX system featuring breakthrough performance for large language model training..."
            }
        }
```

**Validation Rules**:
- `content` max length 10,000 characters (enforces LLM context window limit)
- Content will be truncated if needed before LLM processing

### 2.2 Entity

**Purpose**: Extracted named entity from article text

**Schema**:
```python
class Entity(BaseModel):
    """Named entity extracted from article"""

    text: str = Field(..., min_length=1, description="Entity text (e.g., 'NVIDIA', 'Jensen Huang')")
    type: str = Field(..., description="Entity type: company, person, product, technology")
    mentions: int = Field(default=1, ge=1, description="Number of mentions in article")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "NVIDIA",
                "type": "company",
                "mentions": 5
            }
        }
```

**Validation Rules**:
- `type` must be one of: "company", "person", "product", "technology"
- `mentions` must be positive integer

### 2.3 AnalysisResult (Output Contract)

**Purpose**: Standard output format from analyzer library CLI

**Schema**:
```python
class AnalysisResult(BaseModel):
    """Output contract for intelligence-analyzer library"""

    # Core analysis outputs
    entities: List[Entity] = Field(default=[], description="Extracted named entities")
    summary: str = Field(..., max_length=500, description="Article summary (<100 words)")
    classification: str = Field(..., description="Article category")
    sentimentScore: int = Field(..., ge=1, le=10, description="Business impact sentiment (1=very negative, 10=very positive)")

    # Metadata
    analyzedAt: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    model: str = Field(default="llama3", description="LLM model used")
    processingTime: float = Field(..., ge=0, description="Analysis duration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "entities": [
                    {"text": "NVIDIA", "type": "company", "mentions": 5},
                    {"text": "DGX H200", "type": "product", "mentions": 3},
                    {"text": "Jensen Huang", "type": "person", "mentions": 1}
                ],
                "summary": "NVIDIA launched DGX H200, a new AI supercomputer with 32 petaflops for LLM training, targeting enterprise AI workloads.",
                "classification": "product_launch",
                "sentimentScore": 9,
                "analyzedAt": "2026-01-17T08:35:00Z",
                "model": "llama3",
                "processingTime": 4.2
            }
        }
```

**Validation Rules**:
- `summary` max length 500 characters (~100 words)
- `classification` must be one of: "competitive_news", "personnel_change", "product_launch", "market_trend"
- `sentimentScore` range: 1-10 (inclusive)
- `entities` can be empty array if none extracted
- `processingTime` must be non-negative

**CLI Output Format** (JSON to stdout):
```bash
$ intelligence-analyzer analyze input.json output.json
# Writes AnalysisResult JSON to output.json
# Logs to stderr with structured JSON logging
```

---

## 3. Backend API Models

### 3.1 Article (Database + API Response)

**Purpose**: Complete article entity stored in MongoDB and returned by API

**Schema**:
```python
class Article(BaseModel):
    """Complete article document (MongoDB + API response)"""

    # Identity
    id: str = Field(alias="_id", description="MongoDB ObjectId as string")
    url: HttpUrl = Field(..., description="Source article URL (unique)")

    # Content
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Full article text")
    publishDate: datetime = Field(..., description="Publication date")
    source: str = Field(..., description="Source website")

    # Analysis results (from analyzer library)
    summary: str = Field(..., description="Generated summary")
    entities: List[Entity] = Field(default=[], description="Extracted entities")
    classification: str = Field(..., description="Article classification")
    sentimentScore: int = Field(..., ge=1, le=10, description="Sentiment score")

    # Metadata
    scrapedAt: datetime = Field(..., description="Scraping timestamp")
    analyzedAt: Optional[datetime] = Field(default=None, description="Analysis timestamp")
    status: str = Field(default="complete", description="Processing status: complete, pending, failed")

    # Technical metadata
    metadata: dict = Field(default={}, description="Additional technical metadata")

    class Config:
        populate_by_name = True  # Allow both 'id' and '_id'
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
                    "processingTime": 4.2
                }
            }
        }
```

**Validation Rules**:
- `url` must be unique (enforced by MongoDB index)
- `status` must be one of: "complete", "pending", "failed"
- All analysis fields (`summary`, `entities`, `classification`, `sentimentScore`) can be null if status is "pending" or "failed"

### 3.2 ArticleListItem (API Response)

**Purpose**: Lightweight article representation for list views

**Schema**:
```python
class ArticleListItem(BaseModel):
    """Lightweight article for list views (performance optimization)"""

    id: str = Field(alias="_id")
    url: HttpUrl
    title: str
    summary: str
    classification: str
    sentimentScore: int
    publishDate: datetime
    source: str

    # Preview of entities (first 3 for list view)
    topEntities: List[str] = Field(default=[], max_length=3, description="Top 3 entity names for preview")

    class Config:
        populate_by_name = True
```

### 3.3 PaginatedArticles (API Response)

**Purpose**: Paginated article list response

**Schema**:
```python
class PaginatedArticles(BaseModel):
    """Paginated article list response"""

    total: int = Field(..., ge=0, description="Total number of articles matching filters")
    page: int = Field(..., ge=1, description="Current page number")
    pageSize: int = Field(..., ge=1, le=100, description="Number of items per page")
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
                        "topEntities": ["NVIDIA", "DGX H200", "Jensen Huang"]
                    }
                ]
            }
        }
```

### 3.4 AggregatedStats (API Response)

**Purpose**: Dashboard statistics response

**Schema**:
```python
class AggregatedStats(BaseModel):
    """Aggregated statistics for dashboard"""

    totalArticles: int = Field(..., ge=0, description="Total articles analyzed")
    classificationBreakdown: dict[str, int] = Field(..., description="Count per classification")
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
                    "personnel_change": 25
                },
                "avgSentiment": 6.8,
                "lastUpdated": "2026-01-17T10:30:00Z"
            }
        }
```

### 3.5 EntitySummary (API Response)

**Purpose**: Aggregated entity information across articles

**Schema**:
```python
class EntitySummary(BaseModel):
    """Aggregated entity information"""

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
                "articleIds": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
            }
        }
```

---

## 4. Frontend TypeScript Types

### 4.1 Article Type

**Purpose**: TypeScript representation of Article model

**Schema**:
```typescript
export interface Entity {
  text: string;
  type: 'company' | 'person' | 'product' | 'technology';
  mentions: number;
}

export interface Article {
  id: string;
  url: string;
  title: string;
  content: string;
  publishDate: string; // ISO 8601
  source: string;
  summary: string;
  entities: Entity[];
  classification: 'competitive_news' | 'personnel_change' | 'product_launch' | 'market_trend';
  sentimentScore: number; // 1-10
  scrapedAt: string; // ISO 8601
  analyzedAt: string | null; // ISO 8601
  status: 'complete' | 'pending' | 'failed';
  metadata: {
    scraperMethod?: string;
    contentTruncated?: boolean;
    processingTime?: number;
  };
}
```

### 4.2 Filter State

**Purpose**: UI filter state management

**Schema**:
```typescript
export interface ArticleFilters {
  classification: string | null; // null = all classifications
  sentimentRange: [number, number]; // [min, max] from 1-10
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  searchQuery: string; // Full-text search
}
```

### 4.3 API Response Types

**Purpose**: TypeScript types for API responses

**Schema**:
```typescript
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  pageSize: number;
  data: T[];
}

export interface StatsResponse {
  totalArticles: number;
  classificationBreakdown: Record<string, number>;
  avgSentiment: number;
  lastUpdated: string; // ISO 8601
}
```

---

## 5. MongoDB Schema

### 5.1 Articles Collection

**Document Structure**:
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
  "title": "NVIDIA Announces New AI Supercomputer",
  "content": "NVIDIA today unveiled its latest DGX system...",
  "publishDate": ISODate("2026-01-15T10:00:00Z"),
  "source": "NVIDIA Newsroom",
  "summary": "NVIDIA launched DGX H200...",
  "entities": [
    {
      "text": "NVIDIA",
      "type": "company",
      "mentions": 5
    },
    {
      "text": "DGX H200",
      "type": "product",
      "mentions": 3
    }
  ],
  "classification": "product_launch",
  "sentimentScore": 9,
  "scrapedAt": ISODate("2026-01-17T08:30:00Z"),
  "analyzedAt": ISODate("2026-01-17T08:35:00Z"),
  "status": "complete",
  "metadata": {
    "scraperMethod": "trafilatura",
    "contentTruncated": false,
    "processingTime": 4.2
  }
}
```

**Indexes** (created via init script):
```javascript
db.articles.createIndex({ "url": 1 }, { unique: true });
db.articles.createIndex({ "publishDate": -1 });
db.articles.createIndex({ "classification": 1 });
db.articles.createIndex({ "sentimentScore": 1 });
db.articles.createIndex({ "source": 1 });
db.articles.createIndex({ "status": 1 });
db.articles.createIndex(
  { "publishDate": -1, "classification": 1, "sentimentScore": 1 },
  { name: "filter_compound" }
);
db.articles.createIndex(
  { "title": "text", "content": "text" },
  { name: "fulltext_search" }
);
```

**Constraints**:
- `url` must be unique
- `publishDate` cannot be null
- `status` default: "complete"

---

## 6. State Transitions

### 6.1 Article Processing Flow

```
[New Article URL]
    ↓
[Scraper Library] → ScrapedArticle
    ↓
[Store in MongoDB with status="pending"]
    ↓
[Analyzer Library] → AnalysisResult
    ↓
[Update MongoDB with analysis + status="complete"]
    ↓
[API serves Article to frontend]
```

**State Transitions**:
1. **pending** → **complete**: Analysis succeeds
2. **pending** → **failed**: Analysis fails after retries
3. **failed** → **pending**: Manual re-analysis triggered (future feature)

**Invariants**:
- Articles with `status="complete"` MUST have non-null `analyzedAt`, `summary`, `classification`, `sentimentScore`
- Articles with `status="pending"` or `status="failed"` MAY have partial analysis data
- `scrapedAt` always exists (set during scraping)

---

## 7. Data Flow Contracts

### 7.1 Scraper → Backend

**Input**: CLI invocation with source parameter
**Output**: JSON array of `ScrapedArticle` to file or stdout
**Error Handling**: Failed articles logged to stderr, partial results returned

```bash
intelligence-scraper scrape nvidia /tmp/scraped.json
# Writes: [ScrapedArticle, ScrapedArticle, ...]
# Logs: {"level": "ERROR", "message": "Failed to scrape URL", "url": "..."}
```

### 7.2 Backend → Analyzer

**Input**: `AnalysisInput` JSON via file or stdin
**Output**: `AnalysisResult` JSON to file or stdout
**Error Handling**: Timeout after 30s, return error via stderr

```bash
echo '{"url": "...", "title": "...", "content": "..."}' | intelligence-analyzer analyze - /tmp/analysis.json
# Writes: AnalysisResult JSON
# Logs: {"level": "INFO", "message": "Analysis complete", "processingTime": 4.2}
```

### 7.3 Backend → MongoDB

**Insert**: New article with `status="pending"`, partial data from scraper
**Update**: Add analysis results, set `status="complete"`
**Query**: Filters, pagination, full-text search

### 7.4 Backend → Frontend

**GET /api/articles**: Returns `PaginatedArticles`
**GET /api/articles/{id}**: Returns `Article`
**GET /api/stats**: Returns `AggregatedStats`
**GET /api/entities**: Returns `List[EntitySummary]`

---

## Summary

This data model design ensures:
1. **Constitution Compliance**: Libraries have well-defined I/O contracts (ScrapedArticle, AnalysisResult)
2. **Testability**: Each model has clear validation rules for contract tests
3. **Type Safety**: Pydantic (Python) and TypeScript types prevent runtime errors
4. **Performance**: Optimized MongoDB indexes for common queries
5. **Observability**: Metadata fields enable debugging and monitoring

All models support the TDD workflow: contract tests verify schemas before implementation.

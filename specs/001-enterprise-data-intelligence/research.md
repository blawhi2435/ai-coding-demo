# Phase 0: Research & Technology Decisions

**Feature**: Enterprise Data Intelligence Assistant
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document captures all technology decisions and research findings to resolve "NEEDS CLARIFICATION" items from the Technical Context. All decisions are based on MVP requirements, constitution compliance, and architectural constraints.

---

## Research Tasks

### 1. Web Scraping Strategy

**Question**: How to reliably extract clean article text from NVIDIA Newsroom while maintaining extensibility for future sources?

**Research Conducted**:
- Evaluated trafilatura, newspaper3k, BeautifulSoup4, Playwright
- Analyzed NVIDIA Newsroom HTML structure (JavaScript-rendered content)
- Reviewed best practices for scraper resilience

**Decision**: Hybrid approach with trafilatura primary + Playwright fallback

**Rationale**:
- trafilatura: Excellent text extraction quality, handles 90% of standard HTML
- Playwright: Fallback for JavaScript-heavy pages, renders full DOM
- BeautifulSoup4: Used internally by trafilatura, no need for separate library
- This approach balances speed (trafilatura) with robustness (Playwright fallback)

**Alternatives Considered**:
- **Scrapy**: Rejected - Over-engineered for MVP scope, complex framework overhead
- **newspaper3k**: Rejected - Slower than trafilatura, less actively maintained
- **Playwright-only**: Rejected - Slower, heavier resource usage (headless browser for all requests)

**Implementation Notes**:
- Scraper library will try trafilatura first
- On extraction failure (empty content, errors), fallback to Playwright
- Log which method succeeded for monitoring
- Abstract scraper interface allows adding new sources easily

---

### 2. LLM Integration Pattern

**Question**: How to reliably get structured outputs (NER, classification, sentiment) from Llama 3 8B via Ollama?

**Research Conducted**:
- Reviewed Ollama API documentation (structured output support)
- Analyzed Llama 3 prompt engineering best practices
- Evaluated JSON mode reliability vs prompt engineering

**Decision**: Use Ollama JSON mode with schema-validated prompts

**Rationale**:
- Ollama supports JSON mode (format: "json" parameter) for structured outputs
- Llama 3 8B has strong instruction-following capabilities for JSON generation
- Single-pass analysis (all 4 tasks in one prompt) reduces latency and LLM calls
- Pydantic validation ensures output schema compliance

**Alternatives Considered**:
- **Multi-pass analysis** (separate prompts for NER, summary, classification, sentiment): Rejected - 4x LLM calls increases latency and complexity
- **LangChain**: Rejected - Unnecessary abstraction layer for simple use case
- **Function calling**: Rejected - Llama 3 supports JSON mode directly, no need for wrapper

**Implementation Notes**:
```python
# Prompt template structure
{
  "model": "llama3",
  "format": "json",
  "prompt": """Analyze the following article and return JSON with:
  {
    "entities": [{"text": "...", "type": "company|person|product|technology"}],
    "summary": "string (<100 words)",
    "classification": "competitive_news|personnel_change|product_launch|market_trend",
    "sentimentScore": 1-10
  }

  Article: {content}
  """
}
```
- Pydantic models validate response schema
- Retry logic: 1 retry on JSON parse failure, then mark as "analysis pending"

---

### 3. MongoDB Schema Design

**Question**: How to structure MongoDB documents for efficient queries (filtering, pagination, entity searches)?

**Research Conducted**:
- Reviewed MongoDB best practices for document design
- Analyzed query patterns from functional requirements (FR-010: date/classification/sentiment filters)
- Evaluated embedding vs referencing for entities

**Decision**: Single `articles` collection with embedded entities + compound indexes

**Rationale**:
- Articles are the primary query unit (not entities independently)
- Embedding entities avoids JOIN-like operations (MongoDB is document-oriented)
- Compound indexes on filter fields (publishDate, classification, sentimentScore) enable fast queries
- Text index on title/content enables full-text search

**Alternatives Considered**:
- **Separate entities collection**: Rejected - Adds complexity, requires aggregation pipeline for article+entity queries
- **Normalized schema** (articles + entities + relationships): Rejected - Overkill for MVP, slower queries
- **Elasticsearch for search**: Rejected - Unnecessary additional service for MVP scale (500 articles)

**Schema**:
```json
{
  "_id": ObjectId,
  "url": String (unique index),
  "title": String,
  "content": String,
  "publishDate": ISODate (index),
  "source": String (index),
  "scrapedAt": ISODate,
  "summary": String,
  "entities": [
    {
      "text": String,
      "type": String,  // company, person, product, technology
      "mentions": Number
    }
  ],
  "classification": String (index),  // competitive_news, personnel_change, product_launch, market_trend
  "sentimentScore": Number (index),  // 1-10
  "analyzedAt": ISODate,
  "status": String,  // complete, pending, failed
  "metadata": {
    "scraperMethod": String,  // trafilatura, playwright
    "contentTruncated": Boolean,
    "errorLog": String
  }
}
```

**Indexes**:
```javascript
db.articles.createIndex({ "url": 1 }, { unique: true });
db.articles.createIndex({ "publishDate": -1 });
db.articles.createIndex({ "classification": 1 });
db.articles.createIndex({ "sentimentScore": 1 });
db.articles.createIndex({ "source": 1 });
db.articles.createIndex({ "publishDate": -1, "classification": 1, "sentimentScore": 1 }); // Compound for filters
db.articles.createIndex({ "title": "text", "content": "text" }); // Full-text search
```

---

### 4. API Design Pattern

**Question**: What REST API structure best supports frontend requirements (list, filter, detail, stats)?

**Research Conducted**:
- Reviewed RESTful API best practices
- Analyzed frontend data needs from user stories
- Evaluated pagination strategies

**Decision**: RESTful JSON API with cursor-based pagination

**Rationale**:
- RESTful design is standard, well-understood, and FastAPI-native
- Cursor-based pagination performs better than offset pagination for large datasets
- JSON format aligns with LLM outputs and frontend TypeScript types
- FastAPI auto-generates OpenAPI schema for contract validation

**Alternatives Considered**:
- **GraphQL**: Rejected - Overkill for MVP, adds complexity (schema definition, resolvers)
- **Offset pagination**: Rejected - Slower for large datasets, skip operation inefficient
- **gRPC**: Rejected - Not web-friendly, no browser support without grpc-web

**Endpoints**:
```
GET  /api/articles?page=1&limit=20&classification=product_launch&minSentiment=7&maxSentiment=10&startDate=2026-01-01&endDate=2026-01-17
     → List articles with filters
     Response: { total, page, pageSize, data: [articles] }

GET  /api/articles/{id}
     → Get article details
     Response: { article with all fields }

GET  /api/stats
     → Get aggregated statistics
     Response: { totalArticles, classificationBreakdown, avgSentiment, lastUpdated }

GET  /api/entities?limit=50
     → Get unique entities with mention counts
     Response: { entities: [{ text, type, mentions, articleIds }] }

GET  /api/health
     → Health check
     Response: { status: "healthy", services: { mongodb, llm } }
```

---

### 5. Frontend State Management

**Question**: How to manage article data, filters, and real-time updates in React frontend?

**Research Conducted**:
- Evaluated React Query, Zustand, Redux Toolkit, Context API
- Analyzed state complexity (server data, UI filters, real-time updates)
- Reviewed best practices for data fetching in React 18

**Decision**: React Query (TanStack Query) for server state + Zustand for UI state

**Rationale**:
- React Query: Purpose-built for server data fetching, caching, and synchronization
- Zustand: Lightweight state manager for UI state (filters, selected article)
- Separation of concerns: server data (React Query) vs UI state (Zustand)
- React Query handles real-time updates via polling or WebSocket integration

**Alternatives Considered**:
- **Redux Toolkit**: Rejected - Too heavyweight for MVP, boilerplate overhead
- **Context API only**: Rejected - Poor performance for frequent updates, no caching
- **SWR**: Rejected - React Query has better TypeScript support and caching control

**Implementation**:
```typescript
// React Query for server data
const { data: articles, isLoading } = useQuery({
  queryKey: ['articles', filters],
  queryFn: () => fetchArticles(filters),
  refetchInterval: 5000  // Real-time updates every 5 seconds
});

// Zustand for UI state
const useFilterStore = create((set) => ({
  filters: { classification: null, sentiment: [1, 10], dateRange: null },
  setFilters: (filters) => set({ filters })
}));
```

---

### 6. Real-Time Updates Strategy

**Question**: How to implement real-time article list updates (SC-013: updates within 5 seconds)?

**Research Conducted**:
- Evaluated WebSocket, Server-Sent Events (SSE), polling
- Analyzed complexity vs latency requirements
- Reviewed React Query's real-time update patterns

**Decision**: Short-interval polling (5 seconds) via React Query

**Rationale**:
- Simplest implementation for MVP
- React Query handles polling automatically (`refetchInterval: 5000`)
- 5-second latency meets SC-013 requirement
- No additional server infrastructure (WebSocket server, SSE endpoint)

**Alternatives Considered**:
- **WebSocket**: Rejected - Requires separate WebSocket server in backend, added complexity
- **SSE**: Rejected - One-way communication sufficient but adds FastAPI SSE endpoint complexity
- **Long polling**: Rejected - More complex than short polling, marginal latency benefit

**Implementation Notes**:
- React Query's `refetchInterval` polls `/api/articles` every 5 seconds
- Only refetch when tab is active (React Query's `refetchIntervalInBackground: false`)
- Consider WebSocket upgrade if sub-second latency becomes requirement

---

### 7. Testing Strategy

**Question**: How to structure tests to comply with constitution's Test-First principle?

**Research Conducted**:
- Reviewed TDD best practices for microservices
- Analyzed pytest, Vitest, Playwright capabilities
- Evaluated contract testing tools

**Decision**: Three-tier testing (Contract → Integration → E2E) with TDD workflow

**Rationale**:
- Contract tests verify library I/O schemas (scraper output, analyzer output, API responses)
- Integration tests verify library + service interactions
- E2E tests verify full user flows
- Pytest (backend) and Vitest (frontend) support TDD watch modes

**Testing Stack**:
```
Backend:
  - pytest: Unit and integration tests
  - pytest-asyncio: Async FastAPI tests
  - mongomock: Mock MongoDB for unit tests
  - responses: Mock HTTP requests (Ollama)

Frontend:
  - Vitest: Component and service tests
  - @testing-library/react: Component testing
  - MSW (Mock Service Worker): API mocking

E2E:
  - Playwright: Full stack browser tests
```

**TDD Workflow**:
1. **Contract tests first**: Define expected I/O schemas
2. **Confirm tests fail**: Run tests, verify failures
3. **Implement**: Write minimal code to pass tests
4. **Integration tests**: Test library interactions
5. **E2E tests**: Validate user flows

**Contract Examples**:
```python
# libs/intelligence-scraper/tests/contract/test_output_schema.py
def test_scraper_output_schema():
    """Contract: Scraper output must match expected JSON schema"""
    result = scrape("nvidia", "output.json")
    assert "url" in result
    assert "title" in result
    assert "content" in result
    assert "publishDate" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0

# libs/intelligence-analyzer/tests/contract/test_analysis_schema.py
def test_analyzer_output_schema():
    """Contract: Analyzer output must match expected JSON schema"""
    result = analyze(sample_article)
    assert "entities" in result
    assert "summary" in result
    assert "classification" in result
    assert "sentimentScore" in result
    assert 1 <= result["sentimentScore"] <= 10
    assert result["classification"] in ["competitive_news", "personnel_change", "product_launch", "market_trend"]
```

---

### 8. Logging and Observability Implementation

**Question**: How to implement structured JSON logging across all components?

**Research Conducted**:
- Reviewed Python logging best practices
- Evaluated structlog, python-json-logger
- Analyzed log aggregation patterns

**Decision**: Python `logging` with JSON formatter + centralized log files

**Rationale**:
- Python's built-in `logging` module is sufficient with custom JSON formatter
- Centralized log files (volume-mounted in Docker) enable easy debugging
- Structured format supports future log aggregation (ELK, Loki)
- Each library logs to separate logger (`intelligence.scraper`, `intelligence.analyzer`)

**Alternatives Considered**:
- **structlog**: Rejected - Additional dependency for MVP, built-in logging sufficient
- **python-json-logger**: Considered but custom formatter is simple enough

**Implementation**:
```python
# libs/intelligence-scraper/src/utils/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "context": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        }
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def get_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.FileHandler("/app/logs/{}.log".format(name))
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

**Log Files** (volume-mounted):
```
logs/
├── intelligence.scraper.log  # Scraper library logs
├── intelligence.analyzer.log # Analyzer library logs
├── backend.api.log           # Backend API logs
└── backend.startup.log       # Startup orchestration logs
```

---

### 9. Docker Compose Configuration

**Question**: How to orchestrate 4 containers with proper dependency ordering and health checks?

**Research Conducted**:
- Reviewed Docker Compose best practices
- Analyzed Ollama container requirements (model download, health check)
- Evaluated startup orchestration patterns

**Decision**: Health-check based dependency ordering with init containers

**Rationale**:
- `depends_on` with `condition: service_healthy` ensures proper startup order
- Ollama health check prevents backend from starting before LLM model is ready
- MongoDB init scripts create indexes on first run
- Volume mounts ensure data persistence

**docker-compose.yml Structure**:
```yaml
version: '3.9'

services:
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
    volumes:
      - mongodb_data:/data/db
      - ./docker/init-mongo:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 5s
      retries: 5

  llm:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 10
    deploy:
      resources:
        limits:
          memory: 8G

  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    ports: ["8000:8000"]
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - LLM_SERVICE_URL=http://llm:11434
    volumes:
      - ./logs:/app/logs
      - ./libs:/app/libs  # Mount libraries for development
    depends_on:
      mongodb:
        condition: service_healthy
      llm:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend.Dockerfile
    ports: ["3000:80"]
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  mongodb_data:
  ollama_models:
```

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Web Scraping | trafilatura + Playwright fallback | Speed + robustness balance |
| LLM Integration | Ollama JSON mode with single-pass prompts | Structured outputs, reduced latency |
| Database Schema | Embedded entities in articles collection | Simpler queries, better performance |
| API Design | RESTful with cursor pagination | Standard, FastAPI-native, scalable |
| Frontend State | React Query + Zustand | Separation of server/UI state |
| Real-Time Updates | 5-second polling | Simplest implementation for MVP |
| Testing | Contract → Integration → E2E with TDD | Constitution compliance |
| Logging | JSON formatter with centralized files | Structured, observable, aggregatable |
| Orchestration | Health-check based Docker Compose | Reliable startup ordering |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| LLM inference too slow | Use Llama 3 8B (not 70B), implement timeout (30s), async processing |
| Scraper breaks on site changes | Pluggable scraper architecture, robust error handling, fallback to Playwright |
| MongoDB storage growth | TTL indexes for old articles (future), archive strategy |
| First-time model download fails | Pre-bake model in Docker image (alternative), provide manual pull instructions |
| Real-time updates lag | Polling interval configurable (5s default), upgrade to WebSocket if needed |

---

**Status**: All research complete, ready for Phase 1 (Design & Contracts)

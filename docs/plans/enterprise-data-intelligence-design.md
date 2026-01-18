# Enterprise Data Intelligence Assistant - Architecture Design

**Document Version:** 1.0
**Date:** 2026-01-17
**Status:** Draft
**Project Type:** Proof-of-Concept / MVP

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
4. [Deployment Strategy](#deployment-strategy)
5. [Technology Stack](#technology-stack)
6. [Extensibility & Future Growth](#extensibility--future-growth)
7. [Implementation Considerations](#implementation-considerations)

---

## 1. Project Overview

### 1.1 Purpose

Build a proof-of-concept system that demonstrates automatic intelligence gathering from unstructured web content (news, policy documents, industry commentary) and transforms it into structured, actionable business intelligence.

The system will automatically scrape content from target websites, perform NLP analysis using open-source LLMs, and present the results through a user-friendly web interface.

### 1.2 Success Criteria for MVP

- Successfully extract and analyze content from **NVIDIA Newsroom** (primary target, with architecture designed to easily extend to TechCrunch and Yahoo Finance later)
- Demonstrate all 5 core NLP capabilities working end-to-end:
  - Web content extraction
  - Named Entity Recognition (NER)
  - Text summarization and classification
  - Sentiment analysis
  - Persistent storage and retrieval
- Provide a functional web interface for evaluators to test features
- Store and retrieve analysis results reliably from MongoDB
- Run the entire system with a single `docker-compose up` command

### 1.3 Key Constraints

- **Backend**: Must use Python
- **Frontend**: Web-based (React recommended for modern best practices)
- **LLM**: Must use open-source models (Llama 3 recommended)
- **Database**: MongoDB for data persistence
- **Deployment**: Docker Compose for single-command orchestration
- **Scope**: Focus on demonstrating feasibility over production-scale optimization

### 1.4 Target Users

Evaluators who need to test the system's core intelligence gathering and analysis capabilities through a user-friendly web interface.

---

## 2. System Architecture

### 2.1 Architecture Pattern

**Microservices-lite**: A lightweight microservices approach with 3 core services, optimized for MVP development and demonstration.

### 2.2 Core Components

#### 2.2.1 Web Frontend Service

- **Technology**: React 18 + TypeScript + Vite
- **Responsibilities**:
  - Display analyzed articles in browsable, searchable interface
  - Filter articles by category, sentiment, date range
  - Show detailed article view with entity highlighting
  - Visualize sentiment scores and entity relationships
  - Real-time updates when new articles are processed
- **Communication**: REST API calls to Backend service

#### 2.2.2 Backend API + Scraper Service (Python)

- **Technology**: FastAPI + Python 3.11
- **Responsibilities**:
  - **Automated Scraper Module**: Runs on service startup to scrape target websites
  - Orchestrate LLM processing pipeline for scraped content
  - Expose REST API endpoints for frontend queries
  - Manage data persistence to MongoDB
  - Handle error recovery and logging
- **Key Features**:
  - Pluggable scraper architecture (easy to add new sources)
  - Async processing support
  - Optional periodic re-scraping (configurable schedule)
  - Auto-generated API documentation (FastAPI feature)

#### 2.2.3 LLM Processing Service (Python)

- **Technology**: Ollama + Llama 3 8B
- **Responsibilities**:
  - Execute all NLP tasks: NER, summarization, classification, sentiment analysis
  - Return structured JSON responses
  - Handle prompt engineering and output validation
- **Key Features**:
  - Isolated service (can be scaled independently)
  - Structured output/JSON mode for reliable extraction
  - Model version control and easy updates

#### 2.2.4 Data Storage

- **Technology**: MongoDB 7
- **Schema Design**:
  - Collection: `articles`
  - Document structure:
    ```json
    {
      "_id": ObjectId,
      "url": String,
      "title": String,
      "content": String,
      "publishDate": Date,
      "source": String,
      "scrapedAt": Date,
      "summary": String,
      "entities": [
        {
          "text": String,
          "type": String,  // company, person, product, technology
          "mentions": Number
        }
      ],
      "classification": String,  // competitive_news, personnel_change, product_launch, market_trend
      "sentimentScore": Number,  // 1-10
      "analyzedAt": Date,
      "metadata": Object
    }
    ```
  - Indexes: `publishDate`, `classification`, `sentimentScore`, `source`

### 2.3 Communication Flow

```
Service Startup
    ↓
Backend Scraper Module Activates
    ↓
NVIDIA Newsroom Scraping
    ↓
Content Extraction & Cleaning
    ↓
Send to LLM Service
    ↓
LLM Analysis (NER, Summary, Classification, Sentiment)
    ↓
Structured JSON Response
    ↓
Store to MongoDB
    ↓
Frontend Queries & Displays Results
```

---

## 3. Data Flow & Processing Pipeline

### 3.1 End-to-End Pipeline

```
Startup → Scraping → Extraction → LLM Analysis → Storage → Display
```

### 3.2 Stage 1: Automated Scraping

**Trigger**: Service startup (Backend container initialization)

**Process**:
1. Backend scraper targets NVIDIA Newsroom homepage and article listing pages
2. Extracts article URLs and metadata (publication date, category if available)
3. For each article URL, fetches full HTML content
4. Uses content extraction library to filter noise (ads, navigation, footers, comments)
5. Output: Clean structured data

**Recommended Libraries**:
- **trafilatura**: For clean text extraction (handles most sites well)
- **Playwright** (fallback): For JavaScript-heavy sites requiring rendering
- **BeautifulSoup4**: For HTML parsing and custom extraction logic

**Output Format**:
```python
{
    "url": "https://nvidianews.nvidia.com/...",
    "title": "Article Title",
    "content": "Full article text...",
    "publish_date": "2026-01-15",
    "source": "NVIDIA Newsroom",
    "keywords": ["AI", "GPU", "Technology"]
}
```

### 3.3 Stage 2: LLM Analysis Pipeline

**Approach**: Single-pass analysis (efficient for MVP)

**Process**:
1. Backend sends clean text to LLM service via HTTP API
2. Structured prompt requesting all 4 analyses in JSON format
3. LLM performs:
   - **Named Entity Recognition**: Extract and classify entities (companies, people, products, technologies)
   - **Summarization**: Generate concise summary (<100 words)
   - **Classification**: Categorize into predefined types (competitive news, personnel changes, product launch, market trends)
   - **Sentiment Analysis**: Score 1-10 for business impact
4. LLM returns JSON-structured response
5. Backend validates schema and enriches data

**Prompt Template** (Example):
```
Analyze the following article and return a JSON response with:
1. entities: Array of {text, type} where type is company/person/product/technology
2. summary: String (<100 words)
3. classification: One of [competitive_news, personnel_change, product_launch, market_trend]
4. sentimentScore: Number 1-10 (business impact: 1=very negative, 10=very positive)

Article:
{content}

Return only valid JSON.
```

### 3.4 Stage 3: Data Persistence

**Process**:
1. Backend receives validated LLM response
2. Combines scraped data + analysis results into single document
3. Inserts into MongoDB `articles` collection
4. Updates metadata (analyzedAt timestamp)
5. Logs success/failure for monitoring

**Error Handling**:
- Failed scrapes: Log error, continue to next article
- LLM failures: Retry once, then store partial data with error flag
- Database failures: Retry with exponential backoff

### 3.5 Stage 4: Frontend Display

**API Endpoints** (Backend exposes):
- `GET /api/articles` - List articles (paginated, filterable)
- `GET /api/articles/{id}` - Get article details
- `GET /api/stats` - Get summary statistics (total articles, sentiment distribution, etc.)
- `GET /api/entities` - List all unique entities

**Frontend Features**:
- Article list view with filters (date range, classification, sentiment)
- Detailed article view with entity highlighting
- Sentiment visualization (charts/graphs)
- Search functionality (full-text search)
- Export options (CSV, JSON)

---

## 4. Deployment Strategy

### 4.1 Docker Compose Architecture

**File**: `docker-compose.yml`

**4 Containers**:

#### Container 1: Frontend
```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:80"
  environment:
    - VITE_API_URL=http://localhost:8000
  depends_on:
    - backend
```

- Base: `node:20-alpine` (build) → `nginx:alpine` (serve)
- Serves production React build
- Nginx configuration for SPA routing

#### Container 2: Backend
```yaml
backend:
  build: ./backend
  ports:
    - "8000:8000"
  environment:
    - MONGODB_URL=mongodb://mongodb:27017
    - LLM_SERVICE_URL=http://llm:11434
  depends_on:
    - mongodb
    - llm
  volumes:
    - ./logs:/app/logs
```

- Base: `python:3.11-slim`
- FastAPI app with uvicorn server
- Runs scraper on startup
- Health check endpoint

#### Container 3: LLM Service
```yaml
llm:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_models:/root/.ollama
  environment:
    - OLLAMA_MODELS=/root/.ollama/models
  deploy:
    resources:
      limits:
        memory: 8G
```

- Official Ollama image
- Pre-pulls Llama 3 8B on first run
- Volume mount for model persistence (~4GB)
- Requires minimum 8GB RAM

#### Container 4: MongoDB
```yaml
mongodb:
  image: mongo:7
  ports:
    - "27017:27017"
  volumes:
    - mongodb_data:/data/db
    - ./mongo-init:/docker-entrypoint-initdb.d
  environment:
    - MONGO_INITDB_DATABASE=intelligence
```

- Official MongoDB 7 image
- Data persistence via volume
- Optional: Initialize indexes on startup

### 4.2 Startup Sequence

```
1. MongoDB starts (healthcheck: ready)
2. LLM service starts, pulls model (~5-10 min first time)
3. Backend waits for MongoDB + LLM readiness
4. Backend starts, runs scraper
5. Frontend starts, connects to backend API
```

### 4.3 One-Command Launch

```bash
# First time setup
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Clean restart
docker-compose down -v && docker-compose up -d
```

### 4.4 Resource Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 12GB (8GB for LLM, 4GB for other services)
- Disk: 20GB (models + data)

**Recommended**:
- CPU: 8 cores
- RAM: 16GB
- Disk: 50GB

---

## 5. Technology Stack

### 5.1 Frontend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | React 18 | Industry standard, excellent ecosystem |
| Language | TypeScript | Type safety, better developer experience |
| Build Tool | Vite | Fast dev server, optimized production builds |
| Styling | TailwindCSS | Utility-first, rapid UI development |
| State Management | Zustand / React Query | Simple state + server cache management |
| HTTP Client | Axios | Clean API, interceptors for error handling |

### 5.2 Backend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | FastAPI | Async support, auto API docs, type hints |
| Language | Python 3.11 | Required constraint, excellent ML/NLP ecosystem |
| Validation | Pydantic | Data validation, settings management |
| HTTP Client | httpx | Async HTTP for LLM communication |
| Scraping | trafilatura + Playwright | Text extraction + JS rendering fallback |
| Database Driver | pymongo + motor | Sync + async MongoDB support |
| Task Queue (optional) | Celery + Redis | For future scheduled scraping |

### 5.3 LLM Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Runtime | Ollama | Easy deployment, model management |
| Model | Llama 3 8B | Good quality, reasonable resource requirements |
| Alternative | Mistral 7B | Lighter weight, faster inference |
| JSON Mode | Structured outputs | Reliable extraction, schema validation |

### 5.4 Database

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Database | MongoDB 7 | Required constraint, flexible schema, easy iteration |
| ORM | pymongo | Official driver, widely supported |

### 5.5 DevOps

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Containerization | Docker | Standard, reproducible environments |
| Orchestration | Docker Compose | Simple multi-container deployment |
| Logging | Python logging + file output | Easy debugging, future log aggregation |

---

## 6. Extensibility & Future Growth

### 6.1 Adding New Data Sources

**Design Pattern**: Pluggable Scraper Architecture

**Implementation**:
```python
# base_scraper.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def fetch_article_list(self) -> List[str]:
        """Return list of article URLs"""
        pass

    @abstractmethod
    def extract_content(self, url: str) -> Dict:
        """Extract article content from URL"""
        pass

    @abstractmethod
    def parse_metadata(self, html: str) -> Dict:
        """Parse metadata (date, author, etc.)"""
        pass

# nvidia_scraper.py
class NvidiaScraper(BaseScraper):
    def fetch_article_list(self): ...
    def extract_content(self, url): ...
    def parse_metadata(self, html): ...

# techcrunch_scraper.py
class TechCrunchScraper(BaseScraper):
    def fetch_article_list(self): ...
    def extract_content(self, url): ...
    def parse_metadata(self, html): ...
```

**Configuration**:
```yaml
# scrapers.yaml
scrapers:
  - name: nvidia
    enabled: true
    url: https://nvidianews.nvidia.com/
    interval: 3600  # seconds
  - name: techcrunch
    enabled: false
    url: https://techcrunch.com/
    interval: 1800
```

**Effort to Add New Source**: ~50-100 lines of code per scraper

### 6.2 Scalability Pathways

#### Phase 1: Current MVP
- Startup scraping, synchronous processing
- Single LLM instance
- MongoDB single node

#### Phase 2: Background Processing
- **Add**: Celery + Redis for job queue
- **Benefit**: Periodic scraping, async analysis
- **Effort**: ~2-3 days

#### Phase 3: LLM Scaling
- **Option A**: Multiple Ollama instances + load balancer
- **Option B**: Switch to cloud LLM APIs (OpenAI, Anthropic)
- **Benefit**: Faster processing, higher throughput
- **Effort**: ~1-2 days

#### Phase 4: Database Scaling
- **Add**: MongoDB replica sets, sharding by source/date
- **Benefit**: High availability, horizontal scaling
- **Effort**: ~3-5 days

### 6.3 Feature Expansion Opportunities

**Quick Wins** (1-2 days each):
- Full-text search (MongoDB text indexes)
- CSV/PDF export functionality
- Email alerts on high-impact events
- Article deduplication detection

**Medium Effort** (3-5 days each):
- Scheduled periodic scraping (Celery)
- Advanced entity relationship graphs
- Multi-language support (i18n)
- Custom classification categories

**Larger Features** (1-2 weeks each):
- User authentication & saved searches
- Custom alert rules engine
- Interactive dashboards with charts
- Mobile app (React Native, same API)

### 6.4 Architectural Flexibility

**Built-In Extension Points**:
- **Frontend Swap**: REST API allows CLI tools, mobile apps, desktop apps
- **LLM Upgrade**: Isolated service enables model changes without backend refactor
- **Schema Evolution**: MongoDB flexibility supports adding analysis fields
- **Multi-Environment**: Environment variables for dev/staging/prod configs

### 6.5 Production Migration Path

**From PoC to Production** (recommended steps):

1. **Security Hardening**
   - Add authentication/authorization (JWT)
   - Implement API rate limiting
   - Enable HTTPS/TLS
   - Secret management (HashiCorp Vault, AWS Secrets Manager)

2. **Observability**
   - Structured logging (JSON format)
   - Monitoring (Prometheus + Grafana)
   - Distributed tracing (Jaeger, OpenTelemetry)
   - Error tracking (Sentry)

3. **Resilience**
   - Circuit breakers for LLM calls
   - Retry logic with exponential backoff
   - Graceful degradation
   - Database connection pooling

4. **Infrastructure**
   - Kubernetes deployment (replace Docker Compose)
   - Managed MongoDB (MongoDB Atlas)
   - Cloud LLM services (reduce self-hosting)
   - CI/CD pipeline (GitHub Actions)

5. **Performance**
   - Redis caching layer
   - CDN for frontend assets
   - Database query optimization
   - Horizontal scaling for backend

---

## 7. Implementation Considerations

### 7.1 Development Phases

**Recommended Implementation Order**:

1. **Phase 1: Foundation** (Week 1)
   - Set up Docker Compose configuration
   - Implement MongoDB schema
   - Build basic FastAPI endpoints
   - Create React scaffolding

2. **Phase 2: Scraping** (Week 1-2)
   - Develop NVIDIA Newsroom scraper
   - Test content extraction quality
   - Implement data cleaning pipeline

3. **Phase 3: LLM Integration** (Week 2)
   - Set up Ollama + Llama 3
   - Design structured prompts
   - Validate JSON output reliability

4. **Phase 4: Frontend** (Week 2-3)
   - Build article list/detail views
   - Implement filters and search
   - Add sentiment visualization

5. **Phase 5: Integration & Testing** (Week 3)
   - End-to-end testing
   - Performance optimization
   - Documentation

### 7.2 Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM inference too slow | High | Use smaller model (Mistral 7B), implement caching |
| Scraper breaks when site changes | Medium | Robust selectors, fallback strategies, error logging |
| Memory overflow from large articles | Medium | Implement text truncation, chunk processing |
| MongoDB storage growth | Low | Set TTL indexes, archive old articles |
| First-time Ollama model download fails | Medium | Pre-bake model into Docker image, provide manual download instructions |

### 7.3 Quality Assurance

**Testing Strategy**:
- **Unit Tests**: Core scraping logic, LLM response parsing (pytest)
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Full pipeline from scrape to display (Playwright)
- **Manual Testing**: UI/UX validation by evaluators

**Quality Metrics**:
- Scraping success rate: >90%
- LLM analysis accuracy: Manual validation of 20 samples
- Response time: <2s for frontend queries
- Uptime: System runs continuously for 24 hours without crashes

### 7.4 Documentation Requirements

**For Evaluators**:
- `README.md`: Quick start guide, architecture overview
- `docs/SETUP.md`: Detailed installation instructions
- `docs/API.md`: API endpoint documentation (auto-generated by FastAPI)
- `docs/TROUBLESHOOTING.md`: Common issues and solutions

**For Developers**:
- Code comments for complex logic
- Docstrings for public functions
- Architecture decision records (ADRs) for key choices

---

## Appendix

### A. Example Article Processing

**Input** (Scraped):
```
Title: "NVIDIA Announces New AI Supercomputer"
Content: "NVIDIA today unveiled its latest DGX system, featuring breakthrough performance for large language model training. The DGX H200 delivers 32 petaflops of AI computing power..."
Date: 2026-01-15
Source: NVIDIA Newsroom
```

**Output** (After LLM Analysis):
```json
{
  "url": "https://nvidianews.nvidia.com/...",
  "title": "NVIDIA Announces New AI Supercomputer",
  "content": "NVIDIA today unveiled...",
  "publishDate": "2026-01-15",
  "source": "NVIDIA Newsroom",
  "summary": "NVIDIA launched DGX H200, a new AI supercomputer with 32 petaflops for LLM training, targeting enterprise AI workloads.",
  "entities": [
    {"text": "NVIDIA", "type": "company"},
    {"text": "DGX H200", "type": "product"},
    {"text": "AI supercomputer", "type": "technology"}
  ],
  "classification": "product_launch",
  "sentimentScore": 9,
  "analyzedAt": "2026-01-17T10:30:00Z"
}
```

### B. API Contract Examples

**GET /api/articles**
```json
{
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "...",
      "summary": "...",
      "classification": "product_launch",
      "sentimentScore": 9,
      "publishDate": "2026-01-15",
      "entities": ["NVIDIA", "DGX H200"]
    }
  ]
}
```

**GET /api/stats**
```json
{
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
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | AI Architect | Initial design document |

---

**End of Document**

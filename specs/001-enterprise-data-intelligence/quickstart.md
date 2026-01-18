# Quickstart Guide: Enterprise Data Intelligence Assistant

**Feature**: 001-enterprise-data-intelligence
**Audience**: Developers and Evaluators
**Estimated Time**: 15-20 minutes (first-time setup with model download)

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or later ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0 or later (included with Docker Desktop)
- **Git**: For cloning the repository

### System Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 12GB (8GB for LLM, 4GB for other services)
- Disk: 20GB free space
- OS: Linux, macOS, or Windows with WSL2

**Recommended**:
- CPU: 8 cores
- RAM: 16GB
- Disk: 50GB free space

### Verification

Check your system meets requirements:

```bash
# Check Docker version
docker --version  # Should be 20.10+

# Check Docker Compose version
docker compose version  # Should be 2.0+

# Check available memory
docker info | grep "Total Memory"  # Should show 12GB+

# Check available disk space
df -h .  # Should show 20GB+ free
```

---

## Quick Start (3 Steps)

### Step 1: Clone Repository and Navigate

```bash
git clone <repository-url>
cd vide-coding
```

### Step 2: Start All Services

```bash
# Start all containers in detached mode
docker compose up -d
```

**What Happens**:
1. MongoDB starts and initializes indexes (~10 seconds)
2. Ollama starts and downloads Llama 3 8B model (~5-10 minutes on first run)
3. Backend waits for MongoDB + Ollama health checks, then starts scraping
4. Frontend starts and connects to backend API

**Monitor Startup Progress**:
```bash
# Watch all service logs
docker compose logs -f

# Watch backend specifically (scraping progress)
docker compose logs -f backend

# Check service status
docker compose ps
```

**Expected Output**:
```
NAME                STATUS              PORTS
mongodb             Up (healthy)        0.0.0.0:27017->27017/tcp
llm                 Up (healthy)        0.0.0.0:11434->11434/tcp
backend             Up                  0.0.0.0:8000->8000/tcp
frontend            Up                  0.0.0.0:3000->80/tcp
```

### Step 3: Access the Application

Once backend logs show "Scraping complete", open:

**Frontend**: http://localhost:3000
**Backend API Docs**: http://localhost:8000/docs (FastAPI Swagger UI)

---

## First-Time Experience

### Expected Timeline

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| MongoDB startup | 10-15 seconds | Database initialization |
| LLM model download | 5-10 minutes | First-time only: Llama 3 8B (~4GB) |
| LLM startup | 30 seconds | Model loading into memory |
| Backend startup | 10 seconds | Dependency checks |
| Scraping NVIDIA | 2-3 minutes | Scraping 20+ articles |
| LLM analysis | 2-5 minutes | Analyzing articles (4-8s each) |
| **Total** | **10-20 minutes** | **First run with model download** |

**Subsequent Runs**: 3-5 minutes (model already downloaded)

### Monitoring Scraping Progress

```bash
# Watch backend logs for scraping status
docker compose logs -f backend | grep "intelligence.scraper"

# Expected log output:
# {"timestamp":"...","level":"INFO","component":"intelligence.scraper","message":"Starting scrape for source: nvidia"}
# {"timestamp":"...","level":"INFO","component":"intelligence.scraper","message":"Found 25 article URLs"}
# {"timestamp":"...","level":"INFO","component":"intelligence.scraper","message":"Scraping complete: 23/25 articles successful"}
```

### Monitoring Analysis Progress

```bash
# Watch backend logs for analysis status
docker compose logs -f backend | grep "intelligence.analyzer"

# Expected log output:
# {"timestamp":"...","level":"INFO","component":"intelligence.analyzer","message":"Starting analysis","context":{"url":"https://nvidianews..."}}
# {"timestamp":"...","level":"INFO","component":"intelligence.analyzer","message":"Analysis complete","context":{"processingTime":4.2}}
```

---

## Using the System

### Frontend Features

Once you open http://localhost:3000:

1. **Article List View**:
   - View all analyzed articles with summaries
   - See classification tags (product_launch, competitive_news, etc.)
   - View sentiment scores (1-10 scale with color coding)

2. **Filters**:
   - Classification: Select specific article types
   - Sentiment Range: Slider to filter by sentiment score
   - Date Range: Filter by publication date
   - Search: Full-text search across titles and content

3. **Article Detail View**:
   - Click any article to see full content
   - Highlighted entities (color-coded by type)
   - Complete analysis results
   - Source URL and metadata

4. **Statistics Dashboard**:
   - Total articles count
   - Classification breakdown (pie/bar chart)
   - Average sentiment across all articles
   - Last update timestamp

### API Endpoints

Explore the interactive API docs at http://localhost:8000/docs

**Key Endpoints**:

```bash
# Get articles with filters
curl "http://localhost:8000/api/articles?classification=product_launch&minSentiment=7&page=1&limit=10"

# Get specific article
curl "http://localhost:8000/api/articles/{article-id}"

# Get statistics
curl "http://localhost:8000/api/stats"

# Get unique entities
curl "http://localhost:8000/api/entities?limit=50"

# Health check
curl "http://localhost:8000/api/health"
```

**Example Response** (`/api/articles`):
```json
{
  "total": 23,
  "page": 1,
  "pageSize": 10,
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
```

---

## Testing the Libraries

### Scraper Library

Test the scraper library directly via CLI:

```bash
# Enter backend container
docker compose exec backend bash

# Run scraper (inside container)
intelligence-scraper scrape nvidia /tmp/scraped.json --max-articles 5

# View output
cat /tmp/scraped.json | jq .

# Expected output: Array of ScrapedArticle objects
```

### Analyzer Library

Test the analyzer library directly:

```bash
# Enter backend container
docker compose exec backend bash

# Prepare test input
echo '{"url":"https://example.com","title":"Test Article","content":"NVIDIA launched a new AI product called DGX H200 for enterprise customers seeking powerful machine learning infrastructure..."}' > /tmp/input.json

# Run analyzer
intelligence-analyzer analyze /tmp/input.json /tmp/output.json

# View results
cat /tmp/output.json | jq .

# Expected output: AnalysisResult with entities, summary, classification, sentiment
```

---

## Troubleshooting

### Issue: LLM Model Download Fails

**Symptoms**: Backend logs show "Failed to connect to LLM service"

**Solution**:
```bash
# Manually pull Llama 3 model
docker compose exec llm ollama pull llama3

# Restart backend
docker compose restart backend
```

### Issue: MongoDB Connection Errors

**Symptoms**: Backend logs show "Failed to connect to MongoDB"

**Solution**:
```bash
# Check MongoDB health
docker compose ps mongodb

# If unhealthy, restart
docker compose restart mongodb

# Wait for health check
docker compose ps mongodb  # Should show "healthy"
```

### Issue: Scraper Finds No Articles

**Symptoms**: Backend logs show "Found 0 article URLs"

**Possible Causes**:
1. NVIDIA Newsroom website structure changed
2. Network connectivity issues
3. Rate limiting or blocking

**Solution**:
```bash
# Check scraper logs for errors
docker compose logs backend | grep "intelligence.scraper" | grep "ERROR"

# Test network connectivity from container
docker compose exec backend curl -I https://nvidianews.nvidia.com/

# Try forcing Playwright method
# Edit backend/src/startup.py to use --method playwright flag
```

### Issue: Frontend Shows "No Articles"

**Symptoms**: Frontend loads but shows empty article list

**Solution**:
```bash
# Check if backend has articles
curl http://localhost:8000/api/stats

# If totalArticles is 0, scraping failed - check backend logs
docker compose logs backend

# If totalArticles > 0, check frontend connectivity
# Open browser console (F12) and look for API errors
```

### Issue: "Out of Memory" Errors

**Symptoms**: LLM service crashes or Docker reports OOM

**Solution**:
```bash
# Check Docker memory allocation
docker info | grep "Total Memory"

# Increase Docker Desktop memory limit:
# Docker Desktop → Settings → Resources → Memory → 16GB

# Restart Docker Desktop and retry
docker compose down
docker compose up -d
```

---

## Stopping and Cleaning Up

### Stop All Services

```bash
# Stop containers (keep data)
docker compose stop

# Stop and remove containers (keep data)
docker compose down

# Stop, remove containers, and delete volumes (full cleanup)
docker compose down -v
```

### View Logs

```bash
# View logs in ./logs directory
ls -lh logs/

# Read structured JSON logs
cat logs/intelligence.scraper.log | jq .
cat logs/intelligence.analyzer.log | jq .
cat logs/backend.api.log | jq .
```

### Restart System

```bash
# Quick restart (preserves data)
docker compose restart

# Full restart (fresh start, keeps volumes)
docker compose down
docker compose up -d

# Complete reset (deletes all data)
docker compose down -v
docker compose up -d
```

---

## Development Workflow

### Making Changes to Libraries

```bash
# Libraries are volume-mounted for development
# Edit code in libs/intelligence-scraper/ or libs/intelligence-analyzer/

# Run tests in container
docker compose exec backend bash
cd /app/libs/intelligence-scraper
pytest tests/

# Restart backend to apply changes
docker compose restart backend
```

### Making Changes to Backend

```bash
# Edit code in backend/src/

# Backend uses hot-reload in development mode
# Changes auto-apply without restart

# Run tests
docker compose exec backend bash
cd /app/backend
pytest tests/
```

### Making Changes to Frontend

```bash
# Edit code in frontend/src/

# Frontend uses Vite hot-reload
# Changes auto-apply in browser

# Run tests
docker compose exec frontend bash
npm run test
```

---

## Next Steps

After completing this quickstart:

1. **Explore the codebase**: Read `specs/001-enterprise-data-intelligence/plan.md`
2. **Review contracts**: Check `specs/001-enterprise-data-intelligence/contracts/`
3. **Run tests**: Follow TDD workflow in implementation
4. **Extend functionality**: Add new scrapers or analysis types

---

## Quick Reference

### URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web interface |
| Backend API Docs | http://localhost:8000/docs | Interactive API documentation |
| Backend API | http://localhost:8000/api | REST API endpoints |
| MongoDB | mongodb://localhost:27017 | Database (internal) |
| Ollama | http://localhost:11434 | LLM service (internal) |

### Common Commands

```bash
# Start system
docker compose up -d

# Stop system
docker compose stop

# View logs
docker compose logs -f [service-name]

# Check status
docker compose ps

# Run tests
docker compose exec backend pytest

# Access shell
docker compose exec backend bash

# Clean restart
docker compose down && docker compose up -d

# Full reset
docker compose down -v && docker compose up -d
```

### Log Files

All services log to `./logs/` directory in structured JSON format:

- `intelligence.scraper.log`: Scraper library logs
- `intelligence.analyzer.log`: Analyzer library logs
- `backend.api.log`: Backend API logs
- `backend.startup.log`: Startup orchestration logs

**Read logs**:
```bash
# Pretty-print JSON logs
cat logs/intelligence.scraper.log | jq .

# Filter by level
cat logs/backend.api.log | jq 'select(.level=="ERROR")'

# Watch logs in real-time
tail -f logs/intelligence.analyzer.log | jq .
```

---

**Need Help?**
- Review troubleshooting section above
- Check logs for detailed error messages
- Consult `specs/001-enterprise-data-intelligence/plan.md` for architecture details

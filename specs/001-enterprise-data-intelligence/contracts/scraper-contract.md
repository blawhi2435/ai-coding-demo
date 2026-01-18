# Intelligence Scraper Library Contract

**Library**: `intelligence-scraper`
**Version**: 1.0.0
**Purpose**: Extract clean article text from web sources

## CLI Interface

### Command: `scrape`

**Synopsis**:
```bash
intelligence-scraper scrape <source> <output-file> [options]
```

**Description**: Scrapes articles from the specified source and outputs structured JSON

**Arguments**:
- `source`: Source identifier (e.g., "nvidia", "techcrunch")
- `output-file`: Path to output JSON file (use "-" for stdout)

**Options**:
- `--max-articles N`: Maximum number of articles to scrape (default: 100)
- `--since DATE`: Only scrape articles published after DATE (ISO 8601 format)
- `--method METHOD`: Force scraping method ("trafilatura", "playwright", or "auto" for fallback)
- `--log-level LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file PATH`: Path to JSON log file (default: stderr)

**Exit Codes**:
- `0`: Success (all articles scraped)
- `1`: Partial success (some articles failed, but results written)
- `2`: Total failure (no articles scraped)
- `3`: Invalid arguments

**Examples**:
```bash
# Scrape NVIDIA Newsroom, output to file
intelligence-scraper scrape nvidia /tmp/articles.json

# Scrape with limits
intelligence-scraper scrape nvidia output.json --max-articles 50 --since 2026-01-01

# Force Playwright method
intelligence-scraper scrape nvidia output.json --method playwright

# Output to stdout
intelligence-scraper scrape nvidia - > articles.json
```

## Output Contract

### JSON Schema

**Type**: Array of ScrapedArticle objects

**ScrapedArticle Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "url",
    "title",
    "content",
    "publishDate",
    "source",
    "scrapedAt",
    "scraperMethod",
    "contentTruncated"
  ],
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Source article URL"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "description": "Article title"
    },
    "content": {
      "type": "string",
      "minLength": 50,
      "description": "Clean article text (HTML stripped)"
    },
    "publishDate": {
      "type": "string",
      "format": "date-time",
      "description": "Publication date from article metadata"
    },
    "source": {
      "type": "string",
      "description": "Source website name"
    },
    "keywords": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Extracted keywords if available"
    },
    "scrapedAt": {
      "type": "string",
      "format": "date-time",
      "description": "Scraping timestamp (UTC)"
    },
    "scraperMethod": {
      "type": "string",
      "enum": ["trafilatura", "playwright"],
      "description": "Extraction method used"
    },
    "contentTruncated": {
      "type": "boolean",
      "description": "True if content exceeded max length"
    },
    "errorLog": {
      "type": "string",
      "nullable": true,
      "description": "Error details if scraping partially failed"
    }
  }
}
```

**Example Output**:
```json
[
  {
    "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
    "title": "NVIDIA Announces New AI Supercomputer",
    "content": "NVIDIA today unveiled its latest DGX system featuring breakthrough performance for large language model training...",
    "publishDate": "2026-01-15T10:00:00Z",
    "source": "NVIDIA Newsroom",
    "keywords": ["AI", "supercomputer", "DGX", "machine learning"],
    "scrapedAt": "2026-01-17T08:30:00Z",
    "scraperMethod": "trafilatura",
    "contentTruncated": false,
    "errorLog": null
  },
  {
    "url": "https://nvidianews.nvidia.com/news/nvidia-partners-with-cloud",
    "title": "NVIDIA Partners with Major Cloud Providers",
    "content": "NVIDIA announced strategic partnerships...",
    "publishDate": "2026-01-14T15:30:00Z",
    "source": "NVIDIA Newsroom",
    "keywords": ["cloud", "partnerships", "AI infrastructure"],
    "scrapedAt": "2026-01-17T08:31:15Z",
    "scraperMethod": "playwright",
    "contentTruncated": false,
    "errorLog": null
  }
]
```

## Logging Contract

### JSON Log Format

All logs written to stderr (or `--log-file`) in structured JSON format:

**Schema**:
```json
{
  "timestamp": "ISO 8601 UTC timestamp",
  "level": "DEBUG|INFO|WARNING|ERROR",
  "component": "intelligence.scraper",
  "message": "Human-readable message",
  "context": {
    "file": "Source file name",
    "line": "Line number",
    "function": "Function name",
    "url": "Article URL (if applicable)",
    "method": "Scraper method (if applicable)"
  },
  "error": "Exception traceback (if level=ERROR)"
}
```

**Example Logs**:
```json
{"timestamp": "2026-01-17T08:30:00Z", "level": "INFO", "component": "intelligence.scraper", "message": "Starting scrape for source: nvidia", "context": {"file": "cli.py", "line": 45, "function": "scrape"}}
{"timestamp": "2026-01-17T08:30:05Z", "level": "INFO", "component": "intelligence.scraper", "message": "Found 25 article URLs", "context": {"file": "nvidia.py", "line": 78, "function": "fetch_article_list"}}
{"timestamp": "2026-01-17T08:30:12Z", "level": "WARNING", "component": "intelligence.scraper", "message": "Trafilatura extraction failed, falling back to Playwright", "context": {"file": "cleaner.py", "line": 123, "function": "extract_content", "url": "https://nvidianews.nvidia.com/news/article-123"}}
{"timestamp": "2026-01-17T08:35:00Z", "level": "INFO", "component": "intelligence.scraper", "message": "Scraping complete: 23/25 articles successful", "context": {"file": "cli.py", "line": 67, "function": "scrape"}}
```

## Error Handling

### Partial Failures

If some articles fail to scrape:
- Continue processing remaining articles
- Log errors for failed articles to stderr
- Include failed URLs in error summary
- Exit with code 1 (partial success)
- Write successful articles to output file

**Example Error Log**:
```json
{
  "timestamp": "2026-01-17T08:32:00Z",
  "level": "ERROR",
  "component": "intelligence.scraper",
  "message": "Failed to scrape article",
  "context": {
    "file": "nvidia.py",
    "line": 156,
    "function": "extract_content",
    "url": "https://nvidianews.nvidia.com/news/broken-article",
    "method": "playwright"
  },
  "error": "Timeout: Page load exceeded 30 seconds\n  at extract_content (nvidia.py:156)\n  at scrape_article (nvidia.py:89)"
}
```

### Total Failures

If no articles can be scraped:
- Log detailed error to stderr
- Exit with code 2
- Do not create output file

## Testing Contract

### Contract Test Example

```python
# tests/contract/test_output_schema.py
import json
import subprocess
from jsonschema import validate

def test_scraper_output_schema():
    """Contract: Scraper output must match JSON schema"""
    # Run scraper
    result = subprocess.run(
        ["intelligence-scraper", "scrape", "nvidia", "/tmp/test-output.json", "--max-articles", "5"],
        capture_output=True,
        text=True
    )

    # Verify exit code
    assert result.returncode in [0, 1], "Scraper must exit with 0 or 1"

    # Load output
    with open("/tmp/test-output.json") as f:
        articles = json.load(f)

    # Verify schema compliance
    assert isinstance(articles, list), "Output must be an array"
    assert len(articles) > 0, "Must scrape at least 1 article"

    for article in articles:
        # Required fields
        assert "url" in article
        assert "title" in article
        assert "content" in article
        assert len(article["content"]) >= 50, "Content must be at least 50 characters"

        # Field types
        assert isinstance(article["url"], str)
        assert article["url"].startswith("http")
        assert isinstance(article["scrapedAt"], str)
        assert article["scraperMethod"] in ["trafilatura", "playwright"]
```

## Performance Contract

### Benchmarks

- **Trafilatura method**: < 2 seconds per article (average)
- **Playwright method**: < 10 seconds per article (average)
- **Memory usage**: < 500MB for 100 articles
- **Timeout**: 30 seconds per article (configurable)

### Constraints

- Maximum content length: 100,000 characters (auto-truncate with flag)
- Maximum articles per invocation: 1000 (configurable)
- Network timeout: 30 seconds per HTTP request
- Playwright page timeout: 30 seconds

## Extensibility Contract

### Adding New Sources

To add a new source (e.g., "techcrunch"):

1. Create `extractors/techcrunch.py` implementing `BaseScraper`
2. Register in `cli.py` source mapping
3. Add contract tests in `tests/contract/test_techcrunch.py`

**BaseScraper Interface**:
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    @abstractmethod
    def fetch_article_list(self, max_articles: int, since: Optional[datetime]) -> List[str]:
        """Return list of article URLs to scrape"""
        pass

    @abstractmethod
    def extract_content(self, url: str) -> Dict:
        """Extract content from article URL, return ScrapedArticle dict"""
        pass
```

## Versioning

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to CLI interface or output schema
- **MINOR**: New sources, new optional fields in output
- **PATCH**: Bug fixes, performance improvements

**Current Version**: 1.0.0

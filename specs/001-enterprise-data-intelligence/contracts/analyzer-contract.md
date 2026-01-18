# Intelligence Analyzer Library Contract

**Library**: `intelligence-analyzer`
**Version**: 1.0.0
**Purpose**: Perform NLP analysis (NER, summarization, classification, sentiment) on article text using LLM

## CLI Interface

### Command: `analyze`

**Synopsis**:
```bash
intelligence-analyzer analyze <input-file> <output-file> [options]
```

**Description**: Analyzes article content and outputs structured analysis results

**Arguments**:
- `input-file`: Path to input JSON file (use "-" for stdin)
- `output-file`: Path to output JSON file (use "-" for stdout)

**Options**:
- `--llm-url URL`: Ollama service URL (default: http://localhost:11434)
- `--model NAME`: LLM model name (default: llama3)
- `--timeout SECONDS`: LLM request timeout (default: 30)
- `--log-level LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file PATH`: Path to JSON log file (default: stderr)

**Exit Codes**:
- `0`: Success (analysis complete)
- `1`: Partial failure (analysis attempted but incomplete)
- `2`: Total failure (LLM unavailable or invalid input)
- `3`: Invalid arguments

**Examples**:
```bash
# Analyze article from file
intelligence-analyzer analyze input.json output.json

# Analyze from stdin
cat article.json | intelligence-analyzer analyze - output.json

# Custom LLM service
intelligence-analyzer analyze input.json output.json --llm-url http://llm:11434

# Output to stdout
intelligence-analyzer analyze input.json - > analysis.json
```

## Input Contract

### JSON Schema

**Type**: AnalysisInput object (single article)

**AnalysisInput Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["url", "title", "content"],
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Article URL (for reference)"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "description": "Article title"
    },
    "content": {
      "type": "string",
      "minLength": 50,
      "maxLength": 10000,
      "description": "Article text to analyze (will be truncated if > 10000 chars)"
    }
  }
}
```

**Example Input**:
```json
{
  "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200",
  "title": "NVIDIA Announces New AI Supercomputer",
  "content": "NVIDIA today unveiled its latest DGX system featuring breakthrough performance for large language model training. The DGX H200 delivers 32 petaflops of AI computing power..."
}
```

## Output Contract

### JSON Schema

**Type**: AnalysisResult object

**AnalysisResult Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "entities",
    "summary",
    "classification",
    "sentimentScore",
    "analyzedAt",
    "model",
    "processingTime"
  ],
  "properties": {
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "type", "mentions"],
        "properties": {
          "text": {
            "type": "string",
            "minLength": 1,
            "description": "Entity text"
          },
          "type": {
            "type": "string",
            "enum": ["company", "person", "product", "technology"],
            "description": "Entity classification"
          },
          "mentions": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of mentions in article"
          }
        }
      },
      "description": "Extracted named entities"
    },
    "summary": {
      "type": "string",
      "maxLength": 500,
      "description": "Article summary (<100 words)"
    },
    "classification": {
      "type": "string",
      "enum": [
        "competitive_news",
        "personnel_change",
        "product_launch",
        "market_trend"
      ],
      "description": "Article category"
    },
    "sentimentScore": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "Business impact sentiment (1=very negative, 10=very positive)"
    },
    "analyzedAt": {
      "type": "string",
      "format": "date-time",
      "description": "Analysis timestamp (UTC)"
    },
    "model": {
      "type": "string",
      "description": "LLM model used"
    },
    "processingTime": {
      "type": "number",
      "minimum": 0,
      "description": "Analysis duration in seconds"
    }
  }
}
```

**Example Output**:
```json
{
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
    },
    {
      "text": "Jensen Huang",
      "type": "person",
      "mentions": 1
    },
    {
      "text": "large language model",
      "type": "technology",
      "mentions": 2
    }
  ],
  "summary": "NVIDIA launched DGX H200, a new AI supercomputer with 32 petaflops for LLM training, targeting enterprise AI workloads. CEO Jensen Huang highlighted breakthrough performance improvements.",
  "classification": "product_launch",
  "sentimentScore": 9,
  "analyzedAt": "2026-01-17T08:35:00Z",
  "model": "llama3",
  "processingTime": 4.2
}
```

## Logging Contract

### JSON Log Format

All logs written to stderr (or `--log-file`) in structured JSON format:

**Schema**:
```json
{
  "timestamp": "ISO 8601 UTC timestamp",
  "level": "DEBUG|INFO|WARNING|ERROR",
  "component": "intelligence.analyzer",
  "message": "Human-readable message",
  "context": {
    "file": "Source file name",
    "line": "Line number",
    "function": "Function name",
    "url": "Article URL (if applicable)",
    "model": "LLM model (if applicable)",
    "processingTime": "Duration in seconds (if applicable)"
  },
  "error": "Exception traceback (if level=ERROR)"
}
```

**Example Logs**:
```json
{"timestamp": "2026-01-17T08:35:00Z", "level": "INFO", "component": "intelligence.analyzer", "message": "Starting analysis", "context": {"file": "cli.py", "line": 52, "function": "analyze", "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200"}}
{"timestamp": "2026-01-17T08:35:01Z", "level": "DEBUG", "component": "intelligence.analyzer", "message": "Sending request to LLM service", "context": {"file": "client.py", "line": 89, "function": "call_llm", "model": "llama3"}}
{"timestamp": "2026-01-17T08:35:05Z", "level": "INFO", "component": "intelligence.analyzer", "message": "LLM response received", "context": {"file": "client.py", "line": 102, "function": "call_llm", "processingTime": 4.2}}
{"timestamp": "2026-01-17T08:35:06Z", "level": "INFO", "component": "intelligence.analyzer", "message": "Analysis complete", "context": {"file": "cli.py", "line": 78, "function": "analyze", "url": "https://nvidianews.nvidia.com/news/nvidia-announces-dgx-h200", "processingTime": 4.2}}
```

## LLM Prompt Contract

### Structured Prompt Template

The analyzer uses a single-pass prompt to get all analysis results in one LLM call:

**Prompt Structure**:
```
Analyze the following article and return a JSON response with exactly these fields:

1. entities: Array of objects with {text, type, mentions}
   - type must be one of: company, person, product, technology
   - mentions is the count of times the entity appears in the article

2. summary: String summary of the article in less than 100 words

3. classification: Single category, must be one of:
   - competitive_news: News about competitors or market competition
   - personnel_change: Leadership changes, hiring, departures
   - product_launch: New product or feature announcements
   - market_trend: Industry trends, market analysis, forecasts

4. sentimentScore: Integer from 1-10 indicating business impact
   - 1 = very negative business impact
   - 5 = neutral
   - 10 = very positive business impact

Article Title: {title}

Article Content:
{content}

Return ONLY valid JSON matching this structure. No additional text.
```

**Expected LLM Response Format**:
```json
{
  "entities": [
    {"text": "NVIDIA", "type": "company", "mentions": 5},
    {"text": "DGX H200", "type": "product", "mentions": 3}
  ],
  "summary": "NVIDIA launched DGX H200...",
  "classification": "product_launch",
  "sentimentScore": 9
}
```

### Validation Process

1. Send prompt to Ollama with `format: "json"` parameter
2. Parse LLM response as JSON
3. Validate against AnalysisResult schema using Pydantic
4. If validation fails: retry once, then exit with code 1
5. If retry fails: log error, return partial results if available

## Error Handling

### LLM Unavailable

If Ollama service is unreachable:
- Log error to stderr with full context
- Exit with code 2 (total failure)
- Do not create output file

**Example Error Log**:
```json
{
  "timestamp": "2026-01-17T08:35:00Z",
  "level": "ERROR",
  "component": "intelligence.analyzer",
  "message": "Failed to connect to LLM service",
  "context": {
    "file": "client.py",
    "line": 45,
    "function": "call_llm",
    "url": "http://localhost:11434"
  },
  "error": "ConnectionError: Failed to establish connection to http://localhost:11434\n  at call_llm (client.py:45)\n  at analyze (cli.py:68)"
}
```

### Invalid LLM Response

If LLM returns invalid JSON or fails validation:
- Log warning with LLM response
- Retry once with refined prompt
- If retry fails: exit with code 1, log error with full LLM response

**Example Error Log**:
```json
{
  "timestamp": "2026-01-17T08:35:07Z",
  "level": "WARNING",
  "component": "intelligence.analyzer",
  "message": "LLM response validation failed, retrying",
  "context": {
    "file": "analyzers/ner.py",
    "line": 78,
    "function": "parse_llm_response",
    "validationError": "sentimentScore must be between 1 and 10, got 12"
  }
}
```

### Content Truncation

If input content exceeds 10,000 characters:
- Truncate to 10,000 characters at word boundary
- Log warning with original length
- Continue with truncated content
- Analysis proceeds normally

**Example Log**:
```json
{
  "timestamp": "2026-01-17T08:35:00Z",
  "level": "WARNING",
  "component": "intelligence.analyzer",
  "message": "Content truncated to fit LLM context window",
  "context": {
    "file": "cli.py",
    "line": 62,
    "function": "analyze",
    "originalLength": 15234,
    "truncatedLength": 10000
  }
}
```

## Testing Contract

### Contract Test Example

```python
# tests/contract/test_analysis_schema.py
import json
import subprocess
from jsonschema import validate

def test_analyzer_output_schema():
    """Contract: Analyzer output must match JSON schema"""
    # Prepare input
    input_data = {
        "url": "https://example.com/article",
        "title": "Test Article",
        "content": "This is a test article about NVIDIA launching a new AI product called DGX H200 for enterprise customers..."
    }

    with open("/tmp/test-input.json", "w") as f:
        json.dump(input_data, f)

    # Run analyzer
    result = subprocess.run(
        ["intelligence-analyzer", "analyze", "/tmp/test-input.json", "/tmp/test-output.json"],
        capture_output=True,
        text=True
    )

    # Verify exit code
    assert result.returncode == 0, "Analyzer must exit with 0 on success"

    # Load output
    with open("/tmp/test-output.json") as f:
        analysis = json.load(f)

    # Verify required fields
    assert "entities" in analysis
    assert "summary" in analysis
    assert "classification" in analysis
    assert "sentimentScore" in analysis

    # Verify field constraints
    assert 1 <= analysis["sentimentScore"] <= 10
    assert analysis["classification"] in [
        "competitive_news",
        "personnel_change",
        "product_launch",
        "market_trend"
    ]
    assert len(analysis["summary"]) <= 500

    # Verify entities
    for entity in analysis["entities"]:
        assert "text" in entity
        assert "type" in entity
        assert "mentions" in entity
        assert entity["type"] in ["company", "person", "product", "technology"]
        assert entity["mentions"] >= 1
```

### Integration Test Example

```python
# tests/integration/test_llm_integration.py
def test_llm_service_integration():
    """Integration: Analyzer can communicate with Ollama service"""
    # Assumes Ollama is running locally with llama3 model

    input_data = {
        "url": "https://example.com/article",
        "title": "NVIDIA Announces DGX H200",
        "content": "NVIDIA unveiled the DGX H200 AI supercomputer..."
    }

    result = subprocess.run(
        ["intelligence-analyzer", "analyze", "-", "-"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    analysis = json.loads(result.stdout)

    # Verify analysis quality
    assert len(analysis["entities"]) > 0
    assert "NVIDIA" in [e["text"] for e in analysis["entities"]]
    assert analysis["classification"] == "product_launch"
    assert analysis["processingTime"] > 0
```

## Performance Contract

### Benchmarks

- **Average processing time**: 3-8 seconds per article (depends on LLM model)
- **Memory usage**: < 200MB per analysis
- **LLM timeout**: 30 seconds (configurable)
- **Max concurrent analyses**: 1 (library is single-threaded)

### Constraints

- Input content max length: 10,000 characters (auto-truncate)
- Summary max length: 500 characters (~100 words)
- LLM response timeout: 30 seconds (default)
- Retry attempts: 1 (on validation failure)

## Extensibility Contract

### Adding New Analysis Types

To add new analysis capabilities (e.g., "topic modeling"):

1. Create `analyzers/topic.py` with analysis logic
2. Update prompt template to include new field
3. Update AnalysisResult schema with new field
4. Add contract tests for new field
5. Increment MINOR version (backward-compatible addition)

**NOTE**: Adding required fields to AnalysisResult is a MAJOR version change (breaking)

## Versioning

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to CLI interface, input/output schema (required fields)
- **MINOR**: New optional fields in output, new analysis types
- **PATCH**: Bug fixes, prompt improvements, performance optimizations

**Current Version**: 1.0.0

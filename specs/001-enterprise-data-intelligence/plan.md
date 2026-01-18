# Implementation Plan: Enterprise Data Intelligence Assistant

**Branch**: `001-enterprise-data-intelligence` | **Date**: 2026-01-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-enterprise-data-intelligence/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a proof-of-concept system demonstrating automatic intelligence gathering from NVIDIA Newsroom content, transforming unstructured web articles into structured, actionable business intelligence. The system will automatically scrape articles on startup, perform NLP analysis (NER, summarization, classification, sentiment scoring) using open-source LLMs, and present results through a web interface. All services orchestrated via Docker Compose for single-command deployment.

**Primary Goal**: Prove end-to-end autonomous intelligence gathering with 90% analysis success rate on 20+ articles, deployable in under 10 minutes.

**Technical Approach**: Microservices-lite architecture with 4 containerized services (React frontend, FastAPI backend with integrated scraper, Ollama LLM service, MongoDB), communicating via REST APIs and using structured JSON for LLM outputs.

## Technical Context

**Language/Version**: Python 3.11 (backend/scraper/LLM integration), TypeScript/React 18 (frontend)
**Primary Dependencies**: FastAPI, Ollama (Llama 3 8B), React, Vite, TailwindCSS, MongoDB driver (pymongo/motor), trafilatura (text extraction), Playwright (fallback scraping)
**Storage**: MongoDB 7 (articles collection with analysis results)
**Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)
**Target Platform**: Docker Compose on Linux/macOS/Windows with minimum 12GB RAM
**Project Type**: Web application (backend + frontend + supporting services)
**Performance Goals**:
  - Scrape and analyze 20+ articles within 5 minutes of startup
  - Article list queries < 2 seconds for 500 articles
  - Detail view loads < 1 second per article
  - Real-time updates within 5 seconds
**Constraints**:
  - All services containerized (Docker Compose orchestration)
  - Open-source LLM only (Llama 3 8B via Ollama)
  - Single-command deployment (`docker-compose up -d`)
  - LLM context window: 4000 tokens (truncate longer articles)
  - MVP scope: NVIDIA Newsroom only (architecture extensible to other sources)
**Scale/Scope**:
  - 20-100 articles for MVP demonstration
  - 10 concurrent evaluators
  - 24-hour continuous operation
  - Single MongoDB node (up to 1000 articles capacity)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Library-First ⚠️ VIOLATION

**Status**: VIOLATION - Justification required

**Finding**: The design document specifies a microservices architecture with 4 containers (frontend, backend, LLM, MongoDB). The backend service combines scraping, API, and LLM orchestration without library separation.

**Required**: Each functional component should be a standalone library with CLI interface:
- Scraper library (text extraction)
- LLM analysis library (NER, summarization, classification, sentiment)
- API service library (REST endpoints)

**Justification Path**: This violation must be addressed in Phase 1 design by:
1. Extracting scraper logic into standalone `intelligence-scraper` library with CLI (`scrape <source> <output-json>`)
2. Extracting LLM analysis into `intelligence-analyzer` library with CLI (`analyze <input-json> <output-json>`)
3. Backend API becomes thin orchestration layer calling libraries

**Complexity Tracking Required**: Yes - see "Complexity Tracking" section below

### Principle II: Test-First ✅ PASS

**Status**: COMPLIANT

**Finding**: Specification includes comprehensive testing requirements:
- Contract tests required for API endpoints (SC-012: detail views < 1 second)
- Integration tests implied for end-to-end pipeline (SC-003: 90% analysis success)
- E2E tests specified (Playwright for full stack)

**Action**: TDD workflow MUST be followed during implementation:
1. Write contract tests for scraper library output format
2. Write contract tests for analyzer library output format
3. Write API contract tests before implementation
4. Confirm all tests fail before writing implementation

### Principle III: Observability ⚠️ NEEDS VERIFICATION

**Status**: PARTIAL COMPLIANCE - Enhancement required

**Finding**:
- ✅ Specification requires logging (FR-016: persistent log files)
- ⚠️ No structured logging format specified
- ⚠️ No text I/O protocol for libraries (since libraries not yet designed)

**Required Enhancement**:
1. All libraries MUST use structured JSON logging with fields: timestamp, level, component, message, context
2. CLI interfaces MUST use stdin/stdout protocol (input via args/stdin, output via stdout, errors via stderr)
3. Ensure FR-016 implementation uses JSON format for log files

**Action**: Phase 1 design must specify structured logging contract

### Gate Decision

**Result**: ⚠️ CONDITIONAL PASS with required corrections in Phase 1

**Conditions**:
1. Phase 1 MUST refactor backend into standalone libraries (scraper, analyzer, API)
2. Phase 1 MUST define structured logging contract (JSON format)
3. Phase 1 MUST define CLI interfaces for libraries
4. Complexity Tracking MUST justify any remaining violations

**Re-evaluation**: After Phase 1 design completion

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Root configuration
docker-compose.yml          # Orchestrates all 4 containers
.env.example                # Environment variable template

# Libraries (constitution-compliant standalone components)
libs/
├── intelligence-scraper/   # Scraping library
│   ├── src/
│   │   ├── cli.py         # CLI entry: scrape <source> <output-json>
│   │   ├── extractors/
│   │   │   ├── base.py    # BaseScraper abstract class
│   │   │   └── nvidia.py  # NvidiaScraper implementation
│   │   └── utils/
│   │       ├── cleaner.py # Text extraction/cleaning
│   │       └── logger.py  # Structured JSON logging
│   ├── tests/
│   │   ├── contract/      # Output format validation
│   │   ├── integration/   # Live scraping tests
│   │   └── unit/          # Extractor logic tests
│   └── pyproject.toml     # Standalone package
│
├── intelligence-analyzer/ # LLM analysis library
│   ├── src/
│   │   ├── cli.py         # CLI entry: analyze <input-json> <output-json>
│   │   ├── llm/
│   │   │   ├── client.py  # Ollama HTTP client
│   │   │   └── prompts.py # Structured prompt templates
│   │   ├── analyzers/
│   │   │   ├── ner.py     # Named entity recognition
│   │   │   ├── summary.py # Text summarization
│   │   │   ├── classify.py# Article classification
│   │   │   └── sentiment.py# Sentiment scoring
│   │   └── utils/
│   │       └── logger.py  # Structured JSON logging
│   ├── tests/
│   │   ├── contract/      # JSON schema validation
│   │   ├── integration/   # LLM service integration
│   │   └── unit/          # Analyzer logic tests
│   └── pyproject.toml
│
└── intelligence-api/      # API library (future, if needed for reuse)
    └── [API helpers, if extracted from backend]

# Backend service (thin orchestration layer)
backend/
├── src/
│   ├── main.py            # FastAPI application entry
│   ├── startup.py         # Scraper trigger on startup
│   ├── api/
│   │   ├── routes/
│   │   │   ├── articles.py   # Article CRUD endpoints
│   │   │   ├── entities.py   # Entity endpoints
│   │   │   └── stats.py      # Statistics endpoints
│   │   └── schemas.py     # Pydantic models
│   ├── db/
│   │   ├── mongo.py       # MongoDB connection
│   │   └── models.py      # Document schemas
│   └── config.py          # Environment config
├── tests/
│   ├── contract/          # API contract tests
│   ├── integration/       # DB + library integration
│   └── e2e/               # Full pipeline tests
├── Dockerfile
└── requirements.txt

# Frontend service
frontend/
├── src/
│   ├── main.tsx           # App entry point
│   ├── App.tsx
│   ├── components/
│   │   ├── ArticleList/   # Article list view
│   │   ├── ArticleDetail/ # Detail view
│   │   ├── Filters/       # Filter controls
│   │   └── Stats/         # Statistics dashboard
│   ├── services/
│   │   └── api.ts         # Backend API client
│   ├── types/             # TypeScript types
│   └── styles/
├── tests/
│   ├── component/         # Component unit tests
│   └── e2e/               # Playwright E2E tests
├── Dockerfile
├── package.json
└── vite.config.ts

# LLM service (external container, no custom code)
# Uses official ollama/ollama image

# Database (external container, no custom code)
# Uses official mongo:7 image

# Shared configuration
docker/
├── backend.Dockerfile
├── frontend.Dockerfile
└── init-mongo/            # MongoDB init scripts
    └── create-indexes.js

# Logs (volume mount)
logs/
└── [generated at runtime]
```

**Structure Decision**: Web application with library-first design

This structure addresses Constitution violations by:
1. **Library-First**: `intelligence-scraper` and `intelligence-analyzer` are standalone, independently testable libraries with CLI interfaces
2. **Observability**: Each library includes `logger.py` for structured JSON logging
3. **Test-First**: Each library/service has dedicated test directories (contract/integration/unit)

The backend becomes a thin orchestration layer that:
- Calls scraper library on startup
- Passes scraped data to analyzer library
- Stores results in MongoDB
- Exposes REST API for frontend queries

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Microservices (4 containers) | Docker Compose requirement mandates containerization. LLM service (Ollama) and MongoDB are external dependencies that MUST run in separate containers. | Monolithic approach rejected: (1) Ollama requires dedicated container with 8GB RAM, (2) MongoDB official image simplifies deployment, (3) Frontend must be served separately for SPA architecture |
| Multiple projects (backend, frontend, 2 libs) | Constitution's Library-First principle requires standalone scraper/analyzer libraries. Frontend/backend separation is web app standard. | Single project rejected: (1) Scraper/analyzer MUST be independently testable libraries with CLI, (2) React frontend requires separate build tooling (Vite), (3) Backend/frontend have different deployment targets |

**Justification Summary**:
- The 4-container architecture is driven by external dependencies (Ollama, MongoDB) and Docker Compose constraint, not internal complexity
- The library separation (scraper, analyzer) COMPLIES with constitution's Library-First principle
- Backend/frontend separation is standard web architecture, not additional complexity

---

## Constitution Check - Post-Design Re-evaluation

*Re-evaluation after Phase 1 design completion*

### Principle I: Library-First ✅ NOW COMPLIANT

**Status**: COMPLIANT

**Changes Made**:
1. ✅ Created `intelligence-scraper` standalone library with CLI interface
   - CLI: `intelligence-scraper scrape <source> <output-file>`
   - Output contract: JSON array of ScrapedArticle objects
   - Contract defined in `contracts/scraper-contract.md`

2. ✅ Created `intelligence-analyzer` standalone library with CLI interface
   - CLI: `intelligence-analyzer analyze <input-file> <output-file>`
   - Output contract: AnalysisResult JSON
   - Contract defined in `contracts/analyzer-contract.md`

3. ✅ Backend refactored as thin orchestration layer
   - Calls libraries via CLI or direct Python imports
   - No business logic duplication
   - Focuses on API, DB, and service coordination

**Verification**:
- Both libraries can be tested independently
- Both libraries have CLI interfaces with stdin/stdout protocol
- Both libraries have well-defined input/output contracts
- See `data-model.md` sections 1-2 for complete contracts

### Principle II: Test-First ✅ READY FOR TDD

**Status**: COMPLIANT - Contracts ready for TDD implementation

**Test Structure Defined**:
1. ✅ Contract tests specified for scraper library
   - See `contracts/scraper-contract.md` section "Testing Contract"
   - Validates output JSON schema

2. ✅ Contract tests specified for analyzer library
   - See `contracts/analyzer-contract.md` section "Testing Contract"
   - Validates analysis result schema

3. ✅ API contract tests ready
   - OpenAPI spec in `contracts/openapi.yaml`
   - FastAPI will auto-validate against spec

4. ✅ Integration test patterns defined
   - Library → Backend integration
   - Backend → LLM service integration
   - Backend → MongoDB integration

**Implementation Workflow**:
1. Write contract tests based on specifications
2. Run tests, confirm failures
3. Implement minimal code to pass
4. Refactor and repeat

### Principle III: Observability ✅ NOW COMPLIANT

**Status**: COMPLIANT

**Structured Logging Implemented**:
1. ✅ JSON logging format defined for all components
   - Schema: `{"timestamp", "level", "component", "message", "context", "error"}`
   - See `research.md` section 8 for implementation details

2. ✅ CLI libraries use stdin/stdout protocol
   - Scraper: JSON array to stdout, logs to stderr
   - Analyzer: AnalysisResult to stdout, logs to stderr
   - See library contracts for I/O specifications

3. ✅ Centralized log files with volume mounts
   - `logs/intelligence.scraper.log`
   - `logs/intelligence.analyzer.log`
   - `logs/backend.api.log`
   - `logs/backend.startup.log`

**Verification**:
- All libraries have `utils/logger.py` with JSON formatter
- All logs include required fields (timestamp, level, component, message, context)
- CLI tools follow text I/O protocol (input via args/stdin, output via stdout, errors via stderr)

### Final Gate Decision

**Result**: ✅ ALL PRINCIPLES COMPLIANT

**Summary**:
1. **Library-First**: `intelligence-scraper` and `intelligence-analyzer` are standalone libraries with CLI interfaces
2. **Test-First**: Complete contract definitions enable TDD workflow
3. **Observability**: Structured JSON logging and text I/O protocols implemented

**Complexity Justification**:
- 4-container architecture is externally imposed (Docker Compose requirement, Ollama, MongoDB)
- Library separation COMPLIES with constitution (not additional complexity)
- No unjustified violations remain

**Approved for Implementation**: ✅

---

# Tasks: Enterprise Data Intelligence Assistant

**Input**: Design documents from `/specs/001-enterprise-data-intelligence/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included based on constitution's Test-First principle. All contract tests MUST be written first and confirmed to fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `libs/`, `backend/`, `frontend/`, `docker/`
- Libraries: `libs/intelligence-scraper/`, `libs/intelligence-analyzer/`
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and Docker Compose infrastructure

- [x] T001 Create root-level project structure (docker-compose.yml, .env.example, logs/, docker/)
- [x] T002 [P] Create libs/intelligence-scraper/ directory structure (src/, tests/, pyproject.toml)
- [x] T003 [P] Create libs/intelligence-analyzer/ directory structure (src/, tests/, pyproject.toml)
- [x] T004 [P] Create backend/ directory structure (src/, tests/, Dockerfile, requirements.txt)
- [x] T005 [P] Create frontend/ directory structure (src/, tests/, package.json, vite.config.ts)
- [x] T006 [P] Initialize intelligence-scraper Python package with dependencies (trafilatura, playwright, pydantic)
- [x] T007 [P] Initialize intelligence-analyzer Python package with dependencies (httpx, pydantic)
- [x] T008 [P] Initialize backend FastAPI project with dependencies (fastapi, pymongo, motor, pydantic, uvicorn)
- [x] T009 [P] Initialize frontend React project with dependencies (react, vite, tailwindcss, @tanstack/react-query, zustand, axios)
- [x] T010 [P] Configure backend linting and formatting (black, isort, flake8, mypy)
- [x] T011 [P] Configure frontend linting and formatting (eslint, prettier)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Docker Infrastructure

- [x] T012 Create docker-compose.yml with 4 services (mongodb, llm, backend, frontend) with health checks
- [x] T013 [P] Create docker/backend.Dockerfile for backend service
- [x] T014 [P] Create docker/frontend.Dockerfile with multi-stage build (node build → nginx serve)
- [x] T015 [P] Create docker/init-mongo/create-indexes.js for MongoDB index initialization
- [x] T016 Configure environment variables in .env.example (MONGODB_URL, LLM_SERVICE_URL, VITE_API_URL)

### Shared Logging Infrastructure

- [x] T017 [P] Implement JSON logger utility in libs/intelligence-scraper/src/utils/logger.py
- [x] T018 [P] Implement JSON logger utility in libs/intelligence-analyzer/src/utils/logger.py
- [x] T019 [P] Implement JSON logger utility in backend/src/utils/logger.py

### MongoDB Schema and Models

- [x] T020 Create backend/src/db/mongo.py with MongoDB connection and health check
- [x] T021 [P] Define Article Pydantic model in backend/src/db/models.py
- [x] T022 [P] Define Entity Pydantic model in backend/src/db/models.py

### Backend API Infrastructure

- [x] T023 Create backend/src/main.py FastAPI application with CORS and error handling
- [x] T024 [P] Create backend/src/config.py for environment configuration
- [x] T025 [P] Implement backend/src/api/schemas.py with Pydantic response models (PaginatedArticles, AggregatedStats, EntitySummary)

### Frontend Infrastructure

- [x] T026 Configure TailwindCSS in frontend/tailwind.config.js
- [x] T027 [P] Create frontend/src/services/api.ts with Axios instance and error interceptors
- [x] T028 [P] Create frontend/src/types/index.ts with TypeScript interfaces (Article, Entity, Filters)
- [x] T029 [P] Setup React Query provider in frontend/src/main.tsx
- [x] T030 [P] Setup Zustand filter store in frontend/src/stores/filterStore.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - System Deployment and Health Monitoring (Priority: P1) ✅ COMPLETE

**Goal**: Evaluators can start the entire system with a single command and verify all services are running correctly

**Independent Test**: Run `docker-compose up -d` and verify all 4 containers start with healthy status

### Tests for User Story 4 (Test-First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T031 [P] [US4] Contract test for /api/health endpoint in backend/tests/contract/test_health.py
- [x] T032 [P] [US4] Integration test for Docker Compose startup in backend/tests/integration/test_deployment.py

### Implementation for User Story 4

- [x] T033 [US4] Implement /api/health endpoint in backend/src/api/routes/health.py with MongoDB and LLM connectivity checks
- [x] T034 [US4] Add health check route to FastAPI app in backend/src/main.py
- [x] T035 [US4] Verify docker-compose.yml health checks for all services (mongodb, llm, backend, frontend)
- [x] T036 [US4] Test `docker-compose up -d` command and verify all containers reach healthy status
- [x] T037 [US4] Add structured logging for service startup events in backend/src/main.py

**Checkpoint**: At this point, the entire system should be deployable with `docker-compose up -d` and all services should report healthy status

---

## Phase 4: User Story 2 - Automatic Content Scraping and Analysis (Priority: P2) ✅ COMPLETE

**Goal**: The system automatically scrapes NVIDIA Newsroom articles on startup and performs NLP analysis

**Independent Test**: Start system, verify articles are scraped and analyzed automatically within 5 minutes

### Tests for User Story 2 (Test-First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US2] Contract test for scraper output schema in libs/intelligence-scraper/tests/contract/test_output_schema.py
- [x] T039 [P] [US2] Contract test for analyzer output schema in libs/intelligence-analyzer/tests/contract/test_analysis_schema.py
- [x] T040 [P] [US2] Integration test for scraper → MongoDB pipeline in backend/tests/integration/test_scraping_pipeline.py
- [x] T041 [P] [US2] Integration test for analyzer → MongoDB pipeline in backend/tests/integration/test_analysis_pipeline.py
- [x] T042 [US2] E2E test for full scraping and analysis workflow in backend/tests/e2e/test_full_pipeline.py

### Implementation for User Story 2: Scraper Library

- [x] T043 [US2] Create BaseScraper abstract class in libs/intelligence-scraper/src/extractors/base.py
- [x] T044 [US2] Implement NvidiaScraper in libs/intelligence-scraper/src/extractors/nvidia.py with trafilatura extraction
- [x] T045 [US2] Add Playwright fallback logic to NvidiaScraper for JavaScript-rendered content
- [x] T046 [US2] Implement text cleaner utility in libs/intelligence-scraper/src/utils/cleaner.py
- [x] T047 [US2] Define ScrapedArticle Pydantic model in libs/intelligence-scraper/src/models.py
- [x] T048 [US2] Implement CLI entry point in libs/intelligence-scraper/src/cli.py with argparse
- [x] T049 [US2] Add error handling and retry logic for failed scrapes in libs/intelligence-scraper/src/extractors/nvidia.py
- [x] T050 [US2] Add structured logging to scraper library using logger utility

### Implementation for User Story 2: Analyzer Library

- [x] T051 [US2] Implement Ollama HTTP client in libs/intelligence-analyzer/src/llm/client.py
- [x] T052 [US2] Create structured prompt template in libs/intelligence-analyzer/src/llm/prompts.py
- [x] T053 [US2] Define AnalysisInput and AnalysisResult Pydantic models in libs/intelligence-analyzer/src/models.py
- [x] T054 [US2] Implement single-pass analysis in libs/intelligence-analyzer/src/analyzers/unified.py
- [x] T055 [US2] Add JSON schema validation for LLM responses using Pydantic
- [x] T056 [US2] Implement CLI entry point in libs/intelligence-analyzer/src/cli.py
- [x] T057 [US2] Add content truncation logic (4000 token limit) in libs/intelligence-analyzer/src/utils/truncate.py
- [x] T058 [US2] Add LLM request timeout (30s) and retry logic (1 retry) in llm/client.py
- [x] T059 [US2] Add structured logging to analyzer library using logger utility

### Implementation for User Story 2: Backend Orchestration

- [x] T060 [US2] Implement startup scraper trigger in backend/src/startup.py that calls scraper library
- [x] T061 [US2] Create article storage service in backend/src/services/article_service.py with MongoDB operations
- [x] T062 [US2] Implement scraper → database pipeline in backend/src/startup.py
- [x] T063 [US2] Implement analyzer → database pipeline in backend/src/startup.py
- [x] T064 [US2] Add error handling for partial scraping/analysis failures with status flags (complete/pending/failed)
- [x] T065 [US2] Register startup event handler in backend/src/main.py to trigger scraping on service start
- [x] T066 [US2] Add structured logging for scraping and analysis progress to backend logs

**Checkpoint**: At this point, starting the system should automatically scrape and analyze articles without manual intervention

---

## Phase 5: User Story 1 - View Analyzed Intelligence (Priority: P1) ✅ COMPLETE

**Goal**: Evaluators can view a comprehensive list of analyzed articles with filters and detail views

**Independent Test**: Access web interface, verify article list displays with working filters and detail views

### Tests for User Story 1 (Test-First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T067 [P] [US1] Contract test for GET /api/articles endpoint in backend/tests/contract/test_articles_api.py
- [x] T068 [P] [US1] Contract test for GET /api/articles/{id} endpoint in backend/tests/contract/test_articles_api.py
- [ ] T069 [P] [US1] Frontend component test for ArticleList in frontend/tests/component/ArticleList.test.tsx (Optional)
- [ ] T070 [P] [US1] Frontend component test for ArticleDetail in frontend/tests/component/ArticleDetail.test.tsx (Optional)
- [ ] T071 [US1] E2E test for article browsing workflow in frontend/tests/e2e/article-browsing.spec.ts (Optional)

### Implementation for User Story 1: Backend API

- [x] T072 [US1] Implement GET /api/articles with pagination and filters in backend/src/api/routes/articles.py
- [x] T073 [US1] Implement GET /api/articles/{id} in backend/src/api/routes/articles.py
- [x] T074 [US1] Add query parameter validation (classification, sentiment range, date range, search) using Pydantic
- [x] T075 [US1] Implement MongoDB queries with compound indexes for efficient filtering
- [x] T076 [US1] Add full-text search support using MongoDB text index
- [x] T077 [US1] Register article routes in backend/src/main.py

### Implementation for User Story 1: Frontend Components

- [x] T078 [P] [US1] Create ArticleList component in frontend/src/components/ArticleList/index.tsx with pagination
- [x] T079 [P] [US1] Create ArticleDetail component in frontend/src/components/ArticleDetail/index.tsx with entity highlighting
- [x] T080 [P] [US1] Create Filters component in frontend/src/components/Filters/index.tsx with classification, sentiment, date controls
- [x] T081 [US1] Implement React Query hook useArticles in frontend/src/hooks/useArticles.ts with 5-second polling
- [x] T082 [US1] Implement React Query hook useArticleDetail in frontend/src/hooks/useArticleDetail.ts
- [x] T083 [US1] Connect Filters component to Zustand filterStore for state management
- [x] T084 [US1] Create ArticleListPage in frontend/src/pages/ArticleListPage.tsx
- [x] T085 [US1] Create ArticleDetailPage in frontend/src/pages/ArticleDetailPage.tsx
- [x] T086 [US1] Setup React Router with routes for list and detail views in frontend/src/App.tsx
- [x] T087 [US1] Style components with TailwindCSS (cards, tables, filters, responsive design)
- [x] T088 [US1] Add loading states and error handling to ArticleList and ArticleDetail components
- [x] T089 [US1] Implement entity highlighting in ArticleDetail using color-coded badges

**Checkpoint**: At this point, the web interface should display analyzed articles with working filters and detail views

---

## Phase 6: User Story 3 - Entity and Sentiment Insights (Priority: P3)

**Goal**: Evaluators can explore entity relationships and sentiment trends across articles

**Independent Test**: Access statistics dashboard and entity views to see aggregated insights

### Tests for User Story 3 (Test-First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T090 [P] [US3] Contract test for GET /api/stats endpoint in backend/tests/contract/test_stats_api.py
- [ ] T091 [P] [US3] Contract test for GET /api/entities endpoint in backend/tests/contract/test_entities_api.py
- [ ] T092 [P] [US3] Frontend component test for Stats dashboard in frontend/tests/component/Stats.test.tsx
- [ ] T093 [US3] E2E test for statistics and entity exploration in frontend/tests/e2e/insights.spec.ts

### Implementation for User Story 3: Backend API

- [ ] T094 [US3] Implement GET /api/stats with aggregation pipeline in backend/src/api/routes/stats.py
- [ ] T095 [US3] Implement GET /api/entities with entity aggregation in backend/src/api/routes/entities.py
- [ ] T096 [US3] Add entity filtering by type (company, person, product, technology)
- [ ] T097 [US3] Register stats and entities routes in backend/src/main.py

### Implementation for User Story 3: Frontend Components

- [ ] T098 [P] [US3] Create Stats dashboard component in frontend/src/components/Stats/index.tsx
- [ ] T099 [P] [US3] Create EntityList component in frontend/src/components/EntityList/index.tsx
- [ ] T100 [US3] Implement sentiment distribution visualization (chart) using recharts library
- [ ] T101 [US3] Implement classification breakdown visualization (pie/bar chart)
- [ ] T102 [US3] Implement React Query hook useStats in frontend/src/hooks/useStats.ts
- [ ] T103 [US3] Implement React Query hook useEntities in frontend/src/hooks/useEntities.ts
- [ ] T104 [US3] Create StatsPage in frontend/src/pages/StatsPage.tsx
- [ ] T105 [US3] Add Stats page route to React Router in frontend/src/App.tsx
- [ ] T106 [US3] Create entity detail view showing articles mentioning that entity
- [ ] T107 [US3] Add navigation between Stats, Entity, and Article views

**Checkpoint**: All user stories should now be independently functional with complete analytics capabilities

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

### Documentation

- [ ] T108 [P] Create README.md with quick start instructions based on quickstart.md
- [ ] T109 [P] Add inline code comments for complex scraper and analyzer logic
- [ ] T110 [P] Verify all library CLI interfaces match contracts (scraper-contract.md, analyzer-contract.md)

### Testing and Validation

- [ ] T111 Run all contract tests and verify 100% pass rate
- [ ] T112 Run all integration tests and verify pipeline health
- [ ] T113 Run E2E tests and verify all user stories work end-to-end
- [ ] T114 Validate quickstart.md by following instructions on clean system
- [ ] T115 Verify all success criteria from spec.md are met (SC-001 through SC-014)

### Performance and Optimization

- [ ] T116 [P] Verify scraping performance (20+ articles within 5 minutes)
- [ ] T117 [P] Verify analysis performance (4-8 seconds per article)
- [ ] T118 [P] Verify API query performance (< 2 seconds for 500 articles)
- [ ] T119 [P] Verify real-time updates (< 5 seconds latency)

### Security and Error Handling

- [ ] T120 [P] Verify error logging for all failure scenarios (scraper breaks, LLM unavailable, MongoDB full)
- [ ] T121 [P] Add input validation for all API endpoints
- [ ] T122 [P] Verify graceful degradation when services fail
- [ ] T123 [P] Test edge cases from spec.md (truncation, empty filters, concurrent users)

### Deployment Validation

- [ ] T124 Verify docker-compose up -d starts all services successfully
- [ ] T125 Verify first-time LLM model download completes (within 10 minutes)
- [ ] T126 Test clean restart with docker-compose down && docker-compose up -d
- [ ] T127 Verify log files are created in ./logs/ directory with JSON format
- [ ] T128 Test system runs continuously for 24 hours without crashes (SC-010)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 4 (P1 - Deployment): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2 - Backend): Can start after Foundational - No dependencies on other stories
  - User Story 1 (P1 - Frontend): Depends on User Story 2 (needs scraped data to display)
  - User Story 3 (P3 - Analytics): Depends on User Stories 1 & 2 (needs data and UI foundation)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 4 (Deployment - P1)**: Can start after Foundational - INDEPENDENT (just infrastructure)
- **User Story 2 (Backend - P2)**: Can start after Foundational - INDEPENDENT (scraping and analysis)
- **User Story 1 (Frontend - P1)**: Depends on US2 for data, but can develop with mock data in parallel
- **User Story 3 (Analytics - P3)**: Depends on US1 & US2 for data and UI patterns

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Test-First principle)
- Library models before library CLI
- Backend services before API routes
- Frontend hooks before components
- Components before pages
- Core implementation before integration

### Parallel Opportunities

**Setup Phase (All in parallel)**:
- T002, T003, T004, T005 (directory structures)
- T006, T007, T008, T009 (package initialization)
- T010, T011 (linting configuration)

**Foundational Phase**:
- T013, T014, T015 (Dockerfiles)
- T017, T018, T019 (logger utilities)
- T021, T022 (Pydantic models)
- T024, T025 (config and schemas)
- T026, T027, T028, T029, T030 (frontend infrastructure)

**User Story 4 Tests**:
- T031, T032 (contract and integration tests)

**User Story 2 Tests**:
- T038, T039, T040, T041 (contract and integration tests)

**User Story 1 Tests**:
- T067, T068, T069, T070 (contract and component tests)

**User Story 1 Frontend Components**:
- T078, T079, T080 (ArticleList, ArticleDetail, Filters)

**User Story 3 Tests**:
- T090, T091, T092 (contract and component tests)

**User Story 3 Frontend Components**:
- T098, T099 (Stats, EntityList)

**Polish Phase**:
- T108, T109, T110 (documentation)
- T116, T117, T118, T119 (performance validation)
- T120, T121, T122, T123 (security and error handling)

---

## Parallel Example: User Story 2 (Backend)

```bash
# Launch all tests for User Story 2 together (WRITE FIRST, CONFIRM FAIL):
Task: "Contract test for scraper output schema in libs/intelligence-scraper/tests/contract/test_output_schema.py"
Task: "Contract test for analyzer output schema in libs/intelligence-analyzer/tests/contract/test_analysis_schema.py"
Task: "Integration test for scraper → MongoDB pipeline in backend/tests/integration/test_scraping_pipeline.py"
Task: "Integration test for analyzer → MongoDB pipeline in backend/tests/integration/test_analysis_pipeline.py"

# After tests written and failing, launch parallel implementation:
Task: "Create BaseScraper abstract class in libs/intelligence-scraper/src/extractors/base.py"
Task: "Define ScrapedArticle Pydantic model in libs/intelligence-scraper/src/models.py"
Task: "Implement text cleaner utility in libs/intelligence-scraper/src/utils/cleaner.py"
# (Continue with scraper library tasks)

# Analyzer library can be developed in parallel by different developer:
Task: "Implement Ollama HTTP client in libs/intelligence-analyzer/src/llm/client.py"
Task: "Create structured prompt template in libs/intelligence-analyzer/src/llm/prompts.py"
Task: "Define AnalysisInput and AnalysisResult Pydantic models in libs/intelligence-analyzer/src/models.py"
# (Continue with analyzer library tasks)
```

---

## Parallel Example: User Story 1 (Frontend)

```bash
# Launch all tests for User Story 1 together (WRITE FIRST, CONFIRM FAIL):
Task: "Contract test for GET /api/articles endpoint in backend/tests/contract/test_articles_api.py"
Task: "Contract test for GET /api/articles/{id} endpoint in backend/tests/contract/test_articles_api.py"
Task: "Frontend component test for ArticleList in frontend/tests/component/ArticleList.test.tsx"
Task: "Frontend component test for ArticleDetail in frontend/tests/component/ArticleDetail.test.tsx"

# After tests written and failing, launch parallel implementation:
Task: "Create ArticleList component in frontend/src/components/ArticleList/index.tsx with pagination"
Task: "Create ArticleDetail component in frontend/src/components/ArticleDetail/index.tsx with entity highlighting"
Task: "Create Filters component in frontend/src/components/Filters/index.tsx with classification, sentiment, date controls"

# Backend API can be developed in parallel:
Task: "Implement GET /api/articles with pagination and filters in backend/src/api/routes/articles.py"
Task: "Implement GET /api/articles/{id} in backend/src/api/routes/articles.py"
```

---

## Implementation Strategy

### MVP First (Deployment + Backend + Frontend)

**Phase 1**: Setup (T001-T011)
1. Complete all setup tasks to create project structure
2. Initialize all packages and dependencies

**Phase 2**: Foundational (T012-T030) - CRITICAL BLOCKER
1. Complete Docker infrastructure (T012-T016)
2. Complete logging infrastructure (T017-T019)
3. Complete MongoDB models (T020-T022)
4. Complete backend API infrastructure (T023-T025)
5. Complete frontend infrastructure (T026-T030)
6. **CHECKPOINT**: Foundation must be 100% complete before proceeding

**Phase 3**: User Story 4 - Deployment (T031-T037)
1. Write and confirm tests fail (T031-T032)
2. Implement health checks (T033-T037)
3. **VALIDATE**: `docker-compose up -d` starts all services successfully
4. **DEPLOY/DEMO**: Infrastructure MVP ready

**Phase 4**: User Story 2 - Backend (T038-T066)
1. Write and confirm tests fail (T038-T042)
2. Implement scraper library (T043-T050)
3. Implement analyzer library (T051-T059)
4. Implement backend orchestration (T060-T066)
5. **VALIDATE**: Articles automatically scraped and analyzed on startup
6. **DEPLOY/DEMO**: Backend MVP ready (data pipeline working)

**Phase 5**: User Story 1 - Frontend (T067-T089)
1. Write and confirm tests fail (T067-T071)
2. Implement backend API (T072-T077)
3. Implement frontend components (T078-T089)
4. **VALIDATE**: Web interface displays articles with filters and detail views
5. **DEPLOY/DEMO**: Full MVP ready (end-to-end system working)

**STOP and VALIDATE**: Test entire system end-to-end. This is the minimum viable product.

### Incremental Delivery

After MVP is validated:

**Phase 6**: User Story 3 - Analytics (T090-T107)
1. Write and confirm tests fail (T090-T093)
2. Implement backend aggregation APIs (T094-T097)
3. Implement frontend analytics views (T098-T107)
4. **VALIDATE**: Statistics and entity insights work independently
5. **DEPLOY/DEMO**: Enhanced analytics added

**Phase 7**: Polish (T108-T128)
1. Complete documentation (T108-T110)
2. Run all validation tests (T111-T115)
3. Verify performance benchmarks (T116-T119)
4. Verify security and error handling (T120-T123)
5. Validate deployment (T124-T128)
6. **DEPLOY/DEMO**: Production-ready system

### Parallel Team Strategy

With 3 developers available:

**Week 1**: All developers work together on Setup + Foundational (T001-T030)
- Critical that foundation is solid
- Pair programming recommended for complex infrastructure

**Week 2-3**: Parallel user story development after foundation complete
- Developer A: User Story 4 (Deployment) → User Story 2 (Backend scraper library)
- Developer B: User Story 2 (Backend analyzer library and orchestration)
- Developer C: User Story 1 (Frontend after US2 has data) or prepare tests

**Week 4**: Integration and User Story 3
- Integrate all user stories
- Developer A/B: User Story 3 (Analytics backend)
- Developer C: User Story 3 (Analytics frontend)

**Week 5**: Polish and validation (all developers)

---

## Task Summary

**Total Tasks**: 128
- **Phase 1 (Setup)**: 11 tasks
- **Phase 2 (Foundational)**: 19 tasks (CRITICAL BLOCKER)
- **Phase 3 (US4 - Deployment)**: 7 tasks
- **Phase 4 (US2 - Backend)**: 29 tasks
- **Phase 5 (US1 - Frontend)**: 23 tasks
- **Phase 6 (US3 - Analytics)**: 18 tasks
- **Phase 7 (Polish)**: 21 tasks

**Parallelizable Tasks**: 47 tasks marked with [P]

**User Story Breakdown**:
- User Story 4 (Deployment): 7 tasks
- User Story 2 (Backend): 29 tasks
- User Story 1 (Frontend): 23 tasks
- User Story 3 (Analytics): 18 tasks

**Test Tasks**: 18 test tasks (TDD workflow enforced)
- 12 contract tests
- 4 integration tests
- 2 E2E tests

**Independent Test Criteria**:
- **US4**: All containers start and report healthy status
- **US2**: Articles automatically scraped and analyzed on startup
- **US1**: Web interface displays articles with working filters
- **US3**: Statistics dashboard shows aggregated insights

**Suggested MVP Scope**: User Stories 4 + 2 + 1 (Deployment + Backend + Frontend) = 59 tasks

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label (US1, US2, US3, US4) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Test-First Workflow**: Write tests first, confirm they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance: Library-first (scraper and analyzer are standalone), Test-first (all contracts defined), Observability (structured JSON logging throughout)

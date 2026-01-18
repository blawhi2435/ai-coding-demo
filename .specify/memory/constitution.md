<!--
Sync Impact Report
==================
Version change: [Initial] → 1.0.0
Modified principles: Initial constitution creation with 3 core principles
Added sections: Core Principles (Library-First, Test-First, Observability), Development Standards, Governance
Removed sections: N/A (initial creation)
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns with principles
  ✅ .specify/templates/spec-template.md - Requirements section supports principle validation
  ✅ .specify/templates/tasks-template.md - Task categorization supports TDD workflow
Follow-up TODOs: None
-->

# Vide-Coding Constitution

## Core Principles

### I. Library-First

Every feature MUST start as a standalone library with the following NON-NEGOTIABLE requirements:

- **Self-contained**: Libraries must be independently testable and deployable without external service dependencies during testing
- **CLI Interface**: Every library MUST expose its functionality via a command-line interface using text-based protocols (stdin/args → stdout, errors → stderr)
- **Clear Purpose**: Each library must solve a specific, well-defined problem. Organizational-only libraries (created solely for code grouping without functional purpose) are PROHIBITED
- **Documentation**: Libraries must include usage examples and API contracts

**Rationale**: The library-first approach ensures modularity, reusability, and testability. CLI interfaces provide debuggability and enable composition. This principle prevents monolithic architectures and promotes clear separation of concerns.

### II. Test-First (NON-NEGOTIABLE)

Test-Driven Development is MANDATORY for all implementation work:

- **Red-Green-Refactor Cycle**: Tests MUST be written first, reviewed and approved, confirmed to fail, THEN implementation begins
- **No exceptions**: This principle applies to all features, bug fixes, and refactoring work
- **Contract Tests**: Required for all library interfaces and external API boundaries
- **Integration Tests**: Required when new libraries interact with existing components or when contracts change

**Rationale**: TDD ensures code correctness from the start, produces executable specifications, and prevents regression. The strict enforcement eliminates ambiguity and ensures consistent quality across the codebase.

### III. Observability

All components MUST be observable and debuggable:

- **Text I/O Protocol**: Standard streams (stdin/stdout/stderr) ensure inspectability without specialized tools
- **Structured Logging**: JSON-formatted logs with consistent fields (timestamp, level, component, message, context)
- **Traceability**: Every operation must log sufficient context to reconstruct the execution path
- **Error Transparency**: Errors must be logged with full context (stack traces, input state, environment) before propagating

**Rationale**: Text-based protocols and structured logging enable debugging in any environment without specialized tooling. This principle ensures production issues can be diagnosed quickly and completely.

## Development Standards

### Simplicity Requirements

- **YAGNI Enforcement**: Features must address current, validated requirements. Speculative functionality is PROHIBITED
- **Minimal Abstractions**: Introduce abstractions only when complexity justifies them (DRY violation appears ≥3 times)
- **Explicit Over Implicit**: Configuration, dependencies, and behavior must be explicit and discoverable

### Versioning & Breaking Changes

- **Semantic Versioning**: MAJOR.MINOR.PATCH format strictly enforced
  - MAJOR: Breaking changes to public interfaces
  - MINOR: Backward-compatible functionality additions
  - PATCH: Backward-compatible bug fixes
- **Deprecation Policy**: Breaking changes require one MINOR version deprecation warning before removal in next MAJOR

### Security & Performance

- **Input Validation**: All external inputs (user data, API calls, file reads) MUST be validated at system boundaries
- **Secrets Management**: Credentials and secrets MUST NOT be committed to version control
- **Performance Baselines**: Response time targets defined per-component (e.g., API endpoints <200ms p95, batch processing throughput documented)

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Technical review by maintainers and stakeholders
3. **Version Increment**: Follow semantic versioning rules based on change scope
4. **Migration Plan**: For breaking changes, provide migration guide and timeline
5. **Propagation**: Update all dependent templates and documentation

### Compliance & Enforcement

- **Review Gate**: All pull requests MUST verify compliance with constitutional principles
- **Complexity Justification**: Any violation of Simplicity Requirements must be explicitly justified in implementation plan's "Complexity Tracking" section
- **Constitution Authority**: Constitution supersedes all other practices, guidelines, or conventions

### Roles & Responsibilities

- **Maintainers**: Enforce constitutional compliance during code review
- **Contributors**: Validate work against principles before submission
- **Reviewers**: Verify constitutional alignment as first review step

**Version**: 1.0.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17

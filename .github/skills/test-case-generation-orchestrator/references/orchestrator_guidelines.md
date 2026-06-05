# Orchestrator Guidelines

This document describes how the Test Case Generation Orchestrator coordinates the pipeline.

## Entry Inputs

- User Story
- Acceptance Criteria
- Validation Rules
- Optional OpenAPI Specification

## Pipeline Behavior

- The orchestrator invokes Requirement Analyzer first to extract structured requirements.
- If an OpenAPI specification is present, it also invokes API Contract Analyzer.
- It then invokes Test Design Generator, optionally including API contracts.
- Test Data Generator receives generated tests, validation rules, and any API contracts.
- Gherkin Generator converts tests and test data into feature scenarios.
- Playwright Generator produces Playwright skeletons from test cases, fixtures, and API contracts.
- Traceability Generator links requirements, tests, and artifacts.
- Coverage Analyzer calculates coverage and reports gaps.

## Optional OpenAPI Handling

- If OpenAPI is absent, skip API Contract Analyzer.
- If API contracts are unavailable, Test Design Generator must skip contract tests.
- The remaining workflow continues using Requirement Analyzer outputs only.

## Deterministic Orchestration

- The orchestrator must preserve deterministic IDs from upstream skills.
- It must produce consistent artifact names and outputs for identical inputs.
- It should preserve traceability references across all generated outputs.

## Error Handling

- Invalid OpenAPI input should be reported, not fatal.
- Missing acceptance criteria should be surfaced as a gap.
- Incomplete data should trigger gap reports in downstream artifacts.

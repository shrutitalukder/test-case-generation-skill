# Test Case Generation Orchestrator

## Metadata

- Name: Test Case Generation Orchestrator
- Version: 1.0
- Category: Test Case Generation
- Phase: Orchestration

## Purpose

Coordinate all testing skills to generate test cases, fixtures, Gherkin, Playwright artifacts, traceability, and coverage reports.

## Inputs

- User Story
- Acceptance Criteria
- Validation Rules
- Optional OpenAPI Specification

## Outputs

- Test Cases
- Fixtures
- Gherkin
- Playwright
- Traceability Matrix
- Coverage Report

## Workflow

1. Requirement Analyzer
2. API Contract Analyzer (optional)
3. Test Design Generator
4. Test Data Generator
5. Gherkin Generator
6. Playwright Generator
7. Traceability Generator
8. Coverage Analyzer

## Processing Rules

- If OpenAPI is absent, skip API Contract Analyzer.
- If OpenAPI is absent, skip contract test generation in Test Design Generator.
- Continue remaining flow regardless of optional API input.
- Preserve deterministic outputs and traceability throughout the workflow.

## Anti-Hallucination Rules

- Do not generate tests or artifacts without evidence from the source inputs.
- Do not create API contract content if the OpenAPI specification is missing.

## Error Handling

- Flag missing acceptance criteria.
- Flag incomplete requirements.
- Flag invalid OpenAPI documents without stopping the remaining workflow.

## Success Criteria

- All acceptance criteria are converted into test cases.
- Fixtures are generated for all supported test cases.
- Gherkin and Playwright artifacts are produced for valid test cases.
- Traceability matrix is created.
- Coverage report identifies gaps and coverage metrics.

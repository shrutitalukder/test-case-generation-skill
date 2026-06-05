# Playwright Generator

## Metadata

- Name: Playwright Test Generator
- Version: 1.0
- Category: Test Case Generation
- Phase: Playwright Generation

## Purpose

Generate Playwright TypeScript automation skeletons.

## Inputs

- Test Cases
- Test Fixtures
- API Contracts

## Outputs

- Playwright Test Files

## Responsibilities

1. Generate Playwright test blocks.
2. Generate API requests.
3. Generate assertions.
4. Link fixtures.
5. Preserve traceability.

## Processing Rules

- One test per test case.
- Generate TODO markers for manual enhancement.
- Generate deterministic file names.

## Anti-Hallucination Rules

- Never invent endpoints.
- Never invent assertions.
- Never invent payload fields.

## Error Handling

- Generate placeholders for missing information.
- Log gaps.

## Success Criteria

- TypeScript-valid output.
- Traceable test files.
- Deterministic generation.

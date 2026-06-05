# Playwright Guidelines

This document provides guidelines for generating Playwright automation skeletons from test cases, fixtures, and API definitions.

## Test Structure

- Use one test block per test case.
- Keep test titles aligned with the source test case title.
- Use tags or comments to preserve traceability.

## API Requests

- Generate API requests when endpoints are available.
- Use request fixtures for request payloads.
- Preserve HTTP methods and status code expectations.

## Assertions

- Generate assertions only for explicitly available expected results.
- Use TODO markers for assertions that require manual refinement.
- Avoid adding assertions for data not present in source input.

## Fixtures

- Link fixtures to generated tests using fixture identifiers.
- Preserve positive, negative, and boundary data mappings.

## Traceability

- Include requirement and test case references in comments.
- Generate deterministic file names and test identifiers.

## Error Handling

- Create placeholder tests when information is missing.
- Emit comments or logs for gaps and incomplete data.

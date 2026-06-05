# Traceability Patterns

This document describes patterns for generating traceability matrices between requirements, tests, and artifacts.

## Requirement-to-Test Linkage

- Map each requirement ID to one or more test case IDs.
- Preserve source IDs from requirements and generated test cases.
- Avoid inventing links not present in the source artifacts.

## Test-to-Artifact Linkage

- Link test cases to generated artifacts such as feature files, Playwright tests, and fixtures.
- Use deterministic artifact identifiers when available.
- Include artifact types in the matrix for clarity.

## Coverage Detection

- Detect requirements with no linked test coverage.
- Detect test cases with no requirement mapping.
- Identify orphaned tests and missing requirements.

## Matrix Structure

- Represent mappings in a tabular model.
- Include requirement ID, test case ID, artifact reference, and status.
- Preserve traceability metadata for audit purposes.

## Error Handling

- Flag missing or incomplete mapping data.
- Report uncovered requirements and orphaned tests.

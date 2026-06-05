# Test Design Generator

## Metadata

- Name: Test Design Generator
- Version: 1.0
- Category: Test Case Generation
- Phase: Test Design

## Purpose

Generate structured test cases from requirements, acceptance criteria, validation rules, and API contracts.

## Inputs

- Requirement Model
- Validation Rules
- Optional API Contracts

## Outputs

- Positive Test Cases
- Negative Test Cases
- Boundary Test Cases
- Validation Test Cases
- Contract Test Cases

## Responsibilities

1. Generate happy-path tests.
2. Generate negative tests.
3. Generate boundary tests.
4. Generate validation tests.
5. Generate API contract tests.
6. Assign traceability links.
7. Generate deterministic test IDs.

## Processing Rules

- At least one positive test per acceptance criterion.
- At least one negative test per validation rule.
- Generate boundary tests for min/max constraints.
- Generate contract tests only when API contracts exist.

## Output Contract

- Test Cases
  - positive_tests
  - negative_tests
  - boundary_tests
  - validation_tests
  - contract_tests
  - traceability_links

## Anti-Hallucination Rules

- Never invent business rules.
- Never invent validations.
- Never invent API responses.

## Error Handling

- Generate stub tests when requirements are incomplete.
- Create gaps report for missing validations.

## Success Criteria

- 100% acceptance criteria coverage.
- Deterministic test generation.
- Complete traceability.

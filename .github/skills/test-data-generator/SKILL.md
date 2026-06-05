# Test Data Generator

## Metadata

- Name: Test Data Generator
- Version: 1.0
- Category: Test Case Generation
- Phase: Test Data Generation

## Purpose

Generate deterministic mock data and payloads for generated test cases.

## Inputs

- Test Cases
- Validation Rules
- API Contracts

## Outputs

- Positive Fixtures
- Negative Fixtures
- Boundary Fixtures
- API Payload Examples

## Responsibilities

1. Generate valid data.
2. Generate invalid data.
3. Generate boundary values.
4. Generate request payloads.
5. Generate response payloads.

## Processing Rules

- Use constraints to generate values.
- Use deterministic seed generation.
- Generate repeatable datasets.

## Anti-Hallucination Rules

- Never invent schema fields.
- Never invent enum values.
- Never invent response attributes.

## Error Handling

- Report missing constraints.
- Report incomplete schemas.

## Success Criteria

- Fixtures align with validations.
- Deterministic output.
- Coverage of all constraints.

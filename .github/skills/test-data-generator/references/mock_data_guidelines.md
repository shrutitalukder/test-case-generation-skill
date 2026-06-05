# Mock Data Guidelines

This document provides guidelines for generating deterministic and valid mock data from test cases, validation rules, and API schemas.

## Schema Fields

- Generate values only for fields defined in the schema.
- Preserve required field definitions and field types.
- Do not create fields that are not explicitly present.

## Enum Values

- Use only values listed in `enum` definitions.
- If enum values are absent, use values consistent with type constraints.

## Request and Response Payloads

- Generate request payload examples based on API schemas and required fields.
- Generate response payload examples aligned with response schemas.
- Preserve schema structure and nested object definitions.

## Deterministic Data

- Use deterministic seed generation to produce repeatable fixtures.
- Ensure data remains consistent across runs for the same input.

## Boundary Values

- Derive boundary fixtures from min/max and length constraints.
- Include both valid boundary values and invalid boundary cases.

## Error Handling

- Report missing constraints or schema details.
- Flag incomplete schemas that prevent reliable fixture generation.

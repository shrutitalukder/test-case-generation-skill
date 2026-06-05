# Gherkin Generator

## Metadata

- Name: Gherkin Scenario Generator
- Version: 1.0
- Category: Test Case Generation
- Phase: Gherkin Generation

## Purpose

Convert generated test cases into executable Gherkin scenarios.

## Inputs

- Test Cases
- Test Data

## Outputs

- Feature Files
- Scenarios
- Given/When/Then Steps

## Responsibilities

1. Create feature files.
2. Create scenarios.
3. Create Given steps.
4. Create When steps.
5. Create Then steps.

## Processing Rules

- One scenario per test case.
- Preserve traceability IDs.
- Generate tags by test type.

## Anti-Hallucination Rules

- Do not invent steps.
- Use only available test information.

## Error Handling

- Flag missing actions.
- Flag incomplete assertions.

## Success Criteria

- Valid Gherkin syntax.
- Full scenario coverage.
- Traceability preserved.

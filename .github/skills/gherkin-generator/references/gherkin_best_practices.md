# Gherkin Best Practices

This document describes best practices for generating clear, maintainable Gherkin scenarios.

## Feature Files

- Group related scenarios under a single `Feature`.
- Use descriptive feature names that reflect the business objective.
- Preserve traceability metadata as comments or tags.

## Scenarios

- Create one scenario per test case.
- Keep each scenario focused on a single behavior.
- Use tags to represent test type and traceability.

## Steps

- `Given` steps should establish context and preconditions.
- `When` steps should describe a single action or event.
- `Then` steps should assert expected outcomes.

## Anti-Hallucination

- Do not invent steps that are not supported by the test case.
- Use only available test information to generate step definitions.

## Error Handling

- Flag missing action descriptions as incomplete scenarios.
- Flag assertions with missing expected outcomes.

## Syntax

- Ensure valid Gherkin formatting.
- Indent steps consistently.
- Separate scenarios with blank lines.

# Coverage Rules

This document provides rules and guidelines for measuring test coverage and identifying gaps.

## Coverage Metrics

- Measure acceptance criteria coverage.
- Measure validation coverage.
- Measure API contract coverage.
- Use evidence from test cases and artifacts.

## Coverage Calculation

- Calculate coverage percentages based on total items and covered items.
- Report coverage as a percentage and absolute counts.
- Preserve traceability for each coverage item.

## Gap Identification

- List uncovered requirements.
- List uncovered validations.
- List uncovered API contracts or endpoints.

## Anti-Hallucination

- Only mark items as covered when there is explicit test evidence.
- Do not infer coverage from unrelated artifacts.

## Error Handling

- Flag incomplete inputs affecting coverage calculations.
- Report missing requirement, validation, or API coverage data.

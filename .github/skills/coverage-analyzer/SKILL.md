# Coverage Analyzer

## Metadata

- Name: Coverage Analyzer
- Version: 1.0
- Category: Test Case Generation
- Phase: Coverage Analysis

## Purpose

Measure testing coverage and identify gaps.

## Inputs

- Requirement Model
- Validation Rules
- API Contracts
- Test Cases

## Outputs

- Coverage Report
- Gap Report

## Responsibilities

1. Measure AC coverage.
2. Measure validation coverage.
3. Measure API coverage.
4. Detect uncovered items.

## Processing Rules

- Calculate percentages.
- List uncovered requirements.
- List uncovered validations.

## Anti-Hallucination Rules

- Never report coverage without evidence.

## Error Handling

- Flag incomplete coverage inputs.

## Success Criteria

- Accurate coverage calculations.
- Gap identification.
- Traceable reporting.

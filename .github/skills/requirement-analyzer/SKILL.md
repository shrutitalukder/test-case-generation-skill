# Requirement Analyzer

## Metadata

- Name: Requirement Analyzer
- Version: 1.0
- Category: Test Case Generation
- Phase: Requirements Analysis

## Purpose

Extract structured testing requirements from User Stories and Acceptance Criteria.

## Inputs

- User Stories
- Acceptance Criteria
- Business Requirements

## Outputs

- Requirement Model
  - requirements
  - actors
  - business_rules
  - preconditions
  - postconditions
  - validation_rules
  - normalized_requirement_ids

## Responsibilities

1. Parse user stories.
2. Extract actors.
3. Extract acceptance criteria.
4. Detect business rules.
5. Detect preconditions.
6. Detect postconditions.
7. Generate normalized requirement model.

## Processing Rules

- Preserve original requirement text.
- Generate deterministic IDs when IDs are missing.
- Support markdown input.

## Anti-Hallucination Rules

- Never invent requirements.
- Never invent acceptance criteria.
- Only extract information explicitly present in the source.

## Error Handling

- Missing acceptance criteria should be flagged.
- Ambiguous requirements should be reported.
- Generate gaps report when information is incomplete.

## Examples

### Input

```markdown
# User Story

As a registered shopper,
I want to save my payment card information,
so that I can checkout faster on future orders.

## Acceptance Criteria

- Given I am logged in, when I enter a valid card and save it, then the card is stored securely.
- Given I have no saved payment methods, when I attempt to checkout, then I am prompted to add a payment card.
- The saved card must expire after 3 years and require CVV entry for verification.

## Business Requirements

- Payment card data must be encrypted at rest.
- The system must support card expiration validation.
```

### Expected Output

```json
{
  "requirement_model": {
    "actors": [
      "registered shopper"
    ],
    "requirements": [
      {
        "id": "REQ-001",
        "text": "Given I am logged in, when I enter a valid card and save it, then the card is stored securely.",
        "type": "acceptance_criteria"
      },
      {
        "id": "REQ-002",
        "text": "Given I have no saved payment methods, when I attempt to checkout, then I am prompted to add a payment card.",
        "type": "acceptance_criteria"
      },
      {
        "id": "REQ-003",
        "text": "The saved card must expire after 3 years and require CVV entry for verification.",
        "type": "acceptance_criteria"
      }
    ],
    "business_rules": [
      "Payment card data must be encrypted at rest.",
      "The saved card must expire after 3 years.",
      "Card verification must require CVV entry."
    ],
    "preconditions": [
      "User is logged in.",
      "User has no saved payment methods."
    ],
    "postconditions": [
      "Payment card is stored securely.",
      "User is prompted to add a payment card when no saved payment methods exist."
    ],
    "validation_rules": [
      "Card expiration validation is required.",
      "Payment card data encryption at rest is required."
    ],
    "normalized_requirement_ids": [
      "REQ-001",
      "REQ-002",
      "REQ-003"
    ]
  }
}
```

## Success Criteria

- All acceptance criteria extracted.
- All actors identified.
- Deterministic output generation.
- Traceability preserved.

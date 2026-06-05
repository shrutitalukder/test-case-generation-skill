# API Contract Analyzer

## Metadata

- Name: API Contract Analyzer
- Version: 1.0
- Category: Test Case Generation
- Phase: API Analysis

## Purpose

Extract API testing requirements from OpenAPI and Swagger specifications.

## Inputs

- OpenAPI 3.x
- Swagger 2.0
- JSON Schema

## Outputs

- API Contracts
  - endpoints
  - methods
  - request_schemas
  - response_schemas
  - status_codes
  - field_constraints
  - required_fields
  - validation_rules

## Responsibilities

1. Parse OpenAPI specifications.
2. Extract endpoints and operations.
3. Extract request payload schemas.
4. Extract response payload schemas.
5. Extract validation constraints.
6. Extract status codes.
7. Normalize API contract information into a canonical model.

## Processing Rules

- Support YAML and JSON specifications.
- Resolve schema references where possible.
- Preserve source endpoint definitions.
- Generate deterministic output.

## Anti-Hallucination Rules

- Never invent endpoints.
- Never invent request fields.
- Never invent response fields.
- Only extract information explicitly present in the API specification.

## Error Handling

- Flag invalid OpenAPI documents.
- Flag missing schemas.
- Flag incomplete endpoint definitions.
- Generate gaps report for missing contract information.

## Examples

### Input

```yaml
openapi: 3.0.1
info:
  title: Payment API
  version: 1.0.0
paths:
  /payments:
    post:
      summary: Create a payment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - amount
                - currency
              properties:
                amount:
                  type: number
                currency:
                  type: string
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  status:
                    type: string
```

### Expected Output

```json
{
  "api_contracts": [
    {
      "path": "/payments",
      "method": "post",
      "operationId": null,
      "summary": "Create a payment",
      "request_schema": {
        "type": "object",
        "required": ["amount", "currency"],
        "properties": {
          "amount": {"type": "number"},
          "currency": {"type": "string"}
        }
      },
      "response_schemas": {
        "201": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "status": {"type": "string"}
          }
        }
      },
      "status_codes": ["201"],
      "field_constraints": [
        "amount is a number",
        "currency is a string"
      ],
      "required_fields": ["amount", "currency"]
    }
  ],
  "validation_rules": [
    "Request body is required for POST /payments."
  ]
}
```

## Success Criteria

- All endpoints extracted.
- All request schemas extracted.
- All response schemas extracted.
- All validation constraints extracted.
- Deterministic output generation.
- Traceability preserved.

## Additional Rule

- OpenAPI input is optional in the overall platform.
- If OpenAPI is not provided, this skill should be skipped.
- Downstream generators should continue using Requirement Analyzer outputs only.

# OpenAPI Guidelines

This document provides guidelines for extracting API contract requirements from OpenAPI and Swagger definitions.

## Specification Support

- OpenAPI 3.x
- Swagger 2.0
- JSON Schema in request and response payloads

## Endpoint Extraction

- Extract every path and operation defined in `paths`.
- Preserve HTTP methods exactly as specified.
- Record operation summaries and operationIds when present.

## Request Schema Extraction

- Extract requestBody schemas for OpenAPI 3.x.
- Extract `parameters` with `in: body` or `in: formData` for Swagger 2.0.
- Include required fields and property definitions.
- Resolve `$ref` references when present.

## Response Schema Extraction

- Extract response objects by status code.
- Preserve response content type when available.
- Extract schema details from `content` or `schema`.

## Validation Constraints

- Capture field constraints such as `type`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`.
- Capture required field lists.
- Capture `enum` values and format restrictions.

## Status Code Handling

- Extract all explicit response status codes.
- Include default responses when present.
- Preserve response descriptions.

## Error Handling

- Flag invalid or malformed OpenAPI documents.
- Flag missing request or response schemas.
- Flag endpoints with incomplete definitions.
- Generate a gaps report when contract information is incomplete.

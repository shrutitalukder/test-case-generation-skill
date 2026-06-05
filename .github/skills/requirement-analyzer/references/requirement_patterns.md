# Requirement Extraction Patterns

This document provides common patterns for extracting requirements from user stories and acceptance criteria.

## User Story Patterns

- "As a <actor>, I want <goal>, so that <benefit>."
- "As an <actor>, I want to <action> to <result>."
- "As a <role>, I need <capability> so that <outcome>."

## Acceptance Criteria Patterns

- "Given <precondition>, when <action>, then <outcome>."
- "When <action>, then <outcome>."
- "The system must <requirement>."
- "<Requirement> must be <constraint>."

## Business Rule Patterns

- "The system must <behavior>."
- "<Data> must be <constraint>."
- "<Object> must be encrypted/validated/audited."
- "<Action> is required when <condition>."

## Preconditions and Postconditions

- Preconditions are often introduced by "Given" clauses.
- Postconditions are often introduced by "Then" clauses.
- Look for implied state such as "User is logged in" or "User has no saved payment methods."

## Validation Constraints

- "must expire after"
- "must require"
- "must be encrypted"
- "must validate"

## Normalized IDs

- Use deterministic numbering such as `REQ-001`, `REQ-002`, `REQ-003`.
- If IDs are present in source text, preserve them.
- If IDs are missing, generate using text fingerprinting or sequential assignment.

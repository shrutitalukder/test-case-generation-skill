# Speckit Test Case Generation Prototype

This Phase 1 prototype converts requirements and API contracts into:
- intermediate test case models (`JSON`)
- traceability artifacts
- Gherkin scenarios
- Playwright skeletons
- a deterministic manifest and gaps report

Supported inputs:
- Markdown user stories / acceptance criteria
- OpenAPI 3 YAML/JSON
- validation rules YAML

Usage
1. Run the generator:
```bash
python run_generation.py
```
2. Inspect generated artifacts in `output/<timestamp>/`

Notes
- This implementation is intentionally file-based and minimal.
- It prioritizes `Gherkin` and `Playwright` outputs.
- Missing or ambiguous requirements are recorded in `gaps.json`.

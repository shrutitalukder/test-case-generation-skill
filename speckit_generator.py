import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

GENERATOR_VERSION = "0.1.0"


def _strip_quotes(text: str) -> str:
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    value = _strip_quotes(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() == "null":
        return None
    if re.match(r"^-?[0-9]+$", value):
        return int(value)
    if re.match(r"^-?[0-9]+\.[0-9]+$", value):
        return float(value)
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
        return [_parse_scalar(item) for item in items]
    return value


def _build_container_stack(lines: List[str]) -> Dict[str, Any]:
    root: Any = {}
    stack: List[tuple[int, Any, Any]] = [(-1, root, None)]
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.lstrip(" ")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            item_text = line[2:]
            if isinstance(parent, dict) and not parent:
                this_indent, this_container, this_key = stack[-1]
                if this_key is not None and len(stack) >= 2 and isinstance(stack[-2][1], dict):
                    container = stack[-2][1]
                    new_list: list[Any] = []
                    container[this_key] = new_list
                    stack[-1] = (this_indent, new_list, this_key)
                    parent = new_list
            if isinstance(parent, list):
                if ":" in item_text and not item_text.strip().startswith("{"):
                    key, _, rest = item_text.partition(":")
                    stripped_key = _strip_quotes(key.strip())
                    item = {stripped_key: _parse_scalar(rest)} if rest.strip() else {stripped_key: {}}
                    parent.append(item)
                    if rest.strip() == "":
                        stack.append((indent + 2, item, stripped_key))
                else:
                    parent.append(_parse_scalar(item_text))
            continue
        key, sep, value = line.partition(":")
        if sep != ":":
            continue
        key = _strip_quotes(key.strip())
        if value.strip() == "":
            node: Any = {}
        else:
            node = _parse_scalar(value)
        if isinstance(parent, dict):
            parent[key] = node
        elif isinstance(parent, list) and parent and isinstance(parent[-1], dict):
            parent[-1][key] = node
        if isinstance(node, dict):
            stack.append((indent, node, key))
    return root


def load_yaml_or_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _build_container_stack(text.splitlines())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _build_container_stack(text.splitlines())


def checksum(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def canonicalize(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def make_id(prefix: str, text: str) -> str:
    return f"{prefix}-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:8].upper()}"


def parse_markdown(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    story = {
        "source": str(path),
        "actor": None,
        "description": text.strip(),
        "acceptance_criteria": [],
        "business_rules": [],
        "preconditions": [],
        "postconditions": [],
    }
    in_ac = False
    for line in lines:
        actor_match = re.match(r"\s*As a ([^,\n]+)", line, re.IGNORECASE)
        if actor_match and not story["actor"]:
            story["actor"] = actor_match.group(1).strip()
        if re.match(r"\s*#{1,6}\s*Acceptance Criteria", line, re.IGNORECASE):
            in_ac = True
            continue
        if in_ac and re.match(r"\s*#{1,6}\s*", line):
            break
        if in_ac:
            item_match = re.match(r"\s*[-*+]\s*(.+)", line)
            if item_match:
                story["acceptance_criteria"].append(item_match.group(1).strip())
                continue
        if re.search(r"\bmust\b|\bshould\b|\bonly\b|\brequires\b", line, re.IGNORECASE):
            story["business_rules"].append(line.strip())
        if re.search(r"\bGiven\b|\bwhen\b|\bif\b", line, re.IGNORECASE):
            story["preconditions"].append(line.strip())
        if re.search(r"\bThen\b|\bshould\b|\bresult\b|\breturns\b", line, re.IGNORECASE):
            story["postconditions"].append(line.strip())
    return story


def parse_openapi(path: Path) -> Dict[str, Any]:
    data = load_yaml_or_json(path)
    spec = {
        "source": str(path),
        "title": str(data.get("info", {}).get("title", path.name)),
        "endpoints": [],
    }
    paths = data.get("paths", {}) or {}
    for raw_path, methods in paths.items():
        for method, op in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            endpoint = {
                "path": raw_path,
                "method": method.upper(),
                "summary": op.get("summary", ""),
                "description": op.get("description", ""),
                "request": None,
                "responses": [],
            }
            request_body = op.get("requestBody") or {}
            if request_body:
                content = request_body.get("content", {})
                schema = _find_schema_in_content(content)
                endpoint["request"] = {
                    "required": request_body.get("required", False),
                    "schema": schema,
                }
            for status, response in (op.get("responses") or {}).items():
                schema = _find_schema_in_content((response or {}).get("content", {}))
                endpoint["responses"].append({
                    "status": str(status),
                    "description": (response or {}).get("description", ""),
                    "schema": schema,
                })
            spec["endpoints"].append(endpoint)
    return spec


def _find_schema_in_content(content: Dict[str, Any]) -> Any:
    if not content:
        return None
    for media_type in ["application/json", "application/*", "*/*"]:
        if media_type in content:
            return content[media_type].get("schema")
    first = next(iter(content.values()), {})
    return first.get("schema")


def parse_validation_rules(path: Path) -> Dict[str, Any]:
    data = load_yaml_or_json(path)
    rules = data.get("validation_rules") if isinstance(data, dict) else []
    return {
        "source": str(path),
        "rules": rules or [],
    }


def extract_constraints_from_schema(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(schema, dict):
        return []
    props = schema.get("properties") or {}
    constraints = []
    for name, detail in props.items():
        constraint = {"field": name, "type": detail.get("type"), "rules": {}}
        for key in ["format", "minLength", "maxLength", "minimum", "maximum", "enum", "pattern", "required"]:
            if key in detail:
                constraint["rules"][key] = detail[key]
        if constraint["rules"]:
            constraints.append(constraint)
    return constraints


def build_requirements(story: Dict[str, Any]) -> List[Dict[str, Any]]:
    requirements = []
    for raw in story.get("acceptance_criteria", []):
        match = re.match(r"^(AC-[0-9]+):?\s*(.+)$", raw, re.IGNORECASE)
        if match:
            requirement_id = match.group(1).upper()
            description = match.group(2).strip()
        else:
            requirement_id = make_id("REQ", raw)
            description = raw
        requirements.append({
            "id": requirement_id,
            "text": description,
            "source": story["source"],
            "actor": story.get("actor"),
            "business_rules": story.get("business_rules", []),
            "preconditions": story.get("preconditions", []),
            "postconditions": story.get("postconditions", []),
            "type": "acceptance",
        })
    if not requirements:
        requirements.append({
            "id": make_id("REQ", story.get("description", "missing-ac")),
            "text": "Missing acceptance criteria",
            "source": story["source"],
            "actor": story.get("actor"),
            "business_rules": story.get("business_rules", []),
            "preconditions": story.get("preconditions", []),
            "postconditions": story.get("postconditions", []),
            "type": "acceptance",
        })
    return requirements


def generate_test_cases(requirements: List[Dict[str, Any]], api_spec: Dict[str, Any], validations: Dict[str, Any]) -> List[Dict[str, Any]]:
    test_cases = []
    rule_map = {r["field"]: r for r in validations.get("rules", []) if isinstance(r, dict)}
    endpoint = api_spec["endpoints"][0] if api_spec["endpoints"] else None

    def add_case(case: Dict[str, Any]):
        test_cases.append(case)

    for index, req in enumerate(requirements, start=1):
        add_case({
            "id": f"TC-{req['id']}-POS",
            "sourceIds": [req["id"]],
            "description": f"Positive test for '{req['text']}'",
            "intent": "positive",
            "type": "functional",
            "requestExample": _build_positive_example(endpoint, rule_map),
            "expectedStatus": endpoint_response_status(endpoint, positive=True),
            "rationale": f"Validates acceptance criterion '{req['text']}'.",
            "endpoint": endpoint,
        })
        add_case({
            "id": f"TC-{req['id']}-NEG",
            "sourceIds": [req["id"]],
            "description": f"Negative validation test for '{req['text']}'",
            "intent": "negative",
            "type": "validation",
            "requestExample": _build_invalid_example(endpoint, rule_map),
            "expectedStatus": 400,
            "rationale": f"Exercises invalid field or missing required data for '{req['text']}'.",
            "endpoint": endpoint,
        })
        add_case({
            "id": f"TC-{req['id']}-BOUNDARY",
            "sourceIds": [req["id"]],
            "description": f"Boundary test for '{req['text']}'",
            "intent": "boundary",
            "type": "boundary",
            "requestExample": _build_boundary_example(endpoint, rule_map),
            "expectedStatus": 400,
            "rationale": f"Covers edge-case boundary conditions in schema constraints.",
            "endpoint": endpoint,
        })
    if endpoint:
        for response in endpoint.get("responses", []):
            add_case({
                "id": make_id("TC", f"API-{endpoint['method']}-{endpoint['path']}-{response['status']}"),
                "sourceIds": [api_spec["source"]],
                "description": f"API contract test for {endpoint['method']} {endpoint['path']} -> {response['status']}",
                "intent": "contract",
                "type": "api",
                "requestExample": _build_positive_example(endpoint, rule_map),
                "expectedStatus": int(response["status"]) if response["status"].isdigit() else None,
                "rationale": f"Verifies API response code {response['status']} is defined and handled.",
                "endpoint": endpoint,
            })
    return test_cases


def endpoint_response_status(endpoint: Dict[str, Any], positive: bool = True) -> int:
    if not endpoint:
        return 200 if positive else 400
    statuses = [r.get("status") for r in endpoint.get("responses", []) if str(r.get("status")).isdigit()]
    if positive:
        for code in [201, 200, 202]:
            if str(code) in statuses:
                return code
        return int(statuses[0]) if statuses else 200
    return 400 if "400" in statuses else int(statuses[0]) if statuses else 400


def _build_positive_example(endpoint: Dict[str, Any], rule_map: Dict[str, Any]) -> Dict[str, Any]:
    if not endpoint or not endpoint.get("request") or not endpoint["request"].get("schema"):
        return {}
    schema = endpoint["request"]["schema"]
    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    example = {}
    for name, detail in props.items():
        ptype = detail.get("type", "string")
        if ptype == "string":
            if detail.get("format") == "email":
                example[name] = "user@example.com"
            elif name.lower() == "password":
                example[name] = "Password123"
            else:
                example[name] = detail.get("example", f"sample-{name}")
        elif ptype == "integer":
            minimum = detail.get("minimum", 1)
            example[name] = minimum
        elif ptype == "boolean":
            example[name] = True
        else:
            example[name] = detail.get("example", None)
    for field, rule in rule_map.items():
        if field not in example:
            if rule.get("rule") == "required":
                example[field] = "sample-value"
    return example


def _build_invalid_example(endpoint: Dict[str, Any], rule_map: Dict[str, Any]) -> Dict[str, Any]:
    example = _build_positive_example(endpoint, rule_map)
    if not example:
        return {"invalid": True}
    for field, rule in rule_map.items():
        if rule.get("rule") == "required":
            example.pop(field, None)
            break
        if rule.get("rule") == "minimum":
            example[field] = rule.get("value", 1) - 1
            break
    return example


def _build_boundary_example(endpoint: Dict[str, Any], rule_map: Dict[str, Any]) -> Dict[str, Any]:
    example = _build_positive_example(endpoint, rule_map)
    if not example:
        return {}
    for field, rule in rule_map.items():
        if rule.get("rule") == "minimum":
            example[field] = rule.get("value", 1) - 1
            return example
        if rule.get("rule") == "required" and isinstance(example.get(field), str):
            example[field] = ""
            return example
    return example


def render_gherkin(test_cases: List[Dict[str, Any]], output_dir: Path) -> None:
    feature_lines = ["Feature: Generated acceptance and API tests", "", "  # Generated by speckit generator"]
    for case in test_cases:
        scenario = f"  Scenario: {case['id']} - {case['intent'].capitalize()} {case['description']}"
        feature_lines.append(scenario)
        feature_lines.append(f"    Given a user has a {case['intent']} payload")
        endpoint = case.get("endpoint")
        if endpoint:
            feature_lines.append(f"    When the client submits a {endpoint['method']} request to {endpoint['path']}")
        if case["intent"] == "negative":
            feature_lines.append(f"    Then the response status should be {case['expectedStatus']}")
            feature_lines.append("    And the response must contain an error description")
        else:
            feature_lines.append(f"    Then the response status should be {case['expectedStatus']}")
            feature_lines.append("    And the response body should match the expected schema")
        feature_lines.append("")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "generated_tests.feature"
    path.write_text("\n".join(feature_lines), encoding="utf-8")


def render_playwright(test_cases: List[Dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for case in test_cases:
        endpoint = case.get("endpoint")
        if not endpoint:
            continue
        filename = f"{case['id'].replace(':','').replace('/','_')}.spec.ts"
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            f"test('{case['id']} - {case['intent']}', async ({'{ request }'}) => {{",
            f"  const payload = {json.dumps(case['requestExample'], indent=2)};",
            f"  const response = await request.{endpoint['method'].lower()}('{endpoint['path']}', {{ data: payload }});",
            f"  expect(response.status()).toBe({case['expectedStatus']});",
            "  const body = await response.json();",
            "  expect(body).toBeTruthy();",
            "  // TODO: add field-level assertions and response schema validation",
            "});",
        ]
        (output_dir / filename).write_text("\n".join(lines), encoding="utf-8")


def build_traceability(test_cases: List[Dict[str, Any]], requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    trace = []
    requirement_map = {req["id"]: req for req in requirements}
    for case in test_cases:
        for source_id in case["sourceIds"]:
            trace.append({
                "requirementId": source_id,
                "requirementText": requirement_map.get(source_id, {}).get("text", ""),
                "testCaseId": case["id"],
                "intent": case["intent"],
                "artifact": f"playwright/{case['id']}.spec.ts",
                "rationale": case["rationale"],
            })
    return trace


def build_coverage(requirements: List[Dict[str, Any]], test_cases: List[Dict[str, Any]], api_spec: Dict[str, Any], validations: Dict[str, Any]) -> Dict[str, Any]:
    coverage = {
        "acceptanceCriteriaCoverage": {
            "total": len(requirements),
            "covered": len({tc["sourceIds"][0] for tc in test_cases if tc["type"] in ["functional", "validation", "boundary"]}),
        },
        "validationCoverage": {
            "totalRules": len(validations.get("rules", [])),
            "coveredRules": len({rule["field"] for rule in validations.get("rules", []) if any(rule["field"] in json.dumps(tc.get("requestExample", {})) for tc in test_cases)}),
        },
        "apiCoverage": {
            "totalEndpoints": len(api_spec.get("endpoints", [])),
            "coveredEndpoints": len({tc.get("endpoint", {}).get("path") for tc in test_cases if tc.get("endpoint")}),
            "statusCodesCovered": sorted({tc.get("expectedStatus") for tc in test_cases if tc.get("expectedStatus") is not None}),
        },
        "testCaseSummary": {
            "total": len(test_cases),
            "byIntent": {
                "positive": sum(1 for tc in test_cases if tc["intent"] == "positive"),
                "negative": sum(1 for tc in test_cases if tc["intent"] == "negative"),
                "boundary": sum(1 for tc in test_cases if tc["intent"] == "boundary"),
                "contract": sum(1 for tc in test_cases if tc["intent"] == "contract"),
            },
        },
    }
    coverage["acceptanceCriteriaCoverage"]["percent"] = round(100.0 * coverage["acceptanceCriteriaCoverage"]["covered"] / coverage["acceptanceCriteriaCoverage"]["total"], 2) if coverage["acceptanceCriteriaCoverage"]["total"] else 0
    coverage["validationCoverage"]["percent"] = round(100.0 * coverage["validationCoverage"]["coveredRules"] / coverage["validationCoverage"]["totalRules"], 2) if coverage["validationCoverage"]["totalRules"] else 0
    coverage["apiCoverage"]["percentEndpoints"] = round(100.0 * coverage["apiCoverage"]["coveredEndpoints"] / coverage["apiCoverage"]["totalEndpoints"], 2) if coverage["apiCoverage"]["totalEndpoints"] else 0
    return coverage


def build_gaps(requirements: List[Dict[str, Any]], api_spec: Dict[str, Any], validations: Dict[str, Any]) -> Dict[str, Any]:
    gaps = {
        "missingAcceptanceCriteria": [],
        "ambiguousBusinessRules": [],
        "undefinedValidations": [],
        "incompleteApiContracts": [],
    }
    if not any(req["text"] for req in requirements):
        gaps["missingAcceptanceCriteria"].append("No acceptance criteria were parsed from the input files.")
    for req in requirements:
        if re.search(r"\bshould\b|\bmay\b|\border to\b", req["text"], re.IGNORECASE):
            gaps["ambiguousBusinessRules"].append(req["text"])
    if not validations.get("rules"):
        gaps["undefinedValidations"].append("No validation rules were found.")
    for endpoint in api_spec.get("endpoints", []):
        if not endpoint.get("request"):
            gaps["incompleteApiContracts"].append(f"Endpoint {endpoint['method']} {endpoint['path']} has no request schema.")
        if not endpoint.get("responses"):
            gaps["incompleteApiContracts"].append(f"Endpoint {endpoint['method']} {endpoint['path']} has no response definitions.")
    return gaps


def make_manifest(sources: List[Dict[str, Any]], test_cases: List[Dict[str, Any]], artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    source_entries = []
    for source in sources:
        path = Path(source["path"])
        source_entries.append({"path": str(path), "checksum": source["checksum"]})
    return {
        "generatorVersion": GENERATOR_VERSION,
        "generatedAt": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "deterministicSeed": hashlib.sha256("".join([s["checksum"] for s in source_entries]).encode("utf-8")).hexdigest(),
        "sources": source_entries,
        "testCaseCount": len(test_cases),
        "artifacts": artifacts,
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def generate_from_config(config: Dict[str, Any]) -> Path:
    output_root = Path(config.get("output", "output"))
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_root = output_root / timestamp
    run_root.mkdir(parents=True, exist_ok=True)

    inputs = config.get("inputs", {})
    markdown_paths = [Path(p) for p in inputs.get("markdown", [])]
    openapi_paths = [Path(p) for p in inputs.get("openapi", [])]
    validation_paths = [Path(p) for p in inputs.get("validation_rules", [])]

    stories = [parse_markdown(path) for path in markdown_paths]
    api_specs = [parse_openapi(path) for path in openapi_paths]
    validations = [parse_validation_rules(path) for path in validation_paths]

    requirements = []
    for story in stories:
        requirements.extend(build_requirements(story))
    api_spec = api_specs[0] if api_specs else {"source": None, "endpoints": []}
    validation = validations[0] if validations else {"source": None, "rules": []}

    test_cases = generate_test_cases(requirements, api_spec, validation)

    intermediate = {
        "requirements": requirements,
        "api": api_spec,
        "validationRules": validation,
        "testCases": test_cases,
    }
    write_json(run_root / "intermediate_model.json", intermediate)

    render_gherkin(test_cases, run_root / "gherkin")
    render_playwright(test_cases, run_root / "playwright")

    trace = build_traceability(test_cases, requirements)
    write_json(run_root / "traceability_matrix.json", trace)

    coverage = build_coverage(requirements, test_cases, api_spec, validation)
    write_json(run_root / "coverage_report.json", coverage)

    gaps = build_gaps(requirements, api_spec, validation)
    write_json(run_root / "gaps.json", gaps)

    source_entries = []
    for path_list in [markdown_paths, openapi_paths, validation_paths]:
        for path in path_list:
            source_entries.append({"path": str(path), "checksum": checksum(path)})
    artifacts = [
        {"path": str(run_root / "intermediate_model.json"), "type": "model"},
        {"path": str(run_root / "traceability_matrix.json"), "type": "traceability"},
        {"path": str(run_root / "coverage_report.json"), "type": "coverage"},
        {"path": str(run_root / "gaps.json"), "type": "gaps"},
    ]
    manifest = make_manifest(source_entries, test_cases, artifacts)
    write_json(run_root / "manifest.json", manifest)

    return run_root


if __name__ == "__main__":
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found. Create a config.yaml at repository root.")
    config = load_yaml_or_json(config_path)
    output_path = generate_from_config(config)
    print(f"Output generated in: {output_path}")

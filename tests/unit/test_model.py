"""Unit tests for the core data model."""

import json
import unittest
from datetime import datetime

from src.core.model import (
    ApiSpec,
    Constraint,
    CoverageReport,
    Endpoint,
    Fixture,
    GenerationManifest,
    JsonSchema,
    RequestSchema,
    Response,
    Requirement,
    TestCase,
    TraceabilityRecord,
)


class TestModelSerialization(unittest.TestCase):
    def test_requirement_serialization(self) -> None:
        requirement = Requirement(
            id="AC-001",
            text="The API accepts a valid email, password, and optional age.",
            type="acceptance",
            actor="registered user",
            source="examples/user-story.md",
            business_rules=["Email must be required."],
            preconditions=["User is not registered."],
            postconditions=["User account is created."],
            validation_rules=["Email is required."],
        )

        data = requirement.to_dict()
        self.assertEqual(data["id"], "AC-001")
        self.assertEqual(data["type"], "acceptance")
        self.assertEqual(requirement, Requirement.from_dict(data))

    def test_api_spec_serialization(self) -> None:
        schema = JsonSchema(
            type="object",
            properties={
                "email": JsonSchema(type="string", format="email"),
                "password": JsonSchema(type="string", min_length=8),
            },
            required=("email", "password"),
        )
        request = RequestSchema(required=True, schema=schema)
        response = Response(status="201", description="Created", schema=JsonSchema(type="object"))
        endpoint = Endpoint(
            path="/api/users",
            method="POST",
            summary="Create a new user account",
            request=request,
            responses=(response,),
        )
        api_spec = ApiSpec(source="examples/api-spec.yaml", title="User Registration API", endpoints=(endpoint,))

        serialized = api_spec.to_dict()
        self.assertEqual(serialized["title"], "User Registration API")
        self.assertEqual(serialized["endpoints"][0]["path"], "/api/users")
        deserialized = ApiSpec.from_dict(serialized)
        self.assertEqual(api_spec, deserialized)

    def test_testcase_and_fixture_json(self) -> None:
        endpoint = Endpoint(
            path="/api/users",
            method="POST",
            request=RequestSchema(
                required=True,
                schema=JsonSchema(
                    type="object",
                    properties={"age": JsonSchema(type="integer", minimum=18)},
                ),
            ),
            responses=(Response(status="400", description="Validation error"),),
        )
        test_case = TestCase(
            id="TC-AC-001-POS",
            source_ids=("AC-001",),
            description="Valid registration request.",
            intent="positive",
            type="functional",
            rationale="Ensures happy path registration.",
            endpoint=endpoint,
            request_example={"email": "user@example.com", "password": "Password123", "age": 18},
            expected_response={"id": "abc123", "email": "user@example.com"},
            status_code=201,
            tags=("happy-path",),
        )
        fixture = Fixture(
            test_case_id=test_case.id,
            request_payload=test_case.request_example,
            expected_response=test_case.expected_response,
            headers={"Content-Type": "application/json"},
        )

        testcase_json = test_case.to_json()
        self.assertIsInstance(testcase_json, str)
        self.assertEqual(test_case, TestCase.from_dict(json.loads(testcase_json)))
        self.assertEqual(fixture, Fixture.from_dict(fixture.to_dict()))

    def test_traceability_and_coverage_serialization(self) -> None:
        trace_record = TraceabilityRecord(
            requirement_id="AC-001",
            test_case_id="TC-AC-001-POS",
            artifact_path="playwright/TC-AC-001-POS.spec.ts",
            rationale="Maps requirement to Playwright artifact.",
            requirement_text="The API accepts a valid email, password, and optional age.",
            intent="positive",
        )
        coverage = CoverageReport(
            acceptance_criteria_coverage={"covered": 4, "total": 4, "percent": 100.0},
            validation_coverage={"covered_rules": 3, "total_rules": 3, "percent": 100.0},
            api_coverage={"covered_endpoints": 1, "total_endpoints": 1},
            test_case_summary={"total": 15, "by_intent": {"positive": 4}},
            openapi_included=True,
        )

        self.assertEqual(trace_record, TraceabilityRecord.from_dict(trace_record.to_dict()))
        self.assertEqual(coverage, CoverageReport.from_dict(coverage.to_dict()))

    def test_generation_manifest_round_trip(self) -> None:
        manifest = GenerationManifest(
            generator_version="0.1.0",
            generated_at=datetime.utcnow().isoformat() + "Z",
            deterministic_seed="abc123",
            sources=(
                {"path": "examples/user-story.md", "checksum": "deadbeef"},
            ),
            test_cases=(
                {"id": "TC-AC-001-POS", "source_ids": ["AC-001"]},
            ),
            artifacts=(
                {"path": "playwright/TC-AC-001-POS.spec.ts", "type": "playwright"},
            ),
            openapi_included=True,
        )

        round_trip = GenerationManifest.from_dict(manifest.to_dict())
        self.assertEqual(manifest, round_trip)

    def test_invalid_fixture_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            Fixture(test_case_id="TC-AC-001-POS", request_payload={}, expected_response={})

    def test_json_schema_from_dict_none(self) -> None:
        self.assertIsNone(JsonSchema.from_dict(None))


if __name__ == "__main__":
    unittest.main()

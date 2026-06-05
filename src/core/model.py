"""Core dataclasses for the test case generation model."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union

T = TypeVar("T")


def _validate_required_field(name: str, value: Any) -> None:
    if value is None:
        raise ValueError(f"{name} is required and cannot be empty.")
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{name} is required and cannot be empty.")
    if isinstance(value, (list, tuple, dict, set)) and len(value) == 0:
        raise ValueError(f"{name} is required and cannot be empty.")


def _normalize_sequence(value: Optional[Union[Sequence[T], T]]) -> Tuple[T, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _serialize(value: Any) -> Any:
    if isinstance(value, SerializableModel):
        return value.to_dict()
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


class SerializableModel:
    """Mixin for dataclass serialization and JSON support."""

    def to_dict(self) -> Dict[str, Any]:
        return _serialize(asdict(self))

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, **kwargs)

    @classmethod
    def from_json(cls: Type[T], data: str, **kwargs: Any) -> T:  # type: ignore[override]
        return cls.from_dict(json.loads(data, **kwargs))

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:  # pragma: no cover
        raise NotImplementedError("from_dict must be implemented by subclasses")


@dataclass(frozen=True)
class Constraint(SerializableModel):
    """A validation constraint for a schema field."""

    field: str
    type: str
    rules: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None

    def __post_init__(self) -> None:
        _validate_required_field("field", self.field)
        _validate_required_field("type", self.type)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Constraint":
        return cls(
            field=data["field"],
            type=data["type"],
            rules=data.get("rules", {}),
            message=data.get("message"),
        )


@dataclass(frozen=True)
class JsonSchema(SerializableModel):
    """A JSON schema definition for request or response payloads."""

    type: Optional[str] = None
    format: Optional[str] = None
    properties: Dict[str, "JsonSchema"] = field(default_factory=dict)
    items: Optional["JsonSchema"] = None
    required: Tuple[str, ...] = field(default_factory=tuple)
    enum: Tuple[Any, ...] = field(default_factory=tuple)
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    constraints: Tuple[Constraint, ...] = field(default_factory=tuple)
    description: Optional[str] = None
    additional_properties: Optional[bool] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "required", _normalize_sequence(self.required))
        object.__setattr__(self, "enum", _normalize_sequence(self.enum))
        object.__setattr__(
            self,
            "properties",
            {k: v if isinstance(v, JsonSchema) else JsonSchema.from_dict(v) for k, v in self.properties.items()},
        )
        if self.items is not None and not isinstance(self.items, JsonSchema):
            object.__setattr__(self, "items", JsonSchema.from_dict(self.items))
        object.__setattr__(
            self,
            "constraints",
            tuple(
                c if isinstance(c, Constraint) else Constraint.from_dict(c)
                for c in self.constraints
            ),
        )

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["JsonSchema"]:
        if data is None:
            return None
        return cls(
            type=data.get("type"),
            format=data.get("format"),
            properties={
                key: JsonSchema.from_dict(value) for key, value in data.get("properties", {}).items()
            },
            items=JsonSchema.from_dict(data["items"]) if data.get("items") is not None else None,
            required=_normalize_sequence(data.get("required")),
            enum=_normalize_sequence(data.get("enum")),
            minimum=data.get("minimum"),
            maximum=data.get("maximum"),
            min_length=data.get("min_length", data.get("minLength")),
            max_length=data.get("max_length", data.get("maxLength")),
            constraints=tuple(
                Constraint.from_dict(entry) for entry in data.get("constraints", [])
            ),
            description=data.get("description"),
            additional_properties=data.get("additional_properties", data.get("additionalProperties")),
        )


@dataclass(frozen=True)
class RequestSchema(SerializableModel):
    """A request schema wrapper for endpoint payload definitions."""

    required: bool
    schema: JsonSchema
    content_type: str = "application/json"

    def __post_init__(self) -> None:
        _validate_required_field("schema", self.schema)
        _validate_required_field("content_type", self.content_type)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RequestSchema":
        return cls(
            required=data.get("required", False),
            schema=JsonSchema.from_dict(data["schema"]),
            content_type=data.get("content_type", "application/json"),
        )


@dataclass(frozen=True)
class Response(SerializableModel):
    """A response schema and metadata for an API endpoint."""

    status: str
    description: Optional[str] = None
    schema: Optional[JsonSchema] = None

    def __post_init__(self) -> None:
        _validate_required_field("status", self.status)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        return cls(
            status=str(data["status"]),
            description=data.get("description"),
            schema=JsonSchema.from_dict(data.get("schema")),
        )


@dataclass(frozen=True)
class Endpoint(SerializableModel):
    """An API endpoint with request and response definitions."""

    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    request: Optional[RequestSchema] = None
    responses: Tuple[Response, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _validate_required_field("path", self.path)
        _validate_required_field("method", self.method)
        object.__setattr__(
            self,
            "responses",
            tuple(
                response if isinstance(response, Response) else Response.from_dict(response)
                for response in self.responses
            ),
        )
        if self.request is not None and not isinstance(self.request, RequestSchema):
            object.__setattr__(self, "request", RequestSchema.from_dict(self.request))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Endpoint":
        return cls(
            path=data["path"],
            method=data["method"],
            summary=data.get("summary"),
            description=data.get("description"),
            request=RequestSchema.from_dict(data["request"]) if data.get("request") is not None else None,
            responses=tuple(Response.from_dict(entry) for entry in data.get("responses", [])),
        )


@dataclass(frozen=True)
class ApiSpec(SerializableModel):
    """A canonical API specification model."""

    source: str
    title: str
    endpoints: Tuple[Endpoint, ...] = field(default_factory=tuple)
    version: Optional[str] = None

    def __post_init__(self) -> None:
        _validate_required_field("source", self.source)
        _validate_required_field("title", self.title)
        object.__setattr__(
            self,
            "endpoints",
            tuple(
                endpoint if isinstance(endpoint, Endpoint) else Endpoint.from_dict(endpoint)
                for endpoint in self.endpoints
            ),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiSpec":
        return cls(
            source=data["source"],
            title=data["title"],
            version=data.get("version"),
            endpoints=tuple(Endpoint.from_dict(entry) for entry in data.get("endpoints", [])),
        )


@dataclass(frozen=True)
class Requirement(SerializableModel):
    """A structured requirement extracted from user stories and acceptance criteria."""

    id: str
    text: str
    type: str
    actor: Optional[str] = None
    source: Optional[str] = None
    business_rules: Tuple[str, ...] = field(default_factory=tuple)
    preconditions: Tuple[str, ...] = field(default_factory=tuple)
    postconditions: Tuple[str, ...] = field(default_factory=tuple)
    validation_rules: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _validate_required_field("id", self.id)
        _validate_required_field("text", self.text)
        _validate_required_field("type", self.type)
        object.__setattr__(self, "business_rules", _normalize_sequence(self.business_rules))
        object.__setattr__(self, "preconditions", _normalize_sequence(self.preconditions))
        object.__setattr__(self, "postconditions", _normalize_sequence(self.postconditions))
        object.__setattr__(self, "validation_rules", _normalize_sequence(self.validation_rules))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Requirement":
        return cls(
            id=data["id"],
            text=data["text"],
            type=data["type"],
            actor=data.get("actor"),
            source=data.get("source"),
            business_rules=_normalize_sequence(data.get("business_rules")),
            preconditions=_normalize_sequence(data.get("preconditions")),
            postconditions=_normalize_sequence(data.get("postconditions")),
            validation_rules=_normalize_sequence(data.get("validation_rules")),
        )


@dataclass(frozen=True)
class TestCase(SerializableModel):
    """A test case derived from requirements or API contracts."""

    id: str
    source_ids: Tuple[str, ...]
    description: str
    intent: str
    type: str
    rationale: Optional[str] = None
    endpoint: Optional[Endpoint] = None
    request_example: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _validate_required_field("id", self.id)
        _validate_required_field("description", self.description)
        _validate_required_field("intent", self.intent)
        _validate_required_field("type", self.type)
        object.__setattr__(self, "source_ids", _normalize_sequence(self.source_ids))
        object.__setattr__(self, "tags", _normalize_sequence(self.tags))
        if self.endpoint is not None and not isinstance(self.endpoint, Endpoint):
            object.__setattr__(self, "endpoint", Endpoint.from_dict(self.endpoint))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        return cls(
            id=data["id"],
            source_ids=_normalize_sequence(data.get("source_ids", [])),
            description=data["description"],
            intent=data["intent"],
            type=data["type"],
            rationale=data.get("rationale"),
            endpoint=Endpoint.from_dict(data["endpoint"]) if data.get("endpoint") is not None else None,
            request_example=data.get("request_example"),
            expected_response=data.get("expected_response"),
            status_code=data.get("status_code"),
            tags=_normalize_sequence(data.get("tags", [])),
        )


@dataclass(frozen=True)
class Fixture(SerializableModel):
    """Fixture data associated with a test case."""

    test_case_id: str
    request_payload: Dict[str, Any]
    expected_response: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_required_field("test_case_id", self.test_case_id)
        _validate_required_field("request_payload", self.request_payload)
        _validate_required_field("expected_response", self.expected_response)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fixture":
        return cls(
            test_case_id=data["test_case_id"],
            request_payload=data["request_payload"],
            expected_response=data["expected_response"],
            headers=data.get("headers", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class TraceabilityRecord(SerializableModel):
    """A traceability link between requirements, tests, and artifacts."""

    requirement_id: str
    test_case_id: str
    artifact_path: str
    rationale: Optional[str] = None
    requirement_text: Optional[str] = None
    intent: Optional[str] = None

    def __post_init__(self) -> None:
        _validate_required_field("requirement_id", self.requirement_id)
        _validate_required_field("test_case_id", self.test_case_id)
        _validate_required_field("artifact_path", self.artifact_path)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TraceabilityRecord":
        return cls(
            requirement_id=data["requirement_id"],
            test_case_id=data["test_case_id"],
            artifact_path=data["artifact_path"],
            rationale=data.get("rationale"),
            requirement_text=data.get("requirement_text"),
            intent=data.get("intent"),
        )


@dataclass(frozen=True)
class CoverageReport(SerializableModel):
    """Coverage metrics and gap information for a generation run."""

    acceptance_criteria_coverage: Dict[str, Any] = field(default_factory=dict)
    validation_coverage: Dict[str, Any] = field(default_factory=dict)
    api_coverage: Dict[str, Any] = field(default_factory=dict)
    test_case_summary: Dict[str, Any] = field(default_factory=dict)
    openapi_included: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverageReport":
        return cls(
            acceptance_criteria_coverage=data.get("acceptance_criteria_coverage", {}),
            validation_coverage=data.get("validation_coverage", {}),
            api_coverage=data.get("api_coverage", {}),
            test_case_summary=data.get("test_case_summary", {}),
            openapi_included=data.get("openapi_included", False),
        )


@dataclass(frozen=True)
class GenerationManifest(SerializableModel):
    """Manifest information for a deterministic generation run."""

    generator_version: str
    generated_at: str
    deterministic_seed: str
    sources: Tuple[Dict[str, str], ...] = field(default_factory=tuple)
    test_cases: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    artifacts: Tuple[Dict[str, str], ...] = field(default_factory=tuple)
    openapi_included: bool = False

    def __post_init__(self) -> None:
        _validate_required_field("generator_version", self.generator_version)
        _validate_required_field("generated_at", self.generated_at)
        _validate_required_field("deterministic_seed", self.deterministic_seed)
        object.__setattr__(self, "sources", tuple(self.sources))
        object.__setattr__(self, "test_cases", tuple(self.test_cases))
        object.__setattr__(self, "artifacts", tuple(self.artifacts))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationManifest":
        return cls(
            generator_version=data["generator_version"],
            generated_at=data["generated_at"],
            deterministic_seed=data["deterministic_seed"],
            sources=tuple(data.get("sources", [])),
            test_cases=tuple(data.get("test_cases", [])),
            artifacts=tuple(data.get("artifacts", [])),
            openapi_included=data.get("openapi_included", False),
        )

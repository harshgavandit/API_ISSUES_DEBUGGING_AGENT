"""Pydantic request/response schemas for the public API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogIngest(BaseModel):
    timestamp: datetime | None = None
    service_name: str = "api"
    environment: str = "dev"
    method: str
    endpoint: str
    status_code: int
    latency_ms: float
    request_id: str | None = None
    trace_id: str | None = None
    user_id: str | None = None
    request_body_sample: str | None = None
    response_body_sample: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    meta: dict[str, Any] | None = Field(default=None)


class LogOut(LogIngest):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    title: str
    summary: str
    likely_cause: str
    recommendations: list[str] | None
    severity: str
    affected_endpoints: list[str] | None
    affected_users_count: int
    ai_confidence: float
    status: str


class MetricsOut(BaseModel):
    total_requests: int
    error_rate: float
    silent_failures: int
    p95_latency_ms: float
    active_incidents: int
    risky_endpoints: list[dict[str, Any]]


class AnalysisResult(BaseModel):
    anomalies_created: int
    failure_groups_created: int
    incidents_created: int

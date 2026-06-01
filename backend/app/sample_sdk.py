"""Lightweight client helpers for sending API logs to the copilot ingest endpoint."""

from time import perf_counter
from typing import Any

import httpx


class ApiCopilotClient:
    def __init__(self, ingest_url: str, service_name: str, environment: str = "prod") -> None:
        self.ingest_url = ingest_url.rstrip("/")
        self.service_name = service_name
        self.environment = environment

    def track_request(
        self,
        *,
        method: str,
        endpoint: str,
        status_code: int,
        latency_ms: float,
        trace_id: str | None = None,
        user_id: str | None = None,
        error_message: str | None = None,
        response_body_sample: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "service_name": self.service_name,
            "environment": self.environment,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "trace_id": trace_id,
            "user_id": user_id,
            "error_message": error_message,
            "response_body_sample": response_body_sample,
            "meta": meta,
        }
        httpx.post(f"{self.ingest_url}/logs/ingest", json=payload, timeout=2)


class track_api_call:
    def __init__(self, client: ApiCopilotClient, method: str, endpoint: str, **meta: Any) -> None:
        self.client = client
        self.method = method
        self.endpoint = endpoint
        self.meta = meta
        self.started = 0.0

    def __enter__(self) -> "track_api_call":
        self.started = perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Exception | None, traceback: Any) -> None:
        latency_ms = (perf_counter() - self.started) * 1000
        self.client.track_request(
            method=self.method,
            endpoint=self.endpoint,
            status_code=500 if exc else 200,
            latency_ms=latency_ms,
            error_message=str(exc) if exc else None,
            meta=self.meta,
        )

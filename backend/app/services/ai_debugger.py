"""Generate incident explanations with OpenAI or deterministic fallback."""

import json

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ApiLog, FailureGroup


def fallback_incident(group: FailureGroup, sample_logs: list[ApiLog]) -> dict:
    endpoint = group.endpoint
    status = group.status_code
    timeout_hint = "timeout" in group.normalized_error or any(log.latency_ms > 2000 for log in sample_logs)
    silent_hint = status < 400 and any("success" in (log.response_body_sample or "").lower() for log in sample_logs)
    max_latency = max((log.latency_ms for log in sample_logs), default=0)
    traces = [log.trace_id for log in sample_logs if log.trace_id]
    trace_hint = f" Start with trace {traces[0]}." if traces else ""

    if silent_hint:
        title = f"Silent business failure on {endpoint}"
        cause = (
            "The endpoint is returning HTTP 200 while the response body indicates the business operation failed. "
            "This is likely invisible to basic status-code monitoring."
        )
        recommendations = [
            "Treat response_body_sample values with success=false or error fields as failed transactions.",
            "Inspect checkout/payment provider responses for timeout or authorization failure payloads.",
            "Add an explicit application_error metric for this endpoint, separate from HTTP status.",
            "Update contract tests so HTTP 200 responses must also satisfy the expected business success schema.",
            "Create an alert on silent failure count so customer-impacting failures are not hidden.",
        ]
    elif timeout_hint:
        title = f"Timeout-driven degradation on {endpoint}"
        cause = (
            f"Sample requests reached up to {max_latency:.0f}ms, which points to a slow downstream dependency, "
            "retry storm, queue delay, or database query regression."
        )
        recommendations = [
            "Compare failing trace IDs with healthy traces to isolate the slow span.",
            "Check payment gateway, database, and cache latency around the incident window.",
            "Review retry policy, timeout values, and circuit-breaker behavior for this integration.",
            "Look for a recent deployment or feature flag that changed downstream call volume.",
            "Add endpoint-level p95 and dependency-level timeout alerts.",
        ]
    elif status >= 500:
        title = f"Recurring server errors on {endpoint}"
        cause = "The service is throwing repeated 5xx errors for the same endpoint and normalized error pattern."
        recommendations = [
            "Inspect stack traces and application logs for the sampled trace IDs.",
            "Check recent deployments, configuration changes, and dependency versions.",
            "Replay a failing request payload in staging to confirm reproducibility.",
            "Add a regression test for the failing request shape once the root cause is confirmed.",
        ]
    else:
        title = f"{endpoint} recurring failure pattern"
        cause = "The same client or integration request pattern is repeatedly failing."
        recommendations = [
            "Inspect the sample trace IDs and compare failing requests with healthy requests.",
            "Check client payload shape, auth state, and upstream integration changes.",
            "Review downstream dependency health, timeout values, and retry behavior.",
            "Add contract tests around the response shape for this endpoint.",
        ]

    return {
        "title": title,
        "summary": (
            f"{group.count} related failures were grouped for {endpoint} in the recent analysis window."
            f"{trace_hint}"
        ),
        "likely_cause": cause,
        "recommendations": recommendations,
        "ai_confidence": 0.74 if silent_hint or timeout_hint else 0.68,
    }


def explain_failure_group(db: Session, group: FailureGroup) -> dict:
    sample_logs = db.scalars(
        select(ApiLog).where(ApiLog.id.in_(group.sample_log_ids or [])).limit(8)
    ).all()

    if not settings.enable_ai or not settings.openai_api_key:
        return fallback_incident(group, sample_logs)

    client = OpenAI(api_key=settings.openai_api_key)
    payload = {
        "failure_group": {
            "service_name": group.service_name,
            "endpoint": group.endpoint,
            "status_code": group.status_code,
            "normalized_error": group.normalized_error,
            "count": group.count,
            "severity": group.severity.value,
        },
        "sample_logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "latency_ms": log.latency_ms,
                "error_message": log.error_message,
                "response_body_sample": log.response_body_sample,
                "trace_id": log.trace_id,
            }
            for log in sample_logs
        ],
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an API debugging agent. Return strict JSON with title, summary, "
                    "likely_cause, recommendations array, and ai_confidence number between 0 and 1."
                ),
            },
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content or "{}")

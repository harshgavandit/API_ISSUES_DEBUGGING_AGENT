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

    if silent_hint:
        cause = "The endpoint may be returning HTTP 200 while the business operation is failing."
    elif timeout_hint:
        cause = "A downstream dependency, retry policy, or database query may be adding latency or timing out."
    elif status >= 500:
        cause = "The service is throwing server-side errors for a recurring request pattern."
    else:
        cause = "The same client or integration request pattern is repeatedly failing."

    return {
        "title": f"{endpoint} recurring failure pattern",
        "summary": f"{group.count} related failures were detected for {endpoint} in the recent analysis window.",
        "likely_cause": cause,
        "recommendations": [
            "Inspect the sample trace IDs and compare the failing requests with healthy requests.",
            "Check recent deployments, feature flags, and configuration changes for this service.",
            "Review downstream dependency health, timeout values, and retry behavior.",
            "Add or tighten contract tests around the response shape for this endpoint.",
        ],
        "ai_confidence": 0.66,
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

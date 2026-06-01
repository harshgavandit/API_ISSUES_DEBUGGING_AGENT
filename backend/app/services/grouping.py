"""Group related API failures into incident candidates."""

import re
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApiLog, FailureGroup, Severity


def normalize_error(message: str | None, response: str | None) -> str:
    raw = (message or response or "unknown failure").lower()
    if "timeout" in raw or "timed out" in raw:
        return "downstream payment timeout"
    if "success" in raw and "false" in raw:
        return "business success flag false"
    raw = re.sub(r"\b[0-9a-f]{8,}\b", "<id>", raw)
    raw = re.sub(r"\b\d+\b", "<num>", raw)
    raw = re.sub(r"https?://\S+", "<url>", raw)
    raw = raw.replace("\n", " ")
    return raw[:500].strip()


def status_bucket(status_code: int) -> int:
    if status_code >= 500:
        return 500
    if status_code >= 400:
        return 400
    return status_code


def severity_for(status_code: int, count: int, latency_ms: float) -> Severity:
    if status_code >= 500 and count >= 25:
        return Severity.critical
    if status_code >= 500 or latency_ms > 2000 or count >= 15:
        return Severity.high
    if status_code >= 400 or count >= 5:
        return Severity.medium
    return Severity.low


def group_recent_failures(db: Session, minutes: int = 15) -> list[FailureGroup]:
    since = datetime.utcnow() - timedelta(minutes=minutes)
    logs = db.scalars(
        select(ApiLog).where(
            ApiLog.timestamp >= since,
            (ApiLog.status_code >= 400)
            | (ApiLog.error_message.is_not(None))
            | (ApiLog.response_body_sample.ilike("%success%false%"))
            | (ApiLog.response_body_sample.ilike("%error%")),
        )
    ).all()

    buckets: dict[tuple[str, str, int, str], list[ApiLog]] = defaultdict(list)
    for log in logs:
        key = (
            log.service_name,
            log.endpoint,
            status_bucket(log.status_code),
            normalize_error(log.error_message, log.response_body_sample),
        )
        buckets[key].append(log)

    groups: list[FailureGroup] = []
    for (service, endpoint, status_code, normalized), bucket in buckets.items():
        if len(bucket) < 3:
            continue

        existing = db.scalar(
            select(FailureGroup).where(
                FailureGroup.service_name == service,
                FailureGroup.endpoint == endpoint,
                FailureGroup.status_code == status_code,
                FailureGroup.normalized_error == normalized,
                FailureGroup.last_seen >= since,
            )
        )
        first_seen = min(item.timestamp for item in bucket)
        last_seen = max(item.timestamp for item in bucket)
        avg_latency = sum(item.latency_ms for item in bucket) / len(bucket)
        sample_ids = [item.id for item in bucket[:8]]

        if existing:
            existing.count = len(bucket)
            existing.first_seen = min(existing.first_seen, first_seen)
            existing.last_seen = last_seen
            existing.severity = severity_for(status_code, len(bucket), avg_latency)
            existing.sample_log_ids = sample_ids
            groups.append(existing)
            continue

        group = FailureGroup(
            service_name=service,
            endpoint=endpoint,
            status_code=status_code,
            normalized_error=normalized,
            count=len(bucket),
            first_seen=first_seen,
            last_seen=last_seen,
            severity=severity_for(status_code, len(bucket), avg_latency),
            sample_log_ids=sample_ids,
        )
        db.add(group)
        groups.append(group)

    db.commit()
    return groups

"""Background analysis: anomalies, grouping, incidents, and alerts."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Anomaly, ApiLog, Incident, IncidentStatus, Severity
from app.services.ai_debugger import explain_failure_group
from app.services.alerting import send_incident_alerts
from app.services.grouping import group_recent_failures


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = max(0, int(len(sorted_values) * 0.95) - 1)
    return sorted_values[index]


def create_anomalies(db: Session, minutes: int = 15) -> list[Anomaly]:
    now = datetime.utcnow()
    recent_since = now - timedelta(minutes=minutes)
    baseline_since = now - timedelta(hours=2)

    endpoints = db.scalars(select(ApiLog.endpoint).distinct()).all()
    anomalies: list[Anomaly] = []

    for endpoint in endpoints:
        recent = db.scalars(select(ApiLog).where(ApiLog.endpoint == endpoint, ApiLog.timestamp >= recent_since)).all()
        baseline = db.scalars(
            select(ApiLog).where(
                ApiLog.endpoint == endpoint,
                ApiLog.timestamp >= baseline_since,
                ApiLog.timestamp < recent_since,
            )
        ).all()
        if len(recent) < 5:
            continue

        recent_error_rate = sum(1 for log in recent if log.status_code >= 500) / len(recent)
        baseline_error_rate = (
            sum(1 for log in baseline if log.status_code >= 500) / len(baseline)
            if baseline
            else 0.01
        )
        recent_p95 = p95([log.latency_ms for log in recent])
        baseline_p95 = p95([log.latency_ms for log in baseline]) or 250.0
        silent_failures = [
            log
            for log in recent
            if log.status_code < 400
            and any(token in (log.response_body_sample or "").lower() for token in ["success:false", "success\": false", "error", "failed", "timeout"])
        ]

        service_name = recent[0].service_name
        if recent_error_rate > max(0.08, baseline_error_rate * 2.5):
            anomalies.append(
                Anomaly(
                    type="error_rate_spike",
                    endpoint=endpoint,
                    service_name=service_name,
                    severity=Severity.high,
                    metric_name="error_rate",
                    observed_value=round(recent_error_rate, 4),
                    expected_value=round(baseline_error_rate, 4),
                    description=f"Error rate jumped to {recent_error_rate:.1%} for {endpoint}.",
                )
            )

        if recent_p95 > max(1000, baseline_p95 * 2.2):
            anomalies.append(
                Anomaly(
                    type="latency_spike",
                    endpoint=endpoint,
                    service_name=service_name,
                    severity=Severity.medium if recent_p95 < 2500 else Severity.high,
                    metric_name="p95_latency_ms",
                    observed_value=recent_p95,
                    expected_value=baseline_p95,
                    description=f"P95 latency is {recent_p95:.0f}ms versus baseline {baseline_p95:.0f}ms.",
                )
            )

        if len(silent_failures) >= 3:
            anomalies.append(
                Anomaly(
                    type="silent_failure",
                    endpoint=endpoint,
                    service_name=service_name,
                    severity=Severity.high,
                    metric_name="silent_failure_count",
                    observed_value=len(silent_failures),
                    expected_value=0,
                    description=f"{len(silent_failures)} successful HTTP responses look like failed business operations.",
                )
            )

    db.add_all(anomalies)
    db.commit()
    return anomalies


def create_incidents(db: Session) -> list[Incident]:
    groups = group_recent_failures(db)
    incidents: list[Incident] = []

    for group in groups:
        existing = db.scalar(
            select(Incident).where(
                Incident.failure_group_id == group.id,
                Incident.status != IncidentStatus.resolved,
            )
        )
        if existing:
            explanation = explain_failure_group(db, group)
            existing.title = explanation.get("title") or existing.title
            existing.summary = explanation.get("summary") or existing.summary
            existing.likely_cause = explanation.get("likely_cause") or existing.likely_cause
            existing.recommendations = explanation.get("recommendations") or existing.recommendations
            existing.ai_confidence = float(explanation.get("ai_confidence") or existing.ai_confidence)
            db.commit()
            continue

        explanation = explain_failure_group(db, group)
        affected_users = db.scalar(
            select(func.count(func.distinct(ApiLog.user_id))).where(
                ApiLog.id.in_(group.sample_log_ids or []),
                ApiLog.user_id.is_not(None),
            )
        ) or 0
        incident = Incident(
            failure_group_id=group.id,
            title=explanation.get("title") or f"{group.endpoint} recurring failure",
            summary=explanation.get("summary") or "A recurring API failure pattern was detected.",
            likely_cause=explanation.get("likely_cause") or "More investigation is needed.",
            recommendations=explanation.get("recommendations") or [],
            severity=group.severity,
            affected_endpoints=[group.endpoint],
            affected_users_count=affected_users,
            ai_confidence=float(explanation.get("ai_confidence") or 0.65),
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        try:
            send_incident_alerts(db, incident)
        except Exception:
            # Silently fail if alerting fails to avoid blocking the analysis
            pass
        incidents.append(incident)

    return incidents


def run_analysis(db: Session) -> dict[str, int]:
    anomalies = create_anomalies(db)
    incidents = create_incidents(db)
    return {
        "anomalies_created": len(anomalies),
        "failure_groups_created": len({incident.failure_group_id for incident in incidents}),
        "incidents_created": len(incidents),
    }

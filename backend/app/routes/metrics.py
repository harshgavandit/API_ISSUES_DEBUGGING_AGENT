from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApiLog, Incident, IncidentStatus
from app.schemas import AnalysisResult, MetricsOut
from app.workers.anomaly_detector import p95, run_analysis

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsOut, summary="Dashboard metrics for the last hour")
def summary(db: Session = Depends(get_db)) -> MetricsOut:
    since = datetime.utcnow() - timedelta(hours=1)
    logs = db.scalars(select(ApiLog).where(ApiLog.timestamp >= since)).all()
    total = len(logs)
    errors = sum(1 for log in logs if log.status_code >= 500)
    silent = sum(
        1
        for log in logs
        if log.status_code < 400
        and any(token in (log.response_body_sample or "").lower() for token in ["success:false", "success\": false", "error", "failed", "timeout"])
    )
    active_incidents = db.scalar(
        select(func.count()).select_from(Incident).where(Incident.status != IncidentStatus.resolved)
    ) or 0

    endpoint_rows = db.execute(
        select(ApiLog.endpoint, func.count(ApiLog.id), func.avg(ApiLog.latency_ms))
        .where(ApiLog.timestamp >= since)
        .group_by(ApiLog.endpoint)
        .order_by(desc(func.count(ApiLog.id)))
        .limit(8)
    ).all()
    risky = [
        {"endpoint": endpoint, "requests": count, "avg_latency_ms": round(avg or 0, 1)}
        for endpoint, count, avg in endpoint_rows
    ]

    return MetricsOut(
        total_requests=total,
        error_rate=round(errors / total, 4) if total else 0,
        silent_failures=silent,
        p95_latency_ms=round(p95([log.latency_ms for log in logs]), 1),
        active_incidents=active_incidents,
        risky_endpoints=risky,
    )


@router.post("/analyze", response_model=AnalysisResult, summary="Run anomaly detection and incident grouping")
def analyze(db: Session = Depends(get_db)) -> AnalysisResult:
    return AnalysisResult(**run_analysis(db))

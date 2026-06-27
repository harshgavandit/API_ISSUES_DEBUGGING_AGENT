from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApiLog
from app.schemas import LogIngest, LogOut

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/ingest", response_model=LogOut, summary="Ingest a single API log event")
def ingest_log(payload: LogIngest, db: Session = Depends(get_db)) -> ApiLog:
    log = ApiLog(**payload.model_dump(exclude={"timestamp"}), timestamp=payload.timestamp or datetime.utcnow())
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to persist log event") from exc
    return log


@router.post("/bulk", response_model=list[LogOut], summary="Ingest multiple API log events")
def ingest_bulk(payloads: list[LogIngest], db: Session = Depends(get_db)) -> list[ApiLog]:
    logs = [
        ApiLog(**payload.model_dump(exclude={"timestamp"}), timestamp=payload.timestamp or datetime.utcnow())
        for payload in payloads
    ]
    try:
        db.add_all(logs)
        db.commit()
        for log in logs:
            db.refresh(log)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to persist log batch") from exc
    return logs


@router.get("", response_model=list[LogOut], summary="List recent API logs with optional filters")
def list_logs(
    db: Session = Depends(get_db),
    endpoint: str | None = None,
    service_name: str | None = None,
    status_min: int | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[ApiLog]:
    stmt = select(ApiLog).order_by(desc(ApiLog.timestamp)).limit(limit)
    if endpoint:
        stmt = stmt.where(ApiLog.endpoint == endpoint)
    if service_name:
        stmt = stmt.where(ApiLog.service_name == service_name)
    if status_min:
        stmt = stmt.where(ApiLog.status_code >= status_min)
    return list(db.scalars(stmt).all())

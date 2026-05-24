from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Incident, IncidentStatus
from app.schemas import IncidentOut

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db)) -> list[Incident]:
    return list(db.scalars(select(Incident).order_by(desc(Incident.created_at), desc(Incident.id)).limit(100)).all())


@router.patch("/{incident_id}/status", response_model=IncidentOut)
def update_status(incident_id: int, status: IncidentStatus, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = status
    db.commit()
    db.refresh(incident)
    return incident

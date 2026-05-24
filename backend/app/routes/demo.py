from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApiLog
from app.services.demo_data import make_demo_log
from app.workers.anomaly_detector import run_analysis

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
def seed_demo_data(
    db: Session = Depends(get_db),
    count: int = Query(default=160, ge=50, le=500),
) -> dict[str, int]:
    logs = [ApiLog(**make_demo_log(index)) for index in range(count)]
    db.add_all(logs)
    db.commit()

    analysis = run_analysis(db)
    return {
        "logs_created": len(logs),
        **analysis,
    }

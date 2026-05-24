import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert, Incident


def send_slack_alert(db: Session, incident: Incident) -> None:
    if not settings.slack_webhook_url:
        return

    payload = {
        "text": f"[{incident.severity.value.upper()}] {incident.title}\n{incident.summary}",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{incident.title}*"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": incident.summary}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Likely cause:* {incident.likely_cause}"}},
        ],
    }
    status = "sent"
    try:
        httpx.post(settings.slack_webhook_url, json=payload, timeout=5)
    except httpx.HTTPError:
        status = "failed"

    db.add(Alert(incident_id=incident.id, channel="slack", status=status, payload=payload))
    db.commit()

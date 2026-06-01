"""Deliver incident alerts via Slack and optional email."""

import smtplib
from email.message import EmailMessage

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert, Incident


def format_incident_text(incident: Incident) -> str:
    endpoints = ", ".join(incident.affected_endpoints or []) or "Unknown"
    recommendations = "\n".join(f"- {item}" for item in (incident.recommendations or []))
    return (
        f"API Reliability Copilot detected a new incident.\n\n"
        f"Severity: {incident.severity.value.upper()}\n"
        f"Status: {incident.status.value}\n"
        f"Title: {incident.title}\n"
        f"Affected endpoints: {endpoints}\n"
        f"Affected users: {incident.affected_users_count}\n"
        f"Confidence: {round(incident.ai_confidence * 100)}%\n\n"
        f"Summary:\n{incident.summary}\n\n"
        f"Likely cause:\n{incident.likely_cause}\n\n"
        f"Recommended next steps:\n{recommendations or '- Review the latest logs and traces.'}\n"
    )


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
        httpx.post(settings.slack_webhook_url, json=payload, timeout=3)
    except (httpx.HTTPError, httpx.TimeoutException):
        status = "failed"
    except Exception:
        status = "failed"

    db.add(Alert(incident_id=incident.id, channel="slack", status=status, payload=payload))
    db.commit()


def send_email_alert(db: Session, incident: Incident) -> None:
    if not settings.email_alerts_enabled:
        return
    if not all([settings.smtp_username, settings.smtp_password, settings.alert_email_to]):
        db.add(
            Alert(
                incident_id=incident.id,
                channel="email",
                status="skipped_missing_config",
                payload={"reason": "SMTP username, password, and recipient are required."},
            )
        )
        db.commit()
        return

    sender = settings.alert_email_from or settings.smtp_username
    body = format_incident_text(incident)
    message = EmailMessage()
    message["Subject"] = f"[{incident.severity.value.upper()}] {incident.title}"
    message["From"] = sender
    message["To"] = settings.alert_email_to
    message.set_content(body)

    status = "sent"
    payload = {
        "to": settings.alert_email_to,
        "from": sender,
        "subject": message["Subject"],
        "body_preview": body[:500],
    }
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        status = "failed"
        payload["error"] = str(exc)

    db.add(Alert(incident_id=incident.id, channel="email", status=status, payload=payload))
    db.commit()


def send_incident_alerts(db: Session, incident: Incident) -> None:
    send_slack_alert(db, incident)
    send_email_alert(db, incident)

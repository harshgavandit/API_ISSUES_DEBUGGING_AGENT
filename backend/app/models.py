"""SQLAlchemy ORM models for logs, anomalies, incidents, and alerts."""

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"


class ApiLog(Base):
    __tablename__ = "api_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    service_name: Mapped[str] = mapped_column(String(120), index=True)
    environment: Mapped[str] = mapped_column(String(40), default="dev", index=True)
    method: Mapped[str] = mapped_column(String(12))
    endpoint: Mapped[str] = mapped_column(String(255), index=True)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, index=True)
    request_id: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    request_body_sample: Mapped[str] = mapped_column(Text, nullable=True)
    response_body_sample: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_logs_endpoint_timestamp", "endpoint", "timestamp"),
        Index("ix_logs_service_timestamp", "service_name", "timestamp"),
    )


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    type: Mapped[str] = mapped_column(String(80), index=True)
    endpoint: Mapped[str] = mapped_column(String(255), index=True)
    service_name: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity), default=Severity.medium)
    metric_name: Mapped[str] = mapped_column(String(120))
    observed_value: Mapped[float] = mapped_column(Float)
    expected_value: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="open")


class FailureGroup(Base):
    __tablename__ = "failure_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    endpoint: Mapped[str] = mapped_column(String(255), index=True)
    service_name: Mapped[str] = mapped_column(String(120), index=True)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    normalized_error: Mapped[str] = mapped_column(String(500), index=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen: Mapped[datetime] = mapped_column(DateTime)
    last_seen: Mapped[datetime] = mapped_column(DateTime)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity), default=Severity.medium)
    sample_log_ids: Mapped[list[int]] = mapped_column(JSON, nullable=True)

    incidents: Mapped[list["Incident"]] = relationship(back_populates="failure_group")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    failure_group_id: Mapped[int] = mapped_column(ForeignKey("failure_groups.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    likely_cause: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity), default=Severity.medium, index=True)
    affected_endpoints: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    affected_users_count: Mapped[int] = mapped_column(Integer, default=0)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.68)
    status: Mapped[IncidentStatus] = mapped_column(SqlEnum(IncidentStatus), default=IncidentStatus.open, index=True)

    failure_group: Mapped[FailureGroup] = relationship(back_populates="incidents")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    channel: Mapped[str] = mapped_column(String(40))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

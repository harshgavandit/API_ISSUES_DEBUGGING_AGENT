from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import SessionLocal, init_db
from app.routes import demo, incidents, logs, metrics
from app.workers.anomaly_detector import run_analysis

scheduler = BackgroundScheduler()


def scheduled_analysis() -> None:
    db = SessionLocal()
    try:
        run_analysis(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if not scheduler.running:
        scheduler.add_job(
            scheduled_analysis,
            "interval",
            seconds=settings.analysis_interval_seconds,
            id="api-analysis",
            replace_existing=True,
        )
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="API Reliability Copilot",
    version="0.1.2",
    description="Ingest API logs, detect anomalies, and generate incident reports.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(metrics.router)
app.include_router(demo.router)


@app.get("/health", summary="Liveness check")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-reliability-copilot"}

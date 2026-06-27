# API Reliability Copilot

> Hackathon-ready API reliability agent with FastAPI, Next.js, and MySQL.

An AI-assisted API monitoring and debugging agent for detecting silent failures, latency spikes, recurring integration errors, and developer-actionable incidents before users complain.

It is intended to be practical for demos, local testing, and fast iteration.

This project is designed to be easy to demo, easy to extend, and quick to run locally for experiments and prototypes.

## What It Does

- Ingests API logs through FastAPI endpoints for monitoring and investigation tasks.
- Stores logs, anomalies, grouped failures, incidents, and alerts in MySQL for traceability and review purposes.
- Detects error-rate spikes, latency spikes, recurring failures, and HTTP 200 silent failures quickly and clearly for teams.
- Groups related failures into incident candidates.
- Generates debugging reports using either OpenAI or a deterministic fallback.
- Shows a Next.js command center for metrics, incidents, logs, and configuration.
- Includes a simulator that creates a realistic checkout and payment failure demo flow for presentations.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, PyMySQL, APScheduler
- Frontend: Next.js, TypeScript, lucide-react
- Database: MySQL
- Optional AI: OpenAI API
- Optional alerts: Slack webhook

## Option 1: Docker Startup

Use this on the laptop if Docker is installed and ready to use.

```powershell
docker compose up --build
```

Open the frontend UI at:

```text
http://localhost:3000
```

Backend health check:

```text
http://localhost:8000/health
```

Generate demo logs through Docker:

```powershell
docker compose --profile demo run --rm simulator
```

Then refresh the dashboard or click the Run analysis button to inspect the results.

Stop everything:

```powershell
docker compose down
```

Reset the MySQL demo data:

```powershell
docker compose down -v
```

## Option 2: Manual Startup

Use this on a machine where you want to run MySQL, Python, and Node directly.

### Recommended Versions

- Python 3.11 or 3.12
- Node.js 20 or newer
- MySQL 8.x

Python 3.14 also passed the dependency install on the desktop used to validate this repo, but 3.11 or 3.12 is still the safer laptop setup for hackathon work.

### Clone And Run Checklist

After cloning the repo on your laptop:

1. Start MySQL locally.
2. Create the `api_copilot` database.
3. Run the backend on port `8000`.
4. Run the frontend on port `3000`.
5. Run the simulator to generate demo incidents.

### Manual MySQL Setup

Create a database:

```sql
CREATE DATABASE api_copilot;
```

Or run the SQL file:

```powershell
mysql -u root -p < database/create_database.sql
```

Update `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/api_copilot
ENABLE_AI=false
OPENAI_API_KEY=
SLACK_WEBHOOK_URL=
ANALYSIS_INTERVAL_SECONDS=60
```

### Run Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

The backend creates its database tables automatically when it starts.

### Run Frontend

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open the user interface in your browser at:

```text
http://localhost:3000
```

### Generate Demo Traffic

In another terminal:

```powershell
cd simulator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_logs.py --mode incident --count 160
```

Then refresh the dashboard or click `Run analysis`.

## Validate Before Demo

Backend syntax check:

```powershell
cd backend
python -m compileall app ..\simulator
```

Frontend checks:

```powershell
cd frontend
npm run typecheck
npm run build
```

Quick health URLs:

```text
http://localhost:8000/health
http://localhost:3000
```

## Demo Story

Use this script when presenting:

1. Start with an empty command center.
2. Run the simulator to send normal commerce API logs.
3. The simulator introduces checkout/payment failures.
4. Some failures return HTTP `200` with `success: false`, showing silent failure detection.
5. The agent groups recurring payment timeout logs.
6. It creates an incident with likely cause, confidence, and debugging recommendations.

## API Endpoints

- `POST /logs/ingest` - send one log event
- `POST /logs/bulk` - send many log events
- `GET /logs` - inspect recent events
- `GET /metrics/summary` - dashboard summary
- `POST /metrics/analyze` - trigger anomaly and incident analysis
- `GET /incidents` - list AI debugging reports
- `PATCH /incidents/{id}/status?status=resolved` - update incident status

## Why It Scores Well

- Real-world usability: focused API reliability workflows for engineering teams.
- Good UI/UX: dashboard-first command center, not a marketing page.
- AI integration: structured incident explanations and recommendations.
- Automation: background analysis loop plus alert hooks.
- Product thinking: detects silent failures, not just obvious server errors.

*Last updated: June 2026 — maintenance pass on docs, configs, and local setup notes for demos and walkthroughs.*


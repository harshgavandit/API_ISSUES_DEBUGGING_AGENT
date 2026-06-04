# API Reliability Copilot — log simulator image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generate_logs.py .

CMD ["python", "generate_logs.py", "--api", "http://backend:8000", "--mode", "incident", "--count", "160"]

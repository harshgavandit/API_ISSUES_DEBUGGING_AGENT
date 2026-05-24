import random
import uuid
from datetime import datetime, timedelta


ENDPOINTS = [
    ("GET", "/catalog/items"),
    ("GET", "/users/profile"),
    ("POST", "/checkout/create"),
    ("POST", "/payments/charge"),
    ("POST", "/orders/confirm"),
]


def make_demo_log(index: int, mode: str = "incident") -> dict:
    method, endpoint = random.choice(ENDPOINTS)
    status = 200
    latency = random.gauss(180, 45)
    response = '{"success": true}'
    error = None

    if mode == "incident" and index > 40:
        endpoint = random.choice(["/checkout/create", "/payments/charge"])
        method = "POST"
        latency = random.gauss(2300, 420)
        if random.random() < 0.55:
            status = random.choice([500, 502, 504])
            error = random.choice(
                [
                    "Payment provider timeout while creating charge",
                    "Stripe API timeout after 2000ms",
                    "Downstream payment gateway request timed out",
                ]
            )
            response = '{"success": false, "error": "payment timeout"}'
        else:
            response = '{"success": false, "error": "card_authorization_timeout"}'

    return {
        "timestamp": datetime.utcnow() - timedelta(seconds=random.randint(0, 120)),
        "service_name": "commerce-api",
        "environment": "demo",
        "method": method,
        "endpoint": endpoint,
        "status_code": status,
        "latency_ms": max(25, round(latency, 2)),
        "request_id": str(uuid.uuid4()),
        "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
        "user_id": f"user-{random.randint(1000, 1100)}",
        "response_body_sample": response,
        "error_message": error,
        "meta": {"region": random.choice(["ap-south-1", "us-east-1"]), "release": "2026.05.24"},
    }

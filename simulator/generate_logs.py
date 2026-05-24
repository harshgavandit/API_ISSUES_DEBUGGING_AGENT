import argparse
import random
import time
import uuid
from datetime import datetime, timedelta

import httpx


ENDPOINTS = [
    ("GET", "/catalog/items"),
    ("GET", "/users/profile"),
    ("POST", "/checkout/create"),
    ("POST", "/payments/charge"),
    ("POST", "/orders/confirm"),
]


def make_log(mode: str, index: int) -> dict:
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
            status = 200
            response = '{"success": false, "error": "card_authorization_timeout"}'

    return {
        "timestamp": (datetime.utcnow() - timedelta(seconds=random.randint(0, 120))).isoformat(),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demo API logs for API Reliability Copilot.")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--count", type=int, default=160, help="Number of logs to generate")
    parser.add_argument("--mode", choices=["normal", "incident"], default="incident")
    parser.add_argument("--sleep", type=float, default=0.0, help="Delay between batches")
    args = parser.parse_args()

    client = httpx.Client(timeout=10)
    batch = []
    for index in range(args.count):
        batch.append(make_log(args.mode, index))
        if len(batch) == 25:
            client.post(f"{args.api}/logs/bulk", json=batch).raise_for_status()
            print(f"sent {index + 1}/{args.count}")
            batch = []
            if args.sleep:
                time.sleep(args.sleep)

    if batch:
        client.post(f"{args.api}/logs/bulk", json=batch).raise_for_status()
        print(f"sent {args.count}/{args.count}")

    analysis = client.post(f"{args.api}/metrics/analyze")
    analysis.raise_for_status()
    print("analysis:", analysis.json())


if __name__ == "__main__":
    main()

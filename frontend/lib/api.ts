function getApiBase() {
  if (typeof window === "undefined") {
    return process.env.API_INTERNAL_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  }

  return "/api/backend";
}

export type Summary = {
  total_requests: number;
  error_rate: number;
  silent_failures: number;
  p95_latency_ms: number;
  active_incidents: number;
  risky_endpoints: Array<{ endpoint: string; requests: number; avg_latency_ms: number }>;
};

export type Incident = {
  id: number;
  created_at: string;
  title: string;
  summary: string;
  likely_cause: string;
  recommendations: string[] | null;
  severity: string;
  affected_endpoints: string[] | null;
  affected_users_count: number;
  ai_confidence: number;
  status: string;
};

export type ApiLog = {
  id: number;
  timestamp: string;
  service_name: string;
  environment: string;
  method: string;
  endpoint: string;
  status_code: number;
  latency_ms: number;
  trace_id?: string | null;
  user_id?: string | null;
  error_message?: string | null;
  response_body_sample?: string | null;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBase()}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export function getSummary() {
  return getJson<Summary>("/metrics/summary");
}

export function getIncidents() {
  return getJson<Incident[]>("/incidents");
}

export function getLogs() {
  return getJson<ApiLog[]>("/logs?limit=150");
}

export async function runAnalysis() {
  const response = await fetch(`${getApiBase()}/metrics/analyze`, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.status}`);
  }
  return response.json();
}

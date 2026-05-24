import { AnalyzeButton } from "@/components/AnalyzeButton";
import { IncidentCard } from "@/components/IncidentCard";
import { MetricCard } from "@/components/MetricCard";
import { getIncidents, getSummary, type Incident, type Summary } from "@/lib/api";

export default async function DashboardPage() {
  let summary: Summary;
  let incidents: Incident[] = [];
  try {
    [summary, incidents] = await Promise.all([getSummary(), getIncidents()]);
  } catch {
    summary = {
      total_requests: 0,
      error_rate: 0,
      silent_failures: 0,
      p95_latency_ms: 0,
      active_incidents: 0,
      risky_endpoints: []
    };
  }

  const latest = incidents.slice(0, 3);

  return (
    <>
      <div className="page-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>API reliability command center</h1>
          <p className="muted">Monitor silent failures, latency drift, and recurring integration issues.</p>
        </div>
        <AnalyzeButton />
      </div>

      <section className="grid metrics">
        <MetricCard label="Requests, last hour" value={summary.total_requests} hint="Ingested API events" />
        <MetricCard label="Error rate" value={`${(summary.error_rate * 100).toFixed(1)}%`} hint="HTTP 5xx failures" />
        <MetricCard label="P95 latency" value={`${summary.p95_latency_ms}ms`} hint="Slowest meaningful tail" />
        <MetricCard label="Active incidents" value={summary.active_incidents} hint="Open debugging threads" />
      </section>

      <section className="grid two-col" style={{ marginTop: 16 }}>
        <div className="card">
          <h2>Risky endpoints</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Requests</th>
                <th>Avg latency</th>
              </tr>
            </thead>
            <tbody>
              {summary.risky_endpoints.map((row) => (
                <tr key={row.endpoint}>
                  <td className="code">{row.endpoint}</td>
                  <td>{row.requests}</td>
                  <td>{row.avg_latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="grid">
          {latest.length ? latest.map((incident) => <IncidentCard key={incident.id} incident={incident} />) : (
            <div className="card">
              <h2>No incidents yet</h2>
              <p className="muted">Run the simulator, then trigger analysis to create AI debugging reports.</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}

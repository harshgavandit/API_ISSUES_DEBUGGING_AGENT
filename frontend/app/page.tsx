import { AnalyzeButton } from "@/components/AnalyzeButton";
import { DemoTrafficButton } from "@/components/DemoTrafficButton";
import { IncidentCard } from "@/components/IncidentCard";
import { MetricCard } from "@/components/MetricCard";
import { getIncidents, getSummary, type Incident, type Summary } from "@/lib/api";
import { Activity, AlertTriangle, CheckCircle2, Clock3, Radar, ShieldCheck, Zap } from "lucide-react";

export const dynamic = "force-dynamic";

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
  const errorPercent = summary.error_rate * 100;
  const riskScore = Math.min(
    100,
    Math.round(summary.active_incidents * 28 + errorPercent * 3 + summary.silent_failures * 5 + summary.p95_latency_ms / 80)
  );
  const healthySignals = [
    { label: "Silent failure detection", active: summary.silent_failures > 0 },
    { label: "Latency anomaly scan", active: summary.p95_latency_ms > 1000 },
    { label: "Incident grouping", active: summary.active_incidents > 0 },
  ];
  const maxEndpointRequests = Math.max(...summary.risky_endpoints.map((row) => row.requests), 1);

  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">AI-ready API incident response</p>
          <h1>Catch silent failures before users report them.</h1>
          <p>
            API Copilot ingests logs, detects business-level failures, groups recurring errors, and drafts
            developer-ready debugging reports.
          </p>
          <div className="hero-actions">
            <DemoTrafficButton />
            <AnalyzeButton />
            <span className="status-chip">
              <ShieldCheck size={15} /> Free deterministic mode active
            </span>
          </div>
        </div>
        <div className="risk-console">
          <div className="risk-header">
            <span>
              <Radar size={16} /> Live risk score
            </span>
            <strong>{riskScore}</strong>
          </div>
          <div className="risk-meter">
            <span style={{ width: `${riskScore}%` }} />
          </div>
          <div className="signal-list">
            {healthySignals.map((signal) => (
              <div key={signal.label} className={signal.active ? "signal active" : "signal"}>
                {signal.active ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
                {signal.label}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid metrics">
        <MetricCard label="Requests, last hour" value={summary.total_requests} hint="Ingested API events" tone="info" />
        <MetricCard label="Error rate" value={`${errorPercent.toFixed(1)}%`} hint="HTTP 5xx failures" tone={errorPercent > 8 ? "danger" : "good"} />
        <MetricCard label="Silent failures" value={summary.silent_failures} hint="HTTP 200 but business failed" tone={summary.silent_failures ? "warn" : "good"} />
        <MetricCard label="Active incidents" value={summary.active_incidents} hint="Open debugging threads" tone={summary.active_incidents ? "danger" : "good"} />
      </section>

      <section className="grid two-col section-gap">
        <div className="card">
          <div className="section-title">
            <div>
              <p className="eyebrow">Blast radius</p>
              <h2>Riskiest endpoints</h2>
            </div>
            <span className="mini-chip">
              <Clock3 size={14} /> Last hour
            </span>
          </div>
          <div className="endpoint-list">
            {summary.risky_endpoints.length ? summary.risky_endpoints.map((row) => (
              <div className="endpoint-row" key={row.endpoint}>
                <div>
                  <span className="code">{row.endpoint}</span>
                  <small>{row.requests} requests · {row.avg_latency_ms}ms avg</small>
                </div>
                <div className="endpoint-bar">
                  <span style={{ width: `${Math.max(8, (row.requests / maxEndpointRequests) * 100)}%` }} />
                </div>
              </div>
            )) : (
              <div className="empty-state">
                <Activity size={22} />
                <p>No traffic yet. Run the simulator to populate endpoint risk.</p>
              </div>
            )}
          </div>
        </div>
        <div className="grid">
          <div className="section-title compact">
            <div>
              <p className="eyebrow">Latest reports</p>
              <h2>Debugging queue</h2>
            </div>
            <span className="mini-chip">
              <Zap size={14} /> Auto grouped
            </span>
          </div>
          {latest.length ? latest.map((incident) => <IncidentCard key={incident.id} incident={incident} />) : (
            <div className="card empty-state">
              <Radar size={24} />
              <h2>No incidents yet</h2>
              <p>Run the simulator, then trigger analysis to create debugging reports.</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}

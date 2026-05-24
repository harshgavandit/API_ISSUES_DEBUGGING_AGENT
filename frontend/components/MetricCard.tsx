import type { ReactNode } from "react";

export function MetricCard({ label, value, hint }: { label: string; value: ReactNode; hint: string }) {
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="muted" style={{ fontSize: 13 }}>
        {hint}
      </div>
    </div>
  );
}

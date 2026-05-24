import type { ReactNode } from "react";

export function MetricCard({
  label,
  value,
  hint,
  tone = "neutral",
}: {
  label: string;
  value: ReactNode;
  hint: string;
  tone?: "neutral" | "good" | "warn" | "danger" | "info";
}) {
  return (
    <div className={`card metric-card ${tone}`}>
      <div className="metric-label">
        <span>{label}</span>
        <span className="metric-dot" />
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-hint">{hint}</div>
    </div>
  );
}

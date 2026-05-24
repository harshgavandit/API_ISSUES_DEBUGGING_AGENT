import type { Incident } from "@/lib/api";

export function IncidentCard({ incident }: { incident: Incident }) {
  return (
    <article className={`card incident ${incident.severity}`}>
      <div className="toolbar" style={{ justifyContent: "space-between", marginBottom: 10 }}>
        <span className={`badge ${incident.severity}`}>{incident.severity}</span>
        <span className="muted" style={{ fontSize: 13 }}>
          Confidence {Math.round(incident.ai_confidence * 100)}%
        </span>
      </div>
      <h3 style={{ marginBottom: 8 }}>{incident.title}</h3>
      <p className="muted">{incident.summary}</p>
      <p>
        <strong>Likely cause:</strong> {incident.likely_cause}
      </p>
      {incident.recommendations?.length ? (
        <ul style={{ marginBottom: 0 }}>
          {incident.recommendations.slice(0, 4).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

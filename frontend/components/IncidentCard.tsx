import type { Incident } from "@/lib/api";
import { Brain, Crosshair, Route, ShieldAlert, Users } from "lucide-react";

export function IncidentCard({ incident }: { incident: Incident }) {
  const endpoints = incident.affected_endpoints || [];
  const confidence = Math.round(incident.ai_confidence * 100);

  return (
    <article className={`card incident ${incident.severity}`}>
      <div className="incident-topline">
        <span className={`badge ${incident.severity}`}>
          <ShieldAlert size={13} /> {incident.severity}
        </span>
        <span className="confidence-pill">
          <Brain size={13} /> {confidence}% confidence
        </span>
      </div>
      <h3>{incident.title}</h3>
      <p className="incident-summary">{incident.summary}</p>

      <div className="incident-facts">
        <span>
          <Users size={14} /> {incident.affected_users_count} users
        </span>
        <span>
          <Route size={14} /> {endpoints.length ? endpoints.join(", ") : "endpoint under investigation"}
        </span>
      </div>

      <div className="cause-box">
        <div className="cause-label">
          <Crosshair size={14} /> Likely cause
        </div>
        <p>{incident.likely_cause}</p>
      </div>

      {incident.recommendations?.length ? (
        <ul className="recommendations">
          {incident.recommendations.slice(0, 5).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

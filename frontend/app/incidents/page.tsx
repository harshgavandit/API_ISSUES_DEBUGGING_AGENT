import { AnalyzeButton } from "@/components/AnalyzeButton";
import { IncidentCard } from "@/components/IncidentCard";
import { getIncidents, type Incident } from "@/lib/api";

export default async function IncidentsPage() {
  let incidents: Incident[] = [];
  try {
    incidents = await getIncidents();
  } catch {
    incidents = [];
  }

  return (
    <>
      <div className="page-header">
        <div>
          <p className="eyebrow">Incidents</p>
          <h1>AI debugging reports</h1>
          <p className="muted">Grouped failures with likely causes, blast radius, and next debugging steps.</p>
        </div>
        <AnalyzeButton />
      </div>
      <section className="list">
        {incidents.map((incident) => (
          <IncidentCard key={incident.id} incident={incident} />
        ))}
        {!incidents.length ? (
          <div className="card">
            <h2>No incidents detected</h2>
            <p className="muted">Generate demo logs from the simulator to see incident grouping in action.</p>
          </div>
        ) : null}
      </section>
    </>
  );
}

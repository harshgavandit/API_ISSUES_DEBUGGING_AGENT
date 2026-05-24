import { AnalyzeButton } from "@/components/AnalyzeButton";
import { IncidentCard } from "@/components/IncidentCard";
import { getIncidents, type Incident } from "@/lib/api";
import { BrainCircuit, CheckCircle2, ListChecks, Radar } from "lucide-react";

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
      <section className="insight-strip">
        <div>
          <BrainCircuit size={18} />
          <span>Free deterministic debugging now, OpenAI upgrade path built in</span>
        </div>
        <div>
          <Radar size={18} />
          <span>Silent HTTP 200 failures are treated as real incidents</span>
        </div>
        <div>
          <ListChecks size={18} />
          <span>Recommendations are shaped for on-call engineers</span>
        </div>
      </section>
      <section className="list">
        {incidents.map((incident) => (
          <IncidentCard key={incident.id} incident={incident} />
        ))}
        {!incidents.length ? (
          <div className="card empty-state">
            <CheckCircle2 size={26} />
            <h2>No incidents detected</h2>
            <p>Generate demo logs from the simulator to see incident grouping in action.</p>
          </div>
        ) : null}
      </section>
    </>
  );
}

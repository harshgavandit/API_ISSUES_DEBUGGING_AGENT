import { Bell, Brain, Database, SlidersHorizontal } from "lucide-react";

export default function SettingsPage() {
  return (
    <>
      <div className="page-header">
        <div>
          <p className="eyebrow">Settings</p>
          <h1>Agent configuration</h1>
          <p className="muted">The MVP reads these values from backend environment variables.</p>
        </div>
      </div>
      <section className="card">
        <div className="settings-row">
          <h3>
            <Database size={18} /> MySQL
          </h3>
          <p className="muted">Set <span className="code">DATABASE_URL</span> in <span className="code">backend/.env</span>.</p>
        </div>
        <div className="settings-row">
          <h3>
            <Brain size={18} /> AI reports
          </h3>
          <p className="muted">Set <span className="code">ENABLE_AI=true</span> and <span className="code">OPENAI_API_KEY</span>. Without it, deterministic fallback recommendations are used.</p>
        </div>
        <div className="settings-row">
          <h3>
            <Bell size={18} /> Alerts
          </h3>
          <p className="muted">Add <span className="code">SLACK_WEBHOOK_URL</span> to send incident summaries to Slack.</p>
        </div>
        <div className="settings-row">
          <h3>
            <SlidersHorizontal size={18} /> Detection loop
          </h3>
          <p className="muted">Tune <span className="code">ANALYSIS_INTERVAL_SECONDS</span> for background anomaly checks.</p>
        </div>
      </section>
    </>
  );
}

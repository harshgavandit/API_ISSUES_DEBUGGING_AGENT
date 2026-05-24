import Link from "next/link";
import { Activity, Bell, FileText, Gauge, Settings } from "lucide-react";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <div>API Copilot</div>
            <div className="muted" style={{ color: "#98a2b3", fontSize: 12 }}>
              Reliability command center
            </div>
          </div>
        </div>
        <nav className="nav">
          <Link href="/">
            <Gauge size={18} /> Overview
          </Link>
          <Link href="/incidents">
            <Bell size={18} /> Incidents
          </Link>
          <Link href="/logs">
            <FileText size={18} /> Live logs
          </Link>
          <Link href="/settings">
            <Settings size={18} /> Settings
          </Link>
        </nav>
        <div className="card" style={{ background: "#182230", borderColor: "#344054", marginTop: "auto" }}>
          <Activity size={18} />
          <p style={{ marginTop: 10, marginBottom: 4, color: "white", fontWeight: 700 }}>Agent loop active</p>
          <p style={{ margin: 0, color: "#98a2b3", fontSize: 13 }}>
            Detects anomalies, groups failures, and drafts debugging recommendations.
          </p>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

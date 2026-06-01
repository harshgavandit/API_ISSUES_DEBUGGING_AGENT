import Link from "next/link";
import { Activity, Bell, FileText, Gauge, Radar, Settings, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Radar size={19} />
          </div>
          <div>
            <div>API Copilot</div>
            <div className="muted" style={{ color: "#98a2b3", fontSize: 12 }}>
              AI debugging command center
            </div>
          </div>
        </div>
        <nav className="nav" aria-label="Main navigation">
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
        <div className="side-panel">
          <div className="side-panel-icon">
            <Sparkles size={18} />
          </div>
          <p className="side-panel-title">Agent loop active</p>
          <p className="side-panel-copy">
            Watches logs, catches silent failures, and turns noisy API errors into action plans.
          </p>
          <div className="pulse-row">
            <Activity size={14} /> Analysis every 60s
          </div>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

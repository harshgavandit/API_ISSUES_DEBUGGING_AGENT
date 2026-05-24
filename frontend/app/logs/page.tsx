import { getLogs, type ApiLog } from "@/lib/api";
import { FileSearch, Timer, TriangleAlert } from "lucide-react";

export default async function LogsPage() {
  let logs: ApiLog[] = [];
  try {
    logs = await getLogs();
  } catch {
    logs = [];
  }

  return (
    <>
      <div className="page-header">
        <div>
          <p className="eyebrow">Live logs</p>
          <h1>Recent API events</h1>
          <p className="muted">Raw signal behind each anomaly and incident report.</p>
        </div>
      </div>
      <div className="card">
        <div className="table-toolbar">
          <span>
            <FileSearch size={16} /> {logs.length} events loaded
          </span>
          <span>
            <TriangleAlert size={16} /> Silent failures appear as green HTTP status with failed response bodies
          </span>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Endpoint</th>
              <th>Status</th>
              <th>Latency</th>
              <th>Trace</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleTimeString()}</td>
                <td className="code">
                  {log.method} {log.endpoint}
                </td>
                <td>
                  <span className={`badge ${log.status_code >= 500 ? "high" : log.status_code >= 400 ? "medium" : "low"}`}>
                    {log.status_code}
                  </span>
                </td>
                <td>{Math.round(log.latency_ms)}ms</td>
                <td className="code">{log.trace_id || "-"}</td>
                <td>
                  <span className={log.error_message || log.response_body_sample?.includes("false") ? "log-error" : ""}>
                    {log.error_message || log.response_body_sample || "-"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!logs.length ? (
          <div className="empty-state table-empty">
            <Timer size={24} />
            <h2>No logs ingested yet</h2>
            <p>Run the simulator to stream realistic checkout and payment API events.</p>
          </div>
        ) : null}
      </div>
    </>
  );
}

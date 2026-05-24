import { getLogs, type ApiLog } from "@/lib/api";

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
                <td>{log.error_message || log.response_body_sample || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

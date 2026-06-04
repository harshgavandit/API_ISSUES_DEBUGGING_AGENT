"use client";

import { RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { runAnalysis } from "@/lib/api";

export function AnalyzeButton() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  return (
    <div className="analyze-control">
      <button
        type="button"
        className="btn primary"
        disabled={pending}
        aria-busy={pending}
        onClick={() =>
          startTransition(async () => {
            setMessage(null);
            setFailed(false);
            try {
              const result = await runAnalysis();
              setMessage(
                `Analysis complete: ${result.anomalies_created} anomalies, ${result.incidents_created} new incidents`
              );
              router.refresh();
            } catch {
              setFailed(true);
              setMessage("Analysis failed. Check that the backend is running on port 8000.");
            }
          })
        }
      >
        <RefreshCw size={16} />
        {pending ? "Analyzing" : "Run analysis"}
      </button>
      {message ? <span className={failed ? "action-status error" : "action-status"}>{message}</span> : null}
    </div>
  );
}

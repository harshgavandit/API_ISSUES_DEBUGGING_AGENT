"use client";

import { FlaskConical } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { seedDemoTraffic } from "@/lib/api";

export function DemoTrafficButton() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  return (
    <div className="analyze-control">
      <button
        type="button"
        className="btn"
        disabled={pending}
        onClick={() =>
          startTransition(async () => {
            setMessage(null);
            setFailed(false);
            try {
              const result = await seedDemoTraffic();
              setMessage(
                `Demo ready: ${result.logs_created} logs, ${result.incidents_created} new incidents`
              );
              router.refresh();
            } catch {
              setFailed(true);
              setMessage("Demo generation failed. Check the backend service.");
            }
          })
        }
      >
        <FlaskConical size={16} />
        {pending ? "Generating" : "Generate demo traffic"}
      </button>
      {message ? <span className={failed ? "action-status error" : "action-status"}>{message}</span> : null}
    </div>
  );
}

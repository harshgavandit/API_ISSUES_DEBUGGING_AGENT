"use client";

import { RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { runAnalysis } from "@/lib/api";

export function AnalyzeButton() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  return (
    <button
      className="btn primary"
      onClick={() =>
        startTransition(async () => {
          await runAnalysis();
          router.refresh();
        })
      }
    >
      <RefreshCw size={16} />
      {pending ? "Analyzing" : "Run analysis"}
    </button>
  );
}

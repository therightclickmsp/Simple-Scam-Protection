import { useEffect, useState } from "react";
import axios from "axios";
import { API } from "@/lib/api";

const FALLBACK = ["AnyDesk", "TeamViewer", "UltraViewer", "ScreenConnect", "Supremo", "LogMeIn", "RustDesk", "Quick Assist"];

export default function ToolsStrip() {
  const [tools, setTools] = useState(FALLBACK);

  useEffect(() => {
    axios.get(`${API}/signatures`).then((r) => setTools(r.data.remote_tools)).catch(() => {});
  }, []);

  const loop = [...tools, ...tools];
  return (
    <section className="border-y border-slate-200 bg-slate-900 py-5" data-testid="tools-strip">
      <div className="mx-auto flex max-w-7xl items-center gap-6 overflow-hidden px-4 sm:px-6 lg:px-8">
        <p className="shrink-0 text-xs font-semibold uppercase tracking-widest text-emerald-400">Detects & blocks</p>
        <div className="relative overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_8%,#000_92%,transparent)]">
          <div className="marquee flex w-max gap-10">
            {loop.map((t, i) => (
              <span key={`${t}-${i}`} className="font-mono-gs whitespace-nowrap text-sm text-slate-300">{t}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

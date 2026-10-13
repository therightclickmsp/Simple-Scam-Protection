import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { MonitorX, TerminalSquare, TriangleAlert } from "lucide-react";

const SCENARIOS = {
  remote: {
    bg: "bg-red-600",
    title: "Someone may be trying to control your computer",
    text: "AnyDesk just tried to start, and Guardian Shield closed it. If a caller, pop-up or message asked you to install or open it, it is a SCAM. Hang up the phone now. Microsoft, Apple, your bank and the government never call you to fix your computer.",
  },
  command: {
    bg: "bg-amber-600",
    title: "If someone on the phone asked you to open this, it's a scam",
    text: "Event Viewer was just opened. It is full of normal warnings that every computer has. Scammers show it to make you think your PC is broken or hacked. It is not. Hang up and don't give anyone money or access.",
  },
};

const WarningOverlay = ({ kind, onClose }) => {
  const [count, setCount] = useState(3);
  const s = SCENARIOS[kind];
  useEffect(() => {
    if (count <= 0) return;
    const t = setTimeout(() => setCount((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [count]);
  return createPortal(
    <div data-testid="warning-overlay" className={`fixed inset-0 z-[100] grid place-items-center p-6 text-center text-white ${s.bg}`}>
      <div className="rise max-w-3xl">
        <p className="flex items-center justify-center gap-3 text-2xl font-extrabold tracking-widest"><TriangleAlert className="h-8 w-8" /> STOP</p>
        <h3 className="font-display mt-5 text-3xl font-extrabold sm:text-5xl">{s.title}</h3>
        <p className="mt-6 text-lg leading-relaxed text-white/95 sm:text-xl">{s.text}</p>
        <button
          data-testid="warning-overlay-close-button"
          disabled={count > 0}
          onClick={onClose}
          className="mt-10 rounded-2xl bg-white px-8 py-4 text-lg font-bold text-slate-900 transition-opacity disabled:opacity-60"
        >
          {count > 0 ? `Please read the message (${count})` : "I understand"}
        </button>
        <p className="mt-6 text-sm text-white/70">This is a preview of the Windows app's full-screen warning.</p>
      </div>
    </div>,
    document.body
  );
};

export default function AlertPreview() {
  const [kind, setKind] = useState(null);
  return (
    <section id="preview" className="py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grain relative overflow-hidden rounded-3xl bg-slate-900 p-8 text-white md:p-14">
          <p className="text-xs font-semibold uppercase tracking-widest text-emerald-400 sm:text-sm">See it in action</p>
          <h2 className="font-display mt-3 max-w-2xl text-3xl font-extrabold sm:text-4xl">What happens when a scammer makes their move</h2>
          <p className="mt-4 max-w-2xl text-base text-slate-300 md:text-lg">
            Warnings fill the whole screen, use big plain words, and can't be dismissed for a few seconds - so the
            message gets read, even while someone is talking in your ear.
          </p>
          <div className="mt-10 grid gap-4 md:grid-cols-2">
            <button data-testid="simulate-remote-button" onClick={() => setKind("remote")} className="group flex items-start gap-4 rounded-2xl border border-slate-700 bg-slate-800 p-6 text-left transition-colors hover:border-red-400">
              <MonitorX className="h-8 w-8 shrink-0 text-red-400" />
              <span>
                <span className="block text-lg font-bold">Simulate: caller makes you open AnyDesk</span>
                <span className="mt-1 block text-slate-400">The app is closed instantly and you're warned.</span>
              </span>
            </button>
            <button data-testid="simulate-command-button" onClick={() => setKind("command")} className="group flex items-start gap-4 rounded-2xl border border-slate-700 bg-slate-800 p-6 text-left transition-colors hover:border-amber-400">
              <TerminalSquare className="h-8 w-8 shrink-0 text-amber-400" />
              <span>
                <span className="block text-lg font-bold">Simulate: "technician" opens Event Viewer</span>
                <span className="mt-1 block text-slate-400">You're told why those "errors" are normal.</span>
              </span>
            </button>
          </div>
        </div>
      </div>
      {kind && <WarningOverlay kind={kind} onClose={() => setKind(null)} />}
    </section>
  );
}

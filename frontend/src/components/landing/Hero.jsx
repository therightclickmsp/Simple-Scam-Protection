import { Download, Search, Check, Lock, MonitorSmartphone, Terminal, Globe } from "lucide-react";
import { DOWNLOAD_URL } from "@/lib/api";

const rows = [
  [MonitorSmartphone, "Block remote-access tools"],
  [Terminal, "Warn about scammer tricks"],
  [Globe, "Block scam websites"],
];

const AppMock = () => (
  <div data-testid="hero-app-mock" className="rise d3 relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_30px_80px_-30px_rgba(15,23,42,0.35)]">
    <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-3">
      <span className="h-3 w-3 rounded-full bg-slate-300" />
      <span className="h-3 w-3 rounded-full bg-slate-300" />
      <span className="h-3 w-3 rounded-full bg-slate-300" />
      <span className="ml-3 text-xs font-semibold text-slate-500">Guardian Shield 1.0</span>
    </div>
    <div className="grid grid-cols-[120px_1fr] sm:grid-cols-[150px_1fr]">
      <div className="space-y-1 bg-slate-900 p-4 text-sm">
        {["Status", "Check a Link", "Activity Log", "Settings"].map((n, i) => (
          <div key={n} className={`rounded-lg px-3 py-2 ${i === 0 ? "bg-slate-800 text-white" : "text-slate-400"}`}>{n}</div>
        ))}
      </div>
      <div className="space-y-4 p-5">
        <div className="rounded-xl bg-emerald-50 p-5">
          <div className="flex items-center gap-3">
            <span className="pulse-ring grid h-9 w-9 place-items-center rounded-full bg-emerald-600 text-white">
              <Check className="h-5 w-5" strokeWidth={3} />
            </span>
            <p className="font-display text-xl font-extrabold text-emerald-700 sm:text-2xl">You are Protected</p>
          </div>
          <p className="mt-2 text-sm text-slate-600">Watching for remote-access tools and scammer tricks.</p>
        </div>
        {rows.map(([Icon, label]) => (
          <div key={label} className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3">
            <span className="flex items-center gap-3 text-sm font-semibold text-slate-800">
              <Icon className="h-4 w-4 text-emerald-600" /> {label}
            </span>
            <span className="h-6 w-11 rounded-full bg-emerald-600 p-0.5"><span className="ml-auto block h-5 w-5 translate-x-5 rounded-full bg-white" /></span>
          </div>
        ))}
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm">
          <span className="font-bold text-red-700">Blocked AnyDesk</span>
          <span className="text-slate-600"> · closed 2 seconds after launch</span>
        </div>
      </div>
    </div>
  </div>
);

export default function Hero() {
  return (
    <section id="top" className="grain relative overflow-hidden">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-[1.05fr_1fr] lg:px-8">
        <div>
          <p className="rise inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm font-semibold text-emerald-800">
            <Lock className="h-4 w-4" /> Free anti-scam protection for Windows 10 & 11
          </p>
          <h1 className="rise d1 font-display mt-6 text-4xl font-extrabold leading-[1.05] text-slate-900 sm:text-5xl lg:text-6xl">
            Stop tech-support scammers <span className="text-emerald-700">before they take control.</span>
          </h1>
          <p className="rise d2 mt-6 max-w-xl text-lg leading-relaxed text-slate-600 sm:text-xl">
            Guardian Shield quietly sits in your taskbar. It closes remote-control apps like AnyDesk and TeamViewer
            the moment they start, warns you when a "technician" opens scary-looking Windows tools, and checks links
            for scam signs.
          </p>
          <div className="rise d3 mt-9 flex flex-col gap-3 sm:flex-row">
            <a
              href={DOWNLOAD_URL}
              data-testid="download-hero-button"
              className="inline-flex items-center justify-center gap-2.5 rounded-2xl bg-emerald-600 px-7 py-4 text-lg font-bold text-white shadow-lg shadow-emerald-600/25 transition-[background-color,transform] hover:-translate-y-0.5 hover:bg-emerald-700"
            >
              <Download className="h-5 w-5" /> Download free for Windows
            </a>
            <a
              href="#checker"
              data-testid="hero-test-link-button"
              className="inline-flex items-center justify-center gap-2.5 rounded-2xl border-2 border-slate-300 bg-white px-7 py-4 text-lg font-bold text-slate-800 transition-colors hover:border-slate-900"
            >
              <Search className="h-5 w-5" /> Test a link online
            </a>
          </div>
          <p className="rise d4 mt-6 text-sm font-medium text-slate-500">
            100% free · No account · Nothing leaves your PC · Works alongside Windows Defender
          </p>
        </div>
        <AppMock />
      </div>
    </section>
  );
}

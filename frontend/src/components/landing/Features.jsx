import { MonitorX, TerminalSquare, Link2, Globe2, ScrollText, KeyRound, AppWindow, LockKeyhole } from "lucide-react";

const features = [
  [MonitorX, "Remote-access blocker", "Finds AnyDesk, TeamViewer, UltraViewer, RustDesk, Quick Assist and more. Closes them the instant they start and helps you remove them.", "lg:col-span-2 bg-slate-900 text-white", "text-emerald-400"],
  [AppWindow, "Fake pop-up closer", "Spots fake 'Your PC is locked - call Microsoft' pages in Chrome, Edge, Firefox, Brave and Opera, and closes them automatically.", "bg-red-50", "text-red-600"],
  [LockKeyhole, "Settings password", "A family member sets a password. Without it, nobody can switch protection off, trust a tool, clear the log, quit or uninstall.", "bg-amber-50", "text-amber-700"],
  [TerminalSquare, "Scammer-trick warnings", "Event Viewer, netstat, tree, syskey, msconfig - the tools scammers open to fake 'infections'. You'll get a clear warning.", "bg-white", "text-amber-600"],
  [Link2, "Link & message checker", "Spots misspelled brand names, look-alike letters, odd domain endings, raw IP addresses and scam phrases.", "bg-white", "text-blue-600"],
  [Globe2, "Scam website blocking", "Blocks a built-in list of fake support and refund sites on your whole PC. Asks Windows for permission once.", "bg-white", "text-emerald-600"],
  [KeyRound, "Trusted list, scam-proofed", "Use remote tools for work? Mark them trusted - but only after typing a confirmation, so a caller can't rush you.", "bg-white", "text-red-600"],
  [ScrollText, "Private activity log", "A simple history of everything blocked or flagged. Stored only on your PC. No accounts, no tracking.", "bg-emerald-50", "text-emerald-700"],
];

export default function Features() {
  return (
    <section id="features" className="py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700 sm:text-sm">What it does</p>
        <h2 className="font-display mt-3 max-w-2xl text-3xl font-extrabold text-slate-900 sm:text-4xl">
          Built around how tech-support scams actually work.
        </h2>
        <p className="mt-4 max-w-2xl text-base text-slate-600 md:text-lg">
          Almost every scam call ends the same way: "install this app so I can fix your computer." Guardian Shield breaks that step.
        </p>
        <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map(([Icon, title, text, cls, iconCls]) => (
            <article
              key={title}
              data-testid={`feature-card-${title.split(" ")[0].toLowerCase()}`}
              className={`group rounded-2xl border border-slate-200 p-7 transition-transform duration-300 hover:-translate-y-1 md:p-8 ${cls}`}
            >
              <Icon className={`h-9 w-9 ${iconCls}`} strokeWidth={2} />
              <h3 className="font-display mt-6 text-xl font-bold sm:text-2xl">{title}</h3>
              <p className={`mt-3 text-base leading-relaxed ${cls.includes("slate-900") ? "text-slate-300" : "text-slate-600"}`}>{text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

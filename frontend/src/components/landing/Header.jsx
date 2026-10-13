import { ShieldCheck, Download } from "lucide-react";
import { DOWNLOAD_URL } from "@/lib/api";

const links = [
  ["Check a link", "#checker"],
  ["Features", "#features"],
  ["See a warning", "#preview"],
  ["Install", "#install"],
  ["FAQ", "#faq"],
];

export const Logo = () => (
  <a href="#top" data-testid="brand-logo" className="flex items-center gap-2.5">
    <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-600 text-white">
      <ShieldCheck className="h-6 w-6" strokeWidth={2.4} />
    </span>
    <span className="font-display text-xl font-extrabold text-slate-900">Guardian Shield</span>
  </a>
);

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/85 backdrop-blur-xl">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo />
        <nav className="hidden items-center gap-8 lg:flex">
          {links.map(([label, href]) => (
            <a
              key={href}
              href={href}
              data-testid={`nav-${href.slice(1)}-link`}
              className="text-base font-medium text-slate-600 transition-colors hover:text-emerald-700"
            >
              {label}
            </a>
          ))}
        </nav>
        <a
          href={DOWNLOAD_URL}
          data-testid="header-download-button"
          className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-emerald-700"
        >
          <Download className="h-4 w-4" /> <span className="hidden sm:inline">Download free</span>
          <span className="sm:hidden">Get it</span>
        </a>
      </div>
    </header>
  );
}

import { ShieldCheck, Download, Coffee } from "lucide-react";

export const COFFEE_URL = "https://buymeacoffee.com/trcmsp";
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
    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-emerald-600 text-white sm:h-10 sm:w-10">
      <ShieldCheck className="h-6 w-6" strokeWidth={2.4} />
    </span>
    <span className="font-display whitespace-nowrap text-base font-extrabold text-slate-900 sm:text-xl">Simple Scam Protection</span>
  </a>
);

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/85 backdrop-blur-xl">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo />
        <nav className="hidden items-center gap-7 lg:flex">
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
          <a
            href={COFFEE_URL}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="nav-coffee-link"
            className="inline-flex items-center gap-2 whitespace-nowrap rounded-full bg-[#FFDD00] px-4 py-2 text-sm font-bold text-slate-900 transition-colors hover:bg-[#FACC15]"
          >
            <Coffee className="h-4 w-4" /> Buy me a coffee
          </a>
        </nav>
        <div className="flex shrink-0 items-center gap-2">
        <a
          href={COFFEE_URL}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="mobile-coffee-link"
          aria-label="Buy me a coffee"
          className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[#FFDD00] text-slate-900 lg:hidden"
        >
          <Coffee className="h-5 w-5" />
        </a>
        <a
          href={DOWNLOAD_URL}
          data-testid="header-download-button"
          className="inline-flex shrink-0 items-center gap-2 whitespace-nowrap rounded-full bg-slate-900 px-4 py-2.5 sm:px-5 text-sm font-bold text-white transition-colors hover:bg-emerald-700"
        >
          <Download className="h-4 w-4" /> <span className="hidden sm:inline">Download free</span>
          <span className="sm:hidden">Get it</span>
        </a>
        </div>
      </div>
    </header>
  );
}

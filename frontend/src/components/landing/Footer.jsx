import { Coffee } from "lucide-react";
import { Logo, COFFEE_URL } from "@/components/landing/Header";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <Logo />
        <a href={COFFEE_URL} target="_blank" rel="noopener noreferrer" data-testid="footer-coffee-link" className="inline-flex items-center gap-2 self-start whitespace-nowrap rounded-full bg-[#FFDD00] px-4 py-2 text-sm font-bold text-slate-900 hover:bg-[#FACC15] md:self-auto">
          <Coffee className="h-4 w-4" /> Buy me a coffee
        </a>
        <p className="text-sm text-slate-500" data-testid="footer-note">
          Free anti-scam tool for Windows 10 & 11 · Not affiliated with Microsoft or any listed software vendor.
        </p>
      </div>
    </footer>
  );
}

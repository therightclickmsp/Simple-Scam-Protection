import { Logo } from "@/components/landing/Header";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <Logo />
        <p className="text-sm text-slate-500" data-testid="footer-note">
          Free anti-scam tool for Windows 10 & 11 · Not affiliated with Microsoft or any listed software vendor.
        </p>
      </div>
    </footer>
  );
}

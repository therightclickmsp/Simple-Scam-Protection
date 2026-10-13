import { Download, Info } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DOWNLOAD_URL } from "@/lib/api";
import RmmGuide from "@/components/landing/RmmGuide";

const PC_STEPS = [
  ["Download & extract the zip", "Click the green button. Save the zip, then right-click it and choose \"Extract All\"."],
  ["Double-click build_exe.bat", "It fetches everything it needs by itself - including a private copy of Python - and builds the installer and the MSI. Takes a few minutes. Nothing else on the PC is changed."],
  ["Run SimpleScamProtectionSetup.exe", "You'll find it in the \"dist\" folder. Python is bundled inside, so you can copy this one file to any PC - including a relative's."],
  ["That's it - you're protected", "Simple Scam Protection scans for remote-access tools, then sits in the taskbar tray showing \"Protected\". It starts with Windows."],
];
const GH_STEPS = [
  ["Upload to GitHub", "Create a free GitHub repository and upload the extracted folder."],
  ["Let GitHub build it", "The included workflow builds SimpleScamProtectionSetup.exe, an MSI and a portable SimpleScamProtection.exe on a Windows machine."],
  ["Download the installer", "Open the \"Actions\" tab, pick the latest run, and download \"SimpleScamProtection-windows\" under Artifacts."],
  ["Install on any PC", "Double-click SimpleScamProtectionSetup.exe - or deploy it silently with your RMM (see the IT tab)."],
];

const Steps = ({ steps, prefix }) => (
  <ol className="grid grid-cols-1 gap-5 md:grid-cols-2">
    {steps.map(([title, text], i) => (
      <li key={title} data-testid={`${prefix}-step-${i + 1}`} className="flex min-w-0 gap-4 rounded-2xl border border-slate-200 bg-white p-5 sm:gap-5 sm:p-6">
        <span className="font-display grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-emerald-600 text-xl font-extrabold text-white">{i + 1}</span>
        <div className="min-w-0 [overflow-wrap:anywhere]">
          <h3 className="font-display text-xl font-bold text-slate-900">{title}</h3>
          <p className="mt-1.5 text-base leading-relaxed text-slate-600">{text}</p>
        </div>
      </li>
    ))}
  </ol>
);

const TAB = "rounded-lg px-4 py-2.5 text-sm font-semibold sm:px-5 sm:text-base";

export default function InstallGuide() {
  return (
    <section id="install" className="bg-white py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700 sm:text-sm">Download & install</p>
            <h2 className="font-display mt-3 text-3xl font-extrabold text-slate-900 sm:text-4xl">Set it up in four steps</h2>
          </div>
          <a href={DOWNLOAD_URL} data-testid="download-install-button" className="inline-flex items-center gap-2.5 self-start rounded-2xl bg-emerald-600 px-7 py-4 text-lg font-bold text-white transition-colors hover:bg-emerald-700">
            <Download className="h-5 w-5" /> Download the app (zip)
          </a>
        </div>
        <Tabs defaultValue="pc" className="mt-10">
          <TabsList className="h-auto flex-wrap justify-start rounded-xl bg-slate-100 p-1.5">
            <TabsTrigger value="pc" data-testid="install-tab-pc" className={TAB}>Build on this PC</TabsTrigger>
            <TabsTrigger value="github" data-testid="install-tab-github" className={TAB}>Build on GitHub</TabsTrigger>
            <TabsTrigger value="rmm" data-testid="install-tab-rmm" className={TAB}>IT / RMM silent install</TabsTrigger>
          </TabsList>
          <TabsContent value="pc" className="mt-6"><Steps steps={PC_STEPS} prefix="pc" /></TabsContent>
          <TabsContent value="github" className="mt-6"><Steps steps={GH_STEPS} prefix="github" /></TabsContent>
          <TabsContent value="rmm" className="mt-6"><RmmGuide /></TabsContent>
        </Tabs>
        <div data-testid="smartscreen-notice" className="mt-8 flex gap-4 rounded-2xl border border-amber-300 bg-amber-50 p-6">
          <Info className="h-6 w-6 shrink-0 text-amber-700" />
          <p className="text-base leading-relaxed text-slate-800">
            <strong>"Windows protected your PC"?</strong> That's expected - Simple Scam Protection is free and not
            code-signed yet. Click <strong>More info</strong>, then <strong>Run anyway</strong>. The installer asks for
            administrator permission once.
          </p>
        </div>
      </div>
    </section>
  );
}

import { Download, Info } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DOWNLOAD_URL } from "@/lib/api";

const PC_STEPS = [
  ["Download the zip", "Click the green button below. Save GuardianShield-1.0.0-windows.zip, then right-click it and choose \"Extract All\"."],
  ["Install Python (one time)", "Get the free installer from python.org/downloads. On the first screen, tick \"Add Python to PATH\"."],
  ["Double-click build_exe.bat", "It prepares everything and creates GuardianShield.exe in the \"dist\" folder. Takes 1-3 minutes."],
  ["Run GuardianShield.exe", "It scans for remote-access tools, then moves to your taskbar tray showing \"Protected\". It starts with Windows automatically."],
];
const GH_STEPS = [
  ["Upload to GitHub", "Create a free GitHub repository and upload the extracted folder."],
  ["Let GitHub build it", "The included workflow (.github/workflows) builds the .exe automatically on a Windows machine."],
  ["Download the .exe", "Open the \"Actions\" tab, pick the latest run, and download \"GuardianShield-exe\" under Artifacts."],
  ["Copy to the PC", "Put GuardianShield.exe on your relative's PC and double-click it. No account or setup needed."],
];

const Steps = ({ steps, prefix }) => (
  <ol className="grid gap-5 md:grid-cols-2">
    {steps.map(([title, text], i) => (
      <li key={title} data-testid={`${prefix}-step-${i + 1}`} className="flex gap-5 rounded-2xl border border-slate-200 bg-white p-6">
        <span className="font-display grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-emerald-600 text-xl font-extrabold text-white">{i + 1}</span>
        <div>
          <h3 className="font-display text-xl font-bold text-slate-900">{title}</h3>
          <p className="mt-1.5 text-base leading-relaxed text-slate-600">{text}</p>
        </div>
      </li>
    ))}
  </ol>
);

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
          <TabsList className="h-auto rounded-xl bg-slate-100 p-1.5">
            <TabsTrigger value="pc" data-testid="install-tab-pc" className="rounded-lg px-5 py-2.5 text-base font-semibold">Build on this PC</TabsTrigger>
            <TabsTrigger value="github" data-testid="install-tab-github" className="rounded-lg px-5 py-2.5 text-base font-semibold">Build on GitHub</TabsTrigger>
          </TabsList>
          <TabsContent value="pc" className="mt-6"><Steps steps={PC_STEPS} prefix="pc" /></TabsContent>
          <TabsContent value="github" className="mt-6"><Steps steps={GH_STEPS} prefix="github" /></TabsContent>
        </Tabs>
        <div data-testid="smartscreen-notice" className="mt-8 flex gap-4 rounded-2xl border border-amber-300 bg-amber-50 p-6">
          <Info className="h-6 w-6 shrink-0 text-amber-700" />
          <p className="text-base leading-relaxed text-slate-800">
            <strong>"Windows protected your PC"?</strong> That's expected - Guardian Shield is free and not
            code-signed yet. Click <strong>More info</strong>, then <strong>Run anyway</strong>. Turning on scam-website
            blocking will ask for administrator permission once.
          </p>
        </div>
      </div>
    </section>
  );
}

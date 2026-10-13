import { Copy } from "lucide-react";
import { toast } from "sonner";

const INSTALL = 'SimpleScamProtectionSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /ALLOW=screenconnect /LOG="C:\\Windows\\Temp\\SimpleScamProtection.log"';
const UNINSTALL = '"C:\\Program Files\\Simple Scam Protection\\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART';
const HASH = "SimpleScamProtection.exe --hash-password";
const MSI = 'msiexec /i SimpleScamProtection.msi /qn /norestart ALLOW=screenconnect';
const MSI_UNINSTALL = "msiexec /x SimpleScamProtection.msi /qn /norestart";

const OPTIONS = [
  ["/ALLOW=screenconnect,teamviewer", "Pre-trust your own remote tools so your RMM / remote agent is never blocked"],
  ["/PASSWORDHASH=pbkdf2_sha256$…", "Lock settings & uninstall with a password (hash only - no plain password in scripts)"],
  ["/NOAUTOSTART", "Don't start for every user at logon"],
  ["/NOSITEBLOCK", "Don't add the scam-site block to the hosts file"],
  ["/NOPOPUPBLOCK", "Don't close fake virus pop-ups by default"],
  ['/DIR="D:\\Apps\\Simple Scam Protection"', "Custom install folder"],
];

const Cmd = ({ label, value, id }) => (
  <div>
    <p className="mb-2 text-sm font-semibold text-slate-500">{label}</p>
    <div className="flex items-start gap-3 rounded-xl bg-slate-900 p-4">
      <code data-testid={`rmm-cmd-${id}`} className="font-mono-gs flex-1 break-all text-sm leading-relaxed text-emerald-300">{value}</code>
      <button
        data-testid={`rmm-copy-${id}`}
        onClick={() => { navigator.clipboard?.writeText(value); toast.success("Command copied"); }}
        className="shrink-0 rounded-lg bg-slate-800 p-2 text-slate-300 transition-colors hover:bg-slate-700 hover:text-white"
        aria-label="Copy command"
      >
        <Copy className="h-4 w-4" />
      </button>
    </div>
  </div>
);

export default function RmmGuide() {
  return (
    <div data-testid="rmm-guide" className="grid gap-8 rounded-2xl border border-slate-200 bg-slate-50 p-6 md:p-8 lg:grid-cols-2">
      <div className="space-y-6">
        <p className="text-base leading-relaxed text-slate-700">
          Works with any RMM, Intune, PDQ, SCCM or Group Policy - choose Setup.exe or the MSI. Runs as SYSTEM, installs per-machine to Program Files and
          auto-starts for every user. Python is bundled - no prerequisites.
        </p>
        <Cmd id="install" label="Silent install (Setup.exe)" value={INSTALL} />
        <Cmd id="uninstall" label="Silent uninstall (Setup.exe)" value={UNINSTALL} />
        <Cmd id="msi" label="MSI install (Intune / Group Policy / SCCM)" value={MSI} />
        <Cmd id="msi-uninstall" label="MSI uninstall" value={MSI_UNINSTALL} />
        <Cmd id="hash" label="Create a password hash (run once on any PC)" value={HASH} />
      </div>
      <div>
        <p className="mb-3 text-sm font-semibold text-slate-500">Installer options <span className="font-normal">(MSI: same names without the slash, e.g. NOAUTOSTART=1)</span></p>
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
          {OPTIONS.map(([flag, text]) => (
            <li key={flag} className="p-4">
              <code className="font-mono-gs break-all text-sm font-semibold text-slate-900">{flag}</code>
              <p className="mt-1 text-sm text-slate-600">{text}</p>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-sm text-slate-500">
          Change policy later without reinstalling: <code className="font-mono-gs">SimpleScamProtection.exe --configure --allow …</code>.
          Policy lives in C:\ProgramData\SimpleScamProtection (admin-only).
        </p>
      </div>
    </div>
  );
}

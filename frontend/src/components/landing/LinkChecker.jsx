import { useState } from "react";
import axios from "axios";
import { Loader2, ShieldCheck, ShieldAlert, ShieldX, Copy } from "lucide-react";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";
import { API } from "@/lib/api";

const PRESETS = [
  ["Fake virus pop-up", "WARNING! Your computer is infected with a Trojan virus. Do not shut down your PC. Call Microsoft Support immediately at 1-844-555-0199 or visit support-microsoft-alert-fix.cc"],
  ["Lookalike PayPal", "https://paypa1-secure-login.xyz/verify-account"],
  ["Refund scam", "Your Norton subscription was renewed for $399.99. To get a refund call us today and install AnyDesk so our technician can process it."],
  ["Real Amazon link", "https://www.amazon.com/your-orders"],
];

const STYLES = {
  safe: { Icon: ShieldCheck, label: "Looks safe", box: "border-emerald-300 bg-emerald-50", ink: "text-emerald-700" },
  suspicious: { Icon: ShieldAlert, label: "Suspicious - be careful", box: "border-amber-300 bg-amber-50", ink: "text-amber-700" },
  dangerous: { Icon: ShieldX, label: "Dangerous - do not click", box: "border-red-300 bg-red-50", ink: "text-red-700" },
};

const Verdict = ({ result }) => {
  const s = STYLES[result.verdict];
  const copy = () => {
    navigator.clipboard?.writeText(`Simple Scam Protection says: ${s.label.toUpperCase()}\n- ${result.reasons.join("\n- ")}`);
    toast.success("Result copied - share it with family");
  };
  return (
    <div data-testid="link-checker-verdict-card" className={`rise rounded-2xl border-2 p-6 md:p-8 ${s.box}`}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className={`flex items-center gap-3 ${s.ink}`}>
          <s.Icon className="h-10 w-10" strokeWidth={2.2} />
          <p data-testid="link-checker-verdict" className="font-display text-2xl font-extrabold sm:text-3xl">{s.label}</p>
        </div>
        <div className="flex items-center gap-3">
          <span data-testid="link-checker-score" className="font-mono-gs rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700">risk {result.score}/100</span>
          <button onClick={copy} data-testid="link-checker-copy-button" className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-100">
            <Copy className="h-4 w-4" /> Copy
          </button>
        </div>
      </div>
      <ul className="mt-5 space-y-2.5" data-testid="link-checker-reasons">
        {result.reasons.map((r, i) => (
          <li key={i} className="flex gap-3 text-base leading-relaxed text-slate-800 md:text-lg">
            <span className={`mt-2.5 h-2 w-2 shrink-0 rounded-full ${s.ink.replace("text", "bg")}`} />
            <span className="break-words">{r}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default function LinkChecker() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async (value = text) => {
    if (!value.trim()) return toast.error("Paste a link or message first");
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/check`, { text: value });
      setResult(data);
    } catch {
      toast.error("Couldn't check right now. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="checker" className="bg-white py-16 md:py-24">
      <div className="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[0.8fr_1.2fr] lg:px-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-700 sm:text-sm">Try it now</p>
          <h2 className="font-display mt-3 text-3xl font-extrabold text-slate-900 sm:text-4xl">Is this link or message a scam?</h2>
          <p className="mt-4 text-base leading-relaxed text-slate-600 md:text-lg">
            Paste a suspicious text, email or web address. You'll get a plain-English answer in a second. The same
            checker is built into the Windows app and works offline.
          </p>
          <p className="mt-6 text-sm font-semibold text-slate-500">Try an example:</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {PRESETS.map(([label, value], i) => (
              <button
                key={label}
                data-testid={`link-checker-preset-${i}`}
                onClick={() => { setText(value); run(value); }}
                className="rounded-full border border-slate-300 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:border-slate-900 hover:bg-white"
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 focus-within:border-blue-500">
            <Textarea
              data-testid="link-checker-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. 'Your PC has 5 viruses! Call Microsoft at 1-800-555-0199' or http://paypa1-login.xyz"
              className="min-h-[150px] resize-none border-0 bg-transparent text-lg shadow-none focus-visible:ring-0"
            />
            <div className="flex items-center justify-between border-t border-slate-200 pt-4">
              <span className="text-sm text-slate-500">Rule-based · no AI · nothing is stored</span>
              <button
                data-testid="link-checker-submit-button"
                onClick={() => run()}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-base font-bold text-white transition-colors hover:bg-blue-700 disabled:opacity-60"
              >
                {loading && <Loader2 className="h-4 w-4 animate-spin" />} Check it
              </button>
            </div>
          </div>
          {result && <Verdict result={result} />}
        </div>
      </div>
    </section>
  );
}

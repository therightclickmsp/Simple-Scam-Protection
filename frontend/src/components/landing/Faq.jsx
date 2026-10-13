import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const FAQ = [
  ["Is Guardian Shield really free?", "Yes. No subscription, no account, no ads. Everything runs on your PC."],
  ["Does it send my data anywhere?", "No. The activity log and settings stay in your Windows user folder. The link checker in the app works fully offline."],
  ["Can I install it on my parents' PC?", "That's exactly who it's for. Install it once and it starts with Windows, runs in the tray and needs no attention. Warnings are big and written in plain language."],
  ["What if I use TeamViewer or AnyDesk for work?", "Open Settings & Trusted, select the tool and type the confirmation phrase. That tool will then be allowed. The typed step is there so a scammer can't casually talk someone through it."],
  ["Why does Windows show a warning when I run it?", "The app isn't code-signed yet, so Windows SmartScreen doesn't recognise the publisher. Click More info, then Run anyway."],
  ["Is it an antivirus?", "No. It targets the specific tricks tech-support scammers use. Keep Windows Defender (or your antivirus) turned on as well."],
  ["Can it catch every remote tool or scam link?", "It recognises well-known tools by name and checks links with rules. Brand-new or renamed tools and brand-new scam sites may be missed - when in doubt, hang up and call a family member."],
];

export default function Faq() {
  return (
    <section id="faq" className="py-16 md:py-24">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-[0.7fr_1.3fr] lg:px-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700 sm:text-sm">Questions</p>
          <h2 className="font-display mt-3 text-3xl font-extrabold text-slate-900 sm:text-4xl">Good to know</h2>
          <p className="mt-4 text-base text-slate-600 md:text-lg">The one rule that beats every scam: <strong>real companies never call you to fix your computer.</strong></p>
        </div>
        <Accordion type="single" collapsible className="space-y-3">
          {FAQ.map(([q, a], i) => (
            <AccordionItem key={q} value={`q${i}`} data-testid={`faq-accordion-item-${i}`} className="rounded-2xl border border-slate-200 bg-white px-6">
              <AccordionTrigger data-testid={`faq-trigger-${i}`} className="py-5 text-left text-lg font-bold text-slate-900 hover:no-underline">{q}</AccordionTrigger>
              <AccordionContent className="pb-5 text-base leading-relaxed text-slate-600">{a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}

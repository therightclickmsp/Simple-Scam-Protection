import Header from "@/components/landing/Header";
import Hero from "@/components/landing/Hero";
import ToolsStrip from "@/components/landing/ToolsStrip";
import Features from "@/components/landing/Features";
import LinkChecker from "@/components/landing/LinkChecker";
import AlertPreview from "@/components/landing/AlertPreview";
import InstallGuide from "@/components/landing/InstallGuide";
import Faq from "@/components/landing/Faq";
import Footer from "@/components/landing/Footer";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <Header />
      <main>
        <Hero />
        <ToolsStrip />
        <LinkChecker />
        <Features />
        <AlertPreview />
        <InstallGuide />
        <Faq />
      </main>
      <Footer />
    </div>
  );
}

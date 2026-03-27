import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { PsychReportPreview } from "@/components/landing/PsychReportPreview";
import { TechStack } from "@/components/landing/TechStack";
import { GitaWisdom } from "@/components/landing/GitaWisdom";
import { Privacy } from "@/components/landing/Privacy";
import { Team } from "@/components/landing/Team";
import { Footer } from "@/components/landing/Footer";

const Landing = () => {
  return (
    <div className="font-sans text-slate-900 bg-white overflow-hidden relative">

      <Navbar />
      <Hero />
      <Features />
      <PsychReportPreview />
      <TechStack />
      <GitaWisdom />
      <Privacy />
      <Team />
      <Footer />
    </div>
  );
};

export default Landing;

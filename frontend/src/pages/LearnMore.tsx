import { Navbar } from "@/components/landing/Navbar";
// import { LearnMoreHero } from "@/components/learn-more/LearnMoreHero";
import { Overview } from "@/components/learn-more/Overview";
import { Technology } from "@/components/learn-more/Technology";
import { LearnMoreFeatures } from "@/components/learn-more/LearnMoreFeatures";
import { HowItWorks } from "@/components/learn-more/HowItWorks";
import { ScopeLimitations } from "@/components/learn-more/ScopeLimitations";
import { PerformanceStats } from "@/components/learn-more/PerformanceStats";
import { CallToAction } from "@/components/learn-more/CallToAction";
import { Footer } from "@/components/landing/Footer";

const LearnMore = () => {
  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 overflow-hidden">
      <Navbar />
      {/* <LearnMoreHero /> */}
      <Overview />
      <Technology />
      <LearnMoreFeatures />
      <HowItWorks />
      <ScopeLimitations />
      <PerformanceStats />
      <CallToAction />
      <Footer />
    </div>
  );
};

export default LearnMore;

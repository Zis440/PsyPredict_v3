import { Cpu, Sparkles, Video, Lightbulb } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import BlurFade from "@/components/magicui/blur-fade";
import { BentoGrid, BentoCard } from "@/components/magicui/bento-grid";
import { DotPattern } from "@/components/magicui/dot-pattern";
import { Meteors } from "@/components/magicui/meteors";

export const Features = () => {
  return (
    <section className="bg-slate-50/50 py-24 px-6 relative overflow-hidden">
      <div className="max-w-6xl mx-auto text-center mb-16 relative z-10">
        <BlurFade delay={0.1} inView>
          <Badge variant="outline" className="mb-4 border-indigo-200 text-indigo-600 bg-white">
            Core Intelligence
          </Badge>
        </BlurFade>
        <BlurFade delay={0.2} inView>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Multimodal Precision. Clinical Depth.
          </h2>
        </BlurFade>
        <BlurFade delay={0.3} inView>
          <p className="text-slate-500 max-w-2xl mx-auto">
            PsyPredict combines three layers of intelligence to provide a clinical-grade
            assessment of your mental well-being in real-time.
          </p>
        </BlurFade>
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        <BentoGrid>
          <BentoCard
            name="Multimodal Fusion"
            className="col-span-3 lg:col-span-2"
            Icon={Cpu}
            description="A weighted fusion engine combining (Text × 0.65) and (Face × 0.35) into a unified distress score for maximum accuracy."
            href="/learn-more"
            cta="Learn about the math"
            nameClassName="text-white drop-shadow-md"
            descriptionClassName="text-slate-200"
            iconClassName="text-indigo-400"
            background={
              <div className="absolute inset-0 overflow-hidden bg-slate-950">
                <img src="/images/abstract_neural_fusion_1773465841683.png" className="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-500 group-hover:scale-110" alt="" />
                <DotPattern className="opacity-40" />
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/30 via-transparent to-purple-500/30" />
              </div>
            }
          />
          <BentoCard
            name="Crisis Detection"
            className="col-span-3 lg:col-span-1"
            Icon={Sparkles}
            description="Zero-shot NLI classification across 5 risk dimensions. Not just keywords, but deep semantic understanding."
            href="/learn-more"
            cta="Detection logic"
            nameClassName="text-white drop-shadow-md"
            descriptionClassName="text-slate-200"
            iconClassName="text-indigo-400"
            background={
              <div className="absolute inset-0 overflow-hidden bg-slate-950">
                <img src="/images/abstract_emotion_waveforms_1773465858662.png" className="absolute inset-0 w-full h-full object-cover opacity-60 transition-transform duration-500 group-hover:scale-110" alt="" />
                <Meteors number={15} />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />
              </div>
            }
          />
          <BentoCard
            name="Facial Analysis"
            className="col-span-3 lg:col-span-1"
            Icon={Video}
            description="Live Keras CNN monitoring detecting 7 emotional classes via webcam with sub-second latency."
            href="/learn-more"
            cta="View camera tech"
            nameClassName="text-white drop-shadow-md"
            descriptionClassName="text-slate-200"
            iconClassName="text-emerald-400"
            background={
              <div className="absolute inset-0 overflow-hidden bg-slate-950">
                <img src="/images/abstract_calm_nature_tech_fusion_1773465873966.png" className="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-500 group-hover:scale-110" alt="" />
                <DotPattern className="opacity-30" />
                <div className="absolute inset-0 bg-slate-900/60 mix-blend-multiply" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
              </div>
            }
          />
          <BentoCard
            name="Clinical PsychReport"
            className="col-span-3 lg:col-span-2"
            Icon={Lightbulb}
            description="Every interaction generates a structured report including risk levels, cognitive distortions (CBT), and actionable interventions."
            href="/learn-more"
            cta="See sample report"
            nameClassName="text-white drop-shadow-md"
            descriptionClassName="text-slate-200"
            iconClassName="text-amber-400"
            background={
              <div className="absolute inset-0 overflow-hidden bg-slate-950">
                <img src="/images/abstract_clinical_data_grid_1773465889600.png" className="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-500 group-hover:scale-110" alt="" />
                <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/20 via-transparent to-indigo-500/20" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
              </div>
            }
          />
        </BentoGrid>
      </div>
    </section>
  );
};

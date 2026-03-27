import { Cpu, Sparkles, Video, FileText, BookOpen, Shield } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Badge } from "@/components/ui/badge";
import { MagicCard } from "@/components/magicui/magic-card";
import { cn } from "@/lib/utils";

const features = [
  {
    icon: Cpu,
    title: "Multimodal Fusion Engine",
    desc: "Weighted fusion (Text × 0.65 + Face × 0.35) creates a unified distress score, outperforming single-modality systems.",
    color: "text-indigo-500",
    bg: "bg-indigo-50",
  },
  {
    icon: Sparkles,
    title: "Crisis Detection",
    desc: "Zero-shot NLI classification across 5 risk dimensions provides deep semantic understanding, not just keyword matching.",
    color: "text-rose-500",
    bg: "bg-rose-50",
  },
  {
    icon: Video,
    title: "Facial Emotion Analysis",
    desc: "Live Keras CNN monitoring detects 7 emotional classes via webcam with sub-second latency and a rolling emotion buffer.",
    color: "text-emerald-500",
    bg: "bg-emerald-50",
  },
  {
    icon: FileText,
    title: "Clinical PsychReport",
    desc: "Every session generates a structured report with risk levels, cognitive distortions (CBT), and actionable interventions.",
    color: "text-amber-500",
    bg: "bg-amber-50",
  },
  {
    icon: BookOpen,
    title: "Gita Wisdom Integration",
    desc: "Maps detected emotional states to culturally relevant verses and stories for holistic, dharma-based resilience.",
    color: "text-purple-500",
    bg: "bg-purple-50",
  },
  {
    icon: Shield,
    title: "Encrypted History",
    desc: "Secure user accounts with encrypted session storage. Your data is private, accessible only to you, and deletable anytime.",
    color: "text-sky-500",
    bg: "bg-sky-50",
  },
];

export const LearnMoreFeatures = () => {
  return (
    <section className="bg-slate-50/60 py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <BlurFade delay={0.1} inView>
            <Badge
              variant="outline"
              className="mb-4 border-indigo-200 text-indigo-600 bg-white"
            >
              Capabilities
            </Badge>
          </BlurFade>
          <BlurFade delay={0.2} inView>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Core Features
            </h2>
          </BlurFade>
          <BlurFade delay={0.3} inView>
            <p className="text-slate-500 max-w-2xl mx-auto">
              Six pillars of intelligence that power every PsyPredict session.
            </p>
          </BlurFade>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <BlurFade key={i} delay={0.05 + i * 0.08} inView>
              <MagicCard
                className="p-6 border-slate-200 bg-white h-full"
                gradientColor="#6366f1"
                gradientOpacity={0.05}
              >
                <div
                  className={cn(
                    "w-11 h-11 rounded-xl flex items-center justify-center mb-4",
                    f.bg,
                    f.color
                  )}
                >
                  <f.icon size={22} />
                </div>
                <h3 className="font-bold text-base mb-2">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {f.desc}
                </p>
              </MagicCard>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
};

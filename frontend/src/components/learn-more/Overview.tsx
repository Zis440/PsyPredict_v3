import { Brain, Shield, BookOpen } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Badge } from "@/components/ui/badge";
import { MagicCard } from "@/components/magicui/magic-card";

const benefits = [
  {
    icon: Brain,
    title: "Multimodal Intelligence",
    desc: "Combines facial, textual, and contextual signals for a holistic emotional read — far more reliable than any single modality.",
  },
  {
    icon: Shield,
    title: "Safety-First Design",
    desc: "Built-in crisis detection ensures harm-averse behaviour at all times, with immediate safety overrides when needed.",
  },
  {
    icon: BookOpen,
    title: "Culturally Grounded",
    desc: "Integrates timeless wisdom from the Bhagavad Gita to complement AI reasoning with culturally resonant guidance.",
  },
];

export const Overview = () => {
  return (
    <section className="bg-slate-50/60 py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <BlurFade delay={0.1} inView>
            <Badge
              variant="outline"
              className="mb-4 border-indigo-200 text-indigo-600 bg-white"
            >
              Overview
            </Badge>
          </BlurFade>
          <BlurFade delay={0.2} inView>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              What Is PsyPredict?
            </h2>
          </BlurFade>
          <BlurFade delay={0.3} inView>
            <p className="text-slate-500 max-w-3xl mx-auto">
              Mental health conditions affect millions worldwide, yet many remain
              undiagnosed due to limited access, stigma, and delayed screening.
              PsyPredict explores how AI can support early self-awareness using
              everyday tools like webcams and conversational text — without
              replacing clinical care.
            </p>
          </BlurFade>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {benefits.map((b, i) => (
            <BlurFade key={i} delay={0.1 + i * 0.1} inView>
              <MagicCard
                className="p-8 border-slate-200 bg-white"
                gradientColor="#6366f1"
                gradientOpacity={0.06}
              >
                <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 mb-5">
                  <b.icon size={24} />
                </div>
                <h3 className="font-bold text-lg mb-2">{b.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {b.desc}
                </p>
              </MagicCard>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
};

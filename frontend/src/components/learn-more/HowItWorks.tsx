import { motion } from "framer-motion";
import { MessageSquare, Brain, Layers, FileText, ChevronRight } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Badge } from "@/components/ui/badge";

const steps = [
  {
    num: "01",
    title: "Input",
    desc: "Share your thoughts via text while the webcam captures facial micro-expressions in real time.",
    icon: MessageSquare,
  },
  {
    num: "02",
    title: "Analysis",
    desc: "DistilBERT analyses text for psychological signals while a Keras CNN classifies facial emotions frame-by-frame.",
    icon: Brain,
  },
  {
    num: "03",
    title: "Fusion",
    desc: "A transformer-based multimodal architecture fuses visual and linguistic features into a single distress score.",
    icon: Layers,
  },
  {
    num: "04",
    title: "Report",
    desc: "Llama3 generates an empathetic, guardrailed PsychReport with CBT patterns, risk levels, and interventions.",
    icon: FileText,
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-24 px-6 bg-white">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <BlurFade delay={0.1} inView>
            <Badge
              variant="outline"
              className="mb-4 border-emerald-200 text-emerald-600 bg-white"
            >
              Process
            </Badge>
          </BlurFade>
          <BlurFade delay={0.2} inView>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How PsyPredict Works
            </h2>
          </BlurFade>
          <BlurFade delay={0.3} inView>
            <p className="text-slate-500 max-w-2xl mx-auto">
              From input to insight — a seamless four-step pipeline that runs in
              real time.
            </p>
          </BlurFade>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {steps.map((s, i) => (
            <BlurFade key={i} delay={0.1 + i * 0.12} inView>
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="relative"
              >
                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 h-full text-center">
                  <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 mx-auto mb-4">
                    <s.icon size={22} />
                  </div>
                  <p className="text-xs font-bold text-indigo-600 uppercase tracking-widest mb-2">
                    Step {s.num}
                  </p>
                  <h3 className="font-bold text-lg mb-2">{s.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">
                    {s.desc}
                  </p>
                </div>
                {/* Connector arrow (hidden on last item and on mobile) */}
                {i < steps.length - 1 && (
                  <div className="hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-indigo-600 items-center justify-center text-white">
                    <ChevronRight size={14} />
                  </div>
                )}
              </motion.div>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
};

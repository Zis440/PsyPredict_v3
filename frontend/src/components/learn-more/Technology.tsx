import { Server, Zap, Cpu, Brain } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Badge } from "@/components/ui/badge";
import { MagicCard } from "@/components/magicui/magic-card";

export const Technology = () => {
  return (
    <section id="technology" className="py-24 px-6 bg-white relative overflow-hidden">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <BlurFade delay={0.1} inView>
            <Badge
              variant="outline"
              className="mb-4 border-indigo-200 text-indigo-600 bg-white"
            >
              Technology
            </Badge>
          </BlurFade>
          <BlurFade delay={0.2} inView>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powered by Llama3
            </h2>
          </BlurFade>
          <BlurFade delay={0.3} inView>
            <p className="text-slate-500 max-w-3xl mx-auto">
              PsyPredict's reasoning engine is built on{" "}
              <strong className="text-slate-800">Llama3</strong> — an
              instruction-tuned large language model that delivers empathetic,
              clinically-informed responses with cutting-edge performance and
              reliability.
            </p>
          </BlurFade>
        </div>

        {/* Llama3 Hero Card */}
        <BlurFade delay={0.15} inView>
          <MagicCard
            className="p-0 border-indigo-100 overflow-hidden bg-white max-w-3xl mx-auto"
            gradientColor="#6366f1"
            gradientOpacity={0.08}
          >
            <div className="bg-indigo-600 p-5 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <Server size={20} className="text-white" />
              </div>
              <div>
                <p className="text-white font-bold text-lg">Llama3</p>
                <p className="text-indigo-200 text-xs font-medium">
                  Production LLM Engine
                </p>
              </div>
              <Badge className="ml-auto bg-white/20 text-white border-none">
                PRIMARY
              </Badge>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-slate-600 text-sm leading-relaxed">
                Llama3 serves as PsyPredict's primary reasoning engine,
                generating empathetic, clinically-informed responses grounded in
                structured model outputs. Its large parameter count and
                instruction-tuned nature deliver nuanced understanding of
                psychological context — enabling accurate PsychReports with CBT
                pattern recognition and actionable interventions.
              </p>
              <div className="flex flex-wrap gap-2">
                {[
                  "Instruction-tuned",
                  "Empathetic generation",
                  "Guardrailed output",
                  "Clinical reasoning",
                  "Structured JSON output",
                  "Context-aware prompting",
                ].map((tag) => (
                  <Badge
                    key={tag}
                    variant="outline"
                    className="text-indigo-600 border-indigo-100 bg-indigo-50/50 text-xs"
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </MagicCard>
        </BlurFade>

        {/* Supporting Tech Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-10">
          {[
            {
              icon: Brain,
              title: "DistilBERT",
              desc: "Text emotion classification using a fine-tuned transformer model for real-time psychological signal analysis.",
              color: "text-emerald-600",
              bg: "bg-emerald-100",
            },
            {
              icon: Cpu,
              title: "Keras CNN",
              desc: "Facial emotion recognition across 7 classes with sub-second inference via webcam input.",
              color: "text-amber-600",
              bg: "bg-amber-100",
            },
            {
              icon: Zap,
              title: "Multimodal Fusion",
              desc: "Weighted fusion of text and facial signals (0.65 / 0.35) into a unified distress score for maximum accuracy.",
              color: "text-indigo-600",
              bg: "bg-indigo-100",
            },
          ].map((item, i) => (
            <BlurFade key={i} delay={0.2 + i * 0.1} inView>
              <MagicCard
                className="p-6 border-slate-200 bg-white h-full"
                gradientColor="#6366f1"
                gradientOpacity={0.05}
              >
                <div
                  className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${item.bg} ${item.color}`}
                >
                  <item.icon size={22} />
                </div>
                <h3 className="font-bold text-base mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {item.desc}
                </p>
              </MagicCard>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
};

import { motion } from "framer-motion";
import { CheckCircle, Shield } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { MagicCard } from "@/components/magicui/magic-card";

export const ScopeLimitations = () => {
  return (
    <section className="bg-slate-50/60 py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <BlurFade delay={0.1} inView>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Scope & Limitations
            </h2>
          </BlurFade>
          <BlurFade delay={0.2} inView>
            <p className="text-slate-500 max-w-2xl mx-auto">
              PsyPredict is a research-driven support tool, not a clinical
              replacement. Here's what it can and cannot do.
            </p>
          </BlurFade>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <BlurFade delay={0.15} inView>
            <MagicCard
              className="p-8 border-emerald-100 bg-white"
              gradientColor="#10b981"
              gradientOpacity={0.06}
            >
              <h3 className="text-lg font-bold text-emerald-700 mb-5 flex items-center gap-2">
                <CheckCircle size={20} />
                What PsyPredict Can Do
              </h3>
              <ul className="space-y-3">
                {[
                  "Support emotional self-awareness",
                  "Detect early mental health signals",
                  "Provide empathetic, reflective feedback",
                  "Operate in real time on common devices",
                  "Generate structured clinical-grade reports",
                ].map((text, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.05 * i, duration: 0.3 }}
                    className="flex items-start gap-3 text-sm text-slate-700"
                  >
                    <span className="mt-0.5 w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 shrink-0">
                      <CheckCircle size={12} />
                    </span>
                    {text}
                  </motion.li>
                ))}
              </ul>
            </MagicCard>
          </BlurFade>

          <BlurFade delay={0.25} inView>
            <MagicCard
              className="p-8 border-rose-100 bg-white"
              gradientColor="#f43f5e"
              gradientOpacity={0.06}
            >
              <h3 className="text-lg font-bold text-rose-700 mb-5 flex items-center gap-2">
                <Shield size={20} />
                What PsyPredict Cannot Do
              </h3>
              <ul className="space-y-3">
                {[
                  "Replace therapists or psychiatrists",
                  "Prescribe medication or treatment",
                  "Act as an emergency service",
                  "Provide a clinical diagnosis",
                ].map((text, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.05 * i, duration: 0.3 }}
                    className="flex items-start gap-3 text-sm text-slate-700"
                  >
                    <span className="mt-0.5 w-5 h-5 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 shrink-0">
                      ×
                    </span>
                    {text}
                  </motion.li>
                ))}
              </ul>
            </MagicCard>
          </BlurFade>
        </div>
      </div>
    </section>
  );
};

import { Sparkles, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import BlurFade from "@/components/magicui/blur-fade";
import { MagicCard } from "@/components/magicui/magic-card";

export const GitaWisdom = () => {
  return (
    <section className="py-24 px-6 bg-white relative overflow-hidden">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row gap-16 items-center">
        <BlurFade delay={0.1} inView className="flex-1 order-2 md:order-1">
          <MagicCard className="p-8 border-amber-100 bg-amber-50/30" gradientColor="#fde68a" gradientOpacity={0.2}>
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-700">
                  <Sparkles size={20} />
                </div>
                <h3 className="text-xl font-bold text-amber-900 underline decoration-amber-200 underline-offset-8">Gita Remedy System</h3>
              </div>

              <p className="text-amber-800/80 italic leading-relaxed">
                "You have a right to perform your prescribed duties, but you are not entitled to
                the fruits of your actions. Never consider yourself to be the cause of the results
                of your activities, nor be attached to not doing your duty."
              </p>

              <div className="pt-4 border-t border-amber-200/50">
                <p className="text-sm font-bold text-amber-900 mb-2">Analysis Context:</p>
                <p className="text-sm text-amber-800/70">
                  Applying Verse 2.47 for detected "Anxiety about outcomes" and "Over-responsibility".
                </p>
              </div>

              <Button className="w-full bg-amber-700 hover:bg-amber-800 text-white rounded-lg">
                Explore Wisdom Base
              </Button>
            </div>
          </MagicCard>
        </BlurFade>

        <div className="flex-1 order-1 md:order-2 space-y-6">
          <Badge className="bg-amber-50 text-amber-700 border-none">Ancient Intelligence</Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-slate-900 leading-tight">
            Culturally Grounded <br />
            <span className="text-amber-600">Story-Based Guidance.</span>
          </h2>
          <p className="text-slate-500 leading-relaxed">
            We complement multimodal AI with the timeless wisdom of the Bhagavad Gita.
            Our system maps detected emotional states to culturally relevant stories
            and guidance, providing a holistic path to mental resilience.
          </p>
          <ul className="space-y-4">
            {["Context-aware verse mapping", "Dharma-based resilience training", "Culturally resonant story guidance"].map((item, i) => (
              <li key={i} className="flex items-center gap-3 text-sm font-medium text-slate-700">
                <div className="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">
                  <CheckCircle size={12} />
                </div>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
};

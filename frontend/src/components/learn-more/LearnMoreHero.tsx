import { Sparkles, ArrowRight } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DotPattern } from "@/components/magicui/dot-pattern";
import { cn } from "@/lib/utils";

export const LearnMoreHero = () => {
  return (
    <section className="relative w-full overflow-hidden">
      <DotPattern
        className={cn(
          "[mask-image:radial-gradient(900px_circle_at_center,white,transparent)]",
          "absolute inset-0 opacity-100 text-indigo-400/20"
        )}
      />
      <header className="relative z-10 text-center px-4 sm:px-6 pt-16 sm:pt-24 pb-20 sm:pb-28 max-w-4xl mx-auto">
        <BlurFade delay={0.2}>
          <Badge
            variant="secondary"
            className="mb-5 py-1.5 px-3 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-none rounded-full"
          >
            <Sparkles size={14} className="mr-2" /> Learn More
          </Badge>
        </BlurFade>

        <BlurFade delay={0.3}>
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-extrabold text-neutral-900 leading-tight">
            AI-Powered
          </h1>
        </BlurFade>
        <BlurFade delay={0.4}>
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-extrabold leading-tight text-indigo-700 mt-2">
            Mental Health Awareness.
          </h1>
        </BlurFade>

        <BlurFade delay={0.5}>
          <p className="text-sm sm:text-base md:text-lg text-slate-600 mt-6 mb-8 max-w-2xl mx-auto font-medium">
            PsyPredict combines facial emotion recognition, text-based psychological
            signal analysis, and large language model reasoning to support early
            mental health awareness — safely and privately.
          </p>
        </BlurFade>

        <BlurFade delay={0.6}>
          <Button
            size="lg"
            onClick={() => {
              document
                .getElementById("technology")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
            className="bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition gap-2"
          >
            Explore the Technology <ArrowRight size={16} />
          </Button>
        </BlurFade>
      </header>
    </section>
  );
};

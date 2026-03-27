import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, CheckCircle } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DotPattern } from "@/components/magicui/dot-pattern";
import { cn } from "@/lib/utils";

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative w-full overflow-hidden">
      <DotPattern
        className={cn(
          "[mask-image:radial-gradient(1000px_circle_at_center,white,transparent)]",
          "absolute inset-0 opacity-100 text-indigo-400/20",
        )}
      />
      <header className="relative z-10 text-center px-4 sm:px-6 mt-14 sm:mt-20 mb-20 sm:mb-28 max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Badge variant="secondary" className="mb-5 py-1.5 px-3 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-none rounded-full">
          <Sparkles size={14} className="mr-2" /> AI-Powered Emotional Intelligence
        </Badge>
      </motion.div>

      <div className="mb-5">
        <BlurFade delay={0.3}>
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-extrabold text-neutral-900 drop-shadow-sm leading-tight">
            Understand Your Emotions.
          </h1>
        </BlurFade>
        <BlurFade delay={0.4}>
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-extrabold leading-tight text-indigo-700 mt-2">
            Empower Your Mind.
          </h1>
        </BlurFade>
      </div>

      <BlurFade delay={0.5}>
        <p className="text-sm sm:text-base md:text-lg text-slate-600 mb-8 max-w-2xl mx-auto font-medium">
          Advanced AI-based emotion understanding to help you navigate your
          feelings safely and privately.
        </p>
      </BlurFade>

      {/* Buttons */}
      <BlurFade delay={0.6}>
        <div className="flex flex-row justify-center gap-3 sm:gap-4">
          <Button
            size="lg"
            onClick={() => navigate("/dashboard")}
            className="bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition"
          >
            Start Analysis
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate("/learn-more")}
            className="bg-white border-slate-200 rounded-full font-semibold hover:bg-slate-50 transition"
          >
            Learn More
          </Button>
        </div>
      </BlurFade>

      {/* HERO IMAGE */}
      <BlurFade delay={0.7} yOffset={20}>
        <div className="mt-14 sm:mt-20 relative rounded-xl overflow-hidden shadow-2xl h-56 sm:h-72 md:h-96 group">
          <img
            src="screenshot.webp"
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            alt="App preview"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
          
          <BlurFade delay={1.2} yOffset={0}>
            <div className="absolute bottom-4 left-4 right-4 sm:left-6 sm:right-auto bg-white/90 backdrop-blur px-4 py-3 rounded-xl flex items-center gap-3 shadow-lg border border-white/20 max-w-xs text-left">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                <CheckCircle className="text-indigo-600" size={20} />
              </div>
              <div>
                <p className="font-bold text-xs sm:text-sm">Analysis Complete</p>
                <p className="text-[11px] sm:text-xs text-slate-500">
                  You seem to be feeling reflective today.
                </p>
              </div>
            </div>
          </BlurFade>
        </div>
      </BlurFade>
    </header>
    </section>
  );
};

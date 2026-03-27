import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { Button } from "@/components/ui/button";
import { DotPattern } from "@/components/magicui/dot-pattern";
import { cn } from "@/lib/utils";

export const CallToAction = () => {
  const navigate = useNavigate();

  return (
    <section className="relative py-24 px-6 overflow-hidden">
      <DotPattern
        className={cn(
          "[mask-image:radial-gradient(700px_circle_at_center,white,transparent)]",
          "absolute inset-0 opacity-100 text-indigo-400/15"
        )}
      />
      <div className="relative z-10 max-w-3xl mx-auto text-center">
        <BlurFade delay={0.1} inView>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Understand Your Emotions?
          </h2>
        </BlurFade>
        <BlurFade delay={0.2} inView>
          <p className="text-slate-500 mb-8 max-w-xl mx-auto">
            Start your first AI-powered emotional analysis session today. It's
            private, safe, and completely free.
          </p>
        </BlurFade>
        <BlurFade delay={0.3} inView>
          <div className="flex flex-row justify-center gap-4">
            <Button
              size="lg"
              onClick={() => navigate("/dashboard")}
              className="bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition gap-2"
            >
              Get Started <ArrowRight size={16} />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate("/")}
              className="bg-white border-slate-200 rounded-full font-semibold hover:bg-slate-50 transition"
            >
              Back to Home
            </Button>
          </div>
        </BlurFade>
      </div>
    </section>
  );
};

import { CheckCircle } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { DotPattern } from "@/components/magicui/dot-pattern";
import AnimatedGridPattern from "@/components/magicui/animated-grid-pattern";
import { cn } from "@/lib/utils";
export const Privacy = () => {
  return (
    <div className="relative w-full overflow-hidden">
      <AnimatedGridPattern
        numSquares={100}
        width={40}
        height={40}
        maxOpacity={0.1}
        duration={3}
        repeatDelay={1}
        className={cn(
          "[mask-image:radial-gradient(1000px_circle_at_center,white,transparent)]",
          "absolute inset-0 text-indigo-400/20 fill-indigo-400/10 stroke-indigo-400/20",
        )}
      />
      <section className="py-24 px-6 max-w-6xl mx-auto relative z-10">
        <div className="bg-indigo-50 rounded-4xl sm:rounded-[3rem] p-6 sm:p-10 md:p-16 flex flex-col md:flex-row gap-10 items-center relative overflow-hidden shadow-sm border border-indigo-100/50">
          <DotPattern
            className={cn(
              "[mask-image:radial-gradient(300px_circle_at_center,white,transparent)]",
              "absolute inset-0 opacity-50",
            )}
          />
          <BlurFade delay={0.1} inView className="flex-1 relative z-10">
            <p className="text-indigo-600 text-xs font-bold uppercase mb-2">
              Trust & Safety
            </p>

            <h2 className="text-3xl font-bold mb-6">
              Secure & Private. Your Journey, Recorded Safely.
            </h2>

            <p className="text-slate-600 mb-6">
              PsyPredict provides a safe, secure account to track your emotional progress over time.
              Your history is private, encrypted, and accessible only to you.
            </p>

            <ul className="space-y-3 text-sm font-medium">
              {[
                "Secure User Accounts",
                "Encrypted History Storage",
                "Private & Confidential Analysis",
                "Delete Your Data Anytime"
              ].map((item, index) => (
                <li key={index} className="flex items-center gap-2">
                  <CheckCircle size={16} />
                  {item}
                </li>
              ))}
            </ul>

            <p className="mt-6 text-sm text-slate-500 italic">
              Your data is yours. You have full control to view or delete your history at any time.
            </p>

            <p className="mt-4 text-xs text-slate-400">
              PsyPredict is not a diagnostic or medical service and does not
              replace professional mental health care.
            </p>
          </BlurFade>

          <BlurFade delay={0.2} inView className="flex-1 relative">
            <div className="rounded-3xl overflow-hidden shadow-xl">
              <img
                src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2670&auto=format&fit=crop"
                alt="Secure system visualization"
                className="w-full h-auto object-cover opacity-90"
              />
            </div>
          </BlurFade>
        </div>
      </section>
    </div>
  );
};

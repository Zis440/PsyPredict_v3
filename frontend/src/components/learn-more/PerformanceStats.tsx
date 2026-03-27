import BlurFade from "@/components/magicui/blur-fade";

const stats = [
  { value: "30 ms", label: "Inference Lag" },
  { value: "99.8%", label: "Uptime" },
  { value: "7", label: "Emotion Classes" },
  { value: "12+", label: "CBT Patterns" },
];

export const PerformanceStats = () => {
  return (
    <section className="bg-slate-900 py-16 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
        <div>
          <BlurFade delay={0.1} inView>
            <h3 className="text-white text-2xl font-bold mb-2">
              Proven Performance.
            </h3>
          </BlurFade>
          <BlurFade delay={0.15} inView>
            <p className="text-slate-400 text-sm max-w-md">
              Evaluated on DAIC-WOZ, CMU-MOSEI, FER-2013, and CLPsych datasets.
              Outperforms unimodal and early-fusion baselines.
            </p>
          </BlurFade>
        </div>

        <div className="flex gap-10 sm:gap-14">
          {stats.map((s, i) => (
            <BlurFade key={i} delay={0.1 + i * 0.08} inView>
              <div className="text-center">
                <p className="text-white font-bold text-2xl md:text-3xl">
                  {s.value}
                </p>
                <p className="text-[10px] uppercase font-bold tracking-widest text-slate-500 mt-1">
                  {s.label}
                </p>
              </div>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
};

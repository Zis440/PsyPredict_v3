import Marquee from "@/components/magicui/marquee";
import { techStack } from "./constants";

export const TechStack = () => {
  return (
    <section className="bg-slate-900 py-16 overflow-hidden">
      <div className="max-w-6xl mx-auto px-6 mb-12 flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
        <div>
          <h3 className="text-white text-2xl font-bold mb-2">Production Hardened.</h3>
          <p className="text-slate-400 text-sm">Built with the modern stack for reliability and speed.</p>
        </div>
        <div className="flex gap-12 text-slate-500">
          <div className="text-center">
            <p className="text-white font-bold text-2xl">30 ms</p>
            <p className="text-[10px] uppercase font-bold tracking-widest">Inference Lag</p>
          </div>
          <div className="text-center">
            <p className="text-white font-bold text-2xl">99.8%</p>
            <p className="text-[10px] uppercase font-bold tracking-widest">Uptime</p>
          </div>
        </div>
      </div>

      <Marquee pauseOnHover duration={20}>
        {techStack.map((tech) => (
          <div key={tech.name} className="mx-8 text-slate-500 font-bold text-lg tracking-widest uppercase opacity-50 hover:opacity-100 transition-opacity flex items-center gap-3">
            <tech.Icon size={20} className="text-indigo-500" />
            {tech.name}
          </div>
        ))}
      </Marquee>
    </section>
  );
};

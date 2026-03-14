import { motion } from "framer-motion";
import { Mail, Linkedin, GithubIcon } from "lucide-react";
import BlurFade from "@/components/magicui/blur-fade";
import { MagicCard } from "@/components/magicui/magic-card";
import { team } from "./constants";

export const Team = () => {
  return (
    <section className="py-24 px-6 max-w-6xl mx-auto text-center">
      <BlurFade delay={0.1} inView>
        <h2 className="text-3xl font-bold mb-4">
          Meet the Minds Behind PsyPredict
        </h2>
      </BlurFade>
      <BlurFade delay={0.2} inView>
        <p className="text-slate-500 mb-16">
          A team of engineers, AI researchers, and designers working together.
        </p>
      </BlurFade>

      <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 md:gap-12">
        {team.map((s, i) => (
          <BlurFade key={i} delay={0.1 + i * 0.05} inView>
            <MagicCard className="p-0 border-slate-200 overflow-hidden bg-slate-50 shadow-sm" gradientColor="#6366f1" gradientOpacity={0.08}>
              <div className="aspect-square overflow-hidden mb-2">
                <img
                  src={s.photo}
                  alt={s.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
              </div>
              <div className="p-6 bg-slate-50 text-center">
                <h3 className="font-bold text-slate-900 text-base md:text-lg mb-4">{s.title}</h3>
                <div className="flex gap-4 justify-center">
                  {s.email && (
                    <motion.a
                      whileHover={{ y: -4, scale: 1.1 }}
                      href={`mailto:${s.email}`}
                      className="w-8 h-8 rounded-full flex items-center justify-center text-slate-500 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                      title="Email"
                    >
                      <Mail size={16} />
                    </motion.a>
                  )}
                  {s.linkedin && (
                    <motion.a
                      whileHover={{ y: -4, scale: 1.1 }}
                      href={s.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-8 h-8 rounded-full flex items-center justify-center text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                      title="LinkedIn"
                    >
                      <Linkedin size={16} />
                    </motion.a>
                  )}
                  {s.github && (
                    <motion.a
                      whileHover={{ y: -4, scale: 1.1 }}
                      href={s.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-8 h-8 rounded-full flex items-center justify-center text-slate-500 hover:text-slate-900 hover:bg-slate-200 transition-colors"
                      title="GitHub"
                    >
                      <GithubIcon size={16} />
                    </motion.a>
                  )}
                </div>
              </div>
            </MagicCard>
          </BlurFade>
        ))}
      </div>
    </section>
  );
};

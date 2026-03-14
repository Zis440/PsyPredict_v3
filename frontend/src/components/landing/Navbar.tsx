import { motion } from "framer-motion";
import BlurFade from "@/components/magicui/blur-fade";
import { Link } from "react-router-dom";

export const Navbar = () => {
  return (
    <BlurFade delay={0.1} yOffset={0}>
      <nav className="relative z-10 flex justify-between items-center px-4 sm:px-6 lg:px-8 py-4 max-w-7xl mx-auto">
        <Link to="/">
          <div className="flex items-center gap-2 font-bold text-lg sm:text-xl text-slate-800">
            <motion.span
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
            >
              🧠
            </motion.span>
            PsyPredict
          </div>
        </Link>
      </nav>
    </BlurFade>
  );
};

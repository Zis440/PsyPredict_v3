import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface MarqueeProps {
  className?: string;
  reverse?: boolean;
  pauseOnHover?: boolean;
  children?: React.ReactNode;
  vertical?: boolean;
  repeat?: number;
  duration?: number;
  [key: string]: any;
}

export default function Marquee({
  className,
  reverse,
  pauseOnHover = false,
  children,
  vertical = false,
  repeat = 4,
  duration = 40,
  ...props
}: MarqueeProps) {
  return (
    <div
      {...props}
      className={cn(
        "group flex overflow-hidden p-2 [--gap:1rem] [gap:var(--gap)]",
        {
          "flex-row": !vertical,
          "flex-col": vertical,
        },
        className,
      )}
    >
      <motion.div
        className={cn("flex shrink-0 justify-around [gap:var(--gap)]", {
          "flex-row": !vertical,
          "flex-col": vertical,
        })}
        whileHover={pauseOnHover ? { animationPlayState: "paused" } : undefined}
        animate={{
          x: !vertical ? (reverse ? ["-50%", "0%"] : ["0%", "-50%"]) : 0,
          y: vertical ? (reverse ? ["-50%", "0%"] : ["0%", "-50%"]) : 0,
        }}
        transition={{
          duration: duration,
          ease: "linear",
          repeat: Infinity,
        }}
        style={{
          width: !vertical ? "fit-content" : "100%",
          height: vertical ? "fit-content" : "100%",
        }}
      >
        {Array(2)
          .fill(0)
          .map((_, i) => (
            <div
              key={i}
              className={cn("flex shrink-0 justify-around [gap:var(--gap)]", {
                "flex-row": !vertical,
                "flex-col": vertical,
              })}
            >
              {children}
            </div>
          ))}
      </motion.div>
    </div>
  );
}

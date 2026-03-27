"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

import { cn } from "@/lib/utils";

interface LetterPullupProps {
  className?: string;
  words: string;
  delay?: number;
}

export default function LetterPullup({
  words,
  delay,
  className,
}: LetterPullupProps) {
  const letters = words.split("");
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true });

  const pullupVariant = {
    initial: { y: 100, opacity: 0 },
    animate: (i: number) => ({
      y: 0,
      opacity: 1,
      transition: {
        delay: i * (delay ? delay : 0.03), // Fast stagger for smooth flow
        duration: 0.6,
      },
    }),
  };

  return (
    <div 
      className="flex justify-center flex-wrap" 
      ref={containerRef}
    >
      {letters.map((letter, i) => (
        <motion.span
          key={i}
          variants={pullupVariant}
          initial="initial"
          animate={isInView ? "animate" : "initial"}
          custom={i}
          className={cn(
            "text-center tracking-[-0.02em]",
            className,
          )}
        >
          {letter === " " ? "\u00A0" : letter}
        </motion.span>
      ))}
    </div>
  );
}

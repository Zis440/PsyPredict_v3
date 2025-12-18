import React from "react";
import { Link } from "react-router-dom";
import { motion, type Variants } from "framer-motion";

const LearnMore: React.FC = () => {
  const sectionVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.4 },
    },
  };

  return (
    <div className="min-h-screen bg-gray-50 overflow-hidden">
      {/* Header */}
      <motion.nav 
        initial={{ y: -60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="flex justify-between items-center px-4 sm:px-6 lg:px-8 py-4 max-w-7xl mx-auto"
      >
        <Link to={"/"}>
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-2 font-bold text-lg sm:text-xl text-slate-800"
          >
            <motion.span
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
            >
              🧠
            </motion.span>
            PsyPredict
          </motion.div>
        </Link>
      </motion.nav>

      {/* Hero */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.3 }}
        variants={sectionVariants}
        className="max-w-5xl mx-auto px-6 py-16"
      >
        <motion.h1 
          className="text-4xl font-bold text-gray-900 mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          Learn More About PsyPredict
        </motion.h1>
        <motion.p 
          className="text-lg text-gray-600 max-w-3xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          PsyPredict is a multimodal, safety-first mental health assistant that
          combines facial emotion recognition, text-based psychological signal
          analysis, and large language model (LLM) reasoning to support early
          mental health awareness.
        </motion.p>
      </motion.section>

      {/* Why */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={sectionVariants}
        className="bg-white border-t border-gray-200"
      >
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Why PsyPredict?
          </h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            Mental health conditions such as depression, anxiety, and
            stress-related disorders affect millions worldwide, yet many remain
            undiagnosed due to limited access to professionals, stigma, and
            delayed screening. PsyPredict explores how AI can support early
            self-awareness using everyday tools like webcams and conversational
            text—without replacing clinical care.
          </p>
        </div>
      </motion.section>

      {/* How it Works */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <motion.h2 
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-2xl font-semibold text-gray-900 mb-8"
        >
          How PsyPredict Works
        </motion.h2>

        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          transition={{ staggerChildren: 0.15 }}
          className="grid gap-8"
        >
          {[
            {
              title: "1. Facial Emotion Recognition",
              desc: "A convolutional neural network (CNN) analyzes facial expressions from webcam input to identify core emotions. A rolling emotion buffer smooths predictions over time, reducing noise and capturing short-term emotional trends rather than isolated frames."
            },
            {
              title: "2. Text-Based Psychological Signal Analysis",
              desc: "User text is analyzed using a hybrid NLP pipeline combining keyword-based symptom detection, transformer embeddings, and structured symptom-to-condition mapping. This allows PsyPredict to detect patterns of psychological distress beyond single keywords."
            },
            {
              title: "3. Multimodal Fusion",
              desc: "Visual emotion signals and linguistic features are fused using a transformer-based multimodal architecture. This fusion improves robustness and accuracy compared to single-modality systems."
            },
            {
              title: "4. LLM-Based Reasoning with Guardrails",
              desc: "A large language model generates empathetic, human-readable summaries grounded in structured model outputs. Strict guardrails prevent diagnosis, medication prescription, or unsafe advice."
            }
          ].map((item, index) => (
            <motion.div 
              key={index}
              variants={sectionVariants}
            >
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                {item.title}
              </h3>
              <p className="text-gray-700 leading-relaxed">
                {item.desc}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Safety */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={sectionVariants}
        className="bg-white border-t border-gray-200"
      >
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Safety First
          </h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            PsyPredict includes a dedicated crisis detection module. If language
            indicating self-harm or suicidal ideation is detected, the system
            immediately overrides normal responses and delivers a predefined
            safety-focused message. This ensures responsible, harm-averse
            behavior at all times.
          </p>
        </div>
      </motion.section>

      {/* Can / Cannot */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-2 gap-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            transition={{ staggerChildren: 0.1 }}
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              What PsyPredict Can Do
            </h3>
            <ul className="list-none text-gray-700 space-y-2">
              {[
                "✅ Diagnose mental health conditions",
                "✅ Support emotional self-awareness",
                "✅ Detect early mental health signals",
                "✅ Provide empathetic, reflective feedback",
                "✅ Operate in real time using common devices"
              ].map((text, i) => (
                 <motion.li key={i} variants={itemVariants}>{text}</motion.li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            transition={{ staggerChildren: 0.1, delayChildren: 0.2 }}
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              What PsyPredict Cannot Do
            </h3>
            <ul className="list-none text-gray-700 space-y-2">
              {[
                "❌ Replace therapists or psychiatrists",
                "❌ Prescribe medication or treatment",
                "❌ Act as an emergency service"
              ].map((text, i) => (
                 <motion.li key={i} variants={itemVariants}>{text}</motion.li>
              ))}
            </ul>
          </motion.div>
        </div>
      </section>

      {/* Performance */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={sectionVariants}
        className="bg-white border-t border-gray-200"
      >
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Proven Performance
          </h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            PsyPredict has been evaluated on multiple public datasets including
            DAIC-WOZ, CMU-MOSEI, FER-2013, and CLPsych. The system achieved
            strong performance, outperforming unimodal and early-fusion
            baselines in accuracy, robustness, and interpretability.
          </p>
        </div>
      </motion.section>

      {/* Footer */}
      <motion.footer 
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="border-t py-10 text-center text-sm border-gray-200 bg-gray-50 text-gray-500"
      >
        <div className="max-w-5xl mx-auto px-6 py-6">
          PsyPredict is a research-driven mental health support system designed
          for early awareness and education. It is not a clinical diagnostic
          tool.
        </div>
        © 2025 PsyPredict. All rights reserved.
      </motion.footer>
    </div>
  );
};

export default LearnMore;

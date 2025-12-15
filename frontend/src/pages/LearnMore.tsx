import React from 'react';
import { Link } from 'react-router-dom';
// import { Link } from 'react-router-dom';

const LearnMore: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <Link to={"/"}>
        <div className="flex items-center gap-2 font-bold text-xl text-slate-800">
          <span>🧠</span>
          PsyPredict
        </div>
        </Link>
        {/* <button
          onClick={() => navigate("/dashboard")}
          className="bg-indigo-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-indigo-700 transition"
          >
          Start Analysis
          </button> */}
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Learn More About PsyPredict
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl">
          PsyPredict is a multimodal, safety-first mental health assistant that combines
          facial emotion recognition, text-based psychological signal analysis, and
          large language model (LLM) reasoning to support early mental health awareness.
        </p>
      </section>

      {/* Why */}
      <section className="bg-white border-t border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Why PsyPredict?</h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            Mental health conditions such as depression, anxiety, and stress-related
            disorders affect millions worldwide, yet many remain undiagnosed due to
            limited access to professionals, stigma, and delayed screening. PsyPredict
            explores how AI can support early self-awareness using everyday tools like
            webcams and conversational text—without replacing clinical care.
          </p>
        </div>
      </section>

      {/* How it Works */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-8">How PsyPredict Works</h2>

        <div className="grid gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              1. Facial Emotion Recognition
            </h3>
            <p className="text-gray-700 leading-relaxed">
              A convolutional neural network (CNN) analyzes facial expressions from
              webcam input to identify core emotions. A rolling emotion buffer smooths
              predictions over time, reducing noise and capturing short-term emotional
              trends rather than isolated frames.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              2. Text-Based Psychological Signal Analysis
            </h3>
            <p className="text-gray-700 leading-relaxed">
              User text is analyzed using a hybrid NLP pipeline combining keyword-based
              symptom detection, transformer embeddings, and structured
              symptom-to-condition mapping. This allows PsyPredict to detect patterns of
              psychological distress beyond single keywords.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              3. Multimodal Fusion
            </h3>
            <p className="text-gray-700 leading-relaxed">
              Visual emotion signals and linguistic features are fused using a
              transformer-based multimodal architecture. This fusion improves
              robustness and accuracy compared to single-modality systems.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              4. LLM-Based Reasoning with Guardrails
            </h3>
            <p className="text-gray-700 leading-relaxed">
              A large language model generates empathetic, human-readable summaries
              grounded in structured model outputs. Strict guardrails prevent
              diagnosis, medication prescription, or unsafe advice.
            </p>
          </div>
        </div>
      </section>

      {/* Safety */}
      <section className="bg-white border-t border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Safety First</h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            PsyPredict includes a dedicated crisis detection module. If language
            indicating self-harm or suicidal ideation is detected, the system
            immediately overrides normal responses and delivers a predefined
            safety-focused message. This ensures responsible, harm-averse behavior at
            all times.
          </p>
        </div>
      </section>

      {/* Can / Cannot */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">What PsyPredict Can Do</h3>
            <ul className="list-none text-gray-700 space-y-2">
              <li>✅ Diagnose mental health conditions</li>
              <li>✅ Support emotional self-awareness</li>
              <li>✅ Detect early mental health signals</li>
              <li>✅ Provide empathetic, reflective feedback</li>
              <li>✅ Operate in real time using common devices</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">What PsyPredict Cannot Do</h3>
            <ul className="list-none text-gray-700 space-y-2">
              <li>❌ Replace therapists or psychiatrists</li>
              <li>❌ Prescribe medication or treatment</li>
              <li>❌ Act as an emergency service</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Performance */}
      <section className="bg-white border-t border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Proven Performance</h2>
          <p className="text-gray-700 leading-relaxed max-w-4xl">
            PsyPredict has been evaluated on multiple public datasets including
            DAIC-WOZ, CMU-MOSEI, FER-2013, and CLPsych. The system achieved strong
            performance, outperforming unimodal and early-fusion baselines in accuracy,
            robustness, and interpretability.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-10 text-center text-sm border-gray-200 bg-gray-50 text-gray-500">
        <div className="max-w-5xl mx-auto px-6 py-6">
          PsyPredict is a research-driven mental health support system designed for
          early awareness and education. It is not a clinical diagnostic tool.
        </div>

        © 2025 PsyPredict. All rights reserved.
      </footer>
    </div>
  );
};

export default LearnMore;

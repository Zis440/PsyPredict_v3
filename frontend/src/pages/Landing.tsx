// import React from 'react';
import { useNavigate } from "react-router-dom";
import {
  Video,
  CheckCircle,
  Sparkles,
  GithubIcon,
  Mail,
  Linkedin,
  Cpu,
  Lightbulb,
} from "lucide-react";

const team = [
  {
    photo: "saphalya.webp",
    title: "Saphalya Das",
    email: "szd0238@gmail.com",
    github: "https://github.com/Zis440",
    linkedin: "https://www.linkedin.com/in/saphalya-das-81a06b1b3/",
  },
  {
    photo: "anubhab.webp",
    title: "Anubhab Pal",
    email: "anubhabpal1@gmail.com",
    github: "https://github.com/therandomuser03",
    linkedin: "https://www.linkedin.com/in/therandomuser03/",
  },
  {
    photo: "nilanjana.webp",
    title: "Nilanjana Sarkar",
    email: "nilanjanasarkar2017@gmail.com",
    // github: "#",
    linkedin: "https://www.linkedin.com/in/nianjana-sarkar-4862011b9/",
  },
  {
    photo: "sanjana.webp",
    title: "Sanjana Chatterjee",
    email: "misssanjanachatterjee@gmail.com",
    github: "https://github.com/SanjanaChatterjee",
    linkedin: "https://www.linkedin.com/in/sanjana-jpeg/",
  },
];

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="font-sans text-slate-900 bg-white">
      {/* NAVBAR */}
      <nav className="flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 font-bold text-xl text-slate-800">
          <span>🧠</span>
          PsyPredict
        </div>
      </nav>

      {/* HERO */}
      <header className="text-center px-6 mt-20 mb-28 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-xs font-semibold px-4 py-1.5 rounded-full mb-6">
          <Sparkles size={14} /> AI-Powered Emotional Intelligence
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-6">
          Understand Your Emotions.
          <br />
          <span className="text-indigo-600">Empower Your Mind.</span>
        </h1>

        <p className="text-lg text-slate-500 mb-10 max-w-2xl mx-auto">
          Advanced AI-based emotion understanding to help you navigate your
          feelings safely and privately. Gain clarity and support when you need
          it most.
        </p>

        <div className="flex justify-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="bg-indigo-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-indigo-700 transition"
          >
            Start Analysis
          </button>
          <button
            onClick={() => navigate("/learn-more")}
            className="bg-white border border-slate-200 px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-slate-50 transition"
          >
            Learn More
          </button>
        </div>

        {/* HERO IMAGE */}
        <div className="mt-20 relative rounded-xl overflow-hidden shadow-2xl h-72 md:h-96">
          <img src="screenshot.webp" className="w-full h-full object-cover" />
          <div className="absolute bottom-6 left-6 bg-white/90 backdrop-blur px-6 py-4 rounded-2xl flex items-center gap-4 shadow">
            <CheckCircle className="text-indigo-600" />
            <div className="text-left">
              <p className="font-bold text-sm">Analysis Complete</p>
              <p className="text-xs text-slate-500">
                You seem to be feeling reflective today.
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* STEPS */}
      <section className="bg-slate-50 py-24 px-6">
        <div className="max-w-6xl mx-auto text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Simple Steps to Clarity</h2>
          <p className="text-slate-500">
            Our process is designed to be effortless, private, and supportive
            from the very first moment.
          </p>
        </div>

        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
          {[
            {
              icon: Video,
              title: "1. Share Your Story",
              desc: "Enable your camera or microphone in a secure environment. Speak freely without judgment.",
            },
            {
              icon: Cpu,
              title: "2. AI Processing",
              desc: "Ethical AI analyzes facial expressions, tone, and text sentiment.",
            },
            {
              icon: Lightbulb,
              title: "3. Receive Insight",
              desc: "Get personalized emotional insights and immediate support.",
            },
          ].map((s, i) => (
            <div key={i} className="bg-white p-8 rounded-3xl shadow-sm">
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 mb-6">
                <s.icon />
              </div>
              <h3 className="font-bold mb-2">{s.title}</h3>
              <p className="text-sm text-slate-500">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* PRIVACY */}
      <section className="py-24 px-6 max-w-6xl mx-auto">
        <div className="bg-indigo-50 rounded-[3rem] p-10 md:p-16 flex flex-col md:flex-row gap-12 items-center">
          <div className="flex-1">
            <p className="text-indigo-600 text-xs font-bold uppercase mb-2">
              Trust & Safety
            </p>

            <h2 className="text-3xl font-bold mb-6">
              Privacy by Design. No Memory. No Storage.
            </h2>

            <p className="text-slate-600 mb-6">
              PsyPredict is designed to work without storing your personal data.
              All interactions are processed in real time and automatically
              erased when you refresh or close the page.
            </p>

            <ul className="space-y-3 text-sm font-medium">
              <li className="flex items-center gap-2">
                <CheckCircle size={16} />
                Session-Only Processing (cleared on refresh)
              </li>

              <li className="flex items-center gap-2">
                <CheckCircle size={16} />
                Secure, Encrypted Communication
              </li>

              <li className="flex items-center gap-2">
                <CheckCircle size={16} />
                No Accounts. No Tracking. No Logs
              </li>

              <li className="flex items-center gap-2">
                <CheckCircle size={16} />
                No Hidden or Persistent Storage
              </li>
            </ul>

            {/* Plain-English Guarantee */}
            <p className="mt-6 text-sm text-slate-500 italic">
              In simple terms: if you refresh the page, it&apos;s like you were never
              here.
            </p>

            {/* Disclaimer */}
            <p className="mt-4 text-xs text-slate-400">
              PsyPredict is not a diagnostic or medical service and does not
              replace professional mental health care.
            </p>
          </div>

          <div className="flex-1 relative">
            <div className="rounded-3xl overflow-hidden shadow-xl">
              <img
                src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2670&auto=format&fit=crop"
                alt="Secure system visualization"
                className="opacity-90"
              />
            </div>
          </div>
        </div>
      </section>

      {/* TEAM */}
      <section className="py-24 px-6 max-w-6xl mx-auto text-center">
        <h2 className="text-3xl font-bold mb-4">
          Meet the Minds Behind PsyPredict
        </h2>
        <p className="text-slate-500 mb-16">
          A team of engineers, AI researchers, and designers working together.
        </p>

        <div className="max-w-6xl mx-auto grid md:grid-cols-4 gap-12 text-left">
          {team.map((s, i) => (
            <div key={i} className="bg-white p-8 rounded-3xl shadow-sm">
              <div className="w-20 h-20 rounded-2xl overflow-hidden mb-4">
                <img
                  src={s.photo}
                  alt={s.title}
                  className="w-full h-full object-cover"
                />
              </div>

              <h3 className="font-bold mb-4">{s.title}</h3>

              <div className="flex gap-3 text-slate-500">
                {/* Email */}
                {s.email && (
                  <a
                    href={`mailto:${s.email}`}
                    aria-label="Send email"
                    className="hover:text-yellow-600"
                  >
                    <Mail size={20} />
                  </a>
                )}

                {/* LinkedIn */}
                {s.linkedin && (
                  <a
                    href={s.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600"
                  >
                    <Linkedin size={18} />
                  </a>
                )}

                {/* GitHub */}
                {s.github && (
                  <a
                    href={s.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-neutral-600"
                  >
                    <GithubIcon size={18} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t py-10 text-center text-sm text-slate-400">
        © 2025 PsyPredict. All rights reserved.
      </footer>
    </div>
  );
};

export default Landing;

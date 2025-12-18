import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <div className="font-sans text-slate-900 bg-white overflow-hidden">
      {/* NAVBAR */}
      <motion.nav 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="flex justify-between items-center px-4 sm:px-6 lg:px-8 py-4 max-w-7xl mx-auto"
      >
        <div className="flex items-center gap-2 font-bold text-lg sm:text-xl text-slate-800">
          <motion.span
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
          >
            🧠
          </motion.span>
          PsyPredict
        </div>
      </motion.nav>

      {/* HERO */}
      <header className="text-center px-4 sm:px-6 mt-14 sm:mt-20 mb-20 sm:mb-28 max-w-4xl mx-auto">
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-[11px] sm:text-xs font-semibold px-3 py-1.5 rounded-full mb-5"
        >
          <Sparkles size={14} /> AI-Powered Emotional Intelligence
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-3xl sm:text-4xl md:text-6xl font-extrabold leading-tight mb-5"
        >
          Understand Your Emotions.
          <br />
          <span className="text-indigo-600">Empower Your Mind.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-sm sm:text-base md:text-lg text-slate-500 mb-8 max-w-2xl mx-auto"
        >
          Advanced AI-based emotion understanding to help you navigate your
          feelings safely and privately.
        </motion.p>

        {/* Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-row justify-center gap-3 sm:gap-4"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              // Add a check? We can just let the router handle it
              // Since /dashboard is protected, it will redirect to /login if needed.
              // But explicit /login link is sometimes cleaner if we know they aren't auth'd.
              // For simplicity and adhering to constraints, we'll just go to dashboard and let the guard work.
              navigate("/dashboard");
            }}
            className="bg-indigo-600 text-white px-6 py-3 rounded-full text-sm font-semibold hover:bg-indigo-700 transition"
          >
            Start Analysis
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/learn-more")}
            className="bg-white border border-slate-200 px-6 py-3 rounded-full text-sm font-semibold hover:bg-slate-50 transition"
          >
            Learn More
          </motion.button>
        </motion.div>

        {/* HERO IMAGE */}
        <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-14 sm:mt-20 relative rounded-xl overflow-hidden shadow-2xl h-56 sm:h-72 md:h-96"
        >
          <img
            src="screenshot.webp"
            className="w-full h-full object-cover"
            alt="App preview"
          />

          {/* Floating Card */}
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="absolute bottom-4 left-4 right-4 sm:left-6 sm:right-auto bg-white/90 backdrop-blur px-4 py-3 rounded-xl flex items-center gap-3 shadow max-w-xs"
          >
            <CheckCircle className="text-indigo-600 shrink-0" />
            <div className="text-left">
              <p className="font-bold text-xs sm:text-sm">Analysis Complete</p>
              <p className="text-[11px] sm:text-xs text-slate-500">
                You seem to be feeling reflective today.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </header>

      {/* STEPS */}
      <section className="bg-slate-50 py-24 px-6">
        <div className="max-w-6xl mx-auto text-center mb-16">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold mb-4"
          >
            Simple Steps to Clarity
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-slate-500"
          >
            Our process is designed to be effortless, private, and supportive
            from the very first moment.
          </motion.p>
        </div>

        <motion.div 
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8"
        >
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
            <motion.div 
                key={i} 
                variants={itemVariants}
                whileHover={{ y: -5 }}
                className="bg-white p-8 rounded-3xl shadow-sm"
            >
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 mb-6">
                <s.icon />
              </div>
              <h3 className="font-bold mb-2">{s.title}</h3>
              <p className="text-sm text-slate-500">{s.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* PRIVACY */}
      <section className="py-24 px-6 max-w-6xl mx-auto">
        <div className="bg-indigo-50 rounded-4xl sm:rounded-[3rem] p-6 sm:p-10 md:p-16 flex flex-col md:flex-row gap-10 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex-1"
          >
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
                <motion.li 
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2 + (index * 0.1) }}
                  className="flex items-center gap-2"
                >
                  <CheckCircle size={16} />
                  {item}
                </motion.li>
              ))}
            </ul>

            {/* Plain-English Guarantee */}
            <p className="mt-6 text-sm text-slate-500 italic">
              Your data is yours. You have full control to view or delete your history at any time.
            </p>

            {/* Disclaimer */}
            <p className="mt-4 text-xs text-slate-400">
              PsyPredict is not a diagnostic or medical service and does not
              replace professional mental health care.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex-1 relative"
          >
            <div className="rounded-3xl overflow-hidden shadow-xl">
              <img
                src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2670&auto=format&fit=crop"
                alt="Secure system visualization"
                className="w-full h-auto object-cover opacity-90"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* TEAM */}
      <section className="py-24 px-6 max-w-6xl mx-auto text-center">
        <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold mb-4"
        >
          Meet the Minds Behind PsyPredict
        </motion.h2>
        <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-slate-500 mb-16"
        >
          A team of engineers, AI researchers, and designers working together.
        </motion.p>

        <motion.div 
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 md:gap-12 text-left"
        >
          {team.map((s, i) => (
            <motion.div 
                key={i} 
                variants={itemVariants}
                whileHover={{ scale: 1.05 }}
                className="bg-white p-8 rounded-3xl shadow-sm"
            >
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl overflow-hidden mb-4">
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
                  <motion.a
                    whileHover={{ scale: 1.2, color: "#CA8A04" }}
                    href={`mailto:${s.email}`}
                    aria-label="Send email"
                    className="hover:text-yellow-600"
                  >
                    <Mail size={20} />
                  </motion.a>
                )}

                {/* LinkedIn */}
                {s.linkedin && (
                  <motion.a
                    whileHover={{ scale: 1.2, color: "#2563EB" }}
                    href={s.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600"
                  >
                    <Linkedin size={18} />
                  </motion.a>
                )}

                {/* GitHub */}
                {s.github && (
                  <motion.a
                    whileHover={{ scale: 1.2, color: "#171717" }}
                    href={s.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-neutral-600"
                  >
                    <GithubIcon size={18} />
                  </motion.a>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* FOOTER */}
      <footer className="border-t py-8 text-center text-xs sm:text-sm text-slate-400">
        © 2025 PsyPredict. All rights reserved.
      </footer>
    </div>
  );
};

export default Landing;

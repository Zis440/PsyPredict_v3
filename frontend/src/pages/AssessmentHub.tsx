import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import { useSegment } from '../context/SegmentContext';
import { Shield, Brain, Sparkles, ArrowRight } from 'lucide-react';

const AssessmentHub: React.FC = () => {
  const { segment } = useSegment();
  const navigate = useNavigate();

  const isStudent = segment === 'student';

  const packages = [
    {
      id: 1,
      title: isStudent ? "Student Wellbeing Pulse Assessment" : "Workforce Wellbeing Pulse Assessment",
      short: "Level 1 — Wellbeing Pulse",
      icon: Shield,
      color: "emerald",
      time: "10-15 min",
      description: "Quick mental wellness check. Measures stress, burnout, recovery, sleep, and emotional health.",
      features: ["Stress Indicators", "Burnout Risk", "Sleep Quality", "Emotional State"]
    },
    {
      id: 2,
      title: isStudent ? "Academic Behavioral Intelligence" : "Workforce Behavioral Intelligence",
      short: "Level 2 — Behavioral Intelligence",
      icon: Brain,
      color: "indigo",
      time: "25-35 min",
      description: "Personality + Performance + Team Analysis. Measures emotional intelligence, adaptability, communication, and productivity.",
      features: ["Personality", "Emotional Intelligence", "Adaptability", "Learning Agility"]
    },
    {
      id: 3,
      title: isStudent ? "Student Potential Intelligence" : "Human Potential Intelligence Assessment",
      short: "Level 3 — Advanced Human Potential",
      icon: Sparkles,
      color: "purple",
      time: "30-60+ min",
      description: "Deep psychological analysis. Measures leadership potential, career readiness, job fit, and strategic thinking.",
      features: ["Writing Analysis Lab", "Image Lab", "Logic & Reasoning", "Ethics Cases"]
    }
  ];

  const colorMap: Record<string, { bg: string, text: string, hoverBg: string, shadowHover: string, accent: string, dot: string }> = {
    emerald: {
      bg: "bg-emerald-50", text: "text-emerald-600", hoverBg: "hover:bg-emerald-600", shadowHover: "hover:shadow-emerald-500/30", accent: "bg-emerald-500", dot: "bg-emerald-400"
    },
    indigo: {
      bg: "bg-indigo-50", text: "text-indigo-600", hoverBg: "hover:bg-indigo-600", shadowHover: "hover:shadow-indigo-500/30", accent: "bg-indigo-500", dot: "bg-indigo-400"
    },
    purple: {
      bg: "bg-purple-50", text: "text-purple-600", hoverBg: "hover:bg-purple-600", shadowHover: "hover:shadow-purple-500/30", accent: "bg-purple-500", dot: "bg-purple-400"
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-10 text-center max-w-2xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-black text-gray-900 tracking-tight mb-4">
            Assessment Hub
          </h1>
          <p className="text-gray-500 text-lg">
            Choose an assessment package below. These evaluations are dynamically tailored to your <span className="font-semibold text-indigo-600">{segment}</span> profile.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {packages.map((pkg) => {
            const colors = colorMap[pkg.color];
            return (
            <div 
              key={pkg.id}
              className="bg-white rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col overflow-hidden relative group"
            >
              {/* Top Accent Line */}
              <div className={`h-2 w-full ${colors.accent}`} />
              
              <div className="p-8 flex flex-col flex-1">
                <div className="flex justify-between items-start mb-6">
                  <div className={`p-3 rounded-2xl ${colors.bg} ${colors.text} group-hover:scale-110 transition-transform`}>
                    <pkg.icon size={28} />
                  </div>
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider bg-gray-100 px-3 py-1 rounded-full">
                    {pkg.time}
                  </span>
                </div>

                <div className="mb-2">
                  <span className={`text-xs font-bold ${colors.text} uppercase tracking-wider`}>
                    {pkg.short}
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
                  {pkg.title}
                </h3>
                
                <p className="text-sm text-gray-500 mb-6 flex-1 leading-relaxed">
                  {pkg.description}
                </p>

                <div className="space-y-2 mb-8">
                  {pkg.features.map((feat, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                      <div className={`w-1.5 h-1.5 rounded-full ${colors.dot} shrink-0`} />
                      {feat}
                    </div>
                  ))}
                </div>

                <button 
                  onClick={() => navigate(`/assessments/${pkg.id}`)}
                  className={`w-full py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 font-bold transition-all
                    bg-gray-900 text-white ${colors.hoverBg} hover:shadow-lg ${colors.shadowHover}
                  `}
                >
                  Start Assessment
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )})}
        </div>
      </main>
    </div>
  );
};

export default AssessmentHub;

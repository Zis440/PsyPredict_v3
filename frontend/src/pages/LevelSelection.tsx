import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import { useSegment } from '../context/SegmentContext';
import { Shield, Brain, Sparkles, ArrowRight, BookOpen, Briefcase, Star } from 'lucide-react';

export const LevelSelection: React.FC = () => {
  const { segment, setSegment, isSegmentSelected } = useSegment();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const assignedStr = queryParams.get('assign');
  const assignedIds = assignedStr ? assignedStr.split(',').map(Number) : [];

  // Redirect to segment selection if no segment is chosen
  useEffect(() => {
    if (!isSegmentSelected) {
      navigate('/select-segment');
    }
  }, [isSegmentSelected, navigate]);

  const isStudent = segment === 'student';

  const packages = [
    {
      id: 1,
      title: isStudent ? "Student Wellbeing Pulse (EWSA)" : "Employee Mental Health & Wellbeing (EWSA)",
      short: "Level 1 — Basic",
      icon: Shield,
      color: "emerald",
      time: "10-15 min",
      description: "Unique dynamically generated mental wellness check. Measures stress, burnout, emotional health, distress, sleep, and work-life balance.",
    },
    {
      id: 2,
      title: isStudent ? "Academic Workforce Intelligence (WIA)" : "Workforce Intelligence Assessment (WIA)",
      short: "Level 2 — Intermediate",
      icon: Brain,
      color: "indigo",
      time: "20-25 min",
      description: "Dynamic behavioral analysis. Measures workplace personality, performance drivers, team effectiveness, and adaptability.",
    },
    {
      id: 3,
      title: isStudent ? "Student Career Match Analysis (CAJFA)" : "Candidate Assessment & Job Fit Analysis (CAJFA)",
      short: "Level 3 — Advanced",
      icon: Sparkles,
      color: "purple",
      time: "25-40 min",
      description: "Deep psychological job-fit analysis. Includes logic reasoning, attention tests, ethics scenarios, priority ranking, and reliability mapping.",
    }
  ];

  const colorMap: Record<string, string> = {
    emerald: "border-emerald-200 hover:border-emerald-500 hover:shadow-emerald-100",
    indigo: "border-indigo-200 hover:border-indigo-500 hover:shadow-indigo-100",
    purple: "border-purple-200 hover:border-purple-500 hover:shadow-purple-100"
  };

  const textMap: Record<string, string> = {
    emerald: "text-emerald-700",
    indigo: "text-indigo-700",
    purple: "text-purple-700"
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Navbar />
      
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-black text-gray-900 tracking-tight mb-4">
            Select Assessment Level
          </h1>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto mb-8">
            Please select the specific assessment level you wish to take. The evaluation will be tailored strictly to your chosen track. Cross-level adaptation is disabled.
          </p>
          
          <div className="inline-flex bg-gray-200 p-1 rounded-xl shadow-inner mx-auto">
            <button 
              onClick={() => setSegment('student')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${isStudent ? 'bg-white shadow-sm text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <BookOpen size={16} /> Student Track
            </button>
            <button 
              onClick={() => setSegment('professional')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${!isStudent ? 'bg-white shadow-sm text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <Briefcase size={16} /> Professional Track
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {packages.map((pkg) => {
            const isAssigned = assignedIds.includes(pkg.id);
            const showAssigned = assignedIds.length > 0;
            const dimStyle = showAssigned && !isAssigned ? "opacity-60 hover:opacity-100" : "";
            
            return (
              <div 
                key={pkg.id}
                className={`bg-white rounded-2xl border-2 ${colorMap[pkg.color]} p-6 md:p-8 flex flex-col md:flex-row items-center gap-6 cursor-pointer transition-all duration-200 hover:shadow-lg relative ${dimStyle}`}
                onClick={() => navigate(`/assessments/${pkg.id}`)}
              >
                {isAssigned && (
                  <div className="absolute -top-3 -right-3 bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md flex items-center gap-1">
                    <Star size={12} className="fill-white" /> Required
                  </div>
                )}
                <div className={`p-4 rounded-full bg-gray-50 ${textMap[pkg.color]}`}>
                  <pkg.icon size={36} />
                </div>
                
                <div className="flex-1 text-center md:text-left">
                  <div className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1 flex items-center justify-center md:justify-start gap-2">
                    {pkg.short} • {pkg.time}
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
                    {pkg.title}
                  </h3>
                  <p className="text-gray-600 text-sm md:text-base leading-relaxed">
                    {pkg.description}
                  </p>
                </div>
                
                <div className="mt-4 md:mt-0 flex-shrink-0">
                  <button className={`w-full md:w-auto px-6 py-3 rounded-xl font-bold text-white transition-colors flex items-center justify-center gap-2 ${isAssigned ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-900 hover:bg-gray-800'}`}>
                    Start Level {pkg.id} <ArrowRight size={18} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
};

export default LevelSelection;

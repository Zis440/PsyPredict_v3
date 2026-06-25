import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSegment } from '../context/SegmentContext';
import { GraduationCap, Briefcase, Brain, Sparkles, Shield, BookOpen } from 'lucide-react';

const SegmentSelection: React.FC = () => {
  const { setSegment } = useSegment();
  const navigate = useNavigate();

  const handleSelect = (segment: 'student' | 'professional') => {
    setSegment(segment);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Ambient glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

      <div className="max-w-5xl w-full relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="w-10 h-10 text-indigo-400" />
            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight">
              Psy<span className="text-indigo-400">Predict</span>
            </h1>
          </div>
          <p className="text-lg text-slate-400 max-w-xl mx-auto">
            Choose your edition to receive assessments, scenarios, benchmarks, and recommendations
            tailored specifically to your context.
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Student Card */}
          <button
            onClick={() => handleSelect('student')}
            className="group relative bg-gradient-to-br from-slate-900/80 to-slate-800/60 border border-slate-700/50 rounded-3xl p-8 text-left hover:border-emerald-500/60 hover:shadow-[0_0_60px_rgba(16,185,129,0.1)] transition-all duration-500 backdrop-blur-sm"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="bg-emerald-500/10 p-4 rounded-2xl w-fit mb-6 group-hover:bg-emerald-500/20 transition-colors">
                <GraduationCap className="w-8 h-8 text-emerald-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Student Edition</h2>
              <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                For academic settings, campus placements, career guidance, and student counseling.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <BookOpen className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Academic burnout & exam stress screening</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Campus leadership & peer collaboration analysis</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Career readiness & internship suitability scoring</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm group-hover:translate-x-1 transition-transform">
                Select Student Edition →
              </div>
            </div>
          </button>

          {/* Professional Card */}
          <button
            onClick={() => handleSelect('professional')}
            className="group relative bg-gradient-to-br from-slate-900/80 to-slate-800/60 border border-slate-700/50 rounded-3xl p-8 text-left hover:border-indigo-500/60 hover:shadow-[0_0_60px_rgba(99,102,241,0.1)] transition-all duration-500 backdrop-blur-sm"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="bg-indigo-500/10 p-4 rounded-2xl w-fit mb-6 group-hover:bg-indigo-500/20 transition-colors">
                <Briefcase className="w-8 h-8 text-indigo-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Professional Edition</h2>
              <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                For corporate workforce, HR teams, managers, leadership development, and talent acquisition.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <BookOpen className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span>Workplace burnout & retention risk analysis</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span>Leadership potential & team compatibility scoring</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-300">
                  <Shield className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span>Job fit, hiring match & performance prediction</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm group-hover:translate-x-1 transition-transform">
                Select Professional Edition →
              </div>
            </div>
          </button>
        </div>

        {/* Bottom Note */}
        <p className="text-center text-slate-500 text-xs mt-8">
          You can change your segment anytime from Settings. Your choice tailors all assessments, scenarios, language, and recommendations.
        </p>
      </div>
    </div>
  );
};

export default SegmentSelection;

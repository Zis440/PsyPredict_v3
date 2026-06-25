import React from "react";
import type { MasterReport } from "../../services/api";
import { X, Activity, Brain, Shield, Target, TrendingUp, Zap, FileText, Heart, Compass, Network } from "lucide-react";

interface Props {
  report: MasterReport | null;
  isOpen: boolean;
  onClose: () => void;
  isGenerating: boolean;
}

export const MasterReportModal: React.FC<Props> = ({ report, isOpen, onClose, isGenerating }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-white">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-xl">
              <FileText className="text-white w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Master Intelligence Report</h2>
              <p className="text-sm text-gray-500">Comprehensive Psychological & Behavioral Assessment</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
          {isGenerating ? (
            <div className="flex flex-col items-center justify-center h-64 space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              <p className="text-gray-500 font-medium">PsyPredict is synthesizing your master profile...</p>
              <p className="text-xs text-gray-400">This requires deep contextual reasoning and may take up to 60 seconds.</p>
            </div>
          ) : report ? (
            <div className="space-y-8">
              
              {/* Executive Summary */}
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-3">
                  <Target className="w-5 h-5 text-indigo-500" /> Executive Summary
                </h3>
                <p className="text-gray-700 leading-relaxed">{report.executive_summary}</p>
              </section>

              {/* 15 Executive Scores */}
              <section>
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-4">
                  <Activity className="w-5 h-5 text-indigo-500" /> Intelligence Index
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {Object.entries(report.scores).map(([key, value]) => {
                    const metric = value as any; // Type workaround for MetricScore
                    return (
                      <div key={key} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:border-indigo-200 transition-colors group relative">
                        <span className="text-3xl font-black text-indigo-600 mb-1">{metric.score}</span>
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                          {key.replace(/_/g, " ")}
                        </span>
                        
                        {/* Confidence Badge */}
                        <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                          <span>Conf: {metric.confidence}%</span>
                        </div>

                        {/* Hover Tooltip for Evidence */}
                        {metric.evidence && metric.evidence.length > 0 && (
                          <div className="absolute top-full mt-2 w-48 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none left-1/2 -translate-x-1/2">
                            <p className="font-bold mb-1 text-gray-300">Evidence:</p>
                            <ul className="list-disc list-inside text-left space-y-1">
                              {metric.evidence.map((ev: string, i: number) => <li key={i}>{ev}</li>)}
                            </ul>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* Deep Analysis Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-500" /> Personality Profile
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{report.personality_profile}</p>
                </section>

                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-green-500" /> Emotional Intelligence
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{report.emotional_intelligence_analysis}</p>
                </section>

                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-500" /> Behavioral & Conflict
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    <strong>Behavior:</strong> {report.behavioral_analysis}<br/><br/>
                    <strong>Conflict:</strong> {report.conflict_analysis}
                  </p>
                </section>

                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-blue-500" /> Career & Skills
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    <strong>Career:</strong> {report.career_analysis}<br/><br/>
                    <strong>Skills:</strong> {report.skill_assessment_results}
                  </p>
                </section>

                {/* Advanced Insight Modules */}
                {report.relationship_health_analysis && (
                  <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                      <Heart className="w-4 h-4 text-pink-500" /> Relationship Health
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{report.relationship_health_analysis}</p>
                  </section>
                )}

                {report.life_purpose_analysis && (
                  <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                      <Compass className="w-4 h-4 text-orange-500" /> Life Purpose & Meaning
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{report.life_purpose_analysis}</p>
                  </section>
                )}

                {report.cognitive_patterns_analysis && (
                  <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 md:col-span-2">
                    <h3 className="text-md font-bold text-gray-800 mb-2 flex items-center gap-2">
                      <Network className="w-4 h-4 text-cyan-500" /> Cognitive Patterns & Biases
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{report.cognitive_patterns_analysis}</p>
                  </section>
                )}
              </div>

              {/* Action Plan */}
              <section className="bg-indigo-900 text-white p-8 rounded-2xl shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                  <Target className="w-32 h-32" />
                </div>
                <div className="relative z-10">
                  <h3 className="text-xl font-bold mb-4">Improvement Roadmap & Action Plan</h3>
                  <p className="text-indigo-100 mb-6 leading-relaxed">{report.improvement_roadmap}</p>
                  
                  <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/20">
                    <p className="font-semibold mb-2">Immediate Actions:</p>
                    <p className="text-indigo-50 text-sm leading-relaxed">{report.action_plan}</p>
                  </div>

                  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-green-300 mb-2">Strengths to Leverage</h4>
                      <ul className="list-disc list-inside text-sm text-indigo-100 space-y-1">
                        {report.strengths.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-red-300 mb-2">Risk Indicators</h4>
                      <ul className="list-disc list-inside text-sm text-indigo-100 space-y-1">
                        {report.risk_indicators.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  </div>
                </div>
              </section>

              {/* Bhagavad Gita Wisdom */}
              {report.bhagavad_gita_wisdom && (
                <section className="bg-gradient-to-r from-amber-50 to-orange-50 p-8 rounded-2xl shadow-sm border border-amber-200/50 relative overflow-hidden">
                  <div className="absolute top-4 right-6 text-5xl opacity-10 pointer-events-none select-none">🕉️</div>
                  <div className="relative z-10">
                    <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2 mb-4">
                      🙏 Bhagavad Gita Wisdom
                    </h3>
                    <p className="text-amber-800 leading-relaxed italic text-sm">
                      "{report.bhagavad_gita_wisdom}"
                    </p>
                    <p className="text-xs text-amber-600/70 mt-4">
                      — Personalized spiritual guidance based on your current psychological profile
                    </p>
                  </div>
                </section>
              )}

            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">Failed to load report.</div>
          )}
        </div>
      </div>
    </div>
  );
};

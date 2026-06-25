import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import { useSegment } from '../context/SegmentContext';
import { useUser } from '@clerk/react';
import { useGuestMode } from '../context/GuestModeContext';
import { apiClient } from '../services/api';
import { ShieldAlert, CheckCircle2, ChevronRight, ChevronLeft, AlertTriangle, RefreshCw } from 'lucide-react';

interface Question {
  id: string;
  text: string;
  domain: string;
  is_reverse?: boolean;
  type: string;
  options?: any[];
  correct?: string;
  title?: string;
  tasks?: string[];
  image_url?: string;
  is_validity?: boolean;
}

interface QuestionBank {
  package: number;
  segment: string;
  total_questions: number;
  questions: Question[];
  validity_items: any[];
}

const AssessmentRunner: React.FC = () => {
  const { packageId } = useParams();
  const { segment, isSegmentSelected } = useSegment();
  const { user } = useUser();
  const { isGuestMode } = useGuestMode();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bank, setBank] = useState<QuestionBank | null>(null);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Redirect to segment selection if no segment is chosen
  useEffect(() => {
    if (!isSegmentSelected) {
      navigate('/select-segment');
    }
  }, [isSegmentSelected, navigate]);

  useEffect(() => {
    if (!packageId || !segment) return;
    
    setLoading(true);
    setError(null);
    
    const fetchQuestions = async () => {
      try {
        const res = await apiClient.get(`/assessments/questions/${packageId}?segment=${segment}`);
        const combined = [...res.data.questions];
        
        res.data.sjt_scenarios?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: s.description,
            title: s.title,
            type: 'sjt',
            domain: 'sjt',
            options: Object.entries(s.options || {}).map(([k, v]) => ({ key: k, text: v })),
          });
        });

        res.data.ethics_scenarios?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: s.description,
            title: s.title,
            domain: 'ethics',
            type: 'ethics',
          });
        });

        res.data.priority_tasks?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: s.title,
            tasks: s.tasks,
            domain: 'priority',
            type: 'priority',
          });
        });

        res.data.attention_tests?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: s.instruction,
            domain: 'attention',
            type: 'attention',
          });
        });

        res.data.ei_tasks?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: segment === 'student' ? s.text_student : s.text_professional,
            domain: 'emotional_intelligence',
            type: s.options ? 'ei_mcq' : 'ei_text',
            options: s.options,
          });
        });

        res.data.logic_tasks?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: segment === 'student' ? s.text_student : s.text_professional,
            domain: 'logic',
            type: 'logic_open',
          });
        });

        res.data.picture_tasks?.forEach((s: any) => {
          combined.push({
            id: s.id,
            text: segment === 'student' ? s.text_student : s.text_professional,
            domain: 'visual_analysis',
            type: 'visual',
            image_url: s.image_url,
          });
        });

        // Mix validity items randomly into questions
        res.data.validity_items.forEach((v: any) => {
          const randIdx = Math.floor(Math.random() * combined.length);
          combined.splice(randIdx, 0, { ...v, is_validity: true });
        });
        
        if (combined.length === 0) {
          setError("No questions were loaded for this assessment package. Please try a different level.");
          setLoading(false);
          return;
        }

        setBank({ ...res.data, questions: combined });
        setLoading(false);
      } catch (e: any) {
        console.error("Failed to load assessment questions:", e);
        const message = e?.response?.data?.detail 
          || e?.message 
          || "Failed to load assessment questions. Please check your connection and try again.";
        setError(message);
        setLoading(false);
      }
    };
    fetchQuestions();
  }, [packageId, segment]);

  const handleAnswer = (val: any) => {
    const q = bank!.questions[currentIdx];
    setAnswers(prev => ({ ...prev, [q.id]: val }));
    
    // Auto advance after small delay for non-writing tasks
    const openTextTypes = ['writing', 'ethics', 'ei_text', 'attention', 'logic_open', 'priority'];
    if (!openTextTypes.includes(q.type) && currentIdx < bank!.questions.length - 1) {
      setTimeout(() => setCurrentIdx(c => c + 1), 400);
    }
  };

  const handleSubmit = async () => {
    if (!bank) return;
    const userId = user?.id || (isGuestMode ? 'guest_anonymous' : null);
    if (!userId) return;
    setIsSubmitting(true);

    const submissionAnswers: any[] = [];
    const validityChecks: boolean[] = [];

    bank.questions.forEach((q: any) => {
      const val = answers[q.id];
      if (val === undefined || val === null || val === '') return;

      if (q.is_validity) {
        let passed = true;
        if (q.type === 'attention' && val !== q.expected) passed = false;
        if (q.type === 'random' && val > 3) passed = false; // Usually expected low
        if (q.type === 'faking' && val === 5) passed = false; // Too good to be true
        validityChecks.push(passed);
      } else {
        let scoreVal = 3;
        if (typeof val === 'number') scoreVal = val;
        
        submissionAnswers.push({
          question_id: q.id,
          domain: q.domain || "Unknown",
          score: scoreVal,
          is_reverse: q.is_reverse || false,
          question_text: q.text || q.title || q.description || "",
          raw_response: val
        });
      }
    });

    try {
      const pkgType = packageId === '1' ? 'pkg1_wellbeing' : packageId === '2' ? 'pkg2_workforce' : 'pkg3_jobfit';
      const payload = {
        user_id: userId,
        segment: segment,
        package_type: pkgType,
        answers: submissionAnswers,
        validity_checks: validityChecks
      };
      
      const res = await apiClient.post('/assessments/score', payload);
      setResult(res.data);
    } catch (e) {
      console.error("Submission failed", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
          <p className="text-gray-500 text-sm font-medium">Loading assessment questions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-red-100 text-center max-w-md w-full">
            <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={32} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Could Not Load Assessment</h1>
            <p className="text-gray-500 mb-6 text-sm leading-relaxed">{error}</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-colors"
              >
                <RefreshCw size={18} /> Retry
              </button>
              <button
                onClick={() => navigate('/assessments')}
                className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gray-100 text-gray-700 font-bold hover:bg-gray-200 transition-colors"
              >
                Back to Assessments
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-12 w-full">
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
            <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} />
            </div>
            <h1 className="text-3xl font-black text-gray-900 mb-2 text-center">Employee Role Fitment Report</h1>
            <p className="text-gray-500 mb-8 text-center">PsyPredict Assessment Platform</p>
            
            {result.detailed_report ? (
              <div className="space-y-8">
                {/* Role Fitment Score */}
                <div className={`rounded-2xl p-6 text-center ${result.detailed_report.role_fitment_score > 75 ? 'bg-emerald-50 border-emerald-100' : result.detailed_report.role_fitment_score > 50 ? 'bg-amber-50 border-amber-100' : 'bg-red-50 border-red-100'} border-2`}>
                  <h2 className={`text-2xl font-bold mb-2 ${result.detailed_report.role_fitment_score > 75 ? 'text-emerald-700' : result.detailed_report.role_fitment_score > 50 ? 'text-amber-700' : 'text-red-700'}`}>
                    {result.detailed_report.role_fitment_score > 75 ? 'Excellent Fit for Current Role' : result.detailed_report.role_fitment_score > 50 ? 'Moderate Fit for Current Role' : 'Poor Fit for Current Role'}
                  </h2>
                  <p className="text-gray-700 font-medium">Role Fitment Score: {result.detailed_report.role_fitment_score}/100</p>
                </div>

                {/* Growth Potential */}
                <div className="bg-indigo-50 rounded-2xl p-6 border-2 border-indigo-100 flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-bold text-indigo-900 mb-1">Growth Potential</h3>
                    <p className="text-indigo-700 text-sm">Potential for next-level acceleration</p>
                  </div>
                  <div className="text-4xl font-black text-indigo-600">
                    {result.detailed_report.growth_potential_score}<span className="text-xl text-indigo-400">/100</span>
                  </div>
                </div>

                {/* Psychometric Profile */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4 border-b pb-2">Psychometric Profile</h3>
                  <div className="space-y-4">
                    {result.domain_scores && result.domain_scores.map((ds: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                        <span className="font-medium text-gray-700 w-1/3">{ds.domain_name}</span>
                        <div className="w-1/3 h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div className={`h-full ${ds.score > 70 ? 'bg-emerald-500' : ds.score > 40 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${ds.score}%` }} />
                        </div>
                        <span className="font-bold text-gray-900 w-16 text-right">{ds.score}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key Strengths & Development Areas */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-emerald-50 rounded-2xl p-6 border border-emerald-100 border-l-4 border-l-emerald-500">
                    <h3 className="text-lg font-bold text-emerald-900 mb-3">Key Strengths</h3>
                    <ul className="list-disc pl-5 text-emerald-800 space-y-2 text-sm">
                      {result.detailed_report.key_strengths.map((str: string, i: number) => <li key={i}>{str}</li>)}
                    </ul>
                  </div>
                  <div className="bg-orange-50 rounded-2xl p-6 border border-orange-100 border-l-4 border-l-orange-500">
                    <h3 className="text-lg font-bold text-orange-900 mb-3">Development Areas</h3>
                    <ul className="list-disc pl-5 text-orange-800 space-y-2 text-sm">
                      {result.detailed_report.development_areas.map((str: string, i: number) => <li key={i}>{str}</li>)}
                    </ul>
                  </div>
                </div>

                {/* Co-working Insights */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4 border-b pb-2">Co-working Insights</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(result.detailed_report.coworking_insights).map(([key, val], idx) => (
                      <div key={idx} className="bg-white border rounded-xl p-4 shadow-sm">
                        <p className="text-xs text-gray-500 uppercase tracking-wider font-bold mb-1">{key}</p>
                        <p className="font-semibold text-gray-900">{String(val)}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Executive Summary */}
                <div className="bg-gray-900 text-white rounded-2xl p-6">
                  <h3 className="text-lg font-bold mb-4 border-b border-gray-700 pb-2">Executive Summary</h3>
                  <ul className="list-disc pl-5 space-y-2 text-gray-300">
                    {result.detailed_report.executive_summary.map((str: string, i: number) => <li key={i}>{str}</li>)}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 rounded-2xl p-6 mb-8 text-left w-full mx-auto">
                <h3 className="text-xl font-bold text-gray-900 mb-4 border-b pb-2">Score Summary</h3>
                <div className="flex justify-between items-center mb-6">
                  <span className="text-gray-600 font-medium">Risk Level</span>
                  <span className="font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full text-sm">
                    {result.final_risk_level}
                  </span>
                </div>
              </div>
            )}

            <div className="mt-10 flex justify-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full transition-colors"
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!bank || !bank.questions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100 text-center max-w-md w-full">
            <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <ShieldAlert size={32} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">No Questions Available</h1>
            <p className="text-gray-500 mb-6 text-sm">This assessment package has no questions loaded. Please try a different level or contact support.</p>
            <button
              onClick={() => navigate('/assessments')}
              className="px-6 py-3 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-colors"
            >
              Back to Assessments
            </button>
          </div>
        </main>
      </div>
    );
  }

  const currentQ = bank.questions[currentIdx];
  const progress = ((currentIdx) / bank.questions.length) * 100;
  const isAnswered = answers[currentQ.id] !== undefined && answers[currentQ.id] !== null;
  const isLast = currentIdx === bank.questions.length - 1;

  const options = [
    { val: 1, label: "Strongly Disagree" },
    { val: 2, label: "Disagree" },
    { val: 3, label: "Neutral" },
    { val: 4, label: "Agree" },
    { val: 5, label: "Strongly Agree" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Navbar />
      
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-8 flex flex-col">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">
            <span>Question {currentIdx + 1} of {bank.questions.length}</span>
            <span>{Math.round(progress)}% Completed</span>
          </div>
          <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-indigo-600 transition-all duration-500 ease-out" 
              style={{ width: `${progress}%` }} 
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12 flex-1 flex flex-col justify-center min-h-[400px]">
          {currentQ.title && (
            <h3 className="text-sm font-bold text-indigo-600 uppercase tracking-wider mb-4 text-center">
              {currentQ.title}
            </h3>
          )}
          <h2 className="text-2xl md:text-3xl font-medium text-gray-900 mb-10 text-center leading-relaxed">
            {currentQ.text}
          </h2>

          <div className="space-y-3 max-w-xl mx-auto w-full">
            {/* LIKERT TYPE */}
            {(currentQ.type === 'likert' || !currentQ.type) && options.map((opt) => {
              const selected = answers[currentQ.id] === opt.val;
              return (
                <button
                  key={opt.val}
                  onClick={() => handleAnswer(opt.val)}
                  className={`w-full py-4 px-6 rounded-2xl border-2 transition-all duration-200 flex items-center justify-between group
                    ${selected 
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700' 
                      : 'border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 text-gray-600'
                    }
                  `}
                >
                  <span className="font-medium">{opt.label}</span>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors
                    ${selected ? 'border-indigo-600' : 'border-gray-300 group-hover:border-indigo-300'}
                  `}>
                    {selected && <div className="w-2.5 h-2.5 bg-indigo-600 rounded-full" />}
                  </div>
                </button>
              );
            })}

            {/* LOGIC / MCQ / EI_MCQ TYPE */}
            {(currentQ.type === 'logic' || currentQ.type === 'ei_mcq') && currentQ.options && currentQ.options.map((opt: any, i: number) => {
              const selected = answers[currentQ.id] === opt;
              return (
                <button
                  key={i}
                  onClick={() => handleAnswer(opt)}
                  className={`w-full py-4 px-6 rounded-2xl border-2 transition-all duration-200 flex items-center justify-between group text-left
                    ${selected 
                      ? 'border-purple-600 bg-purple-50 text-purple-700' 
                      : 'border-gray-100 hover:border-purple-200 hover:bg-purple-50/50 text-gray-600'
                    }
                  `}
                >
                  <span className="font-medium">{opt}</span>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors shrink-0 ml-4
                    ${selected ? 'border-purple-600' : 'border-gray-300 group-hover:border-purple-300'}
                  `}>
                    {selected && <div className="w-2.5 h-2.5 bg-purple-600 rounded-full" />}
                  </div>
                </button>
              );
            })}

            {/* SJT TYPE */}
            {currentQ.type === 'sjt' && currentQ.options && currentQ.options.map((opt: any) => {
              const selected = answers[currentQ.id] === opt.key;
              return (
                <button
                  key={opt.key}
                  onClick={() => handleAnswer(opt.key)}
                  className={`w-full py-4 px-6 rounded-2xl border-2 transition-all duration-200 flex items-center justify-between group text-left
                    ${selected 
                      ? 'border-emerald-600 bg-emerald-50 text-emerald-700' 
                      : 'border-gray-100 hover:border-emerald-200 hover:bg-emerald-50/50 text-gray-600'
                    }
                  `}
                >
                  <span className="font-medium pr-4">{opt.text}</span>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors shrink-0
                    ${selected ? 'border-emerald-600' : 'border-gray-300 group-hover:border-emerald-300'}
                  `}>
                    {selected && <div className="w-2.5 h-2.5 bg-emerald-600 rounded-full" />}
                  </div>
                </button>
              );
            })}

            {/* PRIORITY TYPE */}
            {currentQ.type === 'priority' && currentQ.tasks && (
              <div className="space-y-3">
                <p className="text-sm text-gray-500 mb-4 text-center">Click the tasks to set their priority order (1 = highest priority)</p>
                {currentQ.tasks.map((task: string, i: number) => {
                  const currentAns = answers[currentQ.id] || [];
                  const selectedOrder = currentAns.indexOf(i);
                  const isSelected = selectedOrder !== -1;
                  return (
                    <button
                      key={i}
                      onClick={() => {
                        const newAns = [...currentAns];
                        if (isSelected) {
                          newAns.splice(selectedOrder, 1);
                        } else {
                          newAns.push(i);
                        }
                        handleAnswer(newAns);
                      }}
                      className={`w-full p-4 rounded-xl border-2 text-left flex items-center gap-4 transition-all 
                        ${isSelected ? 'border-indigo-600 bg-indigo-50 shadow-sm' : 'border-gray-100 hover:border-indigo-200'}
                      `}
                    >
                      <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center font-bold text-sm
                        ${isSelected ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-400'}
                      `}>
                        {isSelected ? selectedOrder + 1 : ''}
                      </div>
                      <span className="flex-1 text-gray-700">{task}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {/* OPEN TEXT & VISUAL TYPES */}
            {['writing', 'ethics', 'ei_text', 'visual'].includes(currentQ.type) && (
              <div className="w-full flex flex-col items-center">
                {currentQ.type === 'visual' && currentQ.image_url && (
                  <img 
                    src={currentQ.image_url} 
                    alt="Assessment Scenario" 
                    className="w-full max-h-[300px] object-cover rounded-xl mb-6 shadow-md"
                  />
                )}
                <textarea
                  value={answers[currentQ.id] || ''}
                  onChange={(e) => handleAnswer(e.target.value)}
                  placeholder="Type your response here... (Minimum 2 sentences)"
                  className="w-full h-48 p-5 border-2 border-gray-200 rounded-2xl focus:border-indigo-600 focus:ring-4 focus:ring-indigo-600/10 transition-all resize-none text-gray-700"
                />
                <p className="text-xs text-gray-400 mt-2 text-right">
                  {(answers[currentQ.id] || '').length} characters
                </p>
              </div>
            )}

            {/* SHORT OPEN TEXT TYPES */}
            {['attention', 'logic_open'].includes(currentQ.type) && (
              <div className="w-full">
                <input 
                  type="text"
                  value={answers[currentQ.id] || ''}
                  onChange={(e) => handleAnswer(e.target.value)}
                  className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:border-indigo-600 focus:ring-4 focus:ring-indigo-600/10 transition-all text-gray-700 text-center text-lg font-medium"
                  placeholder="Enter your answer..."
                />
              </div>
            )}
          </div>
        </div>

        {/* Navigation Controls */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={() => setCurrentIdx(c => Math.max(0, c - 1))}
            disabled={currentIdx === 0}
            className={`flex items-center gap-2 px-6 py-3 rounded-full font-semibold transition-colors
              ${currentIdx === 0 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'}
            `}
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {isLast ? (
            <button
              onClick={handleSubmit}
              disabled={!isAnswered || isSubmitting}
              className={`flex items-center gap-2 px-8 py-3 rounded-full font-bold transition-all
                ${!isAnswered || isSubmitting
                  ? 'bg-gray-300 text-white cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-500/30'}
              `}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Assessment'}
              {!isSubmitting && <CheckCircle2 size={20} />}
            </button>
          ) : (
            <button
              onClick={() => setCurrentIdx(c => Math.min(bank.questions.length - 1, c + 1))}
              disabled={!isAnswered}
              className={`flex items-center gap-2 px-6 py-3 rounded-full font-semibold transition-all
                ${!isAnswered
                  ? 'text-gray-300 cursor-not-allowed'
                  : 'text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700'}
              `}
            >
              Next
              <ChevronRight size={20} />
            </button>
          )}
        </div>
      </main>
    </div>
  );
};

export default AssessmentRunner;

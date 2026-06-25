import React, { useEffect, useState } from "react";
import { getVisualScenarios, type AssessmentScenario } from "../services/api";
import { Brain, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/react";

export const VisualPsychology: React.FC = () => {
  const [scenarios, setScenarios] = useState<AssessmentScenario[]>([]);
  const [selected, setSelected] = useState<AssessmentScenario | null>(null);
  const [answer, setAnswer] = useState("");
  const navigate = useNavigate();
  const { user } = useUser();

  useEffect(() => {
    if (!user) return;
    getVisualScenarios(user.id).then(res => {
      setScenarios(res.scenarios);
    }).catch(e => console.error("Failed to load visual scenarios", e));
  }, [user]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-indigo-600 font-semibold mb-6 hover:text-indigo-800 transition-colors">
          <ArrowLeft size={16} /> Back to Dashboard
        </button>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 mb-8">
          <div className="bg-indigo-100 p-3 rounded-xl">
            <Brain className="w-8 h-8 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Visual Psychology Analysis</h1>
            <p className="text-gray-500">Analyze ambiguous social and emotional scenarios to build your profile.</p>
          </div>
        </div>

        {!selected ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map(sc => (
              <div 
                key={sc.id} 
                onClick={() => setSelected(sc)}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow group"
              >
                <div className="h-40 bg-gray-100 relative overflow-hidden">
                  {sc.image_url && <img src={sc.image_url} alt={sc.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />}
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-gray-800">{sc.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{sc.description}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex flex-col md:flex-row">
            <div className="w-full md:w-1/2 h-64 md:h-auto bg-gray-100">
              {selected.image_url && <img src={selected.image_url} alt={selected.title} className="w-full h-full object-cover" />}
            </div>
            <div className="p-6 md:w-1/2 flex flex-col">
              <button onClick={() => setSelected(null)} className="text-sm text-gray-400 mb-4 self-start hover:text-gray-600">&larr; Choose another</button>
              <h2 className="text-xl font-bold text-gray-800 mb-2">{selected.title}</h2>
              <p className="text-gray-600 text-sm mb-6">{selected.description}</p>
              
              <div className="space-y-2 mb-6">
                {selected.questions.map((q, i) => (
                  <p key={i} className="text-sm font-semibold text-indigo-700 flex items-start gap-2">
                    <span className="text-indigo-400 opacity-50 mt-0.5">•</span> {q}
                  </p>
                ))}
              </div>

              <textarea 
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                className="w-full min-h-[120px] p-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm mb-4"
                placeholder="Type your analysis here..."
              />
              <button 
                onClick={() => {
                  alert("Analysis submitted to your psychological profile!");
                  setSelected(null);
                  setAnswer("");
                }}
                className="bg-indigo-600 text-white font-semibold py-2 px-4 rounded-xl hover:bg-indigo-700 transition-colors self-end"
              >
                Submit Analysis
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VisualPsychology;

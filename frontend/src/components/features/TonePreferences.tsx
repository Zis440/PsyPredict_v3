import React, { useState, useEffect } from "react";
import { getPatientPreferences, updatePatientPreferences } from "../../services/api";
import { Palette, MessageSquare, BookOpen, Save, CheckCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  userId: string;
}

const TONES = [
  { value: "warm", label: "Warm & Nurturing", icon: "🤗", desc: "Gentle, empathetic, like a caring mentor" },
  { value: "formal", label: "Professional", icon: "🩺", desc: "Clinical, structured, evidence-based" },
  { value: "motivational", label: "Motivational", icon: "💪", desc: "Energetic, empowering, action-oriented" },
  { value: "calm", label: "Calm & Meditative", icon: "🧘", desc: "Grounding, mindful, peaceful" },
  { value: "structured", label: "Structured", icon: "📋", desc: "Step-by-step, organized, clear" },
];

const VERBOSITY = [
  { value: "concise", label: "Concise", desc: "Short and impactful (3-4 sentences)" },
  { value: "moderate", label: "Moderate", desc: "Balanced depth (5-7 sentences)" },
  { value: "detailed", label: "Detailed", desc: "In-depth exploration (7-10 sentences)" },
];

const FRAMEWORKS = [
  { value: "auto", label: "Auto (Let AI decide)", icon: "🤖" },
  { value: "cbt", label: "CBT (Cognitive Behavioral)", icon: "🧠" },
  { value: "dbt", label: "DBT (Dialectical Behavioral)", icon: "⚖️" },
  { value: "psychodynamic", label: "Psychodynamic", icon: "🔍" },
  { value: "gita", label: "Bhagavad Gita Focus", icon: "🕉️" },
];

const TonePreferences: React.FC<Props> = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [tone, setTone] = useState("warm");
  const [verbosity, setVerbosity] = useState("moderate");
  const [framework, setFramework] = useState("auto");

  useEffect(() => {
    if (!userId) return;
    getPatientPreferences(userId)
      .then((p) => {
        setTone(p.preferred_tone || "warm");
        setVerbosity(p.verbosity || "moderate");
        setFramework(p.framework_preference || "auto");
      })
      .catch(() => {/* defaults are fine */})
      .finally(() => setLoading(false));
  }, [userId]);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await updatePatientPreferences(userId, {
        preferred_tone: tone,
        verbosity,
        framework_preference: framework,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("Failed to save preferences:", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Tone Selection */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-2 mb-3">
          <Palette className="w-4 h-4 text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-700">Therapist Tone</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {TONES.map((t) => (
            <button
              key={t.value}
              onClick={() => setTone(t.value)}
              className={`text-left p-3 rounded-xl border-2 transition-all ${
                tone === t.value
                  ? "border-indigo-500 bg-indigo-50 shadow-sm"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-base">{t.icon}</span>
                <span className={`text-sm font-medium ${tone === t.value ? "text-indigo-700" : "text-gray-700"}`}>
                  {t.label}
                </span>
              </div>
              <p className="text-xs text-gray-500 ml-7">{t.desc}</p>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Verbosity Selection */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
        <div className="flex items-center gap-2 mb-3">
          <MessageSquare className="w-4 h-4 text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-700">Response Length</h3>
        </div>
        <div className="flex gap-2">
          {VERBOSITY.map((v) => (
            <button
              key={v.value}
              onClick={() => setVerbosity(v.value)}
              className={`flex-1 p-3 rounded-xl border-2 transition-all text-center ${
                verbosity === v.value
                  ? "border-indigo-500 bg-indigo-50 shadow-sm"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <p className={`text-sm font-medium ${verbosity === v.value ? "text-indigo-700" : "text-gray-700"}`}>
                {v.label}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">{v.desc}</p>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Framework Selection */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-4 h-4 text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-700">Therapeutic Framework</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {FRAMEWORKS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFramework(f.value)}
              className={`text-left p-3 rounded-xl border-2 transition-all ${
                framework === f.value
                  ? "border-indigo-500 bg-indigo-50 shadow-sm"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-base">{f.icon}</span>
                <span className={`text-sm font-medium ${framework === f.value ? "text-indigo-700" : "text-gray-700"}`}>
                  {f.label}
                </span>
              </div>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
        className="flex justify-end"
      >
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-semibold text-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
        >
          {saving ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</>
          ) : saved ? (
            <><CheckCircle className="w-4 h-4" /> Saved!</>
          ) : (
            <><Save className="w-4 h-4" /> Save Preferences</>
          )}
        </button>
      </motion.div>
    </div>
  );
};

export default TonePreferences;

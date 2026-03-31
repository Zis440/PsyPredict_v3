import React, { useState, useEffect } from "react";
import { getPatientProgress } from "../../services/api";
import type { PatientProgress } from "../../services/api";
import { TrendingUp, TrendingDown, Minus, Activity, Brain, Shield, Calendar } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  userId: string;
}

const RISK_COLORS: Record<string, string> = {
  MINIMAL: "#22c55e",
  LOW: "#3b82f6",
  MODERATE: "#eab308",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

const EMOTION_EMOJI: Record<string, string> = {
  sadness: "😢", sad: "😢",
  joy: "😊", happy: "😊",
  anger: "😠", angry: "😠",
  fear: "😰",
  surprise: "😮", surprised: "😮",
  disgust: "🤢",
  neutral: "😐",
  love: "❤️",
};

const ProgressDashboard: React.FC<Props> = ({ userId }) => {
  const [progress, setProgress] = useState<PatientProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    getPatientProgress(userId)
      .then(setProgress)
      .catch(() => setError("No progress data yet. Start chatting to build your journey."))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !progress) {
    return (
      <div className="text-center py-16 text-gray-400">
        <Brain className="w-12 h-12 mx-auto mb-3 opacity-40" />
        <p className="text-sm">{error || "No progress data available."}</p>
      </div>
    );
  }

  // Compute emotion frequency
  const emotionCounts: Record<string, number> = {};
  progress.emotion_trend.forEach(({ emotion }) => {
    emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
  });
  const sortedEmotions = Object.entries(emotionCounts).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const maxEmotionCount = sortedEmotions[0]?.[1] || 1;

  // Trend indicator
  const trendIcon = progress.summary === "improving"
    ? <TrendingUp className="w-4 h-4 text-green-500" />
    : progress.summary === "worsening"
    ? <TrendingDown className="w-4 h-4 text-red-500" />
    : <Minus className="w-4 h-4 text-gray-400" />;

  const trendLabel = progress.summary === "improving" ? "Improving"
    : progress.summary === "worsening" ? "Needs Attention"
    : "Stable";

  const trendColor = progress.summary === "improving" ? "text-green-600 bg-green-50"
    : progress.summary === "worsening" ? "text-red-600 bg-red-50"
    : "text-gray-600 bg-gray-50";

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}
          className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm"
        >
          <div className="flex items-center gap-2 text-gray-500 text-xs font-medium mb-1">
            <Calendar className="w-3.5 h-3.5" /> Sessions
          </div>
          <p className="text-2xl font-bold text-gray-900">{progress.total_sessions}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
          className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm"
        >
          <div className="flex items-center gap-2 text-gray-500 text-xs font-medium mb-1">
            <Shield className="w-3.5 h-3.5" /> Current Risk
          </div>
          <p className="text-2xl font-bold" style={{ color: RISK_COLORS[progress.current_risk_level] || "#6b7280" }}>
            {progress.current_risk_level}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm"
        >
          <div className="flex items-center gap-2 text-gray-500 text-xs font-medium mb-1">
            <Activity className="w-3.5 h-3.5" /> Trend
          </div>
          <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${trendColor}`}>
            {trendIcon} {trendLabel}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm"
        >
          <div className="flex items-center gap-2 text-gray-500 text-xs font-medium mb-1">
            <Brain className="w-3.5 h-3.5" /> First Session
          </div>
          <p className="text-sm font-semibold text-gray-700">
            {progress.first_session ? new Date(progress.first_session).toLocaleDateString() : "—"}
          </p>
        </motion.div>
      </div>

      {/* Emotion Distribution */}
      <motion.div
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
        className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm"
      >
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Emotion Distribution</h3>
        <div className="space-y-2.5">
          {sortedEmotions.map(([emotion, count]) => (
            <div key={emotion} className="flex items-center gap-3">
              <span className="w-6 text-center text-sm">{EMOTION_EMOJI[emotion] || "🔵"}</span>
              <span className="w-20 text-xs text-gray-600 capitalize truncate">{emotion}</span>
              <div className="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(count / maxEmotionCount) * 100}%` }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-indigo-600"
                />
              </div>
              <span className="w-8 text-xs text-gray-400 text-right">{count}×</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Risk Timeline */}
      {progress.risk_trend.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm"
        >
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Risk Level Timeline</h3>
          <div className="flex items-end gap-1 h-24">
            {progress.risk_trend.slice(-30).map((point, i) => {
              const height = Math.max(8, point.score * 100);
              return (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${height}%` }}
                  transition={{ duration: 0.4, delay: 0.02 * i }}
                  className="flex-1 rounded-t-sm min-w-[4px] transition-colors"
                  style={{ backgroundColor: RISK_COLORS[point.risk] || "#d1d5db" }}
                  title={`${point.risk} — ${new Date(point.date).toLocaleDateString()}`}
                />
              );
            })}
          </div>
          <div className="flex justify-between mt-2 text-[10px] text-gray-400">
            <span>Older →</span>
            <span>← Recent</span>
          </div>
        </motion.div>
      )}

      {/* Progress Snapshots */}
      {progress.snapshots.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm"
        >
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Progress Reports</h3>
          <div className="space-y-3">
            {progress.snapshots.slice(0, 5).map((snap, i) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3 text-xs">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-gray-500">{new Date(snap.snapshot_date).toLocaleDateString()}</span>
                  <span className={`px-2 py-0.5 rounded-full font-semibold ${
                    snap.improvement_score > 0.1 ? "bg-green-100 text-green-700" :
                    snap.improvement_score < -0.1 ? "bg-red-100 text-red-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>
                    {snap.improvement_score > 0 ? "+" : ""}{(snap.improvement_score * 100).toFixed(0)}% change
                  </span>
                </div>
                <p className="text-gray-700">{snap.summary}</p>
                {snap.dominant_emotions.length > 0 && (
                  <div className="flex gap-1 mt-1.5">
                    {snap.dominant_emotions.map((e, j) => (
                      <span key={j} className="px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded text-[10px]">{e}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ProgressDashboard;

// src/components/features/ChatInterface.tsx
// Upgraded: Displays structured PsychReport (clinical report panel) below each AI response.
// Convex-powered: Uses Convex queries/mutations for conversation and message persistence.

import React, { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../../services/api";
import type { PsychReport, CrisisResource, RemedyData } from "../../services/api";
import { Bot, User, FileText, ChevronDown, ChevronUp, AlertTriangle, Phone } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { useMutation, useQuery } from "convex/react";
import { api } from "../../../convex/_generated/api";
import type { Id } from "../../../convex/_generated/dataModel";
import { generateChatPDF } from "../../utils/pdfUtils";
import { useNavigate } from "react-router-dom";

interface Message {
  role: "user" | "assistant";
  content: string;
  report?: PsychReport;
  fusionScore?: number;
  remedy?: RemedyData;
}

interface ChatProps {
  currentEmotion: string;
  sessionId?: string;
}

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content: "Hello. I am here to listen. How are you feeling right now?",
};

// ── Risk Level Display Config ──────────────────────────────────────────────
const RISK_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  MINIMAL: { color: "text-green-700", bg: "bg-green-100", label: "Minimal Risk" },
  LOW: { color: "text-blue-700", bg: "bg-blue-100", label: "Low Risk" },
  MODERATE: { color: "text-yellow-700", bg: "bg-yellow-100", label: "Moderate Risk" },
  HIGH: { color: "text-orange-700", bg: "bg-orange-100", label: "High Risk" },
  CRITICAL: { color: "text-red-700", bg: "bg-red-100", label: "Critical Risk" },
};

// ── Remedy Panel ──────────────────────────────────────────────────────────
const RemedyPanel: React.FC<{ remedy: RemedyData }> = ({ remedy }) => {
  const [open, setOpen] = React.useState(false);
  return (
    <div className="mt-2 border border-amber-200 rounded-xl overflow-hidden text-xs bg-white">
      <button
        onClick={() => setOpen(p => !p)}
        className="w-full flex items-center justify-between px-3 py-2 bg-amber-50 hover:bg-amber-100 transition-colors"
      >
        <div className="flex items-center gap-2 text-amber-700 font-semibold">
          <span>🌿</span>
          <span>{remedy.condition} — Ancient Wisdom & Treatment</span>
        </div>
        <span className="text-amber-400">{open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}</span>
      </button>
      {open && (
        <div className="px-3 py-3 space-y-3 bg-amber-50/50">
          <div>
            <p className="font-semibold text-amber-800 uppercase tracking-wide text-[10px] mb-1">🕉️ Gita Wisdom</p>
            <p className="text-gray-700 italic">"{remedy.gita_remedy}"</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white rounded-lg p-2 shadow-sm">
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px] mb-1">💊 Medications</p>
              <p className="text-gray-700">{remedy.medications}</p>
            </div>
            <div className="bg-white rounded-lg p-2 shadow-sm">
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px] mb-1">📋 Dosage</p>
              <p className="text-gray-700">{remedy.dosage}</p>
            </div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow-sm">
            <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px] mb-1">🩺 Recommended Treatments</p>
            <p className="text-gray-700">{remedy.treatments}</p>
          </div>
          <p className="text-[9px] text-gray-400 italic">⚠️ Always consult a licensed healthcare professional before taking any medication.</p>
        </div>
      )}
    </div>
  );
};

const CrisisBanner: React.FC<{ resources: CrisisResource[] }> = ({ resources }) => (
  <div className="mt-2 bg-red-50 border border-red-300 rounded-xl p-3">
    <div className="flex items-center gap-2 text-red-700 font-semibold text-sm mb-2">
      <AlertTriangle size={14} />
      Immediate Crisis Support Resources
    </div>
    <div className="space-y-1">
      {resources.map((r, i) => (
        <div key={i} className="flex items-center gap-2 text-xs text-red-800">
          <Phone size={11} />
          <span className="font-medium">{r.name}:</span>
          <span>{r.contact}</span>
          <span className="text-red-500">({r.available})</span>
        </div>
      ))}
    </div>
  </div>
);

// ── Clinical Report Panel ──────────────────────────────────────────────────
const ClinicalReport: React.FC<{ report: PsychReport; fusionScore?: number }> = ({
  report,
  fusionScore,
}) => {
  const [expanded, setExpanded] = useState(false);
  const risk = RISK_CONFIG[report.risk_classification] ?? RISK_CONFIG.MINIMAL;

  return (
    <div className="mt-2 border border-gray-200 rounded-xl overflow-hidden text-xs">
      {/* Header row — always visible */}
      <button
        onClick={() => setExpanded((p) => !p)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded-full font-semibold text-[10px] ${risk.bg} ${risk.color}`}>
            {risk.label}
          </span>
          {report.service_degraded && (
            <span className="px-2 py-0.5 rounded-full font-semibold text-[10px] bg-gray-200 text-gray-600">
              Service Degraded
            </span>
          )}
          {typeof fusionScore === "number" && (
            <span className="text-gray-400">
              Fusion: {(fusionScore * 100).toFixed(0)}%
            </span>
          )}
          <span className="text-gray-400">
            Confidence: {(report.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
        <span className="text-gray-400">
          {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </span>
      </button>

      {/* Expanded section */}
      {expanded && (
        <div className="px-3 py-3 space-y-2.5 bg-white">
          <div>
            <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">
              Emotional State
            </p>
            <p className="text-gray-700 mt-0.5">{report.emotional_state_summary}</p>
          </div>

          <div>
            <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">
              Behavioral Inference
            </p>
            <p className="text-gray-700 mt-0.5">{report.behavioral_inference}</p>
          </div>

          {report.cognitive_distortions.length > 0 && (
            <div>
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">
                Cognitive Distortions
              </p>
              <div className="flex flex-wrap gap-1 mt-1">
                {report.cognitive_distortions.map((d, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-[10px]"
                  >
                    {d}
                  </span>
                ))}
              </div>
            </div>
          )}

          {report.suggested_interventions.length > 0 && (
            <div>
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">
                Suggested Interventions
              </p>
              <ul className="mt-1 list-disc list-inside space-y-0.5 text-gray-700">
                {report.suggested_interventions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {report.crisis_triggered && report.crisis_resources && (
            <CrisisBanner resources={report.crisis_resources} />
          )}
        </div>
      )}
    </div>
  );
};

// ── Main ChatInterface ─────────────────────────────────────────────────────
const ChatInterface: React.FC<ChatProps> = ({ currentEmotion, sessionId }) => {
  const { user, isLocalMode } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(sessionId || null);
  const [createdDate, setCreatedDate] = useState<string>(new Date().toISOString());

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Convex mutations
  const createConversation = useMutation(api.conversations.create);
  const createMessage = useMutation(api.messages.create);

  // Convex queries (only used when NOT in local mode and we have a sessionId)
  const convexConversation = useQuery(
    api.conversations.get,
    !isLocalMode && sessionId ? { id: sessionId as Id<"conversations"> } : "skip"
  );
  const convexMessages = useQuery(
    api.messages.listByConversation,
    !isLocalMode && sessionId ? { conversationId: sessionId as Id<"conversations"> } : "skip"
  );

  // Load messages from Convex or localStorage
  useEffect(() => {
    if (!user) return;

    if (isLocalMode) {
      if (sessionId) {
        const localHistory = JSON.parse(localStorage.getItem('psypredict_local_history') || '{}');
        const conv = localHistory[sessionId];
        if (conv) {
          setConversationId(sessionId);
          setMessages(conv.messages || []);
          setCreatedDate(conv.created_at);
        } else {
          navigate('/dashboard');
        }
      } else {
        setMessages([]);
        setConversationId(null);
      }
      return;
    }

    // Convex mode — data is handled reactively by queries above
  }, [user, sessionId, isLocalMode]);

  // Sync Convex query results into local state
  useEffect(() => {
    if (isLocalMode || !sessionId) return;

    if (convexConversation === null) {
      // Conversation not found or not authorized
      navigate('/history');
      return;
    }

    if (convexConversation) {
      setCreatedDate(convexConversation.createdAt);
    }

    if (convexMessages) {
      const formatted: Message[] = convexMessages.map((msg) => {
        const meta = msg.metadata as Record<string, any> | null;
        return {
          role: (meta?.role === 'assistant' ? 'assistant' : 'user') as "user" | "assistant",
          content: msg.content,
          report: meta?.report,
          fusionScore: meta?.fusionScore,
        };
      });
      setMessages(formatted);
    }
  }, [convexConversation, convexMessages, isLocalMode, sessionId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !user) return;

    const userText = input;
    setInput("");
    setIsLoading(true);

    const userMsg: Message = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // 0. Ensure Conversation Exists
      let activeConversationId = conversationId;

      if (!activeConversationId) {
        if (isLocalMode) {
          activeConversationId = `local-${Date.now()}`;
          setConversationId(activeConversationId);
          const localHistory = JSON.parse(localStorage.getItem('psypredict_local_history') || '{}');
          localHistory[activeConversationId] = {
            id: activeConversationId,
            title: `Local Chat ${new Date().toLocaleDateString()}`,
            created_at: new Date().toISOString(),
            messages: []
          };
          localStorage.setItem('psypredict_local_history', JSON.stringify(localHistory));
        } else {
          // Create conversation in Convex
          const newConvId = await createConversation({
            title: `Chat on ${new Date().toLocaleDateString()}`
          });
          activeConversationId = newConvId;
          setConversationId(newConvId);
        }
      }

      // 1. Save User Message
      if (isLocalMode) {
        const localHistory = JSON.parse(localStorage.getItem('psypredict_local_history') || '{}');
        if (localHistory[activeConversationId]) {
          localHistory[activeConversationId].messages.push(userMsg);
          localStorage.setItem('psypredict_local_history', JSON.stringify(localHistory));
        }
      } else {
        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: userText,
          metadata: { role: 'user', emotion: currentEmotion },
        });
      }

      // 2. Call AI API
      const historyForApi = [...messages, userMsg];
      const result = await sendChatMessage(userText, currentEmotion, historyForApi);

      const botContent = result.response;
      const botMsg: Message = {
        role: "assistant",
        content: botContent,
        report: result.report,
        fusionScore: result.fusion_risk_score ?? undefined,
        remedy: result.remedy ?? undefined,
      };

      setMessages((prev) => [...prev, botMsg]);

      // 3. Save Assistant Message
      if (isLocalMode) {
        const localHistory = JSON.parse(localStorage.getItem('psypredict_local_history') || '{}');
        if (localHistory[activeConversationId]) {
          localHistory[activeConversationId].messages.push(botMsg);
          localStorage.setItem('psypredict_local_history', JSON.stringify(localHistory));
        }
      } else {
        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: botContent,
          metadata: { role: 'assistant', report: result.report, fusionScore: result.fusion_risk_score },
        });
      }

    } catch (error) {
      console.error("Chat failed:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I'm having trouble connecting right now. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden min-w-0 relative">
      {/* PDF Download Button */}
      <div className="absolute top-4 right-6 z-10">
        <button
          onClick={() => generateChatPDF([WELCOME_MESSAGE, ...messages], createdDate)}
          className="flex items-center gap-2 bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-indigo-100 transition-colors shadow-sm"
          title="Download Prescription PDF"
        >
          <FileText size={14} />
          Print to PDF
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-5 pt-12 space-y-3 bg-gray-50 min-w-0">
        {[WELCOME_MESSAGE, ...messages].map((msg, index) => (
          <div
            key={index}
            className={`flex w-full min-w-0 items-end gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"
              }`}
          >
            {/* Bot Icon */}
            {msg.role === "assistant" && (
              <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-indigo-600" />
              </div>
            )}

            {/* Message Bubble + Clinical Report */}
            <div className="max-w-[80%] min-w-0 flex flex-col">
              <div
                className={`
                  w-fit min-w-0 p-3 text-sm shadow-sm whitespace-pre-wrap overflow-hidden
                  ${msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-2xl rounded-br-none ml-auto"
                    : "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-none"
                  }
                `}
              >
                {msg.content}
              </div>

              {/* Clinical Report Panel (assistant messages with report only) */}
              {msg.role === "assistant" && msg.report && (
                <ClinicalReport report={msg.report} fusionScore={msg.fusionScore} />
              )}

              {/* Remedy Panel (only on assistant messages with remedy data) */}
              {msg.role === "assistant" && msg.remedy && (
                <RemedyPanel remedy={msg.remedy} />
              )}

              {/* Crisis banner at message level if critical & not yet shown in report */}
              {msg.role === "assistant" &&
                msg.report?.crisis_triggered &&
                msg.report.crisis_resources &&
                !msg.report.crisis_resources.length && (
                  <CrisisBanner resources={msg.report.crisis_resources} />
                )}
            </div>

            {/* User Icon */}
            {msg.role === "user" && (
              <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="text-xs text-gray-400 ml-2">
            PsyPredict is analyzing...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 bg-white border-t border-gray-200 flex gap-2 min-w-0 shrink-0 items-end">
        <textarea
          className="flex-1 min-w-0 border border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:border-indigo-500 text-sm resize-none overflow-y-auto max-h-32"
          placeholder="Type your thoughts..."
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="bg-indigo-600 text-white px-4 py-3 rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 transition-colors h-[46px] flex items-center justify-center"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;

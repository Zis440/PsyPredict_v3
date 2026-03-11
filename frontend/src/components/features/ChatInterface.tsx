import React, { useState, useRef, useEffect } from "react";
import { sendChatMessage, streamChatMessage } from "../../services/api";
import type { PsychReport, CrisisResource, RemedyData } from "../../services/api";
import { Bot, User, FileText, ChevronDown, ChevronUp, AlertTriangle, Phone, Lock } from "lucide-react";
import { useUser } from '@clerk/react';
import { useMutation, useQuery } from "convex/react";
import { api } from "../../../convex/_generated/api";
import type { Id } from "../../../convex/_generated/dataModel";
import { generateChatPDF } from "../../utils/pdfUtils";
import { useNavigate } from "react-router-dom";
import { useGuestMode } from "../../context/GuestModeContext";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from "../ui/tooltip";

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
  MINIMAL:  { color: "text-green-700",  bg: "bg-green-100",  label: "Minimal Risk"  },
  LOW:      { color: "text-blue-700",   bg: "bg-blue-100",   label: "Low Risk"      },
  MODERATE: { color: "text-yellow-700", bg: "bg-yellow-100", label: "Moderate Risk" },
  HIGH:     { color: "text-orange-700", bg: "bg-orange-100", label: "High Risk"     },
  CRITICAL: { color: "text-red-700",    bg: "bg-red-100",    label: "Critical Risk" },
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
            <span className="text-gray-400">Fusion: {(fusionScore * 100).toFixed(0)}%</span>
          )}
          <span className="text-gray-400">Confidence: {(report.confidence_score * 100).toFixed(0)}%</span>
        </div>
        <span className="text-gray-400">{expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}</span>
      </button>

      {expanded && (
        <div className="px-3 py-3 space-y-2.5 bg-white">
          <div>
            <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">Emotional State</p>
            <p className="text-gray-700 mt-0.5">{report.emotional_state_summary}</p>
          </div>
          <div>
            <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">Behavioral Inference</p>
            <p className="text-gray-700 mt-0.5">{report.behavioral_inference}</p>
          </div>
          {report.cognitive_distortions.length > 0 && (
            <div>
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">Cognitive Distortions</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {report.cognitive_distortions.map((d, i) => (
                  <span key={i} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-[10px]">{d}</span>
                ))}
              </div>
            </div>
          )}
          {report.suggested_interventions.length > 0 && (
            <div>
              <p className="font-semibold text-gray-500 uppercase tracking-wide text-[10px]">Suggested Interventions</p>
              <ul className="mt-1 list-disc list-inside space-y-0.5 text-gray-700">
                {report.suggested_interventions.map((s, i) => <li key={i}>{s}</li>)}
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
  const { user } = useUser();
  const navigate = useNavigate();
  const {
    isGuestMode,
    createGuestConversation,
    updateGuestConversation,
    getGuestConversation,
  } = useGuestMode();

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(sessionId || null);
  const [createdDate, setCreatedDate] = useState<string>(new Date().toISOString());
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Convex mutations (only used when NOT in guest mode)
  const createConversation = useMutation(api.conversations.create);
  const createMessage = useMutation(api.messages.create);

  // Convex queries (skipped in guest mode)
  const convexConversation = useQuery(
    api.conversations.get,
    !isGuestMode && sessionId ? { id: sessionId as Id<"conversations"> } : "skip"
  );
  const convexMessages = useQuery(
    api.messages.listByConversation,
    !isGuestMode && conversationId ? { conversationId: conversationId as Id<"conversations"> } : "skip"
  );

  // ── Reset / Load Messages ────────────────────────────────────────────────
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setConversationId(null);
      return;
    }

    if (isGuestMode) {
      // Load from in-memory guest store
      const guestConv = getGuestConversation(sessionId);
      if (guestConv) {
        setCreatedDate(guestConv.createdAt);
        setMessages(guestConv.messages as Message[]);
      }
      return;
    }

    // Authenticated: handled by Convex reactive queries below
  }, [sessionId, isGuestMode]);

  // Sync Convex query results into local state (authenticated mode only)
  useEffect(() => {
    if (isGuestMode || !sessionId) return;

    if (convexConversation === null) {
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
  }, [convexConversation, convexMessages, sessionId, isGuestMode]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Send Message ─────────────────────────────────────────────────────────
  const handleSend = async () => {
    if (!input.trim()) return;
    if (!isGuestMode && !user) return;

    const userText = input;
    setInput("");
    setIsLoading(true);

    const userMsg: Message = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // ── Guest Mode: in-memory only, no Convex ──────────────────────────
      if (isGuestMode) {
        let guestConvId = conversationId;
        if (!guestConvId) {
          guestConvId = createGuestConversation(`Chat on ${new Date().toLocaleDateString()}`);
          setConversationId(guestConvId);
        }

        const historyForApi = [...messages, userMsg];
        const botMsg: Message = { role: "assistant", content: "" };
        setMessages((prev) => [...prev, botMsg]);

        let fullResponse = "";
        try {
          const stream = streamChatMessage(userText, currentEmotion, historyForApi);
          for await (const chunk of stream) {
            fullResponse += chunk;
            const displayContent = fullResponse.split("---JSON---")[0].trim();
            setMessages((prev) => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1] = { ...botMsg, content: displayContent };
              return newMsgs;
            });
          }

          let finalReply = fullResponse;
          let report: PsychReport | undefined;
          if (fullResponse.includes("---JSON---")) {
            const parts = fullResponse.split("---JSON---");
            finalReply = parts[0].trim();
            try {
              const jsonStr = parts[1].trim().replace(/```json|```/g, "");
              report = JSON.parse(jsonStr);
            } catch (e) {
              console.warn("Failed to parse streamed JSON:", e);
            }
          }

          const finalBotMsg: Message = { role: "assistant", content: finalReply, report };
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = finalBotMsg;
            // Persist to guest context
            const allMessages = updated;
            updateGuestConversation(guestConvId!, allMessages);
            return updated;
          });
        } catch (streamError) {
          console.warn("Streaming failed, using fallback:", streamError);
          const result = await sendChatMessage(userText, currentEmotion, historyForApi);
          const fbMsg: Message = {
            role: "assistant",
            content: result.response,
            report: result.report,
            fusionScore: result.fusion_risk_score ?? undefined,
            remedy: result.remedy ?? undefined,
          };
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = fbMsg;
            updateGuestConversation(guestConvId!, updated);
            return updated;
          });
        }
        return;
      }

      // ── Authenticated Mode: Convex persistence ─────────────────────────
      let activeConversationId = conversationId;
      if (!activeConversationId) {
        const newConvId = await createConversation({ title: `Chat on ${new Date().toLocaleDateString()}` });
        activeConversationId = newConvId;
        setConversationId(newConvId);
      }

      await createMessage({
        conversationId: activeConversationId as Id<"conversations">,
        content: userText,
        metadata: { role: 'user', emotion: currentEmotion },
      });

      const historyForApi = [...messages, userMsg];
      const botMsg: Message = { role: "assistant", content: "" };
      setMessages((prev) => [...prev, botMsg]);

      let fullResponse = "";
      try {
        const stream = streamChatMessage(userText, currentEmotion, historyForApi);
        for await (const chunk of stream) {
          fullResponse += chunk;
          const displayContent = fullResponse.split("---JSON---")[0].trim();
          setMessages((prev) => {
            const newMsgs = [...prev];
            newMsgs[newMsgs.length - 1] = { ...botMsg, content: displayContent };
            return newMsgs;
          });
        }

        let finalReply = fullResponse;
        let report: PsychReport | undefined;
        if (fullResponse.includes("---JSON---")) {
          const parts = fullResponse.split("---JSON---");
          finalReply = parts[0].trim();
          try {
            const jsonStr = parts[1].trim().replace(/```json|```/g, "");
            report = JSON.parse(jsonStr);
          } catch (e) {
            console.warn("Failed to parse streamed JSON:", e);
          }
        }

        const finalBotMsg: Message = { role: "assistant", content: finalReply, report };
        setMessages((prev) => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = finalBotMsg;
          return newMsgs;
        });

        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: finalReply,
          metadata: { role: 'assistant', report },
        });
      } catch (streamError) {
        console.warn("Streaming failed, using fallback:", streamError);
        const result = await sendChatMessage(userText, currentEmotion, historyForApi);
        const fbMsg: Message = {
          role: "assistant",
          content: result.response,
          report: result.report,
          fusionScore: result.fusion_risk_score ?? undefined,
          remedy: result.remedy ?? undefined,
        };
        setMessages((prev) => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = fbMsg;
          return newMsgs;
        });
        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: result.response,
          metadata: { role: 'assistant', report: result.report },
        });
      }

    } catch (error: any) {
      console.error("Chat failed:", error);
      const errMsg = error?.response?.data?.detail || error.message || String(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `I'm having trouble connecting right now. Error: ${JSON.stringify(errMsg)}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <TooltipProvider>
      <div className="flex flex-col h-full bg-white overflow-hidden min-w-0 relative">

        {/* ── PDF / Top-right action ── */}
        <div className="absolute top-4 right-6 z-10">
          {isGuestMode ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  disabled
                  className="flex items-center gap-2 bg-gray-100 text-gray-400 px-3 py-1.5 rounded-full text-xs font-semibold cursor-not-allowed opacity-60 select-none"
                  aria-label="Print to PDF (requires login)"
                >
                  <Lock size={13} />
                  Print to PDF
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                Log in to use this feature
              </TooltipContent>
            </Tooltip>
          ) : (
            <button
              onClick={() => generateChatPDF([WELCOME_MESSAGE, ...messages], createdDate)}
              className="flex items-center gap-2 bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-indigo-100 transition-colors shadow-sm"
              title="Download Prescription PDF"
            >
              <FileText size={14} />
              Print to PDF
            </button>
          )}
        </div>

        {/* ── Messages Area ── */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-5 pt-12 space-y-3 bg-gray-50 min-w-0">
          {[WELCOME_MESSAGE, ...messages].map((msg, index) => (
            <div
              key={index}
              className={`flex w-full min-w-0 items-end gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-indigo-600" />
                </div>
              )}

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

                {msg.role === "assistant" && msg.report && (
                  <ClinicalReport report={msg.report} fusionScore={msg.fusionScore} />
                )}
                {msg.role === "assistant" && msg.remedy && (
                  <RemedyPanel remedy={msg.remedy} />
                )}
                {msg.role === "assistant" &&
                  msg.report?.crisis_triggered &&
                  msg.report.crisis_resources &&
                  !msg.report.crisis_resources.length && (
                    <CrisisBanner resources={msg.report.crisis_resources} />
                  )}
              </div>

              {msg.role === "user" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="text-xs text-gray-400 ml-2">PsyPredict is analyzing…</div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* ── Input Area ── */}
        <div className="p-3 bg-white border-t border-gray-200 flex gap-2 min-w-0 shrink-0 items-end">
          <textarea
            className="flex-1 min-w-0 border border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:border-indigo-500 text-sm resize-none overflow-y-auto max-h-32"
            placeholder="Type your thoughts…"
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
    </TooltipProvider>
  );
};

export default ChatInterface;

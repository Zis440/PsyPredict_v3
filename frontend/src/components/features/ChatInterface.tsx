import React, { useState, useRef, useEffect } from "react";
import { getGitaAdvice, sendChatMessage, streamChatMessage, submitSessionFeedback } from "../../services/api";
import type { PsychReport, RemedyData, RoutingMetadata } from "../../services/api";
import { Bot, User, FileText, Lock, ThumbsUp, ThumbsDown, Zap, Cloud } from "lucide-react";
import { useUser } from '@clerk/react';
import { useMutation, useQuery } from "convex/react";
import { api } from "../../../convex/_generated/api";
import type { Id } from "../../../convex/_generated/dataModel";
import { generateChatPDF } from "../../utils/pdfUtils";
import { useNavigate } from "react-router-dom";
import { useGuestMode } from "../../context/GuestModeContext";
import { useSegment } from "../../context/SegmentContext";
import { generateMasterReport } from "../../services/api";
import type { MasterReport } from "../../services/api";
import { MasterReportModal } from "./MasterReportModal";
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
  routing?: RoutingMetadata;
}

interface ChatProps {
  currentEmotion: string;
  sessionId?: string;
}

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content: "Hello. I am here to listen. How are you feeling right now?",
};

// ── Risk → Condition mapping (mirrors backend therapist.py) ───────────────
const RISK_TO_CONDITION: Record<string, string> = {
  CRITICAL: "Suicidal Ideation",
  HIGH: "Depression",
  MODERATE: "Anxiety",
  LOW: "Anxiety",
  MINIMAL: "Anxiety",
};

// ── Fetch remedy after streaming ──────────────────────────────────────────
const fetchRemedyForReport = async (report: PsychReport): Promise<RemedyData | undefined> => {
  try {
    const condition = RISK_TO_CONDITION[report.risk_classification] ?? "Anxiety";
    const data = await getGitaAdvice(condition);
    return data as RemedyData;
  } catch (e) {
    console.warn("Remedy fetch failed:", e);
    return undefined;
  }
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
  const { segment } = useSegment();

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(sessionId || null);
  const [createdDate, setCreatedDate] = useState<string>(new Date().toISOString());
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackState, setFeedbackState] = useState<Record<number, 'up' | 'down'>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [masterReport, setMasterReport] = useState<MasterReport | null>(null);

  const createConversation = useMutation(api.conversations.create);
  const createMessage = useMutation(api.messages.create);

  const convexConversation = useQuery(
    api.conversations.get,
    !isGuestMode && sessionId ? { id: sessionId as Id<"conversations"> } : "skip"
  );
  const convexMessages = useQuery(
    api.messages.listByConversation,
    !isGuestMode && conversationId ? { conversationId: conversationId as Id<"conversations"> } : "skip"
  );

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setConversationId(null);
      return;
    }
    if (isGuestMode) {
      const guestConv = getGuestConversation(sessionId);
      if (guestConv) {
        setCreatedDate(guestConv.createdAt);
        setMessages(guestConv.messages as Message[]);
      }
      return;
    }
  }, [sessionId, isGuestMode]);

  useEffect(() => {
    if (isGuestMode || !sessionId) return;
    if (convexConversation === null) {
      navigate('/history');
      return;
    }
    if (convexConversation) setCreatedDate(convexConversation.createdAt);
    if (convexMessages) {
      const formatted: Message[] = convexMessages.map((msg) => {
        const meta = msg.metadata as Record<string, any> | null;
        return {
          role: (meta?.role === 'assistant' ? 'assistant' : 'user') as "user" | "assistant",
          content: msg.content,
          report: meta?.report,
          fusionScore: meta?.fusionScore,
          remedy: meta?.remedy,
          routing: meta?.routing,
        };
      });
      setMessages(formatted);
    }
  }, [convexConversation, convexMessages, sessionId, isGuestMode]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleFeedback = async (index: number, rating: number) => {
    if (isGuestMode || !user) return;
    setFeedbackState(prev => ({ ...prev, [index]: rating > 3 ? 'up' : 'down' }));
    try {
      await submitSessionFeedback(user.id, {
        rating,
        comment: "",
        message_id: String(index)
      });
    } catch (e) {
      console.error("Feedback failed", e);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    if (!isGuestMode && !user) return;

    const userText = input;
    setInput("");
    setIsLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    const userMsg: Message = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // ── Guest Mode ────────────────────────────────────────────────────
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
            const displayContent = fullResponse.split("---JSON---")[0].split("---ROUTING---")[0].trim();
            setMessages((prev) => {
              const n = [...prev];
              n[n.length - 1] = { ...botMsg, content: displayContent };
              return n;
            });
          }

          let finalReply = fullResponse;
          let report: PsychReport | undefined;
          let routing: any = undefined;

          if (fullResponse.includes("---ROUTING---")) {
            const routingParts = fullResponse.split("---ROUTING---");
            fullResponse = routingParts[0];
            try { routing = JSON.parse(routingParts[1].trim()); }
            catch (e) { console.warn("Routing parse failed:", e); }
          }

          if (fullResponse.includes("---JSON---")) {
            const parts = fullResponse.split("---JSON---");
            finalReply = parts[0].trim();
            try { report = JSON.parse(parts[1].trim().replace(/```json|```/g, "")); }
            catch (e) { console.warn("JSON parse failed:", e); }
          } else {
            finalReply = fullResponse.trim();
          }

          const remedy = report ? await fetchRemedyForReport(report) : undefined;
          const finalBotMsg: Message = { role: "assistant", content: finalReply, report, remedy, routing };
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = finalBotMsg;
            updateGuestConversation(guestConvId!, updated);
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
            routing: result.routing ?? undefined,
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

      // ── Authenticated Mode ────────────────────────────────────────────
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
          const displayContent = fullResponse.split("---JSON---")[0].split("---ROUTING---")[0].trim();
          setMessages((prev) => {
            const n = [...prev];
            n[n.length - 1] = { ...botMsg, content: displayContent };
            return n;
          });
        }

        let finalReply = fullResponse;
        let report: PsychReport | undefined;
        let routing: any = undefined;

        if (fullResponse.includes("---ROUTING---")) {
          const routingParts = fullResponse.split("---ROUTING---");
          fullResponse = routingParts[0];
          try { routing = JSON.parse(routingParts[1].trim()); }
          catch (e) { console.warn("Routing parse failed:", e); }
        }

        if (fullResponse.includes("---JSON---")) {
          const parts = fullResponse.split("---JSON---");
          finalReply = parts[0].trim();
          try { report = JSON.parse(parts[1].trim().replace(/```json|```/g, "")); }
          catch (e) { console.warn("JSON parse failed:", e); }
        } else {
          finalReply = fullResponse.trim();
        }

        const remedy = report ? await fetchRemedyForReport(report) : undefined;
        const finalBotMsg: Message = { role: "assistant", content: finalReply, report, remedy, routing };
        setMessages((prev) => {
          const n = [...prev];
          n[n.length - 1] = finalBotMsg;
          return n;
        });

        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: finalReply,
          metadata: { role: 'assistant', report, remedy, routing },
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
          routing: result.routing ?? undefined,
        };
        setMessages((prev) => {
          const n = [...prev];
          n[n.length - 1] = fbMsg;
          return n;
        });
        await createMessage({
          conversationId: activeConversationId as Id<"conversations">,
          content: result.response,
          metadata: { role: 'assistant', report: result.report, remedy: result.remedy, routing: result.routing },
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

  const handleGenerateReport = async () => {
    if (!user) return;
    setIsReportModalOpen(true);
    setIsGeneratingReport(true);
    try {
      const report = await generateMasterReport(user.id, segment || 'professional');
      setMasterReport(report);
    } catch (e) {
      console.error("Failed to generate master report", e);
    } finally {
      setIsGeneratingReport(false);
    }
  };



  return (
    <TooltipProvider>
      <div className="flex flex-col h-full bg-white overflow-hidden min-w-0 relative">
        <MasterReportModal
          isOpen={isReportModalOpen}
          onClose={() => setIsReportModalOpen(false)}
          isGenerating={isGeneratingReport}
          report={masterReport}
        />

        {/* ── PDF Button ── */}
        <div className="absolute top-4 right-6 z-10">
          {isGuestMode ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  disabled
                  className="flex items-center gap-2 bg-gray-100 text-gray-400 px-3 py-1.5 rounded-full text-xs font-semibold cursor-not-allowed opacity-60 select-none"
                >
                  <Lock size={13} />
                  Print to PDF
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom">Log in to use this feature</TooltipContent>
            </Tooltip>
          ) : (
            <button
              onClick={() => generateChatPDF([WELCOME_MESSAGE, ...messages], createdDate)}
              className="flex items-center gap-2 bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-indigo-100 transition-colors shadow-sm"
            >
              <FileText size={14} />
              Print to PDF
            </button>
          )}
        </div>

        {/* ── Intelligence Action Bar ── */}
        <div className="bg-indigo-50/50 border-b border-indigo-100 p-3 flex flex-wrap items-center gap-2 px-5">
          {!isGuestMode && (
            <button
              onClick={handleGenerateReport}
              className="flex items-center gap-2 bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm hover:bg-indigo-700 transition-colors"
            >
              <Zap size={14} /> Generate Master Report
            </button>
          )}
        </div>

        {/* ── Messages ── */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-5 space-y-3 bg-gray-50 min-w-0">
          {[WELCOME_MESSAGE, ...messages].map((msg, index) => (
            <div
              key={index}
              className={`flex w-full min-w-0 items-start gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {/* Bot avatar — top aligned */}
              {msg.role === "assistant" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mt-0.5">
                  <Bot className="w-4 h-4 text-indigo-600" />
                </div>
              )}

              <div className="max-w-[80%] min-w-0 flex flex-col">
                <div
                  className={`
                    w-fit min-w-0 p-3 text-sm shadow-sm whitespace-pre-wrap overflow-hidden
                    ${msg.role === "user"
                      ? "bg-indigo-600 text-white rounded-2xl rounded-tr-none ml-auto"
                      : "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-tl-none"
                    }
                  `}
                >
                  {msg.content}

                  {/* Routing Indicator & Feedback (only for assistant) */}
                  {msg.role === "assistant" && (
                    <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100">
                      <div className="flex items-center gap-2">
                        {msg.routing?.provider_used ? (
                          <span className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded border ${msg.routing.provider_used === 'ollama'
                            ? 'bg-blue-50 text-blue-600 border-blue-100'
                            : msg.routing.provider_used === 'groq'
                              ? 'bg-purple-50 text-purple-600 border-purple-100'
                              : 'bg-gray-50 text-gray-500 border-gray-200'
                            }`}>
                            {msg.routing.provider_used === 'ollama' ? <Zap size={10} /> : <Cloud size={10} />}
                            {msg.routing.provider_used.toUpperCase()}
                            {msg.routing.latency_ms && <span className="text-gray-400 ml-1">{msg.routing.latency_ms}ms</span>}
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded border bg-blue-50 text-blue-600 border-blue-100">
                            <Zap size={10} /> OLLAMA
                            <span className="text-gray-400 ml-1">Streamed</span>
                          </span>
                        )}
                        {msg.routing?.fallback_used && (
                          <span className="text-[10px] text-amber-600 font-medium whitespace-nowrap">Fallback</span>
                        )}
                      </div>

                      {!isGuestMode && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleFeedback(index, 5)}
                            className={`p-1 rounded hover:bg-gray-100 transition-colors ${feedbackState[index] === 'up' ? 'text-green-600 bg-green-50' : 'text-gray-400'}`}
                            title="Helpful"
                          >
                            <ThumbsUp size={14} />
                          </button>
                          <button
                            onClick={() => handleFeedback(index, 1)}
                            className={`p-1 rounded hover:bg-gray-100 transition-colors ${feedbackState[index] === 'down' ? 'text-red-600 bg-red-50' : 'text-gray-400'}`}
                            title="Not Helpful"
                          >
                            <ThumbsDown size={14} />
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* User avatar — top aligned */}
              {msg.role === "user" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center mt-0.5">
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

        {/* ── Input ── */}
        <div className="p-3 bg-white border-t border-gray-200 flex gap-2 min-w-0 shrink-0 items-end">
          <textarea
            ref={textareaRef}
            className="flex-1 min-w-0 min-h-[46px] border border-gray-300 rounded-xl px-4 py-3 text-sm resize-none overflow-y-auto max-h-40 bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow"
            placeholder="Type your thoughts…"
            rows={1}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-grow
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
            }}
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
            className="bg-indigo-600 text-white px-5 py-3 rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors h-[46px] flex items-center justify-center"
          >
            Send
          </button>
        </div>
      </div>
    </TooltipProvider>
  );
};

export default ChatInterface;

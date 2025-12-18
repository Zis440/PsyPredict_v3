// src/components/features/ChatInterface.tsx

import React, { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../../services/api";
import { Bot, User, FileText } from "lucide-react";
import { supabase } from "../../lib/supabase";
import { useAuth } from "../../hooks/useAuth";
import type { Database } from "../../types/supabase";
import { generateChatPDF } from "../../utils/pdfUtils";
import { useNavigate } from "react-router-dom";


interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatProps {
  currentEmotion: string;
  sessionId?: string; // Optional: If provided, loads history; else creates new session
}

type MessageRow = Database['public']['Tables']['messages']['Row'];
type ConversationRow = Database['public']['Tables']['conversations']['Row'];

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content: "Hello. I am here to listen. How are you feeling right now?",
};

const ChatInterface: React.FC<ChatProps> = ({ currentEmotion, sessionId }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(sessionId || null);
  const [createdDate, setCreatedDate] = useState<string>(new Date().toISOString());
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch messages on load
  useEffect(() => {
    if (!user) return;

    const fetchMessages = async () => {
      // 1. If we have a sessionId, fetch associated messages
      if (sessionId) {
        setConversationId(sessionId);
        
        // Fetch conversation details for date AND verify ownership
        const { data: convData, error: convError } = await supabase
           .from('conversations')
           .select('created_at, user_id')
           .eq('id', sessionId)
           .eq('user_id', user.id) // Security: Ensure user owns this conversation
           .single();
           
        if (convError || !convData) {
            console.warn("Access denied or conversation not found.");
            navigate('/history'); // Redirect if not found or not owned
            return;
        }

        if (convData) setCreatedDate((convData as { created_at: string }).created_at);

        const { data, error } = await supabase
          .from('messages')
          .select('*')
          .eq('conversation_id', sessionId) // Filter by session, not just user
          .order('created_at', { ascending: true });

        if (error) {
             console.error('Error fetching messages:', error);
        } else if (data) {
             const formatted: Message[] = (data as MessageRow[]).map((msg) => {
                const meta = msg.metadata as Record<string, any> | null;
                return {
                     role: (meta?.role === 'assistant' ? 'assistant' : 'user') as "user" | "assistant",
                     content: msg.content,
                };
             });
             setMessages(formatted);
        }
      } else {
         // No session ID -> New Chat Mode
         // Reset messages
         setMessages([]);
         setConversationId(null);
      }
    };
    
    fetchMessages();
  }, [user, sessionId]);

  // Auto-scroll (keep existing)
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !user) return;

    const userText = input;
    setInput("");
    setIsLoading(true);

    // Optimistic UI update
    const userMsg = { role: "user" as const, content: userText };
    setMessages((prev) => [...prev, userMsg]);



    try {
      // 0. Ensure Conversation Exists
      let activeConversationId = conversationId;
      
      if (!activeConversationId) {
         const { data: newConv, error: convError } = await supabase
           .from('conversations')
           .insert({
              user_id: user.id,
              title: `Chat on ${new Date().toLocaleDateString()}`
           })
           .select()
           .single();
           
         if (convError || !newConv) {
            throw new Error('Failed to create conversation');
         }
         
         const conversation = newConv as ConversationRow;
         activeConversationId = conversation.id;
         setConversationId(conversation.id);
      }

      // 1. Save User Message to DB
      await supabase.from('messages').insert({
        user_id: user.id,
        conversation_id: activeConversationId,
        content: userText,
        metadata: { role: 'user', emotion: currentEmotion }, 
        created_at: new Date().toISOString()
      } as any);

      // 2. Call AI API
      // Note: we pass the updated local history including the new message
      // We also include the welcome message in context if needed, but usually we just want last few.
      // For simplicity, let's keep passing messages + userMsg.
      
      const historyForApi = [...messages, userMsg];
      const result = await sendChatMessage(userText, currentEmotion, historyForApi);
      
      const botContent = result.response;
      const botMsg = {
        role: "assistant" as const,
        content: botContent,
      };

      setMessages((prev) => [...prev, botMsg]);

      // 3. Save Assistant Message to DB
      await supabase.from('messages').insert({
        user_id: user.id,
        conversation_id: activeConversationId,
        content: botContent,
        metadata: { role: 'assistant' },
        created_at: new Date().toISOString()
      } as any);

    } catch (error) {
      console.error("Chat failed:", error);
      const errorMsg = "I'm having trouble connecting right now.";
      
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMsg },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden min-w-0 relative">
      {/* PDF Download Button (Absolute Top Right) */}
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
            className={`flex w-full min-w-0 items-end gap-2 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {/* Bot Icon */}
            {msg.role === "assistant" && (
              <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-indigo-600" />
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`
                max-w-[80%]
                w-fit
                min-w-0
                p-3
                text-sm
                shadow-sm
                wrap-break-word
                whitespace-pre-wrap
                overflow-hidden
                ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-2xl rounded-br-none"
                    : "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-none"
                }
              `}
            >
              {msg.content}
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
            PsyPredict is thinking...
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

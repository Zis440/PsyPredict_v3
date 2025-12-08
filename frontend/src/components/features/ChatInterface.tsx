// src/components/features/ChatInterface.tsx

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatProps {
  currentEmotion: string; // The chat needs to know your face!
}

const ChatInterface: React.FC<ChatProps> = ({ currentEmotion }) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello. I am here to listen. How are you feeling right now?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      // Send text + Current Emotion + History
      const result = await sendChatMessage(input, currentEmotion, messages);
      
      const botMsg = { role: 'assistant' as const, content: result.response };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-3 bg-gray-50">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg text-sm shadow-sm ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-2xl rounded-br-none' 
                : 'bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-xs text-gray-400 ml-2">PsyPredict is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 bg-white border-t border-gray-200 flex gap-2">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:border-indigo-500 text-sm"
          placeholder="Type your thoughts..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button 
          onClick={handleSend}
          disabled={isLoading}
          className="bg-indigo-600 text-white px-4 py-2 rounded-full font-bold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
import React, { useState, useRef, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { MessageSquare, Send, X, Bot, User, ChevronDown } from 'lucide-react';

interface ChatMessage {
  role: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

const AssistantBot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    { role: 'bot', content: 'Hello! I am the NeuroCloak AI Assistant. How can I help you with your AI system audit today?', timestamp: new Date() }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, isOpen]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMsg = message;
    setMessage('');
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }]);
    setIsLoading(true);

    try {
      const data = await apiClient('/chat', {
        method: 'POST',
        body: JSON.stringify({ message: userMsg })
      });
      setChatHistory(prev => [...prev, {
        role: 'bot',
        content: data.response,
        timestamp: new Date()
      }]);
    } catch (error) {
      setChatHistory(prev => [...prev, {
        role: 'bot',
        content: "I'm having trouble connecting to my cognitive core. Please try again in a moment.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-8 right-8 z-[100]">
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-16 h-16 bg-gradient-to-br from-primary to-accent-indigo text-white rounded-2xl flex items-center justify-center shadow-[0_0_30px_-5px_rgba(59,130,246,0.6)] transition-all hover:scale-110 active:scale-95 group relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
          <MessageSquare className="w-8 h-8 group-hover:rotate-12 transition-transform relative z-10" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="bg-[#0F172A]/80 backdrop-blur-2xl border border-white/10 rounded-3xl w-[400px] h-[600px] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-10 duration-500">
          {/* Header */}
          <div className="bg-white/5 p-6 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/50">
                <Bot className="w-7 h-7 text-primary" />
              </div>
              <div>
                <h3 className="font-black text-white text-lg tracking-tight">NeuroAssistant</h3>
                <span className="text-[10px] text-accent-emerald font-black uppercase tracking-widest flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
                  Neural Core Online
                </span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
          >
            {chatHistory.map((chat, idx) => (
              <div
                key={idx}
                className={`flex ${chat.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in duration-500`}
              >
                <div className={`flex gap-3 max-w-[85%] ${chat.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-8 h-8 rounded-xl flex-shrink-0 flex items-center justify-center ${chat.role === 'user' ? 'bg-white/10' : 'bg-primary/20 border border-primary/30'
                    }`}>
                    {chat.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-primary" />}
                  </div>
                  <div className={`p-4 rounded-2xl text-sm leading-relaxed ${chat.role === 'user'
                    ? 'bg-primary text-white rounded-tr-none shadow-lg shadow-primary/20 font-medium'
                    : 'bg-white/5 text-slate-100 rounded-tl-none border border-white/5 shadow-inner'
                    }`}>
                    {chat.content}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Suggested Chips */}
            {!isLoading && chatHistory.length === 1 && (
              <div className="flex flex-wrap gap-2 pt-4 animate-in fade-in slide-in-from-bottom-2 duration-700 delay-300">
                {['Accuracy metrics', 'Active anomalies', 'Model compliance', 'Total systems'].map((chip) => (
                  <button
                    key={chip}
                    onClick={() => {
                      setMessage(chip);
                    }}
                    className="text-[10px] font-bold uppercase tracking-widest px-3 py-2 rounded-lg bg-white/5 border border-white/5 text-slate-400 hover:text-white hover:bg-primary/20 hover:border-primary/50 transition-all"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex gap-2 items-center bg-white/5 p-4 rounded-2xl rounded-tl-none border border-white/5 shadow-inner">
                  <div className="flex gap-1.5">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <form
            onSubmit={handleSendMessage}
            className="p-6 border-t border-white/5 bg-white/5 backdrop-blur-xl"
          >
            <div className="relative group">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Query the cognitive core..."
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all pr-14 shadow-inner group-hover:border-white/20"
              />
              <button
                type="submit"
                disabled={!message.trim() || isLoading}
                className="absolute right-2.5 top-2 w-11 h-11 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:bg-slate-700 text-white rounded-xl flex items-center justify-center transition-all active:scale-90 shadow-lg shadow-primary/30"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default AssistantBot;

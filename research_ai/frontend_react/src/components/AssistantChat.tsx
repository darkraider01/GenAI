import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Bot, User, Sparkles, ChevronDown, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const MODELS = [
  "Gemini Pro",
  "Gemini Flash",
  "GPT-4",
  "Claude"
];

export const AssistantChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I'm the ResearchNex AI Assistant. How can I help you explore our platform and AI research workflows today?" }
  ]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMsg];
    
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages, model: selectedModel })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let aiContent = "";

      setMessages([...newMessages, { role: 'assistant', content: "" }]);

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          aiContent += decoder.decode(value, { stream: true });
          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: 'assistant', content: aiContent };
            return updated;
          });
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I encountered an error. Please try again later." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      <div style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 100 }}>
        <AnimatePresence>
          {!isOpen && (
            <motion.button
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(99, 102, 241, 0.6)' }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsOpen(true)}
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                color: 'white',
                border: 'none',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                cursor: 'pointer',
                boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.5)'
              }}
            >
              <Sparkles size={28} />
            </motion.button>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 50, scale: 0.9, transition: { duration: 0.2 } }}
              style={{
                position: 'absolute',
                bottom: '80px',
                right: '0',
                width: '380px',
                height: '600px',
                maxHeight: '80vh',
                background: 'rgba(15, 23, 42, 0.85)',
                backdropFilter: 'blur(16px)',
                borderRadius: '24px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(99, 102, 241, 0.1)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
              }}
            >
              {/* Header */}
              <div style={{
                padding: '1.25rem 1.5rem',
                borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'radial-gradient(circle at top left, rgba(99, 102, 241, 0.15), transparent 70%)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{
                    width: '36px', height: '36px', borderRadius: '10px',
                    background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                    display: 'flex', justifyContent: 'center', alignItems: 'center'
                  }}>
                    <Bot size={20} color="white" />
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'white' }}>ResearchNex AI</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#10b981' }}>
                      <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
                      Online
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <div style={{ position: 'relative' }}>
                    <button 
                      onClick={() => setShowModelDropdown(!showModelDropdown)}
                      style={{
                        background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '8px', padding: '0.4rem 0.75rem', color: '#e2e8f0',
                        fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      {selectedModel} <ChevronDown size={14} />
                    </button>
                    <AnimatePresence>
                      {showModelDropdown && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95, y: 10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.95, y: 10 }}
                          style={{
                            position: 'absolute', top: '100%', right: 0, marginTop: '8px',
                            background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '12px', overflow: 'hidden', width: '140px', zIndex: 10
                          }}
                        >
                          {MODELS.map(model => (
                            <div 
                              key={model}
                              onClick={() => { setSelectedModel(model); setShowModelDropdown(false); }}
                              style={{
                                padding: '0.75rem 1rem', fontSize: '0.8rem', color: 'white',
                                cursor: 'pointer', display: 'flex', justifyContent: 'space-between',
                                background: selectedModel === model ? 'rgba(99,102,241,0.2)' : 'transparent',
                                borderBottom: '1px solid rgba(255,255,255,0.05)'
                              }}
                            >
                              {model}
                              {selectedModel === model && <Check size={14} color="#a5b4fc" />}
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                  <button 
                    onClick={() => setIsOpen(false)}
                    style={{
                      background: 'transparent', border: 'none', color: '#94a3b8',
                      cursor: 'pointer', padding: '0.4rem', borderRadius: '8px',
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}
                    onMouseOver={e => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                    onMouseOut={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Chat Area */}
              <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '85%',
                      flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                    }}
                  >
                    <div style={{
                      width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0,
                      background: msg.role === 'user' ? 'rgba(99,102,241,0.2)' : 'rgba(168,85,247,0.2)',
                      display: 'flex', justifyContent: 'center', alignItems: 'center',
                      color: msg.role === 'user' ? '#a5b4fc' : '#e9d5ff',
                      border: `1px solid ${msg.role === 'user' ? 'rgba(99,102,241,0.3)' : 'rgba(168,85,247,0.3)'}`
                    }}>
                      {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                    </div>
                    <div style={{
                      background: msg.role === 'user' ? 'linear-gradient(135deg, #4f46e5, #4338ca)' : 'rgba(30, 41, 59, 0.8)',
                      padding: '0.85rem 1rem',
                      borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                      color: 'white',
                      fontSize: '0.9rem',
                      lineHeight: 1.5,
                      border: msg.role === 'assistant' ? '1px solid rgba(255,255,255,0.05)' : 'none',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} className="chat-markdown">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </motion.div>
                ))}
                
                {isTyping && (
                  <motion.div 
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', maxWidth: '85%' }}
                  >
                    <div style={{
                      width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0,
                      background: 'rgba(168,85,247,0.2)', display: 'flex', justifyContent: 'center', alignItems: 'center',
                      color: '#e9d5ff', border: '1px solid rgba(168,85,247,0.3)'
                    }}>
                      <Bot size={14} />
                    </div>
                    <div style={{
                      background: 'rgba(30, 41, 59, 0.8)', padding: '0.85rem 1rem', borderRadius: '4px 16px 16px 16px',
                      border: '1px solid rgba(255,255,255,0.05)', display: 'flex', gap: '4px'
                    }}>
                      <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%' }} />
                      <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%' }} />
                      <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%' }} />
                    </div>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div style={{ padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(15,23,42,0.95)' }}>
                <form onSubmit={handleSubmit} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Ask about ResearchNex..."
                    style={{
                      width: '100%',
                      padding: '0.9rem 3rem 0.9rem 1.2rem',
                      borderRadius: '16px',
                      border: '1px solid rgba(255,255,255,0.1)',
                      background: 'rgba(0,0,0,0.2)',
                      color: 'white',
                      fontSize: '0.9rem',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={e => e.target.style.borderColor = 'rgba(99,102,241,0.5)'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                  <button 
                    type="submit"
                    disabled={!input.trim() || isTyping}
                    style={{
                      position: 'absolute',
                      right: '0.5rem',
                      background: input.trim() ? '#6366f1' : 'rgba(255,255,255,0.1)',
                      border: 'none',
                      width: '32px',
                      height: '32px',
                      borderRadius: '10px',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      color: input.trim() ? 'white' : '#64748b',
                      cursor: input.trim() ? 'pointer' : 'default',
                      transition: 'all 0.2s'
                    }}
                  >
                    <Send size={16} />
                  </button>
                </form>
                <div style={{ textAlign: 'center', marginTop: '0.75rem', fontSize: '0.7rem', color: '#64748b' }}>
                  AI Assistant may produce inaccurate information.
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <style>{`
        .chat-markdown p { margin: 0 0 0.5em 0; }
        .chat-markdown p:last-child { margin: 0; }
        .chat-markdown code { background: rgba(0,0,0,0.3); padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.85em; }
        .chat-markdown pre { background: rgba(0,0,0,0.4); padding: 0.8rem; border-radius: 8px; overflow-x: auto; margin: 0.5em 0; }
        .chat-markdown ul, .chat-markdown ol { margin: 0.5em 0; padding-left: 1.5em; }
      `}</style>
    </>
  );
};

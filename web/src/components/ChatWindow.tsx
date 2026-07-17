import { useEffect, useRef, useState, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const MAX_HISTORY = 10;

interface Message {
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
  error?: boolean;
  meta?: Record<string, unknown>;
}

interface Props {
  visitorName: string;
  token: string | null;
  onNewMessage?: (userText: string) => void;
  onAuthError?: () => void;
}

function ChatWindow({ visitorName, token, onNewMessage, onAuthError }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }, [input]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: Message = { role: "user", content: text };
    const loadingMsg: Message = { role: "assistant", content: "", loading: true };

    const history = messages
      .filter((m) => !m.loading && !m.error && m.content)
      .slice(-MAX_HISTORY)
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev.slice(-MAX_HISTORY), userMsg, loadingMsg]);
    setInput("");
    setSending(true);

    if (messages.length === 0) {
      onNewMessage?.(text);
    }

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: text,
          mode: "external_allowed",
          use_memory: true,
          history,
        }),
      });

      if (res.status === 401) {
        onAuthError?.();
        throw new Error("Sesi berakhir. Silakan masuk lagi.");
      }
      if (res.status === 429) {
        throw new Error("Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.");
      }
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        meta: {
          source: data.source,
          cache_hit: data.metadata?.cache_hit,
          used_memory: data.metadata?.used_memory,
        },
      };

      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = assistantMsg;
        return updated;
      });
    } catch (err: unknown) {
      const errorMsg: Message = {
        role: "assistant",
        content: err instanceof Error ? err.message : "Terjadi kesalahan. Coba lagi.",
        error: true,
      };
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = errorMsg;
        return updated;
      });
    } finally {
      setSending(false);
    }
  }, [input, sending, messages, token, onNewMessage, onAuthError]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const useSuggestion = (text: string) => {
    setInput(text);
    textareaRef.current?.focus();
  };



  const showWelcome = messages.length === 0;

  return (
    <div className="flex-1 overflow-hidden flex flex-col relative">
      
      {/* Chat Container */}
      <div className="flex-1 overflow-y-auto" id="chatContainer">
        
        {/* Welcome State */}
        {showWelcome ? (
          <div className="min-h-full flex flex-col items-center justify-center px-6 py-12">
            <div className="text-center max-w-3xl w-full">
              <div className="relative w-24 h-24 mx-auto mb-6 logo-glow">
                <svg viewBox="0 0 300 300" className="w-full h-full">
                  <defs>
                    <linearGradient id="chatWelcomeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#FFB627"/>
                      <stop offset="100%" stopColor="#FF3D00"/>
                    </linearGradient>
                  </defs>
                  <polygon points="150,30 254,90 254,210 150,270 46,210 46,90" fill="none" stroke="url(#chatWelcomeGrad)" strokeWidth="3"/>
                  <path d="M 110 115 L 190 115 L 110 185 L 190 185" fill="none" stroke="url(#chatWelcomeGrad)" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="190" cy="115" r="8" fill="#FFB627" className="spark-blink"/>
                </svg>
              </div>
              
              <h2 className="font-display font-bold text-3xl md:text-4xl mb-2">
                Halo, {visitorName} <span className="text-[var(--accent-2)]">👋</span>
              </h2>
              <p className="text-[var(--muted)] text-lg mb-10">Apa yang ingin kamu nyalakan hari ini?</p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                <div className="suggestion-card glass rounded-2xl p-5" onClick={() => useSuggestion('Jelaskan konsep black hole dengan analogi yang anak 12 tahun bisa paham.')}>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFB627]/20 to-[#FF3D00]/10 border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                      <i className="fa-solid fa-graduation-cap text-[var(--accent-2)]"></i>
                    </div>
                    <div>
                      <div className="font-display font-medium text-sm mb-1">Jelaskan konsep rumit</div>
                      <div className="text-xs text-[var(--muted)]">dengan analogi yang mudah dipahami</div>
                    </div>
                  </div>
                </div>
                
                <div className="suggestion-card glass rounded-2xl p-5" onClick={() => useSuggestion('Bantu saya debug kode React yang error: TypeError: Cannot read properties of undefined (reading map).')}>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFB627]/20 to-[#FF3D00]/10 border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                      <i className="fa-solid fa-bug text-[var(--accent-2)]"></i>
                    </div>
                    <div>
                      <div className="font-display font-medium text-sm mb-1">Debug kode saya</div>
                      <div className="text-xs text-[var(--muted)]">temukan & perbaiki error dengan cepat</div>
                    </div>
                  </div>
                </div>
                
                <div className="suggestion-card glass rounded-2xl p-5" onClick={() => useSuggestion('Bantu saya ide 10 konten Instagram untuk brand kafe lokal yang ingin naik kelas.')}>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFB627]/20 to-[#FF3D00]/10 border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                      <i className="fa-solid fa-lightbulb text-[var(--accent-2)]"></i>
                    </div>
                    <div>
                      <div className="font-display font-medium text-sm mb-1">Buat ide konten</div>
                      <div className="text-xs text-[var(--muted)]">untuk media sosial brand-mu</div>
                    </div>
                  </div>
                </div>
                
                <div className="suggestion-card glass rounded-2xl p-5" onClick={() => useSuggestion('Tulis email profesional untuk menolak tawaran kerja dengan sopan tapi tegas.')}>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFB627]/20 to-[#FF3D00]/10 border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                      <i className="fa-solid fa-pen-nib text-[var(--accent-2)]"></i>
                    </div>
                    <div>
                      <div className="font-display font-medium text-sm mb-1">Tulis untuk saya</div>
                      <div className="text-xs text-[var(--muted)]">email, caption, artikel, dan lainnya</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={`message-in flex ${msg.role === 'user' ? 'justify-end' : 'justify-start gap-3'}`}>
                {msg.role === 'user' ? (
                  <div className="chat-bubble-user max-w-[80%] px-5 py-3.5">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ) : (
                  <>
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#FFB627] to-[#FF3D00] flex items-center justify-center flex-shrink-0">
                      <svg viewBox="0 0 24 24" className="w-5 h-5">
                        <path d="M 8 9 L 16 9 L 8 15 L 16 15" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                      </svg>
                    </div>
                    <div className={`chat-bubble-ai max-w-[80%] px-5 py-4 ${msg.error ? 'border-red-500 bg-red-500/10' : ''}`}>
                      {msg.loading ? (
                         <div className="flex items-center gap-2">
                           <span className="typing-dot"></span>
                           <span className="typing-dot"></span>
                           <span className="typing-dot"></span>
                           <span className="text-xs text-[var(--muted)] ml-2">Zippo sedang menyalakan jawaban...</span>
                         </div>
                      ) : (
                        <>
                          <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                          <div className="flex flex-wrap items-center gap-4 mt-3 pt-3 border-t border-[var(--border)] text-xs text-[var(--muted)]">
                            <button className="hover:text-[var(--accent-2)] flex items-center gap-1.5"><i className="fa-regular fa-copy"></i> Salin</button>
                            <button className="hover:text-[var(--accent-2)] flex items-center gap-1.5"><i className="fa-solid fa-rotate"></i> Regenerasi</button>
                            <button className="hover:text-[var(--accent-2)] flex items-center gap-1.5"><i className="fa-regular fa-thumbs-up"></i></button>
                            <button className="hover:text-[var(--accent-2)] flex items-center gap-1.5"><i className="fa-regular fa-thumbs-down"></i></button>
                            {msg.meta && (
                              <span className="ml-auto font-mono text-[10px]">
                                {msg.meta.source ? `📡 ${String(msg.meta.source)} ` : null}
                                {msg.meta.cache_hit ? '⚡ Cache' : ''}
                              </span>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </>
                )}
              </div>
            ))}
            <div ref={bottomRef} className="h-4" />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-[var(--border)] glass-strong p-3 md:p-4">
        <div className="max-w-3xl mx-auto">
          {/* Tool chips */}
          <div className="flex items-center gap-2 mb-3 overflow-x-auto pb-1">
            <button className="tool-chip chip px-3 py-1.5 text-xs font-mono flex items-center gap-1.5 whitespace-nowrap">
              <i className="fa-solid fa-brain text-[10px]"></i>
              <span>Reasoning</span>
            </button>
            <button className="tool-chip chip px-3 py-1.5 text-xs font-mono flex items-center gap-1.5 whitespace-nowrap">
              <i className="fa-solid fa-globe text-[10px]"></i>
              <span>Web search</span>
            </button>
            <button className="tool-chip chip px-3 py-1.5 text-xs font-mono flex items-center gap-1.5 whitespace-nowrap">
              <i className="fa-solid fa-image text-[10px]"></i>
              <span>Image gen</span>
            </button>
          </div>
          
          {/* Input box */}
          <div className="glass rounded-2xl p-2 flex items-end gap-2">
            <button className="w-9 h-9 rounded-xl hover:bg-[var(--card)] flex items-center justify-center text-[var(--muted)] hover:text-[var(--accent-2)] transition flex-shrink-0" title="Lampirkan file">
              <i className="fa-solid fa-paperclip text-sm"></i>
            </button>
            <textarea 
              ref={textareaRef}
              placeholder="Ketik pesan ke Zippo AI..." 
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={sending}
              className="textarea-auto flex-1 bg-transparent outline-none text-sm py-2 px-1 placeholder:text-[var(--muted-2)] resize-none"
            ></textarea>
            <button className="w-9 h-9 rounded-xl hover:bg-[var(--card)] flex items-center justify-center text-[var(--muted)] hover:text-[var(--accent-2)] transition flex-shrink-0" title="Rekam suara">
              <i className="fa-solid fa-microphone text-sm"></i>
            </button>
            <button onClick={sendMessage} disabled={sending || !input.trim()} className="btn-primary w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed">
              <i className="fa-solid fa-arrow-up text-sm"></i>
            </button>
          </div>
          
          <div className="flex items-center justify-between mt-2 px-2 text-[10px] font-mono text-[var(--muted-2)]">
            <span>Zippo bisa membuat kesalahan. Verifikasi info penting.</span>
            <span className="hidden sm:inline">↵ untuk kirim</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;

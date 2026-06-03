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
  onNewMessage?: (userText: string) => void;
}

// Send icon SVG
function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M22 2L11 13" />
      <path d="M22 2L15 22L11 13L2 9L22 2Z" />
    </svg>
  );
}

function ChatWindow({ visitorName, onNewMessage }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Halo ${visitorName}! 👋 Aku Zippo AI, asisten kecerdasan buatan kamu. Ada yang bisa aku bantu hari ini?`,
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
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
    const loadingMsg: Message = {
      role: "assistant",
      content: "",
      loading: true,
    };

    // Keep only last MAX_HISTORY messages (excluding welcome) + new ones
    setMessages((prev) => {
      const history = prev.slice(-MAX_HISTORY);
      return [...history, userMsg, loadingMsg];
    });
    setInput("");
    setSending(true);

    // Notify parent for chat history title
    onNewMessage?.(text);

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          mode: "external_allowed",
          use_memory: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
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
  }, [input, sending, onNewMessage]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const initials = visitorName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const suggestions = [
    { label: "Analisis", text: "Bantu aku menganalisis tren pasar terbaru" },
    { label: "Riset", text: "Carikan informasi tentang teknologi AI terkini" },
    { label: "Rangkuman", text: "Rangkumkan berita penting hari ini" },
    { label: "Diskusi", text: "Mari diskusi tentang masa depan AI" },
  ];

  const showWelcome = messages.length <= 1;

  return (
    <div className="chat-view">
      {/* Messages */}
      <div className="chat-messages-area" id="chat-messages-area">
        <div className="messages-inner">
          {showWelcome && (
            <div className="welcome-screen">
              <img src="/zippo-ai.png" alt="Zippo AI" className="welcome-logo" />
              <h2>Halo, {visitorName}!</h2>
              <p>
                Aku siap membantu kamu dengan riset, analisis, dan percakapan cerdas
                berbasis data real-time.
              </p>
              <div className="welcome-suggestions">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    id={`suggestion-${i}`}
                    className="suggestion-btn"
                    onClick={() => {
                      setInput(s.text);
                      textareaRef.current?.focus();
                    }}
                  >
                    <span className="suggestion-label">{s.label}</span>
                    {s.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              id={`msg-${i}`}
              className={`msg-row ${msg.role === "user" ? "user-row" : "assistant-row"}`}
            >
              {/* Avatar */}
              <div
                className={`msg-avatar ${msg.role === "user" ? "user-avatar-msg" : "ai-avatar"}`}
              >
                {msg.role === "user" ? (
                  initials
                ) : (
                  <img src="/zippo-ai.png" alt="AI" />
                )}
              </div>

              {/* Content */}
              <div className="msg-content-wrap">
                <div className="msg-sender">
                  {msg.role === "user" ? visitorName : "Zippo AI"}
                </div>
                <div
                  className={`msg-bubble${msg.loading ? " loading-bubble" : ""}${msg.error ? " error-bubble" : ""}`}
                >
                  {msg.loading ? (
                    <div className="typing-dots">
                      <span />
                      <span />
                      <span />
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>

                {/* Meta tags */}
                {msg.meta && (
                  <div className="msg-meta-row">
                    {Boolean(msg.meta.source) && (
                      <span className="msg-meta-tag">
                        📡 {String(msg.meta.source)}
                      </span>
                    )}
                    {msg.meta.cache_hit !== undefined && (
                      <span className="msg-meta-tag">
                        {Boolean(msg.meta.cache_hit) ? "⚡ Cache" : "🔄 Fresh"}
                      </span>
                    )}
                    {msg.meta.used_memory !== undefined && (
                      <span className="msg-meta-tag">
                        🧠 Memory: {String(msg.meta.used_memory)}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} style={{ height: "8px" }} />
        </div>
      </div>

      {/* Input Bar */}
      <div className="chat-input-bar">
        <div className="chat-input-inner">
          <textarea
            id="chat-input"
            ref={textareaRef}
            className="chat-input-field"
            placeholder="Ketik pesan... (Enter untuk kirim, Shift+Enter untuk baris baru)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
            rows={1}
          />
          <div className="chat-input-actions">
            <span className="input-hint">Shift+Enter untuk baris baru</span>
            <button
              id="send-btn"
              className="send-btn"
              onClick={sendMessage}
              disabled={sending || !input.trim()}
              title="Kirim pesan"
            >
              <SendIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;

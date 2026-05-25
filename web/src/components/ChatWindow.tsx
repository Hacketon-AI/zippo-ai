import { useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const LOADING_MSG ="Please give me a moment while I confirm it with the system first, as I want to ensure I fully understand the question you’ve asked."


interface Message {
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
  error?: boolean;
  meta?: Record<string, unknown>;
}

interface Props {
  visitorName: string;
}

function ChatWindow({ visitorName }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `halo ${visitorName}, bagaimana kabar mu? mari kita cerita`,
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: Message = { role: "user", content: text };
    const loadingMsg: Message = {
      role: "assistant",
      content: LOADING_MSG,
      loading: true,
    };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setInput("");
    setSending(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          mode: "local_only",
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
        // Replace the loading message (last item)
        updated[updated.length - 1] = assistantMsg;
        return updated;
      });
    } catch (err: unknown) {
      const errorMsg: Message = {
        role: "assistant",
        content: err instanceof Error ? err.message : "Terjadi kesalahan",
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
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">Personal AI Assistant</div>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`msg ${msg.role}${msg.loading ? " loading" : ""}${msg.error ? " error" : ""}`}
          >
            {msg.content}
            {msg.meta && (
              <div className="msg-meta">
                source: {String(msg.meta.source)} | cache:{" "}
                {String(msg.meta.cache_hit)} | memory:{" "}
                {String(msg.meta.used_memory)}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          placeholder="Ketik pesan..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={sending}
        />
        <button onClick={sendMessage} disabled={sending || !input.trim()}>
          Kirim
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;

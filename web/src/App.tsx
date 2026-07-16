import { useState, useCallback } from "react";
import ChatWindow from "./components/ChatWindow";
import NameModal from "./components/NameModal";
import Sidebar from "./components/Sidebar";
import "./App.css";

const STORAGE_KEY = "visitor_name";
const MAX_CHAT_HISTORY = 10;

interface ChatHistoryItem {
  id: string;
  title: string;
  msgCount: number;
}

function generateId() {
  return Math.random().toString(36).slice(2, 10);
}

function App() {
  const [name, setName] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [chatKey, setChatKey] = useState(0);

  const handleNameSubmit = (n: string) => {
    // TODO(security): Name is stored in localStorage for UX only, no sensitive data
    localStorage.setItem(STORAGE_KEY, n);
    setName(n);
    // Start first chat session
    const id = generateId();
    setChatHistory([{ id, title: "Percakapan Baru", msgCount: 0 }]);
    setActiveChatId(id);
  };

  const handleNewChat = useCallback(() => {
    const id = generateId();
    const newItem: ChatHistoryItem = { id, title: "Percakapan Baru", msgCount: 0 };
    // Keep only last MAX_CHAT_HISTORY sessions
    setChatHistory((prev) => [newItem, ...prev].slice(0, MAX_CHAT_HISTORY));
    setActiveChatId(id);
    setChatKey((k) => k + 1);
  }, []);

  const handleSelectChat = useCallback((id: string) => {
    setActiveChatId(id);
    setChatKey((k) => k + 1);
  }, []);

  const handleFirstMessage = useCallback((userText: string) => {
    // Update the active chat title with first message snippet
    const title = userText.length > 36 ? userText.slice(0, 36) + "…" : userText;
    setChatHistory((prev) =>
      prev.map((item) =>
        item.id === activeChatId
          ? { ...item, title, msgCount: item.msgCount + 1 }
          : item
      )
    );
  }, [activeChatId]);

  if (!name) {
    return (
      <div className="name-modal-wrapper">
        <NameModal onSubmit={handleNameSubmit} />
      </div>
    );
  }

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onCollapse={() => setSidebarCollapsed((c) => !c)}
        visitorName={name}
        chatHistory={chatHistory}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
      />

      {/* Main Content */}
      <div className="main-content">
        {/* Top Bar */}
        <header className="topbar">
          {/* Mobile / collapsed toggle */}
          <button
            id="topbar-toggle-btn"
            className="topbar-toggle-btn"
            onClick={() => setSidebarCollapsed((c) => !c)}
            title="Toggle sidebar"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <h1 className="topbar-title">Chat AI</h1>
        </header>

        {/* Content */}
        <ChatWindow
          key={chatKey}
          visitorName={name}
          onNewMessage={handleFirstMessage}
        />
      </div>
    </div>
  );
}

export default App;

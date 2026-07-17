import { useState, useCallback } from "react";
import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";
import Welcome from "./components/Welcome";
import Login from "./components/Login";
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
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("auth_token")
  );
  
  // page state: 'welcome', 'login', 'chat'
  const [page, setPage] = useState<'welcome' | 'login' | 'chat'>(token ? 'chat' : 'welcome');
  
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [chatKey, setChatKey] = useState(0);

  const handleLogin = (authToken: string, displayName: string) => {
    localStorage.setItem("auth_token", authToken);
    localStorage.setItem(STORAGE_KEY, displayName);
    setToken(authToken);
    setName(displayName);
    
    // Create initial chat
    const id = generateId();
    setChatHistory([{ id, title: "Percakapan Baru", msgCount: 0 }]);
    setActiveChatId(id);
    setPage('chat');
  };
  
  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setName(null);
    setPage('welcome');
  };

  const handleNewChat = useCallback(() => {
    const id = generateId();
    const newItem: ChatHistoryItem = { id, title: "Percakapan Baru", msgCount: 0 };
    setChatHistory((prev) => [newItem, ...prev].slice(0, MAX_CHAT_HISTORY));
    setActiveChatId(id);
    setChatKey((k) => k + 1);
  }, []);

  const handleSelectChat = useCallback((id: string) => {
    setActiveChatId(id);
    setChatKey((k) => k + 1);
  }, []);

  const handleFirstMessage = useCallback((userText: string) => {
    const title = userText.length > 36 ? userText.slice(0, 36) + "…" : userText;
    setChatHistory((prev) =>
      prev.map((item) =>
        item.id === activeChatId
          ? { ...item, title, msgCount: item.msgCount + 1 }
          : item
      )
    );
  }, [activeChatId]);

  if (page === 'welcome') {
    return <Welcome onLoginClick={() => setPage('login')} />;
  }
  
  if (page === 'login') {
    return <Login onBack={() => setPage('welcome')} onLogin={handleLogin} />;
  }

  // Chat Page Layout
  return (
    <section id="chatPage" className="page active h-screen overflow-hidden w-full">
      <div className="flex h-screen w-full">
        {/* Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onCollapse={() => setSidebarCollapsed((c) => !c)}
          visitorName={name || "User"}
          chatHistory={chatHistory}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          onLogout={handleLogout}
        />

        {/* Sidebar overlay (mobile) */}
        {!sidebarCollapsed && (
          <div className="sidebar-overlay fixed inset-0 bg-black/60 z-40 md:hidden" onClick={() => setSidebarCollapsed(true)}></div>
        )}

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 relative">
          {/* Top bar */}
          <header className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-[var(--border)] glass-strong">
            <div className="flex items-center gap-3">
              <button onClick={() => setSidebarCollapsed(false)} className="md:hidden w-9 h-9 rounded-lg hover:bg-[var(--card)] flex items-center justify-center">
                <i className="fa-solid fa-bars"></i>
              </button>
              
              {/* Model selector (static mock) */}
              <div className="relative group">
                <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[var(--card)] transition">
                  <span className="status-dot w-2 h-2 rounded-full bg-[var(--accent-2)]"></span>
                  <span className="font-display font-medium text-sm">Zippo-4o</span>
                  <i className="fa-solid fa-chevron-down text-[10px] text-[var(--muted)]"></i>
                </button>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button className="w-9 h-9 rounded-lg hover:bg-[var(--card)] flex items-center justify-center text-[var(--muted)] hover:text-[var(--fg)] transition" title="Bagikan">
                <i className="fa-solid fa-share-nodes text-sm"></i>
              </button>
              <button className="w-9 h-9 rounded-lg hover:bg-[var(--card)] flex items-center justify-center text-[var(--muted)] hover:text-[var(--fg)] transition" title="Pengaturan">
                <i className="fa-solid fa-gear text-sm"></i>
              </button>
              <div className="w-px h-6 bg-[var(--border)] mx-1"></div>
              <div className="flex items-center gap-2 chip px-3 py-1.5 text-xs font-mono">
                <i className="fa-solid fa-fire text-[var(--accent-2)] text-[10px]"></i>
                <span>1,247 spark</span>
              </div>
            </div>
          </header>

          {/* Chat Window Container */}
          <ChatWindow
            key={chatKey}
            visitorName={name || "User"}
            token={token}
            onNewMessage={handleFirstMessage}
            onAuthError={handleLogout}
          />
        </main>
      </div>
    </section>
  );
}

export default App;

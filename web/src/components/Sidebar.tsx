

interface ChatHistoryItem {
  id: string;
  title: string;
  msgCount: number;
  active?: boolean;
}

interface Props {
  collapsed: boolean;
  onCollapse: () => void;
  visitorName: string;
  chatHistory: ChatHistoryItem[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
}

function Sidebar({
  collapsed,
  onCollapse,
  visitorName,
  chatHistory,
  activeChatId,
  onSelectChat,
  onNewChat,
}: Props) {
  const initials = visitorName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <>
      {/* Mobile Overlay */}
      {!collapsed && (
        <div className="sidebar-overlay" onClick={onCollapse} />
      )}

      <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
        {/* Header with Logo */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <img src="/zippo-ai.png" alt="Zippo AI Logo" />
          </div>
          <button
            className="sidebar-collapse-btn"
            onClick={onCollapse}
            title="Tutup sidebar"
            id="sidebar-collapse-btn"
          >
            {/* Sidebar close icon */}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M9 3v18" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <button className="new-chat-btn" onClick={onNewChat} id="new-chat-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Percakapan Baru
        </button>

        {/* Main Navigation */}
        <nav className="sidebar-nav">
          <button id="nav-chat" className="nav-item active">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <span className="nav-item-text">Chat AI</span>
          </button>
        </nav>

        <div className="sidebar-divider" />

        {/* Chat History */}
        <div className="sidebar-section">
          <div className="sidebar-section-label">Riwayat Chat</div>
          {chatHistory.length === 0 ? (
            <div style={{ padding: "0.5rem 0.625rem", fontSize: "0.8rem", color: "var(--sidebar-text-muted)" }}>
              Belum ada percakapan
            </div>
          ) : (
            chatHistory.map((item) => (
              <button
                key={item.id}
                id={`chat-history-${item.id}`}
                className={`chat-history-item${activeChatId === item.id ? " active" : ""}`}
                onClick={() => onSelectChat(item.id)}
                title={item.title}
              >
                <svg className="chat-history-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <span className="chat-history-title">{item.title}</span>
                {item.msgCount > 0 && (
                  <span className="chat-history-count">{item.msgCount}</span>
                )}
              </button>
            ))
          )}
        </div>

        {/* User Profile Footer */}
        <div className="sidebar-footer">
          <button className="user-profile-btn" id="user-profile-btn">
            <div className="user-avatar">{initials}</div>
            <div style={{ flex: 1, textAlign: "left", minWidth: 0 }}>
              <div className="user-name">{visitorName}</div>
              <div className="user-status">
                <span className="user-status-dot" />
                Online
              </div>
            </div>
          </button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;

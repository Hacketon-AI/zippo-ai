import { useState } from "react";

interface ChatHistoryItem {
  id: string;
  title: string;
  msgCount: number;
}

interface Props {
  collapsed: boolean;
  onCollapse: () => void;
  visitorName: string;
  chatHistory: ChatHistoryItem[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onLogout: () => void;
}

function Sidebar({
  collapsed,
  onCollapse,
  visitorName,
  chatHistory,
  activeChatId,
  onSelectChat,
  onNewChat,
  onLogout
}: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const initials = visitorName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <aside id="chatSidebar" className={`chat-sidebar glass-strong border-r border-[var(--border)] flex flex-col flex-shrink-0 ${collapsed ? '' : 'open'}`}>
      {/* Sidebar header */}
      <div className="p-4 border-b border-[var(--border)]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <svg viewBox="0 0 48 48" className="w-8 h-8">
              <defs>
                <linearGradient id="sideLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFB627"/>
                  <stop offset="100%" stopColor="#FF3D00"/>
                </linearGradient>
              </defs>
              <polygon points="24,3 42,13.5 42,34.5 24,45 6,34.5 6,13.5" fill="none" stroke="url(#sideLogoGrad)" strokeWidth="1.5" opacity="0.6"/>
              <path d="M 16 18 L 32 18 L 16 30 L 32 30" fill="none" stroke="url(#sideLogoGrad)" strokeWidth="3" strokeLinecap="round"/>
              <circle cx="32" cy="18" r="2" fill="#FFB627"/>
            </svg>
            <div className="flex flex-col leading-none">
              <span className="font-display font-bold text-sm">Zippo<span className="gradient-text">AI</span></span>
            </div>
          </div>
          <button onClick={onCollapse} className="md:hidden w-8 h-8 rounded-lg hover:bg-[var(--card)] flex items-center justify-center text-[var(--muted)]">
            <i className="fa-solid fa-xmark"></i>
          </button>
        </div>
        
        <button onClick={onNewChat} className="btn-primary w-full py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2">
          <i className="fa-solid fa-plus text-xs"></i>
          <span>Chat Baru</span>
        </button>
      </div>
      
      {/* Search */}
      <div className="p-3 border-b border-[var(--border)]">
        <div className="relative">
          <i className="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-xs text-[var(--muted-2)]"></i>
          <input type="text" placeholder="Cari chat..." className="input-field w-full pl-9 pr-3 py-2 rounded-lg text-xs" />
        </div>
      </div>
      
      {/* History */}
      <div className="flex-1 overflow-y-auto py-2">
        <div className="px-3 py-2">
          <div className="text-[10px] font-mono text-[var(--muted-2)] tracking-widest px-2 mb-2">HARI INI</div>
          <div className="space-y-0.5">
            {chatHistory.length === 0 ? (
               <div className="text-xs text-[var(--muted-2)] px-2">Belum ada percakapan</div>
            ) : chatHistory.map((item) => (
              <div 
                key={item.id} 
                className={`history-item px-3 py-2.5 rounded-lg flex items-center gap-3 ${activeChatId === item.id ? 'active' : ''}`}
                onClick={() => onSelectChat(item.id)}
              >
                <i className={`fa-solid fa-message text-xs ${activeChatId === item.id ? 'text-[var(--accent-2)]' : 'text-[var(--muted-2)]'}`}></i>
                <span className="text-sm flex-1 truncate">{item.title}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* User profile */}
      <div className="p-3 border-t border-[var(--border)] relative">
        <button onClick={() => setMenuOpen(!menuOpen)} className="w-full flex items-center gap-3 p-2 rounded-xl hover:bg-[var(--card)] transition">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FFB627] to-[#FF3D00] flex items-center justify-center font-display font-bold text-sm text-white">{initials}</div>
          <div className="flex-1 text-left min-w-0">
            <div className="text-sm font-medium truncate">{visitorName}</div>
            <div className="text-[10px] font-mono text-[var(--muted-2)]">PLAN PRO · 14 hari tersisa</div>
          </div>
          <i className="fa-solid fa-ellipsis-vertical text-[var(--muted-2)] text-xs"></i>
        </button>
        
        {/* User menu dropdown */}
        <div className={`user-menu absolute bottom-full left-3 right-3 mb-2 glass-strong rounded-xl p-2 shadow-2xl ${menuOpen ? 'open' : ''}`}>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--card)] transition text-sm">
            <i className="fa-solid fa-user text-[var(--accent-2)] text-xs w-4"></i>
            <span>Profil</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--card)] transition text-sm">
            <i className="fa-solid fa-gear text-[var(--accent-2)] text-xs w-4"></i>
            <span>Pengaturan</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--card)] transition text-sm">
            <i className="fa-solid fa-credit-card text-[var(--accent-2)] text-xs w-4"></i>
            <span>Upgrade plan</span>
          </button>
          <div className="h-px bg-[var(--border)] my-1"></div>
          <button onClick={onLogout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--card)] transition text-sm text-red-400">
            <i className="fa-solid fa-right-from-bracket text-xs w-4"></i>
            <span>Keluar</span>
          </button>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

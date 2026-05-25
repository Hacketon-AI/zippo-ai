import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import NameModal from "./components/NameModal";
import ResearchPanel from "./components/ResearchPanel";

const STORAGE_KEY = "visitor_name";
type Tab = "chat" | "research";

function App() {
  const [name, setName] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  );
  const [tab, setTab] = useState<Tab>("chat");

  const handleNameSubmit = (n: string) => {
    localStorage.setItem(STORAGE_KEY, n);
    setName(n);
  };

  if (!name) {
    return (
      <div className="name-modal-wrapper">
        <NameModal onSubmit={handleNameSubmit} />
      </div>
    );
  }

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>ZippoAI Live Intelligence Agent</h1>
        <nav className="app-tabs">
          <button
            className={`tab-btn${tab === "chat" ? " active" : ""}`}
            onClick={() => setTab("chat")}
          >
            Chat
          </button>
          <button
            className={`tab-btn${tab === "research" ? " active" : ""}`}
            onClick={() => setTab("research")}
          >
            Live Research
          </button>
        </nav>
      </header>
      <main className="app-main">
        {tab === "chat" ? <ChatWindow visitorName={name} /> : <ResearchPanel />}
      </main>
    </div>
  );
}

export default App;

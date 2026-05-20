import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import NameModal from "./components/NameModal";

const STORAGE_KEY = "visitor_name";

function App() {
  const [name, setName] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  );

  const handleNameSubmit = (n: string) => {
    localStorage.setItem(STORAGE_KEY, n);
    setName(n);
  };

  if (!name) {
    return <NameModal onSubmit={handleNameSubmit} />;
  }

  return <ChatWindow visitorName={name} />;
}

export default App;

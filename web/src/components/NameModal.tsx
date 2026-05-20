import { useState } from "react";

interface Props {
  onSubmit: (name: string) => void;
}

function NameModal({ onSubmit }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  };

  return (
    <form className="name-modal" onSubmit={handleSubmit}>
      <h2>👋 Halo!</h2>
      <p style={{ marginBottom: "1rem", color: "#aaa" }}>
        Siapa nama kamu?
      </p>
      <input
        type="text"
        placeholder="Masukkan nama kamu..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        autoFocus
      />
      <button type="submit">Mulai Chat</button>
    </form>
  );
}

export default NameModal;

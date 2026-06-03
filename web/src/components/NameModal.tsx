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
    <form className="name-modal" onSubmit={handleSubmit} id="name-modal-form">
      {/* Logo */}
      <div className="name-modal-logo">
        <img src="/zippo-ai.png" alt="Zippo AI Logo" />
      </div>

      <h2>Selamat Datang!</h2>
      <p className="name-modal-desc">
        Siapa nama kamu? Aku akan menyapa kamu secara personal di setiap sesi.
      </p>

      <input
        id="name-input"
        type="text"
        placeholder="Masukkan nama kamu..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        autoFocus
        maxLength={50}
        autoComplete="off"
      />
      <button type="submit" id="name-submit-btn" disabled={!value.trim()}>
        Mulai Chat →
      </button>
    </form>
  );
}

export default NameModal;

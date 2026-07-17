import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface Props {
  onBack: () => void;
  onLogin: (token: string, name: string) => void;
}

function Login({ onBack, onLogin }: Props) {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      
      if (res.status === 429) {
        throw new Error("Terlalu banyak percobaan. Tunggu sebentar lalu coba lagi.");
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Login failed" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      
      const data = await res.json();
      onLogin(data.token, data.display_name);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page active login min-h-screen">
      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden border-r border-[var(--border)] login-brand">
        <div className="grid-pattern absolute inset-0 opacity-40"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--bg-2)] via-transparent to-[var(--bg)]"></div>
        
        <div className="relative z-10 flex flex-col justify-between p-12 w-full login-brand-inner">
          {/* Back button */}
          <button onClick={onBack} className="flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--fg)] transition w-fit back-btn">
            <i className="fa-solid fa-arrow-left"></i>
            <span>Kembali</span>
          </button>
          
          {/* Center logo + quote */}
          <div className="flex flex-col items-center text-center max-w-md mx-auto login-brand-center">
            <div className="relative w-48 h-48 mb-8 logo-glow">
              <svg viewBox="0 0 300 300" className="w-full h-full">
                <defs>
                  <linearGradient id="loginLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#FFB627"/>
                    <stop offset="100%" stopColor="#FF3D00"/>
                  </linearGradient>
                </defs>
                <polygon points="150,30 254,90 254,210 150,270 46,210 46,90" fill="none" stroke="url(#loginLogoGrad)" strokeWidth="2"/>
                <path d="M 110 115 L 190 115 L 110 185 L 190 185" fill="none" stroke="url(#loginLogoGrad)" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="190" cy="115" r="6" fill="#FFB627" className="spark-blink"/>
              </svg>
            </div>
            <h2 className="font-display font-bold text-3xl mb-4">
              Nyalakan <span className="gradient-text">idemu.</span>
            </h2>
            <p className="text-[var(--muted)] leading-relaxed">
              Masuk untuk melanjutkan ke ruang bakar Zippo AI. Semua percakapanmu tersimpan aman dan privat.
            </p>
          </div>
          
          {/* Bottom stats */}
          <div className="grid grid-cols-3 gap-4 max-w-md mx-auto w-full">
            <div className="text-center">
              <div className="font-display font-bold text-2xl gradient-text">LOKAL</div>
              <div className="text-[10px] font-mono text-[var(--muted-2)] tracking-widest mt-1">LLM DI VPS</div>
            </div>
            <div className="text-center">
              <div className="font-display font-bold text-2xl gradient-text">PRIVAT</div>
              <div className="text-[10px] font-mono text-[var(--muted-2)] tracking-widest mt-1">DATA MILIKMU</div>
            </div>
            <div className="text-center">
              <div className="font-display font-bold text-2xl gradient-text">MEMORI</div>
              <div className="text-[10px] font-mono text-[var(--muted-2)] tracking-widest mt-1">MAKIN PINTAR</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 relative login-form-panel">
        {/* Mobile back button */}
        <button onClick={onBack} className="lg:hidden absolute top-6 left-6 flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--fg)] transition back-btn mobile">
          <i className="fa-solid fa-arrow-left"></i>
          <span>Kembali</span>
        </button>
        
        <div className="w-full max-w-md login-box">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center mb-8 mt-12">
            <svg viewBox="0 0 48 48" className="w-12 h-12 logo-glow">
              <defs>
                <linearGradient id="mobileLoginGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFB627"/>
                  <stop offset="100%" stopColor="#FF3D00"/>
                </linearGradient>
              </defs>
              <polygon points="24,3 42,13.5 42,34.5 24,45 6,34.5 6,13.5" fill="none" stroke="url(#mobileLoginGrad)" strokeWidth="1.5"/>
              <path d="M 16 18 L 32 18 L 16 30 L 32 30" fill="none" stroke="url(#mobileLoginGrad)" strokeWidth="3" strokeLinecap="round"/>
            </svg>
          </div>
          
          <div className="mb-8">
            <h2 className="font-display font-bold text-3xl mb-2">Selamat datang kembali</h2>
            <p className="text-[var(--muted)] text-sm sub">Masuk untuk melanjutkan ke Zippo AI</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-5 login-form">
            <div>
              <label className="block text-xs font-mono text-[var(--muted)] tracking-widest mb-2 login-label">EMAIL</label>
              <div className="login-input-wrap">
                <input 
                  type="email" 
                  required 
                  placeholder="kamu@email.com" 
                  className="input-field w-full pl-12 pr-4 py-3.5 rounded-xl text-sm"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <i className="fa-solid fa-envelope lead"></i>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-mono text-[var(--muted)] tracking-widest login-label">PASSWORD</label>
              </div>
              <div className="login-input-wrap">
                <input 
                  type={showPassword ? "text" : "password"} 
                  required 
                  placeholder="••••••••" 
                  className="input-field w-full pl-12 pr-12 py-3.5 rounded-xl text-sm"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <i className="fa-solid fa-lock lead"></i>
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)} 
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--muted-2)] hover:text-[var(--accent)] transition eye-btn"
                >
                  <i className={`fa-solid ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                </button>
              </div>
            </div>
            
            {error && (
               <div className="text-red-400 text-sm mt-2">{error}</div>
            )}
            
            <button type="submit" disabled={loading} className="btn-primary w-full py-4 rounded-xl font-medium flex items-center justify-center gap-3 login-submit">
              <span>{loading ? "Menyalakan..." : "Masuk ke Zippo AI"}</span>
              {loading ? (
                <i className="fa-solid fa-spinner fa-spin text-sm"></i>
              ) : (
                <i className="fa-solid fa-arrow-right text-sm"></i>
              )}
            </button>
          </form>
          
          <div className="mt-8 flex items-center justify-center gap-2 text-[10px] font-mono text-[var(--muted-2)] tracking-widest login-secure">
            <i className="fa-solid fa-shield-halved"></i>
            <span>SELF-HOSTED · DATA TERSIMPAN DI SERVER SENDIRI</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Login;

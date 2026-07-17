

interface Props {
  onLoginClick: () => void;
}

function Welcome({ onLoginClick }: Props) {
  return (
    <section className="page active min-h-screen relative items-center justify-center px-6 landing">
      <div className="grid-pattern absolute inset-0 opacity-40"></div>
      
      <div className="relative z-10 text-center max-w-3xl mx-auto landing-inner">
        {/* Logo Big */}
        <div className="relative w-[300px] h-[300px] md:w-[380px] md:h-[380px] mx-auto mb-8 fade-up" style={{ animationDelay: "0.1s" }}>
          {/* Outer ring */}
          <svg viewBox="0 0 500 500" className="absolute inset-0 ring-rotate">
            <circle cx="250" cy="250" r="240" fill="none" stroke="rgba(255, 87, 34, 0.15)" strokeWidth="1" strokeDasharray="4 8"/>
            <circle cx="250" cy="10" r="3" fill="#FFB627"/>
            <circle cx="490" cy="250" r="2" fill="#FF5722"/>
            <circle cx="250" cy="490" r="2.5" fill="#FF3D00"/>
          </svg>
          
          {/* Middle ring */}
          <svg viewBox="0 0 500 500" className="absolute inset-0 ring-rotate-rev">
            <circle cx="250" cy="250" r="200" fill="none" stroke="rgba(255, 182, 39, 0.2)" strokeWidth="1"/>
            <circle cx="250" cy="50" r="4" fill="#FFB627" opacity="0.6"/>
            <circle cx="450" cy="250" r="3" fill="#FF5722" opacity="0.8"/>
          </svg>
          
          {/* Main logo */}
          <div className="absolute inset-0 flex items-center justify-center logo-glow">
            <svg viewBox="0 0 300 300" className="w-full h-full">
              <defs>
                <linearGradient id="welcomeLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFB627"/>
                  <stop offset="50%" stopColor="#FF5722"/>
                  <stop offset="100%" stopColor="#FF3D00"/>
                </linearGradient>
                <radialGradient id="welcomeCoreGlow">
                  <stop offset="0%" stopColor="#FFB627" stopOpacity="0.5"/>
                  <stop offset="100%" stopColor="#FF3D00" stopOpacity="0"/>
                </radialGradient>
              </defs>
              <circle cx="150" cy="150" r="80" fill="url(#welcomeCoreGlow)"/>
              <polygon points="150,30 254,90 254,210 150,270 46,210 46,90" fill="none" stroke="url(#welcomeLogoGrad)" strokeWidth="2"/>
              <polygon points="150,60 228,105 228,195 150,240 72,195 72,105" fill="none" stroke="url(#welcomeLogoGrad)" strokeWidth="1" opacity="0.4"/>
              <path d="M 110 115 L 190 115 L 110 185 L 190 185" fill="none" stroke="url(#welcomeLogoGrad)" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="190" cy="115" r="6" fill="#FFB627" className="spark-blink"/>
              <circle cx="190" cy="115" r="12" fill="#FFB627" opacity="0.3" className="spark-blink"/>
              <circle cx="254" cy="90" r="3" fill="#FFB627" className="spark-blink"/>
              <circle cx="46" cy="210" r="3" fill="#FF5722" className="spark-blink"/>
            </svg>
          </div>
        </div>
        
        {/* Version badge */}
        <div className="chip inline-flex items-center gap-2 px-4 py-2 text-xs font-mono mb-8 fade-up" style={{ animationDelay: "0.3s" }}>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent)] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent-2)]"></span>
          </span>
          <span className="text-[var(--muted)]">v2.4 · Zippo-4o sekarang tersedia</span>
        </div>
        
        <h1 className="font-display font-bold text-5xl md:text-7xl leading-[0.95] tracking-tight mb-6 fade-up" style={{ animationDelay: "0.4s" }}>
          Percikan ide,<br/>
          <span className="underline-fire gradient-text">dalam sekejap.</span>
        </h1>
        
        <p className="text-[var(--muted)] text-lg md:text-xl max-w-xl mx-auto mb-12 leading-relaxed fade-up" style={{ animationDelay: "0.5s" }}>
          Zippo AI bukan sekadar chatbot. Ruang bakar tempat ide, kode, dan pertanyaanmu dinyalakan menjadi jawaban.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 fade-up landing-cta" style={{ animationDelay: "0.6s" }}>
          <button onClick={onLoginClick} className="btn-primary px-8 py-4 rounded-full font-medium flex items-center gap-3 text-lg w-full sm:w-auto justify-center">
            <i className="fa-solid fa-fire"></i>
            <span>Masuk ke Zippo AI</span>
          </button>
          <button onClick={onLoginClick} className="btn-ghost px-8 py-4 rounded-full font-medium flex items-center gap-3 text-lg w-full sm:w-auto justify-center">
            <span>Belum punya akun? Daftar</span>
            <i className="fa-solid fa-arrow-right text-xs"></i>
          </button>
        </div>
        
        <div className="mt-16 flex items-center justify-center gap-6 text-xs font-mono text-[var(--muted-2)] fade-up landing-footer" style={{ animationDelay: "0.7s" }}>
          <span className="flex items-center gap-2"><i className="fa-solid fa-shield-halved text-[var(--accent-2)]"></i> End-to-end encrypted</span>
          <span className="hidden sm:flex items-center gap-2"><i className="fa-solid fa-bolt text-[var(--accent-2)]"></i> 50ms response</span>
          <span className="flex items-center gap-2"><i className="fa-solid fa-globe text-[var(--accent-2)]"></i> 100+ bahasa</span>
        </div>
      </div>
    </section>
  );
}

export default Welcome;

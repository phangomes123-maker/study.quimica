import { Link, useLocation } from "react-router-dom";

export default function Nav() {
  const loc = useLocation();
  const link = (to, label, testid) => {
    const active = loc.pathname === to || (to !== "/" && loc.pathname.startsWith(to));
    return (
      <Link
        to={to}
        data-testid={testid}
        className={`font-mono text-xs uppercase tracking-[0.2em] px-3 py-2 border transition-colors ${
          active
            ? "bg-[#0F1115] text-white border-[#0F1115]"
            : "bg-transparent text-[#0F1115] border-transparent hover:border-[#0F1115]"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="border-b border-[#E0E2DB] bg-white sticky top-0 z-40" data-testid="site-nav">
      <div className="max-w-7xl mx-auto px-6 lg:px-10 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3" data-testid="nav-logo">
          <div className="w-8 h-8 bg-[#0F1115] text-[#FFD500] flex items-center justify-center font-heading text-lg">
            Q
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-display font-bold text-base tracking-tight">
              Estúdio<span className="text-[#0022FF]">.</span>Química
            </span>
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-[#5C5F66]">
              plataforma de estudos
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {link("/", "Início", "nav-home")}
          {link("/topicos", "Tópicos", "nav-topics")}
          {link("/revisao", "Revisão", "nav-revision")}
          {link("/progresso", "Progresso", "nav-progress")}
        </nav>

        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-block font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66]">
            Cinética · Eletroquímica
          </span>
        </div>
      </div>
    </header>
  );
}

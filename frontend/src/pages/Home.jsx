import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchTopics } from "../lib/api";
import TopicCard from "../components/TopicCard";
import { ArrowRight, Lightning, BookOpen, ListChecks, VideoCamera, Sparkle } from "@phosphor-icons/react";

export default function Home() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTopics().then((data) => {
      setTopics(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const modules = [...new Set(topics.map((t) => t.module))];

  return (
    <div data-testid="home-page">
      {/* HERO */}
      <section className="relative overflow-hidden border-b border-[#E0E2DB] grid-bg">
        <div className="max-w-7xl mx-auto px-6 lg:px-10 pt-16 pb-24 lg:pt-24 lg:pb-32">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
            <div className="lg:col-span-8">
              <div className="flex items-center gap-3 mb-6">
                <span className="w-8 h-px bg-[#0F1115]" />
                <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66]">
                  Plataforma de estudos · Química · Pt-BR
                </span>
              </div>
              <h1 className="font-heading text-5xl sm:text-6xl lg:text-[88px] leading-[0.95] mb-6">
                Aprenda química<br />
                <span className="italic font-normal">como quem faz</span>{" "}
                <span className="inline-block bg-[#FFD500] px-3 -rotate-1">ciência.</span>
              </h1>
              <p className="text-lg text-[#5C5F66] max-w-xl leading-relaxed mb-10">
                Conteúdo teórico organizado, resumos gerados por IA, exercícios comentados
                e vídeoaulas. Sem cadastro, sem fricção — só estudo de verdade.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <Link
                  to="/topicos"
                  data-testid="hero-cta-start"
                  className="inline-flex items-center gap-2 bg-[#0022FF] hover:bg-[#0019C0] text-white px-6 py-4 font-mono text-xs uppercase tracking-[0.2em] transition-colors"
                >
                  Começar a estudar <ArrowRight size={16} weight="bold" />
                </Link>
                <Link
                  to="/revisao"
                  data-testid="hero-cta-revision"
                  className="inline-flex items-center gap-2 border border-[#0F1115] bg-white hover:bg-[#0F1115] hover:text-white px-6 py-4 font-mono text-xs uppercase tracking-[0.2em] transition-colors"
                >
                  Modo revisão
                </Link>
              </div>
            </div>

            <div className="lg:col-span-4 border border-[#0F1115] bg-white p-6">
              <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-4">
                >> Diagnóstico rápido
              </div>
              <div className="space-y-4">
                <Stat label="Módulos" value={modules.length || 2} />
                <Stat label="Tópicos" value={topics.length || 5} />
                <Stat label="Exercícios" value="20+" />
                <Stat label="Vídeoaulas" value="7" />
              </div>
              <div className="mt-6 pt-6 border-t border-[#E0E2DB]">
                <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-2">
                  Foco atual
                </div>
                <div className="font-display font-bold text-lg">Cinética · Eletroquímica</div>
              </div>
            </div>
          </div>
        </div>

        {/* Ticker */}
        <div className="border-t border-[#0F1115] bg-[#0F1115] text-white overflow-hidden">
          <div className="flex ticker-track whitespace-nowrap py-3 font-mono text-xs uppercase tracking-[0.3em]">
            {Array(2).fill(0).map((_, i) => (
              <div key={i} className="flex items-center">
                {["Velocidade Média", "Teoria das Colisões", "Lei da Velocidade", "Arrhenius", "NOX", "Redox", "Células Voltaicas", "Ponte Salina", "ΔE° > 0"].map((w) => (
                  <span key={w + i} className="px-6 flex items-center gap-6">
                    {w} <span className="text-[#FFD500]">✦</span>
                  </span>
                ))}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="max-w-7xl mx-auto px-6 lg:px-10 py-20 border-b border-[#E0E2DB]">
        <div className="flex items-baseline justify-between mb-10">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
              /01 · O que você tem aqui
            </div>
            <h2 className="font-heading text-4xl lg:text-5xl">Cinco ferramentas. Um só objetivo.</h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-0 border border-[#0F1115]">
          <Feature icon={BookOpen} title="Conteúdo" text="Teoria estruturada por tópicos, com fórmulas e conceitos-chave." />
          <Feature icon={Sparkle} title="Resumos IA" text="Resumos gerados por IA sob demanda, com macetes e destaques." />
          <Feature icon={ListChecks} title="Exercícios" text="Múltipla escolha com correção automática + questões abertas." />
          <Feature icon={VideoCamera} title="Vídeos" text="Vídeoaulas curadas de canais brasileiros de química." />
          <Feature icon={Lightning} title="Revisão" text="Modo revisão que devolve as questões que você errou." last />
        </div>
      </section>

      {/* TOPICS GRID */}
      <section className="max-w-7xl mx-auto px-6 lg:px-10 py-20">
        <div className="flex items-baseline justify-between mb-10 flex-wrap gap-4">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
              /02 · Índice
            </div>
            <h2 className="font-heading text-4xl lg:text-5xl">Todos os tópicos</h2>
          </div>
          <Link
            to="/topicos"
            data-testid="home-view-all"
            className="font-mono text-xs uppercase tracking-[0.2em] border-b border-[#0F1115] hover:text-[#0022FF] hover:border-[#0022FF]"
          >
            Ver todos →
          </Link>
        </div>

        {loading ? (
          <div className="font-mono text-sm text-[#5C5F66]">Carregando tópicos...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="home-topics-grid">
            {topics.map((t, i) => (
              <TopicCard key={t.id} topic={t} index={i} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="flex items-baseline justify-between border-b border-[#E0E2DB] pb-2">
      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66]">
        {label}
      </span>
      <span className="font-display font-bold text-2xl">{value}</span>
    </div>
  );
}

function Feature({ icon: Icon, title, text, last }) {
  return (
    <div className={`p-6 lg:p-8 ${!last ? "border-b lg:border-b-0 lg:border-r border-[#0F1115]" : ""} bg-white hover:bg-[#F4F5F2] transition-colors`}>
      <Icon size={28} weight="duotone" className="mb-4 text-[#0022FF]" />
      <div className="font-display font-bold text-lg mb-1">{title}</div>
      <p className="text-sm text-[#5C5F66] leading-relaxed">{text}</p>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchTopics } from "../lib/api";
import TopicCard from "../components/TopicCard";
import { getStreak } from "../lib/streak";
import { ArrowRight, Flame, Camera, ChatCircleDots, Sparkle, Atom, Lightning, Gauge, Flask } from "@phosphor-icons/react";

const MODULE_META = {
  "Cinética Química": { icon: Gauge, color: "#FF3300", desc: "Como e por quê as reações acontecem em determinada velocidade." },
  "Eletroquímica": { icon: Lightning, color: "#FFD500", desc: "Reações redox, pilhas e eletrólise." },
  "Equilíbrio Químico": { icon: Atom, color: "#00D65B", desc: "Reações reversíveis e o equilíbrio dinâmico." },
  "Termoquímica": { icon: Flask, color: "#0022FF", desc: "Calor, entalpia, entropia e espontaneidade." },
};

export default function Home() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const streak = getStreak();

  useEffect(() => {
    fetchTopics().then((d) => { setTopics(d); setLoading(false); });
  }, []);

  const modules = [...new Set(topics.map((t) => t.module))];

  return (
    <div data-testid="home-page">
      {/* HERO */}
      <section className="relative overflow-hidden border-b border-[#E0E2DB] grid-bg">
        <div className="max-w-7xl mx-auto px-6 lg:px-10 pt-14 pb-20 lg:pt-20 lg:pb-24">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
            <div className="lg:col-span-8">
              <div className="flex items-center gap-3 mb-6">
                <span className="w-8 h-px bg-[#0F1115]" />
                <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66]">
                  Plataforma de estudos · Química · Pt-BR
                </span>
              </div>
              <h1 className="font-heading text-5xl sm:text-6xl lg:text-[80px] leading-[0.95] mb-6">
                Aprenda química<br />
                <span className="italic font-normal">como quem faz</span>{" "}
                <span className="inline-block bg-[#FFD500] px-3 -rotate-1">ciência.</span>
              </h1>
              <p className="text-lg text-[#5C5F66] max-w-xl leading-relaxed mb-10">
                Conteúdo, resumos por IA, exercícios com correção automática, Tutor Socrático 24/7 e Scanner de foto.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <Link to="/topicos" data-testid="hero-cta-start" className="inline-flex items-center gap-2 bg-[#0022FF] hover:bg-[#0019C0] text-white px-6 py-4 font-mono text-xs uppercase tracking-[0.2em] transition-colors">
                  Começar a estudar <ArrowRight size={16} weight="bold" />
                </Link>
                <Link to="/scanner" data-testid="hero-cta-scanner" className="inline-flex items-center gap-2 border border-[#0F1115] bg-white hover:bg-[#0F1115] hover:text-white px-6 py-4 font-mono text-xs uppercase tracking-[0.2em] transition-colors">
                  <Camera size={16} weight="bold" /> Scanner IA
                </Link>
              </div>
            </div>

            <div className="lg:col-span-4 space-y-3">
              <div className="border border-[#0F1115] bg-gradient-to-br from-[#FF3300] to-[#FFD500] p-5 text-white">
                <div className="flex items-center gap-3 mb-2">
                  <Flame size={22} weight="fill" />
                  <div className="font-mono text-[10px] uppercase tracking-[0.25em]">Streak</div>
                </div>
                <div className="font-heading text-4xl leading-none">{streak.count || 0} <span className="text-lg">dias</span></div>
                <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-80 mt-2">
                  {streak.count ? "Continue estudando hoje!" : "Comece hoje sua sequência"}
                </div>
              </div>
              <div className="border border-[#0F1115] bg-white p-5">
                <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-2">Diagnóstico</div>
                <div className="grid grid-cols-2 gap-3">
                  <MiniStat label="Módulos" value={modules.length || 4} />
                  <MiniStat label="Tópicos" value={topics.length || 13} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature strip */}
      <section className="max-w-7xl mx-auto px-6 lg:px-10 py-12 border-b border-[#E0E2DB]">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-[#0F1115]">
          <FeatureLink to="/scanner" icon={Camera} title="Scanner IA" desc="Foto do exercício → IA identifica o assunto" />
          <FeatureLink icon={ChatCircleDots} title="Tutor 24/7" desc="Chat socrático — te guia sem dar a resposta" middle />
          <FeatureLink icon={Sparkle} title="Resumos IA" desc="Claude gera resumos didáticos sob demanda" />
        </div>
      </section>

      {/* MODULES */}
      <section className="max-w-7xl mx-auto px-6 lg:px-10 py-16">
        <div className="flex items-baseline justify-between mb-10 flex-wrap gap-4">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">/01 · Módulos</div>
            <h2 className="font-heading text-4xl lg:text-5xl">Escolha por onde começar</h2>
          </div>
          <Link to="/topicos" data-testid="home-view-all" className="font-mono text-xs uppercase tracking-[0.2em] border-b border-[#0F1115] hover:text-[#0022FF] hover:border-[#0022FF]">
            Ver todos os tópicos →
          </Link>
        </div>

        {loading ? (
          <div className="font-mono text-sm text-[#5C5F66]">Carregando módulos...</div>
        ) : (
          <div className="space-y-12" data-testid="home-modules">
            {modules.map((mod) => {
              const meta = MODULE_META[mod] || { icon: Flask, color: "#0F1115", desc: "" };
              const Icon = meta.icon;
              const ts = topics.filter((t) => t.module === mod);
              return (
                <section key={mod} data-testid={`home-module-${mod}`}>
                  <div className="flex items-start gap-4 mb-6 pb-3 border-b-2 border-[#0F1115]">
                    <div className="w-12 h-12 flex items-center justify-center flex-shrink-0" style={{ background: meta.color }}>
                      <Icon size={24} weight="duotone" color="#0F1115" />
                    </div>
                    <div className="flex-1">
                      <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-1">
                        Módulo · {ts.length} {ts.length === 1 ? "tópico" : "tópicos"}
                      </div>
                      <h3 className="font-heading text-3xl leading-none">{mod}</h3>
                      <p className="text-sm text-[#5C5F66] mt-1">{meta.desc}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {ts.map((t, i) => (<TopicCard key={t.id} topic={t} index={i} />))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div className="border border-[#E0E2DB] p-2">
      <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-[#5C5F66]">{label}</div>
      <div className="font-display font-bold text-xl">{value}</div>
    </div>
  );
}

function FeatureLink({ to, icon: Icon, title, desc, middle }) {
  const inner = (
    <div className={`p-5 lg:p-6 ${middle ? "border-l border-r border-[#0F1115]" : ""} bg-white hover:bg-[#F4F5F2] transition-colors flex items-start gap-4`}>
      <Icon size={26} weight="duotone" className="text-[#0022FF] flex-shrink-0" />
      <div>
        <div className="font-display font-bold text-base mb-1">{title}</div>
        <p className="text-xs text-[#5C5F66] leading-relaxed">{desc}</p>
      </div>
    </div>
  );
  return to ? <Link to={to}>{inner}</Link> : inner;
}

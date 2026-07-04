import { useEffect, useState } from "react";
import { fetchTopics } from "../lib/api";
import TopicCard from "../components/TopicCard";
import { Atom, Lightning, Gauge, Flask } from "@phosphor-icons/react";

const MODULE_META = {
  "Cinética Química": { icon: Gauge, color: "#FF3300", desc: "Como e por quê as reações acontecem em determinada velocidade." },
  "Eletroquímica": { icon: Lightning, color: "#FFD500", desc: "Reações redox, pilhas e eletrólise." },
  "Equilíbrio Químico": { icon: Atom, color: "#00D65B", desc: "Reações reversíveis e o equilíbrio dinâmico." },
  "Termoquímica": { icon: Flask, color: "#0022FF", desc: "Calor, entalpia, entropia e espontaneidade." },
};

export default function Topics() {
  const [topics, setTopics] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTopics().then((d) => { setTopics(d); setLoading(false); });
  }, []);

  const modules = [...new Set(topics.map((t) => t.module))];
  const visible = filter === "all" ? modules : [filter];

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-16" data-testid="topics-page">
      <div className="mb-10">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
          Índice completo · {topics.length} tópicos · {modules.length} módulos
        </div>
        <h1 className="font-heading text-5xl lg:text-6xl">Tópicos</h1>
        <p className="text-lg text-[#5C5F66] mt-3 max-w-2xl">
          Escolha um tópico para acessar conteúdo teórico, resumo IA, exercícios e vídeos.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-12 border-b border-[#E0E2DB] pb-4">
        <button
          data-testid="filter-all"
          onClick={() => setFilter("all")}
          className={`font-mono text-xs uppercase tracking-[0.2em] px-4 py-2 border transition-colors ${filter === "all" ? "bg-[#0F1115] text-white border-[#0F1115]" : "border-[#E0E2DB] hover:border-[#0F1115]"}`}
        >Todos</button>
        {modules.map((m) => (
          <button
            key={m}
            data-testid={`filter-${m}`}
            onClick={() => setFilter(m)}
            className={`font-mono text-xs uppercase tracking-[0.2em] px-4 py-2 border transition-colors ${filter === m ? "bg-[#0F1115] text-white border-[#0F1115]" : "border-[#E0E2DB] hover:border-[#0F1115]"}`}
          >{m}</button>
        ))}
      </div>

      {loading ? (
        <div className="font-mono text-sm text-[#5C5F66]">Carregando...</div>
      ) : (
        <div className="space-y-16">
          {visible.map((mod) => {
            const meta = MODULE_META[mod] || { icon: Flask, color: "#0F1115", desc: "" };
            const Icon = meta.icon;
            const ts = topics.filter((t) => t.module === mod);
            return (
              <section key={mod} data-testid={`module-section-${mod}`}>
                <div className="flex items-start gap-4 mb-8 pb-4 border-b-2 border-[#0F1115]">
                  <div
                    className="w-14 h-14 flex items-center justify-center flex-shrink-0"
                    style={{ background: meta.color }}
                  >
                    <Icon size={28} weight="duotone" color="#0F1115" />
                  </div>
                  <div className="flex-1">
                    <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-1">
                      Módulo · {ts.length} {ts.length === 1 ? "tópico" : "tópicos"}
                    </div>
                    <h2 className="font-heading text-3xl lg:text-4xl leading-none">{mod}</h2>
                    <p className="text-sm text-[#5C5F66] mt-1">{meta.desc}</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {ts.map((t, i) => (
                    <TopicCard key={t.id} topic={t} index={i} />
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

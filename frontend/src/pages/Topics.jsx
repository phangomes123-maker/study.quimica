import { useEffect, useState } from "react";
import { fetchTopics } from "../lib/api";
import TopicCard from "../components/TopicCard";

export default function Topics() {
  const [topics, setTopics] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTopics().then((d) => { setTopics(d); setLoading(false); });
  }, []);

  const modules = ["all", ...new Set(topics.map((t) => t.module))];
  const filtered = filter === "all" ? topics : topics.filter((t) => t.module === filter);

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-16" data-testid="topics-page">
      <div className="mb-10">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
          Índice completo
        </div>
        <h1 className="font-heading text-5xl lg:text-6xl">Tópicos</h1>
        <p className="text-lg text-[#5C5F66] mt-3 max-w-2xl">
          Escolha um tópico para acessar conteúdo teórico, resumo IA, exercícios e vídeoaulas.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-10 border-b border-[#E0E2DB] pb-4">
        {modules.map((m) => (
          <button
            key={m}
            data-testid={`filter-${m}`}
            onClick={() => setFilter(m)}
            className={`font-mono text-xs uppercase tracking-[0.2em] px-4 py-2 border transition-colors ${
              filter === m
                ? "bg-[#0F1115] text-white border-[#0F1115]"
                : "border-[#E0E2DB] text-[#0F1115] hover:border-[#0F1115]"
            }`}
          >
            {m === "all" ? "Todos" : m}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="font-mono text-sm text-[#5C5F66]">Carregando...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="topics-grid">
          {filtered.map((t, i) => (
            <TopicCard key={t.id} topic={t} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}

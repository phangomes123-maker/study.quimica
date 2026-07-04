import { useEffect, useState } from "react";
import { fetchProgress, fetchTopics, fetchOpenAnswers } from "../lib/api";
import { getSessionId } from "../lib/session";
import { TrendUp, Target, CheckCircle, NotePencil } from "@phosphor-icons/react";

export default function Progress() {
  const [progress, setProgress] = useState(null);
  const [topics, setTopics] = useState([]);
  const [openAnswers, setOpenAnswers] = useState([]);

  useEffect(() => {
    Promise.all([
      fetchProgress(getSessionId()),
      fetchTopics(),
      fetchOpenAnswers(getSessionId()),
    ]).then(([p, t, oa]) => {
      setProgress(p);
      setTopics(t);
      setOpenAnswers(oa);
    });
  }, []);

  const topicName = (id) => topics.find((t) => t.id === id)?.title || id;

  return (
    <div className="max-w-6xl mx-auto px-6 lg:px-10 py-12" data-testid="progress-page">
      <div className="mb-10">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
          Seu desempenho
        </div>
        <h1 className="font-heading text-5xl lg:text-6xl">Progresso</h1>
      </div>

      {!progress ? (
        <div className="font-mono text-sm text-[#5C5F66]">Carregando...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-[#0F1115] mb-10">
            <Stat icon={Target} label="Total respondido" value={progress.total} />
            <Stat icon={CheckCircle} label="Acertos" value={progress.correct} middle />
            <Stat
              icon={TrendUp}
              label="Precisão"
              value={`${progress.accuracy.toFixed(0)}%`}
              accent
            />
          </div>

          <h2 className="font-display font-bold text-2xl mb-4">Por tópico</h2>
          {Object.keys(progress.per_topic).length === 0 ? (
            <div className="border border-dashed border-[#E0E2DB] p-10 text-center">
              <p className="font-mono text-sm text-[#5C5F66]">
                Nenhum exercício respondido ainda. Comece por um tópico e volte aqui.
              </p>
            </div>
          ) : (
            <div className="space-y-3" data-testid="progress-per-topic">
              {Object.entries(progress.per_topic).map(([tid, s]) => {
                const pct = s.total ? (s.correct / s.total) * 100 : 0;
                return (
                  <div key={tid} className="border border-[#E0E2DB] p-5">
                    <div className="flex items-baseline justify-between mb-2">
                      <span className="font-display font-semibold">{topicName(tid)}</span>
                      <span className="font-mono text-xs text-[#5C5F66]">
                        {s.correct}/{s.total}
                      </span>
                    </div>
                    <div className="h-3 bg-[#F4F5F2]">
                      <div
                        className="h-full bg-[#FFD500]"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-14">
            <div className="flex items-center gap-3 mb-4">
              <NotePencil size={22} weight="duotone" className="text-[#0022FF]" />
              <h2 className="font-display font-bold text-2xl">Minhas respostas abertas</h2>
            </div>
            {openAnswers.length === 0 ? (
              <div className="border border-dashed border-[#E0E2DB] p-10 text-center">
                <p className="font-mono text-sm text-[#5C5F66]">
                  Você ainda não salvou nenhuma resposta aberta. Vá em um tópico → Exercícios → questão aberta e clique em &quot;Salvar resposta&quot;.
                </p>
              </div>
            ) : (
              <div className="space-y-4" data-testid="open-answers-list">
                {openAnswers.map((oa) => (
                  <details
                    key={oa.id}
                    className="border border-[#E0E2DB] bg-white p-5 group"
                    data-testid={`open-answer-${oa.exercise_id}`}
                  >
                    <summary className="cursor-pointer flex items-baseline justify-between gap-4">
                      <span className="font-display font-semibold text-sm flex-1">{oa.question}</span>
                      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66]">
                        {topicName(oa.topic_id).slice(0, 30)}…
                      </span>
                    </summary>
                    <div className="mt-4 space-y-3">
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
                          Sua resposta
                        </div>
                        <div className="text-sm whitespace-pre-wrap bg-[#F4F5F2] p-3 border-l-2 border-[#0F1115]">
                          {oa.answer_text}
                        </div>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
                          Gabarito
                        </div>
                        <div className="text-sm bg-[#F4F5F2] p-3 border-l-2 border-[#0022FF]">
                          {oa.gabarito}
                        </div>
                      </div>
                    </div>
                  </details>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value, middle, accent }) {
  return (
    <div className={`p-8 ${middle ? "border-l border-r border-[#0F1115]" : ""} ${accent ? "bg-[#0F1115] text-white" : "bg-white"}`}>
      <Icon size={24} weight="duotone" className="mb-4" />
      <div className={`font-mono text-[10px] uppercase tracking-[0.25em] ${accent ? "text-white/60" : "text-[#5C5F66]"} mb-2`}>
        {label}
      </div>
      <div className="font-heading text-5xl">{value}</div>
    </div>
  );
}

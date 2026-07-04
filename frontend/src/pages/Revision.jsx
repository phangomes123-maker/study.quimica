import { useEffect, useState } from "react";
import { toast } from "sonner";
import { fetchRevision, submitAnswer } from "../lib/api";
import { getSessionId } from "../lib/session";
import { ArrowClockwise, CheckCircle, XCircle, Sparkle } from "@phosphor-icons/react";

export default function Revision() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);

  const load = () => {
    setLoading(true);
    setIdx(0);
    setSelected(null);
    setResult(null);
    fetchRevision(getSessionId(), 10)
      .then((d) => setQuestions(d))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const current = questions[idx];

  const submit = async () => {
    if (selected === null) return;
    const res = await submitAnswer({
      session_id: getSessionId(),
      exercise_id: current.id,
      selected_index: selected,
    });
    setResult(res);
  };

  const next = () => {
    setSelected(null);
    setResult(null);
    if (idx + 1 < questions.length) setIdx(idx + 1);
    else {
      toast.success("Revisão concluída!");
      load();
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 lg:px-10 py-12 bg-[#FFFBEC] min-h-screen" data-testid="revision-page">
      <div className="border-b border-[#0F1115] pb-6 mb-8">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2 flex items-center gap-2">
          <ArrowClockwise size={12} weight="bold" /> Modo revisão · Foco
        </div>
        <h1 className="font-heading text-4xl lg:text-5xl">Revise o que você errou</h1>
        <p className="text-[#5C5F66] mt-3 max-w-2xl">
          Estas são as questões que você respondeu incorretamente. Se não houver erros, mostramos uma amostra aleatória para você praticar.
        </p>
      </div>

      {loading ? (
        <div className="font-mono text-sm text-[#5C5F66]">Carregando revisão...</div>
      ) : !current ? (
        <Empty />
      ) : current.type === "mcq" ? (
        <div className="border border-[#0F1115] p-6 bg-white" data-testid="revision-mcq">
          <div className="flex items-center justify-between mb-4">
            <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66]">
              Questão {idx + 1} de {questions.length}
            </div>
            <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66]">
              {current.difficulty}
            </div>
          </div>
          <p className="text-lg font-medium mb-6 leading-relaxed">{current.question}</p>
          <div className="space-y-2">
            {current.options.map((opt, i) => {
              const isSel = selected === i;
              const isCorrect = result && i === result.correct_index;
              const isWrongPick = result && isSel && !result.correct;
              let cls = "border-[#E0E2DB] bg-white hover:border-[#0F1115]";
              if (result) {
                if (isCorrect) cls = "border-[#00D65B] bg-[#00D65B] text-white";
                else if (isWrongPick) cls = "border-[#FF3300] bg-[#FF3300] text-white";
                else cls = "border-[#E0E2DB] opacity-60";
              } else if (isSel) cls = "border-[#0022FF] bg-blue-50";
              return (
                <button
                  key={i}
                  onClick={() => !result && setSelected(i)}
                  disabled={!!result}
                  data-testid={`revision-option-${i}`}
                  className={`w-full text-left border p-4 flex items-center gap-4 transition-colors ${cls}`}
                >
                  <span className="font-mono text-xs w-6">{String.fromCharCode(65 + i)}</span>
                  <span className="flex-1 text-sm">{opt}</span>
                  {result && isCorrect && <CheckCircle size={20} weight="fill" />}
                  {result && isWrongPick && <XCircle size={20} weight="fill" />}
                </button>
              );
            })}
          </div>

          {result && (
            <div className="mt-6 border-l-4 border-[#0F1115] pl-4 py-2 bg-[#F4F5F2]">
              <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
                Explicação
              </div>
              <p className="text-sm leading-relaxed">{result.explanation}</p>
            </div>
          )}

          <div className="mt-6 flex gap-3">
            {!result ? (
              <button
                onClick={submit}
                disabled={selected === null}
                data-testid="revision-submit"
                className="bg-[#0F1115] text-white hover:bg-[#0022FF] px-5 py-3 font-mono text-xs uppercase tracking-[0.2em] disabled:opacity-40"
              >
                Verificar
              </button>
            ) : (
              <button
                onClick={next}
                data-testid="revision-next"
                className="bg-[#0022FF] text-white hover:bg-[#0019C0] px-5 py-3 font-mono text-xs uppercase tracking-[0.2em]"
              >
                Próxima →
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="border border-[#0F1115] p-6 bg-white">
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-3">
            Questão {idx + 1} · Aberta · {current.difficulty}
          </div>
          <p className="text-lg font-medium mb-4">{current.question}</p>
          <div className="border-l-4 border-[#0022FF] pl-4 py-2 bg-[#F4F5F2]">
            <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
              Gabarito comentado
            </div>
            <p className="text-sm">{current.explanation}</p>
          </div>
          <button
            onClick={next}
            data-testid="revision-next-open"
            className="mt-6 bg-[#0022FF] text-white hover:bg-[#0019C0] px-5 py-3 font-mono text-xs uppercase tracking-[0.2em]"
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  );
}

function Empty() {
  return (
    <div className="border border-dashed border-[#0F1115] p-12 text-center bg-white">
      <Sparkle size={36} className="mx-auto mb-3 text-[#0022FF]" weight="duotone" />
      <h3 className="font-display font-bold text-xl mb-2">Nada para revisar ainda</h3>
      <p className="text-sm text-[#5C5F66]">
        Responda alguns exercícios primeiro para o modo revisão preencher com o que você errou.
      </p>
    </div>
  );
}

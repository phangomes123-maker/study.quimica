import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, BookOpen, Sparkle, ListChecks, VideoCamera, ArrowClockwise, CheckCircle, XCircle } from "@phosphor-icons/react";
import { toast } from "sonner";
import {
  fetchTopic,
  fetchContent,
  fetchVideos,
  fetchExercises,
  fetchSummary,
  generateSummary,
  submitAnswer,
  saveOpenAnswer,
  fetchOpenAnswer,
} from "../lib/api";
import { getSessionId } from "../lib/session";

const TABS = [
  { id: "content", label: "Conteúdo", icon: BookOpen },
  { id: "summary", label: "Resumo IA", icon: Sparkle },
  { id: "exercises", label: "Exercícios", icon: ListChecks },
  { id: "videos", label: "Vídeos", icon: VideoCamera },
];

export default function TopicDetail() {
  const { id } = useParams();
  const [topic, setTopic] = useState(null);
  const [content, setContent] = useState([]);
  const [videos, setVideos] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [summary, setSummary] = useState(null);
  const [tab, setTab] = useState("content");
  const [genLoading, setGenLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchTopic(id),
      fetchContent(id),
      fetchVideos(id),
      fetchExercises(id),
      fetchSummary(id),
    ]).then(([t, c, v, e, s]) => {
      setTopic(t);
      setContent(c);
      setVideos(v);
      setExercises(e);
      if (s.exists) setSummary(s.content);
    }).catch((err) => {
      console.error(err);
      toast.error("Erro ao carregar tópico");
    });
  }, [id]);

  const handleGenerate = async () => {
    setGenLoading(true);
    try {
      const res = await generateSummary(id);
      setSummary(res.content);
      toast.success("Resumo gerado com sucesso");
    } catch (e) {
      toast.error("Erro ao gerar resumo");
    } finally {
      setGenLoading(false);
    }
  };

  if (!topic) return <div className="max-w-7xl mx-auto px-6 py-16 font-mono text-sm">Carregando...</div>;

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10" data-testid="topic-detail">
      <Link
        to="/topicos"
        data-testid="back-to-topics"
        className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] hover:text-[#0F1115] mb-6"
      >
        <ArrowLeft size={14} /> Voltar
      </Link>

      {/* Header */}
      <div className="border-b border-[#0F1115] pb-8 mb-8">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-3">
          Módulo · {topic.module}
        </div>
        <h1 className="font-heading text-4xl lg:text-6xl leading-[1] mb-4" data-testid="topic-title">
          {topic.title}
        </h1>
        <p className="text-lg text-[#5C5F66] max-w-3xl">{topic.description}</p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-0 border-b border-[#E0E2DB] mb-8">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              data-testid={`tab-${t.id}`}
              className={`flex items-center gap-2 px-5 py-3 font-mono text-xs uppercase tracking-[0.2em] border-b-2 transition-colors ${
                active
                  ? "border-[#0022FF] text-[#0022FF]"
                  : "border-transparent text-[#5C5F66] hover:text-[#0F1115]"
              }`}
            >
              <Icon size={16} weight={active ? "fill" : "regular"} />
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "content" && <ContentView content={content} />}
      {tab === "summary" && (
        <SummaryView
          summary={summary}
          onGenerate={handleGenerate}
          loading={genLoading}
        />
      )}
      {tab === "exercises" && <ExercisesView exercises={exercises} />}
      {tab === "videos" && <VideosView videos={videos} topic={topic} />}
    </div>
  );
}

function ContentView({ content }) {
  if (!content.length) return <Empty text="Sem conteúdo para este tópico." />;
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8" data-testid="content-view">
      <div className="lg:col-span-8 space-y-8">
        {content.map((c, i) => (
          <section key={c.id} className="border-l-4 border-[#0F1115] pl-6 py-2 fade-in-up" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-2">
              §{String(i + 1).padStart(2, "0")}
            </div>
            <h2 className="font-display font-bold text-2xl mb-3">{c.heading}</h2>
            <div className="whitespace-pre-wrap text-[15px] leading-relaxed text-[#0F1115]">
              {c.body}
            </div>
          </section>
        ))}
      </div>
      <aside className="lg:col-span-4">
        <div className="sticky top-24 border border-[#0F1115] p-6 bg-[#F4F5F2]">
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-4">
            {">>"} Sumário
          </div>
          <ol className="space-y-2">
            {content.map((c, i) => (
              <li key={c.id} className="flex gap-3 text-sm">
                <span className="font-mono text-[#5C5F66]">{String(i + 1).padStart(2, "0")}</span>
                <span>{c.heading}</span>
              </li>
            ))}
          </ol>
        </div>
      </aside>
    </div>
  );
}

function SummaryView({ summary, onGenerate, loading }) {
  return (
    <div data-testid="summary-view">
      {!summary ? (
        <div className="border border-dashed border-[#0F1115] p-12 text-center bg-[#F4F5F2]">
          <Sparkle size={36} weight="duotone" className="mx-auto mb-4 text-[#0022FF]" />
          <h3 className="font-display font-bold text-2xl mb-2">Ainda não gerado</h3>
          <p className="text-sm text-[#5C5F66] mb-6 max-w-md mx-auto">
            Clique abaixo para gerar um resumo completo desse tópico usando IA (Claude Sonnet 4.5).
          </p>
          <button
            onClick={onGenerate}
            disabled={loading}
            data-testid="generate-summary-btn"
            className="bg-[#0022FF] hover:bg-[#0019C0] text-white px-6 py-3 font-mono text-xs uppercase tracking-[0.2em] disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
          >
            {loading ? "Gerando..." : (<>Gerar resumo com IA <Sparkle size={14} /></>)}
          </button>
        </div>
      ) : (
        <div className="border-l-4 border-[#0022FF] bg-[#F4F5F2] p-8" data-testid="summary-content">
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-4 flex items-center justify-between">
            <span>{">>"} Resumo gerado por IA</span>
            <button onClick={onGenerate} disabled={loading} className="hover:text-[#0022FF] disabled:opacity-50" data-testid="regenerate-summary-btn">
              {loading ? "gerando..." : "regenerar ↻"}
            </button>
          </div>
          <div className="summary-content" dangerouslySetInnerHTML={{ __html: markdownToHtml(summary) }} />
        </div>
      )}
    </div>
  );
}

function ExercisesView({ exercises }) {
  if (!exercises.length) return <Empty text="Sem exercícios para este tópico." />;
  const mcq = exercises.filter((e) => e.type === "mcq");
  const open = exercises.filter((e) => e.type === "open");

  return (
    <div className="space-y-10" data-testid="exercises-view">
      {mcq.length > 0 && (
        <div>
          <h2 className="font-display font-bold text-2xl mb-1">Múltipla escolha</h2>
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-6">
            Correção automática · {mcq.length} {mcq.length === 1 ? "questão" : "questões"}
          </div>
          <div className="space-y-6">
            {mcq.map((ex, i) => (
              <MCQCard key={ex.id} exercise={ex} index={i} />
            ))}
          </div>
        </div>
      )}
      {open.length > 0 && (
        <div>
          <h2 className="font-display font-bold text-2xl mb-1">Questões abertas</h2>
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-6">
            Prática livre · confira o gabarito depois
          </div>
          <div className="space-y-6">
            {open.map((ex, i) => (
              <OpenCard key={ex.id} exercise={ex} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MCQCard({ exercise, index }) {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (selected === null) return;
    setLoading(true);
    try {
      const res = await submitAnswer({
        session_id: getSessionId(),
        exercise_id: exercise.id,
        selected_index: selected,
      });
      setResult(res);
    } catch {
      toast.error("Erro ao enviar resposta");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border border-[#0F1115] p-6" data-testid={`mcq-${exercise.id}`}>
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66]">
          Q{String(index + 1).padStart(2, "0")} · {exercise.difficulty}
        </div>
      </div>
      <p className="text-[17px] font-medium mb-6 leading-relaxed">{exercise.question}</p>
      <div className="space-y-2">
        {exercise.options.map((opt, i) => {
          const isSelected = selected === i;
          const isCorrect = result && i === result.correct_index;
          const isWrongPick = result && isSelected && !result.correct;
          let cls = "border-[#E0E2DB] bg-white hover:border-[#0F1115]";
          if (result) {
            if (isCorrect) cls = "border-[#00D65B] bg-[#00D65B] text-white";
            else if (isWrongPick) cls = "border-[#FF3300] bg-[#FF3300] text-white";
            else cls = "border-[#E0E2DB] bg-white opacity-60";
          } else if (isSelected) {
            cls = "border-[#0022FF] bg-blue-50";
          }
          return (
            <button
              key={i}
              onClick={() => !result && setSelected(i)}
              disabled={!!result}
              data-testid={`mcq-option-${exercise.id}-${i}`}
              className={`w-full text-left border p-4 flex items-start gap-4 transition-colors ${cls}`}
            >
              <span className="font-mono text-xs font-semibold w-6">{String.fromCharCode(65 + i)}</span>
              <span className="flex-1 text-sm">{opt}</span>
              {result && isCorrect && <CheckCircle size={20} weight="fill" />}
              {result && isWrongPick && <XCircle size={20} weight="fill" />}
            </button>
          );
        })}
      </div>

      {!result ? (
        <button
          onClick={handleSubmit}
          disabled={selected === null || loading}
          data-testid={`submit-mcq-${exercise.id}`}
          className="mt-6 bg-[#0F1115] text-white hover:bg-[#0022FF] px-5 py-3 font-mono text-xs uppercase tracking-[0.2em] disabled:opacity-40"
        >
          {loading ? "Verificando..." : "Verificar resposta"}
        </button>
      ) : (
        <div className="mt-6 border-l-4 border-[#0F1115] pl-4 py-2 bg-[#F4F5F2]" data-testid={`explanation-${exercise.id}`}>
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
            Explicação
          </div>
          <p className="text-sm leading-relaxed">{result.explanation}</p>
        </div>
      )}
    </div>
  );
}

function OpenCard({ exercise, index }) {
  const [answer, setAnswer] = useState("");
  const [showAnswer, setShowAnswer] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchOpenAnswer(getSessionId(), exercise.id).then((d) => {
      if (d && d.answer_text) {
        setAnswer(d.answer_text);
        setSaved(true);
      }
    }).catch(() => {});
  }, [exercise.id]);

  const handleSave = async () => {
    if (!answer.trim()) return;
    setSaving(true);
    try {
      await saveOpenAnswer({
        session_id: getSessionId(),
        exercise_id: exercise.id,
        answer_text: answer,
      });
      setSaved(true);
      toast.success("Resposta salva");
    } catch {
      toast.error("Erro ao salvar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="border border-[#0F1115] p-6" data-testid={`open-${exercise.id}`}>
      <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-3 flex items-center justify-between">
        <span>Q{String(index + 1).padStart(2, "0")} · Aberta · {exercise.difficulty}</span>
        {saved && <span className="text-[#00D65B]">✓ Salva</span>}
      </div>
      <p className="text-[17px] font-medium mb-4 leading-relaxed">{exercise.question}</p>
      <textarea
        rows={4}
        value={answer}
        onChange={(e) => { setAnswer(e.target.value); setSaved(false); }}
        placeholder="Escreva sua resposta aqui..."
        data-testid={`open-textarea-${exercise.id}`}
        className="w-full border-b-2 border-[#E0E2DB] focus:border-[#0022FF] outline-none py-2 bg-transparent resize-none text-sm"
      />
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={handleSave}
          disabled={saving || !answer.trim()}
          data-testid={`save-open-${exercise.id}`}
          className="font-mono text-xs uppercase tracking-[0.2em] bg-[#0022FF] text-white px-4 py-2 hover:bg-[#0019C0] disabled:opacity-40 transition-colors"
        >
          {saving ? "Salvando..." : saved ? "Salvar novamente" : "Salvar resposta"}
        </button>
        <button
          onClick={() => setShowAnswer((v) => !v)}
          data-testid={`toggle-answer-${exercise.id}`}
          className="font-mono text-xs uppercase tracking-[0.2em] border border-[#0F1115] px-4 py-2 hover:bg-[#0F1115] hover:text-white transition-colors"
        >
          {showAnswer ? "Ocultar gabarito" : "Ver gabarito"}
        </button>
      </div>
      {showAnswer && (
        <div className="mt-4 border-l-4 border-[#0022FF] pl-4 py-2 bg-[#F4F5F2]" data-testid={`open-explanation-${exercise.id}`}>
          <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
            Gabarito comentado
          </div>
          <p className="text-sm leading-relaxed">{exercise.explanation}</p>
        </div>
      )}
    </div>
  );
}

function VideosView({ videos, topic }) {
  if (!videos.length) return <Empty text="Sem vídeos para este tópico." />;
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-testid="videos-view">
      {videos.map((v) => {
        const q = encodeURIComponent(`${topic.title} ${topic.module} aula`);
        const searchUrl = `https://www.youtube.com/results?search_query=${q}`;
        return (
          <a
            key={v.id}
            href={searchUrl}
            target="_blank"
            rel="noopener noreferrer"
            data-testid={`video-${v.id}`}
            className="block border border-[#0F1115] hard-shadow-hover bg-white group"
          >
            <div className="aspect-video bg-gradient-to-br from-[#FF3300] to-[#0022FF] flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 grid-bg opacity-30" />
              <div className="relative w-16 h-16 bg-white flex items-center justify-center rounded-full shadow-2xl group-hover:scale-110 transition-transform">
                <div className="w-0 h-0 border-l-[16px] border-l-[#FF3300] border-y-[10px] border-y-transparent ml-1" />
              </div>
            </div>
            <div className="p-4 border-t border-[#0F1115]">
              <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">
                Buscar no YouTube · {v.duration}
              </div>
              <div className="font-display font-semibold text-base group-hover:text-[#0022FF]">
                {v.title}
              </div>
              <div className="mt-2 font-mono text-[9px] uppercase tracking-[0.2em] text-[#5C5F66]">
                Abre a busca no YouTube →
              </div>
            </div>
          </a>
        );
      })}
    </div>
  );
}

function Empty({ text }) {
  return (
    <div className="border border-dashed border-[#E0E2DB] p-12 text-center">
      <p className="font-mono text-sm text-[#5C5F66]">{text}</p>
    </div>
  );
}

// tiny markdown-ish renderer
function markdownToHtml(md) {
  if (!md) return "";
  let html = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
  html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
  html = html.replace(/^# (.*$)/gim, "<h2>$1</h2>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
  html = html.replace(/`(.+?)`/g, "<code>$1</code>");
  // Lists
  html = html.replace(/(^|\n)([\-\*] .+(?:\n[\-\*] .+)*)/g, (_, pre, block) => {
    const items = block.split(/\n/).map((l) => l.replace(/^[\-\*]\s+/, "").trim());
    return pre + "<ul>" + items.map((i) => `<li>${i}</li>`).join("") + "</ul>";
  });
  // Paragraphs
  html = html.split(/\n{2,}/).map((p) => {
    if (p.startsWith("<h") || p.startsWith("<ul")) return p;
    return `<p>${p.replace(/\n/g, "<br/>")}</p>`;
  }).join("\n");
  return html;
}

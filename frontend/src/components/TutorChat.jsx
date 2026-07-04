import { useState, useRef, useEffect } from "react";
import { ChatCircleDots, X, PaperPlaneRight, Sparkle } from "@phosphor-icons/react";
import { tutorChat } from "../lib/api";
import { getSessionId } from "../lib/session";

export default function TutorChat({ exerciseId, topicId, inline = false }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Oi! Eu sou seu tutor. Me conta onde você travou — não vou dar a resposta pronta, vou te guiar até você chegar nela. Por onde começamos?" },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, open]);

  const send = async () => {
    if (!input.trim() || sending) return;
    const userMsg = { role: "user", content: input.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setSending(true);
    try {
      const res = await tutorChat({
        session_id: getSessionId(),
        exercise_id: exerciseId || null,
        topic_id: topicId || null,
        user_message: userMsg.content,
        history: messages,
      });
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Ops, tive um problema. Tenta de novo?" }]);
    } finally {
      setSending(false);
    }
  };

  const Panel = (
    <div className={`flex flex-col bg-white border border-[#0F1115] ${inline ? "h-[420px]" : "fixed bottom-6 right-6 w-[360px] h-[520px] shadow-2xl z-50"}`} data-testid="tutor-panel">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#0F1115] bg-[#0F1115] text-white">
        <div className="flex items-center gap-2">
          <Sparkle size={16} weight="fill" className="text-[#FFD500]" />
          <span className="font-mono text-xs uppercase tracking-[0.2em]">Tutor · Plantão</span>
        </div>
        {!inline && (
          <button onClick={() => setOpen(false)} data-testid="tutor-close">
            <X size={18} />
          </button>
        )}
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#F4F5F2]">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm ${m.role === "user" ? "text-right" : ""}`}>
            <div className={`inline-block max-w-[85%] px-3 py-2 ${m.role === "user" ? "bg-[#0022FF] text-white" : "bg-white border border-[#E0E2DB]"}`}>
              {m.content}
            </div>
          </div>
        ))}
        {sending && <div className="text-xs text-[#5C5F66] font-mono">tutor digitando…</div>}
      </div>
      <div className="border-t border-[#0F1115] p-2 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Digite sua dúvida..."
          data-testid="tutor-input"
          className="flex-1 border border-[#E0E2DB] px-3 py-2 text-sm outline-none focus:border-[#0022FF]"
        />
        <button
          onClick={send}
          disabled={sending || !input.trim()}
          data-testid="tutor-send"
          className="bg-[#0022FF] text-white px-3 disabled:opacity-40"
        >
          <PaperPlaneRight size={16} weight="fill" />
        </button>
      </div>
    </div>
  );

  if (inline) return Panel;

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          data-testid="tutor-fab"
          className="fixed bottom-6 right-6 z-50 bg-[#0F1115] text-white flex items-center gap-2 px-4 py-3 font-mono text-xs uppercase tracking-[0.2em] hover:bg-[#0022FF] shadow-2xl"
        >
          <ChatCircleDots size={18} weight="fill" /> Tutor IA
        </button>
      )}
      {open && Panel}
    </>
  );
}

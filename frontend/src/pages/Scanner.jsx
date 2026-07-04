import { useState } from "react";
import { Link } from "react-router-dom";
import { Camera, MagnifyingGlass, ArrowRight, Sparkle } from "@phosphor-icons/react";
import { toast } from "sonner";
import { scannerAnalyze } from "../lib/api";

export default function Scanner() {
  const [preview, setPreview] = useState(null);
  const [b64, setB64] = useState(null);
  const [mime, setMime] = useState("image/jpeg");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    setMime(file.type || "image/jpeg");
    const r = new FileReader();
    r.onload = () => {
      setPreview(r.result);
      setB64(r.result);
      setResult(null);
    };
    r.readAsDataURL(file);
  };

  const analyze = async () => {
    if (!b64) return;
    setLoading(true);
    try {
      const res = await scannerAnalyze({ image_base64: b64, mime_type: mime });
      setResult(res);
    } catch {
      toast.error("Falha ao analisar a foto");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 lg:px-10 py-12" data-testid="scanner-page">
      <div className="mb-8">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#5C5F66] mb-2">
          Ferramenta IA
        </div>
        <h1 className="font-heading text-5xl lg:text-6xl">Scanner de Questões</h1>
        <p className="text-lg text-[#5C5F66] mt-3 max-w-2xl">
          Tirou uma foto de um exercício de química do colégio ou cursinho? Envia aqui — a IA identifica o assunto e sugere onde estudar dentro do Estúdio.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <label className="border-2 border-dashed border-[#0F1115] p-8 flex flex-col items-center justify-center bg-[#F4F5F2] cursor-pointer hover:bg-white transition-colors min-h-[300px]" data-testid="scanner-upload">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => handleFile(e.target.files?.[0])}
              className="hidden"
              data-testid="scanner-input"
            />
            {preview ? (
              <img src={preview} alt="preview" className="max-h-72 object-contain" />
            ) : (
              <>
                <Camera size={48} weight="duotone" className="text-[#0022FF] mb-3" />
                <div className="font-display font-bold text-lg">Clique para enviar foto</div>
                <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66] mt-2">
                  jpg · png · webp
                </div>
              </>
            )}
          </label>
          {b64 && (
            <button
              onClick={analyze}
              disabled={loading}
              data-testid="scanner-analyze"
              className="mt-4 w-full bg-[#0022FF] text-white px-5 py-3 font-mono text-xs uppercase tracking-[0.2em] hover:bg-[#0019C0] disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? "Analisando..." : (<><MagnifyingGlass size={16} weight="bold" /> Analisar com IA</>)}
            </button>
          )}
        </div>

        <div>
          {!result ? (
            <div className="border border-dashed border-[#E0E2DB] p-8 text-center h-full flex flex-col justify-center">
              <Sparkle size={32} weight="duotone" className="mx-auto mb-3 text-[#0022FF]" />
              <div className="font-display font-bold text-lg mb-1">Aguardando análise</div>
              <p className="text-sm text-[#5C5F66]">Envie uma foto e clique em Analisar para ver aqui o assunto identificado e sugestões de estudo.</p>
            </div>
          ) : (
            <div className="border border-[#0F1115] p-6 bg-white space-y-4" data-testid="scanner-result">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">Assunto identificado</div>
                <div className="font-display font-bold text-xl">{result.assunto || "—"}</div>
              </div>
              {result.resumo_questao && (
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">Resumo da questão</div>
                  <p className="text-sm">{result.resumo_questao}</p>
                </div>
              )}
              {result.dica && (
                <div className="border-l-4 border-[#FFD500] pl-3 py-2 bg-[#FFFBEC]">
                  <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-1">Dica socrática</div>
                  <p className="text-sm">{result.dica}</p>
                </div>
              )}
              {result.suggested_topics?.length > 0 && (
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66] mb-2">Estude aqui</div>
                  <div className="space-y-2">
                    {result.suggested_topics.map((t) => (
                      <Link
                        key={t.id}
                        to={`/topico/${t.id}`}
                        data-testid={`scanner-suggestion-${t.slug}`}
                        className="flex items-center justify-between border border-[#E0E2DB] p-3 hover:border-[#0F1115] hover:bg-[#F4F5F2] transition-colors"
                      >
                        <div>
                          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66]">{t.module}</div>
                          <div className="font-display font-semibold text-sm">{t.title}</div>
                        </div>
                        <ArrowRight size={16} weight="bold" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}
              {result.raw && (
                <div className="text-xs text-[#5C5F66] whitespace-pre-wrap">{result.raw}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

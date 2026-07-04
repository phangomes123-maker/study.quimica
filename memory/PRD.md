# PRD — Estúdio.Química

## Original Problem Statement
"eu quero fazer uma plataforma de estudo com exercicios, revisao, conteudo, resumo, videos"
Uploaded artifacts: 3 PDFs on Cinética Química + 2 PDFs on Eletroquímica.

## User Choices
- Scope: focused only on **Química** (Chemistry)
- Content generation: **AI (Claude Sonnet 4.5 via Emergent LLM Key) + manual seed content**
- Videos: **YouTube embeds**
- Authentication: **none** (public, anonymous session tracked via localStorage)
- Exercises: **MCQ with auto-grading & progress + open questions with gabarito**

## Architecture
- **Backend**: FastAPI + MongoDB (Motor). Routes under `/api`. Auto-seeds DB with 5 topics, 15 content sections, 7 videos, 15 exercises. LLM via `emergentintegrations.LlmChat` (`anthropic/claude-sonnet-4-5-20250929`).
- **Frontend**: React + Tailwind + shadcn primitives. Routes: `/`, `/topicos`, `/topico/:id`, `/revisao`, `/progresso`. Phosphor icons. Fraunces (headings) + IBM Plex Sans (body) + IBM Plex Mono (labels).
- **Session**: anonymous `sess_xxx` stored in localStorage → drives progress + revision.
- **Design**: Swiss / Lab Minimalist — white background, ink black text, Klein Blue (#0022FF) + Acid Yellow (#FFD500) accents, sharp 1px borders, hard shadows on hover.

## Implemented (2026-02-04)
- Auto-seeding of 5 topics (Cinética 3 + Eletroquímica 2), including didactic Portuguese content, MCQ + open questions with explanations, YouTube references.
- Home with hero + ticker + features + topics grid.
- Topics index with module filter.
- Topic detail with 4 tabs: Conteúdo, Resumo IA (on-demand), Exercícios (MCQ + Aberta), Vídeos.
- MCQ auto-grading with green/red feedback + explanation card.
- Revision mode (`/revisao`) that returns wrongly-answered questions and cycles through them.
- Progress dashboard (`/progresso`) with total/correct/accuracy + per-topic bars.
- AI summary generation via Claude Sonnet 4.5 with markdown-lite renderer.

## Implemented (Iteration 2 - 2026-02-04)
- Expanded content: **5 new topics** → total 10 topics.
  - Eletroquímica: Tabela de Potenciais Padrão + Eletrólise Ígnea/Aquosa (com Leis de Faraday).
  - Equilíbrio Químico: Introdução, Constante Kc/Kp, Cálculos de K + Le Chatelier.
- Seed idempotente por slug (preserva progresso e respostas existentes).
- **Persistência de respostas abertas**:
  - `POST /api/open-answers` (upsert por session+exercise).
  - `GET /api/open-answers/{session_id}` para listar.
  - `GET /api/open-answers/{session_id}/exercise/{exercise_id}` para pré-carregar.
- OpenCard agora carrega resposta salva ao abrir e mostra badge "✓ Salva".
- Página `/progresso` traz nova seção "Minhas respostas abertas" com question + sua resposta + gabarito colapsável.

## User Personas
- Estudante de ensino médio ou pré-vestibular brasileiro estudando química (foco em vestibulares como ENEM, FUVEST).

## Backlog / Next
- P1: Expand content beyond current 5 topics (add more from PDFs like tabelas de potencial, eletrólise, cinética avançada).
- P1: Persist open-question answers for teacher review.
- P2: PDF export of summary; dark theme; add other subjects (Física, Biologia) if user requests.
- P2: Streak/gamification (dias seguidos estudando).
- P3: Google Auth (Emergent) to save progress across devices.

## Testing
Iteration 1: /app/test_reports/iteration_1.json — 100% pass on backend + frontend.

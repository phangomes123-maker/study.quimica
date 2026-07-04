from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone

from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ============ MODELS ============
class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    title: str
    subject: str = "Química"
    module: str  # e.g. "Cinética", "Eletroquímica"
    order: int
    description: str
    icon: str = "flask"  # phosphor icon name
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Content(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    heading: str
    body: str  # markdown-like text
    order: int = 0


class Video(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    title: str
    youtube_id: str
    channel: str = ""
    duration: str = ""
    order: int = 0


class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    question: str
    type: Literal["mcq", "open"] = "mcq"
    options: List[str] = []
    correct_index: Optional[int] = None
    explanation: str = ""
    difficulty: Literal["fácil", "médio", "difícil"] = "médio"


class Summary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    content: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProgressEntry(BaseModel):
    session_id: str
    exercise_id: str
    topic_id: str
    correct: bool
    selected_index: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AnswerRequest(BaseModel):
    session_id: str
    exercise_id: str
    selected_index: Optional[int] = None
    answer_text: Optional[str] = None


# ============ SEED DATA ============
SEED_TOPICS = [
    {
        "slug": "cinetica-velocidade-media",
        "title": "Velocidade Média, Teoria das Colisões e Lei da Velocidade",
        "module": "Cinética Química",
        "order": 1,
        "description": "Introdução à cinética química: como medimos a velocidade das reações, a teoria das colisões e os fatores que afetam a velocidade.",
        "icon": "gauge",
    },
    {
        "slug": "cinetica-leis-velocidade",
        "title": "Leis de Velocidade",
        "module": "Cinética Química",
        "order": 2,
        "description": "Ordem de reação, constante de velocidade e determinação experimental das leis cinéticas.",
        "icon": "chart-line",
    },
    {
        "slug": "cinetica-mecanismo-arrhenius",
        "title": "Mecanismo, Etapas Elementares e Equação de Arrhenius",
        "module": "Cinética Química",
        "order": 3,
        "description": "Etapas elementares, molecularidade, energia de ativação e a equação de Arrhenius.",
        "icon": "atom",
    },
    {
        "slug": "eletroquimica-nox-redox",
        "title": "NOX, Agentes Redutores e Oxidantes",
        "module": "Eletroquímica",
        "order": 4,
        "description": "Número de oxidação, balanceamento de reações redox e identificação de agentes redutores e oxidantes.",
        "icon": "lightning",
    },
    {
        "slug": "eletroquimica-celulas-voltaicas",
        "title": "Células Voltaicas (Pilhas)",
        "module": "Eletroquímica",
        "order": 5,
        "description": "Funcionamento de pilhas galvânicas, potenciais padrão, ponte salina e força eletromotriz.",
        "icon": "battery-charging",
    },
]

SEED_CONTENT = {
    "cinetica-velocidade-media": [
        {"heading": "O que é Cinética Química?",
         "body": "A cinética química é o ramo da química que estuda a velocidade das reações e os fatores que a influenciam. Diferente da termodinâmica, que diz se uma reação é possível, a cinética diz **com que rapidez** ela acontece."},
        {"heading": "Velocidade Média de Reação",
         "body": "A velocidade média é definida pela variação da concentração de reagentes ou produtos em um intervalo de tempo:\n\nv = |Δ[X]| / Δt\n\nOnde Δ[X] é a variação de concentração (mol/L) e Δt é o intervalo de tempo (s). Para reagentes usamos o módulo pois a concentração diminui."},
        {"heading": "Teoria das Colisões",
         "body": "Para que uma reação ocorra, é necessário que:\n\n1. As partículas colidam entre si.\n2. A colisão tenha energia igual ou superior à energia de ativação (Ea).\n3. A colisão ocorra em uma **orientação favorável**.\n\nColisões que atendem essas condições são chamadas de **colisões efetivas**."},
        {"heading": "Fatores que Afetam a Velocidade",
         "body": "- **Concentração**: maior concentração → mais colisões → maior velocidade.\n- **Temperatura**: aumenta a energia cinética das partículas.\n- **Superfície de contato**: quanto maior, mais colisões.\n- **Catalisador**: diminui a energia de ativação, acelerando a reação.\n- **Pressão** (gases): maior pressão → maior concentração."},
    ],
    "cinetica-leis-velocidade": [
        {"heading": "Lei da Velocidade",
         "body": "A lei da velocidade relaciona a velocidade de uma reação com a concentração dos reagentes:\n\nv = k · [A]^m · [B]^n\n\nOnde k é a constante de velocidade, e m, n são as ordens de reação em relação a A e B. A soma m + n é a **ordem global**."},
        {"heading": "Ordem de Reação",
         "body": "A ordem NÃO é determinada pelos coeficientes estequiométricos, mas sim **experimentalmente**. Pode ser 0, 1, 2 ou até fracionária."},
        {"heading": "Determinação Experimental",
         "body": "Pelo método das velocidades iniciais: variam-se as concentrações dos reagentes e observa-se como a velocidade muda. Se dobrar [A] dobra v → ordem 1 em A. Se dobrar [A] quadruplica v → ordem 2 em A."},
    ],
    "cinetica-mecanismo-arrhenius": [
        {"heading": "Etapas Elementares",
         "body": "A maioria das reações ocorre em várias etapas chamadas **etapas elementares**. A etapa mais lenta é a **etapa determinante da velocidade**."},
        {"heading": "Molecularidade",
         "body": "Número de espécies que colidem em uma etapa elementar: unimolecular (1), bimolecular (2), termolecular (3, rara)."},
        {"heading": "Equação de Arrhenius",
         "body": "Relaciona a constante de velocidade com a temperatura:\n\nk = A · e^(-Ea/RT)\n\nOnde A é o fator de frequência, Ea é a energia de ativação, R é a constante dos gases e T a temperatura em Kelvin. Aumentar T aumenta k exponencialmente."},
    ],
    "eletroquimica-nox-redox": [
        {"heading": "Número de Oxidação (NOX)",
         "body": "É a carga elétrica que um átomo teria se todas as ligações fossem iônicas. Regras principais:\n\n- Substância simples: NOX = 0\n- Íon monoatômico: NOX = carga do íon\n- H: geralmente +1 (com metais: -1)\n- O: geralmente -2 (peróxidos: -1)"},
        {"heading": "Oxidação e Redução",
         "body": "- **Oxidação**: perde elétrons → NOX aumenta.\n- **Redução**: ganha elétrons → NOX diminui.\n\nUse o macete: **PERDOX** (PERdeu elétrons → OXidou) e **GARED** (GAnhou → REDuziu)."},
        {"heading": "Agentes Oxidantes e Redutores",
         "body": "- **Agente oxidante**: espécie que **sofre redução** (causa oxidação em outra).\n- **Agente redutor**: espécie que **sofre oxidação** (causa redução em outra)."},
    ],
    "eletroquimica-celulas-voltaicas": [
        {"heading": "Pilha Galvânica",
         "body": "Uma pilha (célula voltaica) converte energia química em elétrica de maneira espontânea através de uma reação redox. Tem dois eletrodos separados, conectados por um fio e uma ponte salina."},
        {"heading": "Ânodo e Cátodo",
         "body": "- **Ânodo**: eletrodo onde ocorre **oxidação** (polo negativo em pilhas).\n- **Cátodo**: eletrodo onde ocorre **redução** (polo positivo em pilhas).\n\nOs elétrons fluem pelo fio externo do ânodo para o cátodo."},
        {"heading": "Potencial Padrão (ΔE°)",
         "body": "ΔE° = E°(cátodo) − E°(ânodo)\n\nSe ΔE° > 0, a reação é espontânea. Valores tabelados em condições padrão (25°C, 1 mol/L, 1 atm)."},
        {"heading": "Ponte Salina",
         "body": "Contém eletrólito inerte (ex: KNO₃) e serve para manter a neutralidade elétrica das soluções, permitindo o fluxo de íons entre os eletrodos."},
    ],
}

SEED_VIDEOS = {
    "cinetica-velocidade-media": [
        {"title": "Cinética Química - Introdução e Velocidade Média", "youtube_id": "n8xLVXn2FCQ", "channel": "Professor Boaro", "duration": "12:34"},
        {"title": "Teoria das Colisões", "youtube_id": "5Gk9lrxbAKY", "channel": "Química em Ação", "duration": "08:20"},
    ],
    "cinetica-leis-velocidade": [
        {"title": "Lei de Velocidade e Ordem de Reação", "youtube_id": "wYqQxTZg8fw", "channel": "Professor Boaro", "duration": "15:10"},
    ],
    "cinetica-mecanismo-arrhenius": [
        {"title": "Equação de Arrhenius Explicada", "youtube_id": "kZQYQxaupHk", "channel": "Química em Ação", "duration": "11:45"},
    ],
    "eletroquimica-nox-redox": [
        {"title": "NOX - Número de Oxidação", "youtube_id": "3sN4o9c9Vqc", "channel": "Professor Boaro", "duration": "14:22"},
        {"title": "Balanceamento Redox passo a passo", "youtube_id": "n4mV5Q5uw3E", "channel": "Química em Ação", "duration": "18:05"},
    ],
    "eletroquimica-celulas-voltaicas": [
        {"title": "Pilhas Galvânicas - Funcionamento", "youtube_id": "8vG7XZKZ9G0", "channel": "Professor Boaro", "duration": "16:40"},
    ],
}

SEED_EXERCISES = {
    "cinetica-velocidade-media": [
        {"question": "Em uma reação, a concentração de um reagente cai de 0,80 mol/L para 0,20 mol/L em 30 segundos. Qual a velocidade média de consumo desse reagente?",
         "type": "mcq",
         "options": ["0,010 mol/L·s", "0,020 mol/L·s", "0,030 mol/L·s", "0,060 mol/L·s"],
         "correct_index": 1,
         "explanation": "v = |Δ[X]|/Δt = |0,20 − 0,80|/30 = 0,60/30 = 0,020 mol/L·s.",
         "difficulty": "fácil"},
        {"question": "Segundo a teoria das colisões, para uma reação ocorrer é NECESSÁRIO que a colisão:",
         "type": "mcq",
         "options": ["Seja apenas frequente", "Tenha energia mínima e orientação adequada", "Ocorra apenas em altas pressões", "Envolva sempre catalisador"],
         "correct_index": 1,
         "explanation": "Colisões efetivas exigem energia ≥ Ea e orientação favorável.",
         "difficulty": "fácil"},
        {"question": "Qual dos fatores NÃO afeta a velocidade de uma reação química?",
         "type": "mcq",
         "options": ["Temperatura", "Concentração dos reagentes", "Presença de catalisador", "Cor do recipiente"],
         "correct_index": 3,
         "explanation": "A cor do recipiente é irrelevante para a cinética da reação.",
         "difficulty": "fácil"},
        {"question": "Explique com suas palavras por que aumentar a superfície de contato de um reagente sólido aumenta a velocidade da reação.",
         "type": "open",
         "options": [],
         "correct_index": None,
         "explanation": "Ao aumentar a superfície, mais partículas ficam disponíveis para colidir com o outro reagente, aumentando o número de colisões efetivas por segundo.",
         "difficulty": "médio"},
    ],
    "cinetica-leis-velocidade": [
        {"question": "Para a reação A + B → C, dobrar [A] mantendo [B] constante quadruplica a velocidade. Qual a ordem em relação a A?",
         "type": "mcq",
         "options": ["0", "1", "2", "3"],
         "correct_index": 2,
         "explanation": "Se dobrar [A] (fator 2) faz v aumentar 4 vezes (2²), a ordem é 2.",
         "difficulty": "médio"},
        {"question": "A lei da velocidade v = k[A][B]² tem ordem global igual a:",
         "type": "mcq",
         "options": ["1", "2", "3", "4"],
         "correct_index": 2,
         "explanation": "Ordem global = 1 + 2 = 3.",
         "difficulty": "fácil"},
        {"question": "A ordem de reação é sempre determinada pelos coeficientes estequiométricos da equação balanceada. Verdadeiro ou falso? Justifique.",
         "type": "open",
         "options": [],
         "correct_index": None,
         "explanation": "Falso. A ordem é determinada experimentalmente, e pode não coincidir com os coeficientes.",
         "difficulty": "médio"},
    ],
    "cinetica-mecanismo-arrhenius": [
        {"question": "Segundo a equação de Arrhenius, quando a temperatura aumenta, a constante de velocidade k:",
         "type": "mcq",
         "options": ["Diminui linearmente", "Aumenta exponencialmente", "Permanece constante", "Diminui exponencialmente"],
         "correct_index": 1,
         "explanation": "k = A·e^(-Ea/RT). Como Ea/RT diminui com T maior, o expoente fica menos negativo e k cresce exponencialmente.",
         "difficulty": "médio"},
        {"question": "Em um mecanismo com múltiplas etapas, qual determina a velocidade global da reação?",
         "type": "mcq",
         "options": ["A etapa mais rápida", "A etapa mais lenta", "A média das etapas", "A última etapa"],
         "correct_index": 1,
         "explanation": "A etapa lenta é chamada etapa determinante da velocidade.",
         "difficulty": "fácil"},
    ],
    "eletroquimica-nox-redox": [
        {"question": "Qual o NOX do enxofre no H₂SO₄?",
         "type": "mcq",
         "options": ["+2", "+4", "+6", "-2"],
         "correct_index": 2,
         "explanation": "2(+1) + S + 4(-2) = 0 → S = +6.",
         "difficulty": "médio"},
        {"question": "Em uma reação redox, o agente oxidante é a espécie que:",
         "type": "mcq",
         "options": ["Sofre oxidação", "Sofre redução", "Não muda de NOX", "Perde elétrons"],
         "correct_index": 1,
         "explanation": "O agente oxidante ganha elétrons (sofre redução) e faz outro se oxidar.",
         "difficulty": "fácil"},
        {"question": "Identifique o agente redutor e o agente oxidante em: Zn + Cu²⁺ → Zn²⁺ + Cu",
         "type": "open",
         "options": [],
         "correct_index": None,
         "explanation": "Zn passa de 0 para +2 (oxida) → agente redutor. Cu²⁺ passa de +2 para 0 (reduz) → agente oxidante.",
         "difficulty": "médio"},
    ],
    "eletroquimica-celulas-voltaicas": [
        {"question": "Em uma pilha galvânica, no ânodo ocorre:",
         "type": "mcq",
         "options": ["Redução, é o polo positivo", "Oxidação, é o polo negativo", "Redução, é o polo negativo", "Oxidação, é o polo positivo"],
         "correct_index": 1,
         "explanation": "Ânodo = oxidação = polo negativo (fonte de elétrons).",
         "difficulty": "fácil"},
        {"question": "A ponte salina em uma pilha serve para:",
         "type": "mcq",
         "options": ["Aumentar a corrente", "Manter a neutralidade elétrica das soluções", "Isolar os eletrodos", "Aumentar a diferença de potencial"],
         "correct_index": 1,
         "explanation": "A ponte salina permite o fluxo de íons entre as duas semi-células, mantendo a neutralidade.",
         "difficulty": "médio"},
        {"question": "Dados E°(Zn²⁺/Zn) = -0,76 V e E°(Cu²⁺/Cu) = +0,34 V, qual o ΔE° da pilha Zn|Cu?",
         "type": "mcq",
         "options": ["+0,42 V", "+1,10 V", "-1,10 V", "-0,42 V"],
         "correct_index": 1,
         "explanation": "ΔE° = E°(cátodo) - E°(ânodo) = 0,34 - (-0,76) = 1,10 V.",
         "difficulty": "difícil"},
    ],
}


async def seed_database():
    """Seed the database if empty."""
    existing = await db.topics.count_documents({})
    if existing > 0:
        return

    logger.info("Seeding database with chemistry topics...")
    topic_id_by_slug = {}

    for t in SEED_TOPICS:
        topic = Topic(**t)
        await db.topics.insert_one(topic.model_dump())
        topic_id_by_slug[t["slug"]] = topic.id

    for slug, contents in SEED_CONTENT.items():
        tid = topic_id_by_slug[slug]
        for i, c in enumerate(contents):
            content = Content(topic_id=tid, order=i, **c)
            await db.contents.insert_one(content.model_dump())

    for slug, videos in SEED_VIDEOS.items():
        tid = topic_id_by_slug[slug]
        for i, v in enumerate(videos):
            video = Video(topic_id=tid, order=i, **v)
            await db.videos.insert_one(video.model_dump())

    for slug, exs in SEED_EXERCISES.items():
        tid = topic_id_by_slug[slug]
        for e in exs:
            ex = Exercise(topic_id=tid, **e)
            await db.exercises.insert_one(ex.model_dump())

    logger.info("Database seeded successfully.")


# ============ ROUTES ============
@api_router.get("/")
async def root():
    return {"message": "Plataforma de Estudos - Química", "status": "ok"}


@api_router.get("/topics", response_model=List[Topic])
async def list_topics():
    docs = await db.topics.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [Topic(**d) for d in docs]


@api_router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic(topic_id: str):
    doc = await db.topics.find_one({"id": topic_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Topic not found")
    return Topic(**doc)


@api_router.get("/topics/{topic_id}/content", response_model=List[Content])
async def get_content(topic_id: str):
    docs = await db.contents.find({"topic_id": topic_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return [Content(**d) for d in docs]


@api_router.get("/topics/{topic_id}/videos", response_model=List[Video])
async def get_videos(topic_id: str):
    docs = await db.videos.find({"topic_id": topic_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return [Video(**d) for d in docs]


@api_router.get("/topics/{topic_id}/exercises", response_model=List[Exercise])
async def get_exercises(topic_id: str):
    docs = await db.exercises.find({"topic_id": topic_id}, {"_id": 0}).to_list(100)
    return [Exercise(**d) for d in docs]


@api_router.get("/topics/{topic_id}/summary")
async def get_summary(topic_id: str):
    doc = await db.summaries.find_one({"topic_id": topic_id}, {"_id": 0})
    if not doc:
        return {"exists": False, "content": None}
    return {"exists": True, "content": doc["content"], "generated_at": doc.get("generated_at")}


@api_router.post("/topics/{topic_id}/summary/generate")
async def generate_summary(topic_id: str):
    topic_doc = await db.topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic_doc:
        raise HTTPException(404, "Topic not found")

    content_docs = await db.contents.find({"topic_id": topic_id}, {"_id": 0}).sort("order", 1).to_list(100)
    if not content_docs:
        raise HTTPException(404, "No content to summarize")

    joined = "\n\n".join([f"## {c['heading']}\n{c['body']}" for c in content_docs])

    system = (
        "Você é um professor de Química brasileiro especializado em criar resumos didáticos claros "
        "e concisos para alunos do ensino médio e pré-vestibular. Responda sempre em português (pt-BR). "
        "Use markdown simples com títulos ##, bullet points e negritos onde ajudar."
    )

    prompt = (
        f"Crie um resumo focado e didático do tópico '{topic_doc['title']}' baseado no conteúdo abaixo. "
        f"O resumo deve ter: (1) definição principal em 2 linhas, (2) pontos-chave em bullets, "
        f"(3) fórmulas importantes destacadas, (4) uma dica final de memorização/macete.\n\n"
        f"CONTEÚDO:\n{joined}"
    )

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"summary-{topic_id}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        response = await chat.send_message(UserMessage(text=prompt))
        summary_text = response if isinstance(response, str) else str(response)
    except Exception as e:
        logger.exception("LLM generation failed")
        raise HTTPException(500, f"Falha ao gerar resumo: {str(e)}")

    # Upsert
    await db.summaries.delete_many({"topic_id": topic_id})
    summary = Summary(topic_id=topic_id, content=summary_text)
    await db.summaries.insert_one(summary.model_dump())

    return {"content": summary_text, "generated_at": summary.generated_at}


@api_router.post("/exercises/answer")
async def submit_answer(req: AnswerRequest):
    ex_doc = await db.exercises.find_one({"id": req.exercise_id}, {"_id": 0})
    if not ex_doc:
        raise HTTPException(404, "Exercise not found")

    ex = Exercise(**ex_doc)
    correct = False
    if ex.type == "mcq" and req.selected_index is not None:
        correct = (req.selected_index == ex.correct_index)

    entry = ProgressEntry(
        session_id=req.session_id,
        exercise_id=req.exercise_id,
        topic_id=ex.topic_id,
        correct=correct,
        selected_index=req.selected_index,
    )
    await db.progress.insert_one(entry.model_dump())

    return {
        "correct": correct,
        "correct_index": ex.correct_index,
        "explanation": ex.explanation,
    }


@api_router.get("/progress/{session_id}")
async def get_progress(session_id: str):
    docs = await db.progress.find({"session_id": session_id}, {"_id": 0}).to_list(1000)
    total = len(docs)
    correct = sum(1 for d in docs if d["correct"])

    # per topic breakdown
    per_topic = {}
    for d in docs:
        tid = d["topic_id"]
        if tid not in per_topic:
            per_topic[tid] = {"total": 0, "correct": 0}
        per_topic[tid]["total"] += 1
        if d["correct"]:
            per_topic[tid]["correct"] += 1

    return {
        "session_id": session_id,
        "total": total,
        "correct": correct,
        "accuracy": (correct / total * 100) if total else 0,
        "per_topic": per_topic,
    }


@api_router.get("/revision/questions")
async def revision_questions(session_id: str, limit: int = 10):
    """Returns questions the user got wrong (for revision mode)."""
    wrong = await db.progress.find(
        {"session_id": session_id, "correct": False}, {"_id": 0}
    ).to_list(1000)
    ex_ids = list({w["exercise_id"] for w in wrong})[:limit]
    if not ex_ids:
        # fallback: random mix
        exs = await db.exercises.find({}, {"_id": 0}).limit(limit).to_list(limit)
    else:
        exs = await db.exercises.find({"id": {"$in": ex_ids}}, {"_id": 0}).to_list(limit)
    return [Exercise(**e) for e in exs]


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    await seed_database()


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

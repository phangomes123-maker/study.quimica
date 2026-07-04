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

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent


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


class OpenAnswer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    exercise_id: str
    topic_id: str
    question: str
    answer_text: str
    gabarito: str
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OpenAnswerRequest(BaseModel):
    session_id: str
    exercise_id: str
    answer_text: str


class TutorMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TutorChatRequest(BaseModel):
    session_id: str
    exercise_id: Optional[str] = None
    topic_id: Optional[str] = None
    user_message: str
    history: List[TutorMessage] = []


class ScannerRequest(BaseModel):
    image_base64: str  # data URL or plain base64
    mime_type: str = "image/jpeg"


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
    {
        "slug": "eletroquimica-tabela-potenciais",
        "title": "Tabela de Potenciais Padrão de Redução",
        "module": "Eletroquímica",
        "order": 6,
        "description": "Como ler e usar a tabela de potenciais padrão para prever espontaneidade, força de oxidantes/redutores e calcular ΔE°.",
        "icon": "gauge",
    },
    {
        "slug": "eletroquimica-eletrolise",
        "title": "Eletrólise Ígnea e Aquosa",
        "module": "Eletroquímica",
        "order": 7,
        "description": "Processos não-espontâneos: eletrólise, prioridade de descarga, leis de Faraday e aplicações industriais.",
        "icon": "lightning",
    },
    {
        "slug": "equilibrio-introducao",
        "title": "Introdução ao Equilíbrio Químico",
        "module": "Equilíbrio Químico",
        "order": 8,
        "description": "Reações reversíveis, equilíbrio dinâmico e as características do estado de equilíbrio.",
        "icon": "atom",
    },
    {
        "slug": "equilibrio-constante",
        "title": "Constante de Equilíbrio (Kc e Kp)",
        "module": "Equilíbrio Químico",
        "order": 9,
        "description": "Lei da ação das massas, Kc, Kp, relação entre eles e o significado dos valores.",
        "icon": "chart-line",
    },
    {
        "slug": "equilibrio-calculos-k",
        "title": "Cálculos de K e Princípio de Le Chatelier",
        "module": "Equilíbrio Químico",
        "order": 10,
        "description": "Como calcular K a partir de concentrações, quociente Q vs K, e o deslocamento de equilíbrio segundo Le Chatelier.",
        "icon": "flask",
    },
    {
        "slug": "termoquimica-entalpia",
        "title": "Entalpia e Reações Exo/Endotérmicas",
        "module": "Termoquímica",
        "order": 11,
        "description": "Calor de reação, variação de entalpia (ΔH), reações exotérmicas e endotérmicas, diagramas de energia.",
        "icon": "flask",
    },
    {
        "slug": "termoquimica-lei-hess",
        "title": "Lei de Hess e Entalpias Padrão",
        "module": "Termoquímica",
        "order": 12,
        "description": "Lei de Hess, entalpia de formação, combustão, ligação e como somar equações para achar ΔH.",
        "icon": "chart-line",
    },
    {
        "slug": "termoquimica-entropia-gibbs",
        "title": "Entropia e Energia Livre de Gibbs",
        "module": "Termoquímica",
        "order": 13,
        "description": "2ª lei da termodinâmica, entropia (ΔS), energia livre de Gibbs (ΔG) e critério de espontaneidade.",
        "icon": "atom",
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
    "eletroquimica-tabela-potenciais": [
        {"heading": "O que é a tabela?",
         "body": "É a lista de potenciais padrão de **redução** (E°red) de cada semi-reação, medidos em relação ao eletrodo padrão de hidrogênio (E° = 0,00 V), a 25°C, 1 mol/L, 1 atm."},
        {"heading": "Interpretação",
         "body": "- Quanto **maior** o E°red → maior tendência de **sofrer redução** → melhor **agente oxidante**.\n- Quanto **menor** (mais negativo) o E°red → maior tendência de **sofrer oxidação** → melhor **agente redutor**.\n\nExemplos:\n- F₂/F⁻ = +2,87 V (melhor oxidante)\n- Li⁺/Li = -3,04 V (melhor redutor)"},
        {"heading": "Calculando ΔE° da pilha",
         "body": "ΔE° = E°(cátodo) − E°(ânodo)\n\nO cátodo é a semi-reação de **maior** E°red (sofre redução) e o ânodo é a de **menor** E°red (sofre oxidação, escrita invertida).\n\nSe ΔE° > 0 → espontânea (pilha). Se ΔE° < 0 → não espontânea (precisa de eletrólise)."},
        {"heading": "Previsão de reações",
         "body": "Um metal só desloca outro que esteja **acima** dele na fila de reatividade (potencial mais positivo). Ex: Zn desloca Cu²⁺, mas Cu não desloca Zn²⁺."},
    ],
    "eletroquimica-eletrolise": [
        {"heading": "O que é Eletrólise?",
         "body": "Processo **não-espontâneo** (ΔE° < 0) em que se usa **corrente elétrica externa** para forçar uma reação redox. Inversa da pilha: converte energia elétrica em química."},
        {"heading": "Ígnea vs Aquosa",
         "body": "- **Ígnea**: composto fundido, sem água. Só há cátions e ânions do composto. Ex: NaCl fundido → Na (cátodo) + Cl₂ (ânodo).\n- **Aquosa**: composto em solução. Água também pode reagir; obedece à **prioridade de descarga**."},
        {"heading": "Prioridade de Descarga (aquosa)",
         "body": "Cátions (descarregam no cátodo):\n1º Metais nobres (Cu, Ag, Au...) e H⁺\n2º H⁺ da água (se cátion for alcalino, alcalino-terroso ou Al³⁺)\n\nÂnions (descarregam no ânodo):\n1º Não-oxigenados (Cl⁻, Br⁻, I⁻) e OH⁻\n2º OH⁻ da água (se ânion for oxigenado como SO₄²⁻, NO₃⁻)"},
        {"heading": "Leis de Faraday",
         "body": "1ª lei: **m = (M · i · t) / (n · F)**\n\nOnde m = massa depositada, M = massa molar, i = corrente (A), t = tempo (s), n = nº de elétrons, F = constante de Faraday = 96500 C/mol.\n\n2ª lei: para mesma carga, massas depositadas são proporcionais aos equivalentes-grama."},
        {"heading": "Aplicações",
         "body": "- Obtenção de Al metálico (processo Hall-Héroult).\n- Refino eletrolítico de Cu.\n- Galvanoplastia (cromagem, prateação).\n- Produção de Cl₂ e NaOH (eletrólise da salmoura)."},
    ],
    "equilibrio-introducao": [
        {"heading": "Reações Reversíveis",
         "body": "Muitas reações ocorrem nos **dois sentidos** ao mesmo tempo: produtos podem reagir de volta formando reagentes. Representamos por ⇌.\n\nEx: N₂ + 3H₂ ⇌ 2NH₃"},
        {"heading": "Equilíbrio Dinâmico",
         "body": "O equilíbrio é atingido quando a **velocidade da reação direta = velocidade da reação inversa**. As concentrações **param de mudar**, mas ambas as reações continuam ocorrendo (dinâmico, não estático)."},
        {"heading": "Características do Equilíbrio",
         "body": "- Sistema **fechado** (sem troca de matéria com o meio).\n- Concentrações constantes (não iguais, apenas constantes).\n- Ocorre em **qualquer temperatura** (mas o valor de K depende dela).\n- É atingido por ambos os lados (partindo de reagentes ou de produtos)."},
    ],
    "equilibrio-constante": [
        {"heading": "Lei da Ação das Massas",
         "body": "Para uma reação genérica: aA + bB ⇌ cC + dD\n\nA constante de equilíbrio é:\n\n**Kc = ([C]^c · [D]^d) / ([A]^a · [B]^b)**\n\nSempre **produtos sobre reagentes**, elevados aos coeficientes estequiométricos. Sólidos e líquidos puros **não entram** na expressão."},
        {"heading": "Kp para Gases",
         "body": "Quando os participantes são gasosos, usa-se pressão parcial:\n\n**Kp = (P_C^c · P_D^d) / (P_A^a · P_B^b)**\n\nRelação com Kc:\n\n**Kp = Kc · (RT)^Δn**\n\nOnde Δn = (mols de gás produtos) − (mols de gás reagentes)."},
        {"heading": "Interpretando o Valor de K",
         "body": "- **K >> 1**: equilíbrio deslocado para produtos (reação favorece produtos).\n- **K << 1**: equilíbrio deslocado para reagentes.\n- **K ≈ 1**: quantidades comparáveis de reagentes e produtos.\n\nK depende **apenas da temperatura**; não muda com concentração, pressão ou catalisador."},
    ],
    "equilibrio-calculos-k": [
        {"heading": "Calculando K",
         "body": "Passos:\n1. Escreva a expressão de K.\n2. Monte a **tabela ICE** (Início, Change/Variação, Equilíbrio) com concentrações.\n3. Substitua os valores no equilíbrio.\n\nEx: H₂ + I₂ ⇌ 2HI, com [H₂]eq = 0,2, [I₂]eq = 0,2 e [HI]eq = 1,6 → Kc = (1,6)²/(0,2·0,2) = 64."},
        {"heading": "Quociente Q vs K",
         "body": "Q é calculado com concentrações **fora do equilíbrio** (mesmo formato de K).\n\n- **Q < K**: reação avança para direita (produtos).\n- **Q > K**: reação retrocede (reagentes).\n- **Q = K**: sistema em equilíbrio."},
        {"heading": "Princípio de Le Chatelier",
         "body": "Se um sistema em equilíbrio sofrer perturbação, ele se desloca no sentido que **minimize** essa perturbação.\n\n- **↑ Concentração** de A → equilíbrio se desloca para consumi-la (direita).\n- **↑ Pressão** → desloca para o lado com **menos** mols de gás.\n- **↑ Temperatura** (endotérmica) → desloca para direita; se exotérmica, para esquerda.\n- **Catalisador** não desloca o equilíbrio, só acelera para atingi-lo."},
    ],
    "termoquimica-entalpia": [
        {"heading": "O que é Termoquímica?",
         "body": "Estuda o **calor** trocado durante reações químicas e mudanças de estado. O calor a pressão constante é chamado **variação de entalpia (ΔH)**."},
        {"heading": "Exotérmica vs Endotérmica",
         "body": "- **Exotérmica**: libera calor → ΔH < 0. Ex: combustão, respiração. Produtos têm menos energia que reagentes.\n- **Endotérmica**: absorve calor → ΔH > 0. Ex: fotossíntese, cozimento. Produtos têm mais energia que reagentes."},
        {"heading": "Cálculo de ΔH",
         "body": "ΔH = H(produtos) − H(reagentes)\n\nUnidade: kJ/mol. É medido experimentalmente em um **calorímetro**. Também pode ser calculado por:\n\nq = m · c · ΔT\n\nOnde q = calor, m = massa, c = calor específico, ΔT = variação de temperatura."},
        {"heading": "Diagramas de Energia",
         "body": "Gráfico H vs caminho da reação. **Exotérmica**: produtos abaixo dos reagentes. **Endotérmica**: produtos acima. O 'morro' entre eles é a **energia de ativação (Ea)**."},
    ],
    "termoquimica-lei-hess": [
        {"heading": "Lei de Hess",
         "body": "O **ΔH total de uma reação é independente do caminho** — depende apenas dos estados inicial e final.\n\nIsso permite calcular ΔH somando equações intermediárias (com seus ΔH), como um quebra-cabeça."},
        {"heading": "Regras de Manipulação",
         "body": "- Se **inverter** a equação → **inverter o sinal** de ΔH.\n- Se **multiplicar** por um fator → **multiplicar ΔH** pelo mesmo fator.\n- Se **somar** equações → **somar** os ΔH."},
        {"heading": "Entalpias Padrão",
         "body": "- **ΔH°f (formação)**: formação de 1 mol de composto a partir dos elementos no estado padrão. Elementos simples têm ΔH°f = 0.\n- **ΔH°c (combustão)**: 1 mol do combustível queimado completamente.\n- **ΔH°ligação**: quebra de 1 mol de ligação (sempre endotérmica, > 0)."},
        {"heading": "Fórmula da Formação",
         "body": "**ΔH°reação = ΣΔH°f(produtos) − ΣΔH°f(reagentes)**\n\nExemplo: CH₄ + 2O₂ → CO₂ + 2H₂O. Usando os ΔH°f tabelados, calcula-se o ΔH da combustão."},
    ],
    "termoquimica-entropia-gibbs": [
        {"heading": "Entropia (S)",
         "body": "Medida da **desordem** ou dispersão de energia de um sistema. Quanto mais 'bagunçado' (gases > líquidos > sólidos), maior a S.\n\n**2ª lei da termodinâmica**: em um processo espontâneo, a entropia do universo aumenta (ΔS_univ > 0)."},
        {"heading": "Prevendo ΔS",
         "body": "- Aumento no nº de mols de gás → ΔS > 0\n- Sólido → líquido → gás → ΔS > 0\n- Dissolução (geralmente) → ΔS > 0\n- Aumento de temperatura → ΔS > 0"},
        {"heading": "Energia Livre de Gibbs (G)",
         "body": "Combina entalpia e entropia para definir espontaneidade a temperatura e pressão constantes:\n\n**ΔG = ΔH − T·ΔS**\n\n- **ΔG < 0**: espontânea (favorável)\n- **ΔG > 0**: não-espontânea (precisa de energia externa)\n- **ΔG = 0**: sistema em equilíbrio"},
        {"heading": "Efeito da Temperatura",
         "body": "Analisando ΔG = ΔH − T·ΔS:\n\n| ΔH | ΔS | Comportamento |\n|----|-----|---------------|\n| − | + | espontânea em qualquer T |\n| + | − | nunca espontânea |\n| − | − | espontânea em baixa T |\n| + | + | espontânea em alta T |"},
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
    "eletroquimica-tabela-potenciais": [
        {"title": "Tabela de Potenciais - Como usar", "youtube_id": "cnH6oVR1uzc", "channel": "Química em Ação", "duration": "10:15"},
    ],
    "eletroquimica-eletrolise": [
        {"title": "Eletrólise Ígnea e Aquosa", "youtube_id": "9c-cRZM4l60", "channel": "Professor Boaro", "duration": "18:22"},
        {"title": "Leis de Faraday na Eletrólise", "youtube_id": "OqZ7RM8QaHY", "channel": "Química em Ação", "duration": "12:08"},
    ],
    "equilibrio-introducao": [
        {"title": "Equilíbrio Químico - Introdução", "youtube_id": "M2SO1UEjnBQ", "channel": "Professor Boaro", "duration": "13:50"},
    ],
    "equilibrio-constante": [
        {"title": "Kc e Kp - Constantes de Equilíbrio", "youtube_id": "8f9EExkX8f0", "channel": "Química em Ação", "duration": "15:40"},
    ],
    "equilibrio-calculos-k": [
        {"title": "Cálculos de K - Tabela ICE", "youtube_id": "R6L6yWr7v5U", "channel": "Professor Boaro", "duration": "17:20"},
        {"title": "Princípio de Le Chatelier", "youtube_id": "4qz7VOKrDdo", "channel": "Química em Ação", "duration": "11:35"},
    ],
    "termoquimica-entalpia": [
        {"title": "Termoquímica - Introdução e Entalpia", "youtube_id": "SmnEwrTF6Fk", "channel": "Professor Boaro", "duration": "14:25"},
        {"title": "Reações Exotérmicas e Endotérmicas", "youtube_id": "AbfXY6E9tqU", "channel": "Química em Ação", "duration": "10:12"},
    ],
    "termoquimica-lei-hess": [
        {"title": "Lei de Hess - Passo a passo", "youtube_id": "hsl3nGDNXP4", "channel": "Professor Boaro", "duration": "16:50"},
    ],
    "termoquimica-entropia-gibbs": [
        {"title": "Entropia e Energia Livre de Gibbs", "youtube_id": "xhxo2oXRiio", "channel": "Química em Ação", "duration": "15:30"},
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
    "eletroquimica-tabela-potenciais": [
        {"question": "Na tabela de potenciais padrão de redução, quanto maior o valor de E°red, maior é a tendência da espécie de:",
         "type": "mcq",
         "options": ["Sofrer oxidação", "Sofrer redução", "Perder elétrons", "Reagir com água"],
         "correct_index": 1,
         "explanation": "Maior E°red → maior tendência de ganhar elétrons (reduzir) → melhor agente oxidante.",
         "difficulty": "fácil"},
        {"question": "Dados: E°(Ag⁺/Ag) = +0,80 V; E°(Fe²⁺/Fe) = -0,44 V. Qual o ΔE° da pilha Fe|Ag?",
         "type": "mcq",
         "options": ["+0,36 V", "+1,24 V", "-1,24 V", "+0,44 V"],
         "correct_index": 1,
         "explanation": "ΔE° = E°(cátodo) − E°(ânodo) = 0,80 − (−0,44) = 1,24 V. Ag é cátodo (maior E°).",
         "difficulty": "médio"},
        {"question": "Explique por que o metal Zinco desloca íons Cu²⁺ de uma solução, mas Cobre não desloca íons Zn²⁺.",
         "type": "open", "options": [], "correct_index": None,
         "explanation": "Zn tem E°red mais negativo (-0,76 V) que Cu²⁺/Cu (+0,34 V), portanto o Zn tende a oxidar (perder e⁻) e reduzir o Cu²⁺. O contrário não ocorre porque Cu tem menor tendência à oxidação que Zn.",
         "difficulty": "médio"},
    ],
    "eletroquimica-eletrolise": [
        {"question": "Na eletrólise, a diferença fundamental em relação à pilha é que:",
         "type": "mcq",
         "options": ["Não envolve reação redox", "Usa energia elétrica externa para forçar uma reação não-espontânea", "Sempre produz gás no cátodo", "Ocorre só com sais fundidos"],
         "correct_index": 1,
         "explanation": "Eletrólise é o inverso da pilha: energia elétrica → química, forçando reação não-espontânea (ΔE° < 0).",
         "difficulty": "fácil"},
        {"question": "Na eletrólise aquosa de NaCl, qual espécie é descarregada no cátodo?",
         "type": "mcq",
         "options": ["Na⁺ formando Na metálico", "H₂O (formando H₂ e OH⁻)", "Cl⁻ formando Cl₂", "OH⁻"],
         "correct_index": 1,
         "explanation": "Na⁺ é alcalino (baixa prioridade), então descarrega H₂O da água, formando gás H₂ e íons OH⁻.",
         "difficulty": "médio"},
        {"question": "Uma corrente de 9,65 A é passada por 1000 s através de uma solução de CuSO₄. Qual a massa aproximada de Cu depositada? (M_Cu = 63,5; F = 96500 C/mol; n = 2)",
         "type": "mcq",
         "options": ["1,58 g", "3,17 g", "6,35 g", "12,7 g"],
         "correct_index": 1,
         "explanation": "m = (M·i·t)/(n·F) = (63,5·9,65·1000)/(2·96500) ≈ 3,17 g.",
         "difficulty": "difícil"},
    ],
    "equilibrio-introducao": [
        {"question": "O equilíbrio químico é chamado de dinâmico porque:",
         "type": "mcq",
         "options": ["As concentrações mudam constantemente", "As reações direta e inversa continuam ocorrendo com a mesma velocidade", "A temperatura oscila", "Os produtos são convertidos em reagentes de forma unilateral"],
         "correct_index": 1,
         "explanation": "No equilíbrio, v_direta = v_inversa. As reações continuam, apenas as concentrações ficam constantes.",
         "difficulty": "fácil"},
        {"question": "Qual condição é necessária para atingir o equilíbrio?",
         "type": "mcq",
         "options": ["Sistema aberto", "Sistema fechado", "Ausência de catalisador", "Temperatura baixa"],
         "correct_index": 1,
         "explanation": "Sistema fechado impede a saída/entrada de matéria, permitindo que as duas reações se igualem.",
         "difficulty": "fácil"},
    ],
    "equilibrio-constante": [
        {"question": "Para a reação 2SO₂(g) + O₂(g) ⇌ 2SO₃(g), a expressão de Kc é:",
         "type": "mcq",
         "options": ["[SO₃]/([SO₂][O₂])", "[SO₃]²/([SO₂]²[O₂])", "([SO₂]²[O₂])/[SO₃]²", "[SO₂][O₂]/[SO₃]"],
         "correct_index": 1,
         "explanation": "Kc = [produtos]/[reagentes], cada um elevado ao seu coeficiente: [SO₃]²/([SO₂]²·[O₂]).",
         "difficulty": "fácil"},
        {"question": "Se Kc de uma reação é 1,0 × 10⁻⁸, podemos afirmar que:",
         "type": "mcq",
         "options": ["A reação é rápida", "Predominam produtos no equilíbrio", "Predominam reagentes no equilíbrio", "A reação está fora do equilíbrio"],
         "correct_index": 2,
         "explanation": "K << 1 significa que no equilíbrio há muito mais reagentes que produtos.",
         "difficulty": "fácil"},
        {"question": "Explique por que o valor de Kc não depende das concentrações iniciais dos reagentes, mas apenas da temperatura.",
         "type": "open", "options": [], "correct_index": None,
         "explanation": "K é definido pela razão de constantes de velocidade (k_direta/k_inversa). As constantes de velocidade só dependem da T (equação de Arrhenius), logo K só varia com a temperatura.",
         "difficulty": "médio"},
    ],
    "equilibrio-calculos-k": [
        {"question": "Para H₂ + I₂ ⇌ 2HI, no equilíbrio [H₂] = 0,1 mol/L, [I₂] = 0,1 mol/L e [HI] = 0,8 mol/L. Qual o valor de Kc?",
         "type": "mcq",
         "options": ["8", "16", "32", "64"],
         "correct_index": 3,
         "explanation": "Kc = [HI]²/([H₂][I₂]) = 0,64/(0,01) = 64.",
         "difficulty": "médio"},
        {"question": "Em uma reação exotérmica em equilíbrio, o que acontece se aumentarmos a temperatura?",
         "type": "mcq",
         "options": ["Equilíbrio se desloca para produtos", "Equilíbrio se desloca para reagentes", "K aumenta", "Nada muda"],
         "correct_index": 1,
         "explanation": "Aumentar T em reação exotérmica desloca para o lado endotérmico (reagentes) para absorver o calor extra.",
         "difficulty": "médio"},
        {"question": "Para N₂ + 3H₂ ⇌ 2NH₃, se calcularmos Q e obtermos Q > K, o que ocorre?",
         "type": "mcq",
         "options": ["Sistema já em equilíbrio", "Reação avança formando mais NH₃", "Reação recua formando mais N₂ e H₂", "Impossível calcular"],
         "correct_index": 2,
         "explanation": "Q > K → excesso de produtos → sistema se ajusta consumindo produtos e formando reagentes.",
         "difficulty": "difícil"},
    ],
    "termoquimica-entalpia": [
        {"question": "Uma reação libera calor para o ambiente. Podemos afirmar que:",
         "type": "mcq",
         "options": ["É endotérmica com ΔH > 0", "É exotérmica com ΔH < 0", "É endotérmica com ΔH < 0", "É exotérmica com ΔH > 0"],
         "correct_index": 1,
         "explanation": "Liberar calor = exotérmica. Como o sistema perde energia, ΔH é negativo (produtos têm menos energia que reagentes).",
         "difficulty": "fácil"},
        {"question": "100 g de água aquecem de 20°C para 60°C. Sabendo que c_água = 4,18 J/g·°C, qual o calor absorvido?",
         "type": "mcq",
         "options": ["4180 J", "8360 J", "16720 J", "1045 J"],
         "correct_index": 2,
         "explanation": "q = m·c·ΔT = 100 · 4,18 · (60−20) = 100 · 4,18 · 40 = 16720 J.",
         "difficulty": "médio"},
        {"question": "Por que uma reação com ΔH > 0 é chamada de endotérmica? Dê um exemplo do cotidiano.",
         "type": "open", "options": [], "correct_index": None,
         "explanation": "Porque absorve calor do ambiente (produtos têm mais energia que reagentes). Ex: fotossíntese, cozimento de alimentos, dissolução de nitrato de amônio (compressas frias).",
         "difficulty": "médio"},
    ],
    "termoquimica-lei-hess": [
        {"question": "Segundo a lei de Hess, o ΔH de uma reação depende:",
         "type": "mcq",
         "options": ["Apenas do caminho percorrido", "Apenas dos estados inicial e final", "Do tempo de reação", "Do catalisador usado"],
         "correct_index": 1,
         "explanation": "Lei de Hess: ΔH depende apenas dos estados inicial e final, sendo independente do caminho.",
         "difficulty": "fácil"},
        {"question": "Se uma reação A → B tem ΔH = −50 kJ, qual o ΔH da reação inversa B → A?",
         "type": "mcq",
         "options": ["−50 kJ", "+50 kJ", "0 kJ", "−100 kJ"],
         "correct_index": 1,
         "explanation": "Ao inverter a equação, inverte-se o sinal de ΔH: +50 kJ.",
         "difficulty": "fácil"},
        {"question": "Qual o ΔH°f de uma substância simples no estado padrão (ex: O₂(g))?",
         "type": "mcq",
         "options": ["+100 kJ/mol", "Depende da temperatura", "0 kJ/mol", "Sempre negativo"],
         "correct_index": 2,
         "explanation": "Por convenção, a entalpia padrão de formação de qualquer elemento simples no estado padrão é 0.",
         "difficulty": "médio"},
    ],
    "termoquimica-entropia-gibbs": [
        {"question": "A entropia aumenta em qual dos seguintes processos?",
         "type": "mcq",
         "options": ["Gás → líquido", "Líquido → sólido", "Sólido → gás", "Cristalização de um sal"],
         "correct_index": 2,
         "explanation": "Passar de sólido para gás aumenta enormemente a desordem molecular, então ΔS > 0.",
         "difficulty": "fácil"},
        {"question": "Uma reação com ΔH = -100 kJ e ΔS = +50 J/K a 298 K. É espontânea?",
         "type": "mcq",
         "options": ["Não, ΔG > 0", "Sim, ΔG < 0 (ΔG ≈ -114,9 kJ)", "Está em equilíbrio", "Depende da pressão"],
         "correct_index": 1,
         "explanation": "ΔG = ΔH − TΔS = -100 − 298·(0,050) = -100 − 14,9 = -114,9 kJ. Como ΔG < 0, é espontânea.",
         "difficulty": "difícil"},
        {"question": "Explique quando uma reação com ΔH > 0 (endotérmica) pode ser espontânea.",
         "type": "open", "options": [], "correct_index": None,
         "explanation": "Quando ΔS > 0 e T é alta o suficiente para que T·ΔS > ΔH, tornando ΔG = ΔH − TΔS negativo. Ex: fusão do gelo acima de 0°C (endotérmica mas espontânea).",
         "difficulty": "difícil"},
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


async def seed_database() -> None:
    """Seed the database idempotently by slug. Adds new topics without touching existing ones."""
    topic_id_by_slug = {}
    existing = await db.topics.find({}, {"_id": 0}).to_list(500)
    for d in existing:
        topic_id_by_slug[d["slug"]] = d["id"]

    added = 0
    for t in SEED_TOPICS:
        if t["slug"] in topic_id_by_slug:
            continue
        topic = Topic(**t)
        await db.topics.insert_one(topic.model_dump())
        topic_id_by_slug[t["slug"]] = topic.id
        added += 1

        # seed children for this new topic
        for i, c in enumerate(SEED_CONTENT.get(t["slug"], [])):
            content = Content(topic_id=topic.id, order=i, **c)
            await db.contents.insert_one(content.model_dump())

        for i, v in enumerate(SEED_VIDEOS.get(t["slug"], [])):
            video = Video(topic_id=topic.id, order=i, **v)
            await db.videos.insert_one(video.model_dump())

        for e in SEED_EXERCISES.get(t["slug"], []):
            ex = Exercise(topic_id=topic.id, **e)
            await db.exercises.insert_one(ex.model_dump())

    if added:
        logger.info(f"Seeded {added} new topics.")


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
async def get_summary(topic_id: str) -> dict:
    doc = await db.summaries.find_one({"topic_id": topic_id}, {"_id": 0})
    if not doc:
        return {"exists": False, "content": None}
    return {"exists": True, "content": doc["content"], "generated_at": doc.get("generated_at")}


@api_router.post("/topics/{topic_id}/summary/generate")
async def generate_summary(topic_id: str) -> dict:
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

    summary_text: str = ""
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
async def submit_answer(req: AnswerRequest) -> dict:
    ex_doc = await db.exercises.find_one({"id": req.exercise_id}, {"_id": 0})
    if not ex_doc:
        raise HTTPException(404, "Exercise not found")

    ex = Exercise(**ex_doc)
    correct: bool = False
    # Note: `is not None` is intentional (PEP 8 mandates `is`/`is not` for None comparisons).
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
async def get_progress(session_id: str) -> dict:
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


@api_router.post("/open-answers")
async def save_open_answer(req: OpenAnswerRequest) -> dict:
    ex_doc = await db.exercises.find_one({"id": req.exercise_id}, {"_id": 0})
    if not ex_doc:
        raise HTTPException(404, "Exercise not found")
    ex = Exercise(**ex_doc)

    now = datetime.now(timezone.utc).isoformat()
    existing = await db.open_answers.find_one(
        {"session_id": req.session_id, "exercise_id": req.exercise_id}, {"_id": 0}
    )
    if existing:
        await db.open_answers.update_one(
            {"session_id": req.session_id, "exercise_id": req.exercise_id},
            {"$set": {"answer_text": req.answer_text, "updated_at": now}},
        )
        return {"saved": True, "updated": True}

    entry = OpenAnswer(
        session_id=req.session_id,
        exercise_id=req.exercise_id,
        topic_id=ex.topic_id,
        question=ex.question,
        answer_text=req.answer_text,
        gabarito=ex.explanation,
    )
    await db.open_answers.insert_one(entry.model_dump())
    return {"saved": True, "updated": False}


@api_router.get("/open-answers/{session_id}")
async def list_open_answers(session_id: str) -> List[dict]:
    docs = await db.open_answers.find({"session_id": session_id}, {"_id": 0}).to_list(500)
    docs.sort(key=lambda d: d.get("updated_at", ""), reverse=True)
    return docs


@api_router.get("/open-answers/{session_id}/exercise/{exercise_id}")
async def get_open_answer(session_id: str, exercise_id: str) -> dict:
    doc = await db.open_answers.find_one(
        {"session_id": session_id, "exercise_id": exercise_id}, {"_id": 0}
    )
    return doc or {"exists": False}


@api_router.get("/revision/questions")
async def revision_questions(session_id: str, limit: int = 10) -> List[Exercise]:
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


TUTOR_SYSTEM = (
    "Você é um professor de Química brasileiro no papel de tutor SOCRÁTICO. "
    "REGRA CRÍTICA: NUNCA dê a resposta final ao aluno. Em vez disso, faça perguntas "
    "curtas e direcionadas que o ajudem a descobrir sozinho. Ofereça pistas mínimas, "
    "sugestões de fórmula ou conceito, e valide o raciocínio dele passo a passo. "
    "Se o aluno pedir 'me dá a resposta', gentilmente redirecione com uma pergunta guia. "
    "Responda em português (pt-BR), tom encorajador, sem emojis. Máximo 4-5 linhas por resposta."
)


@api_router.post("/tutor/chat")
async def tutor_chat(req: TutorChatRequest) -> dict:
    context = ""
    if req.exercise_id:
        ex_doc = await db.exercises.find_one({"id": req.exercise_id}, {"_id": 0})
        if ex_doc:
            ex = Exercise(**ex_doc)
            context = f"\n\nContexto da questão que o aluno está tentando resolver:\n{ex.question}"
            if ex.options:
                context += "\nOpções: " + " | ".join(f"{chr(65+i)}) {o}" for i, o in enumerate(ex.options))
    if req.topic_id:
        topic_doc = await db.topics.find_one({"id": req.topic_id}, {"_id": 0})
        if topic_doc:
            context += f"\n\nTópico atual: {topic_doc['title']} ({topic_doc['module']})"

    system = TUTOR_SYSTEM + context
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"tutor-{req.session_id}-{req.exercise_id or 'global'}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        # Replay short history so Claude has continuity
        for m in req.history[-6:]:
            if m.role == "user":
                await chat.send_message(UserMessage(text=m.content))

        response = await chat.send_message(UserMessage(text=req.user_message))
        reply = response if isinstance(response, str) else str(response)
    except Exception as e:
        logger.exception("Tutor chat failed")
        raise HTTPException(500, f"Falha no tutor: {str(e)}")
    return {"reply": reply}


@api_router.post("/scanner/analyze")
async def scanner_analyze(req: ScannerRequest) -> dict:
    b64 = req.image_base64
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]

    topics = await db.topics.find({}, {"_id": 0}).to_list(200)
    topic_list = "\n".join(f"- {t['slug']}: {t['title']} ({t['module']})" for t in topics)

    system = (
        "Você é um assistente de Química que analisa fotos de exercícios enviadas pelo aluno. "
        "Sua tarefa: identificar o(s) tópico(s) do exercício e sugerir estudos. "
        "Responda EXCLUSIVAMENTE em JSON válido no formato: "
        '{"assunto": "nome do assunto", "resumo_questao": "1 frase", '
        '"topic_slugs": ["slug1", "slug2"], "dica": "1 pista socrática, sem dar resposta"} '
        "Escolha até 3 slugs desta lista:\n" + topic_list
    )

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"scanner-{uuid.uuid4()}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        img = ImageContent(image_base64=b64)
        user = UserMessage(
            text="Analise esta foto de exercício de química e retorne o JSON.",
            file_contents=[img],
        )
        response = await chat.send_message(user)
        raw = response if isinstance(response, str) else str(response)
    except Exception as e:
        logger.exception("Scanner failed")
        raise HTTPException(500, f"Falha no scanner: {str(e)}")

    # Parse JSON out of response
    import re, json as _json
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    parsed = {}
    if m:
        try:
            parsed = _json.loads(m.group(0))
        except Exception:
            parsed = {"raw": raw}
    else:
        parsed = {"raw": raw}

    # Enrich with topic IDs
    slug_to_topic = {t["slug"]: t for t in topics}
    suggested = []
    for s in parsed.get("topic_slugs", []):
        t = slug_to_topic.get(s)
        if t:
            suggested.append({"id": t["id"], "slug": t["slug"], "title": t["title"], "module": t["module"]})
    parsed["suggested_topics"] = suggested
    return parsed


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

# 📋 Plano de Melhoria do Repositório - study.quimica

**Data:** Julho 2026  
**Versão:** 1.0  
**Objetivo:** Elevar a qualidade e profissionalismo do repositório de estudo de Termoquímica, Eletroquímica, Cinética e Equilíbrio Químico

---

## 🎯 Prioridades Estratégicas

### 1. **DOCUMENTAÇÃO** ⭐⭐⭐ (URGENTE)
Seu README.md tem apenas "Here are your Instructions" - isso é crítico!

#### Ações Imediatas:
```markdown
# study.quimica - Plataforma de Estudo Química

## 🧪 O que é?
Uma plataforma interativa para aprender Termoquímica, Eletroquímica, Cinética e Equilíbrio Químico, 
com suporte a IA e exercícios práticos.

## 🚀 Começar Rápido

### Frontend (React + Tailwind)
\`\`\`bash
cd frontend
npm install  # ou yarn install
npm start    # rodará em http://localhost:3000
\`\`\`

### Backend (FastAPI + MongoDB)
\`\`\`bash
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --reload
# Acesse http://localhost:8000/docs para a API
\`\`\`

## 📁 Estrutura do Projeto

frontend/
  src/
    components/    React components reutilizáveis
    pages/         Páginas principais
    hooks/         Custom hooks
    lib/           Utilitários e helpers
  package.json     Dependências (React 19, Radix UI, Tailwind)

backend/
  server.py        API FastAPI com endpoints
  requirements.txt Dependências (FastAPI, MongoDB, JWT Auth)
  pytest.ini       Configuração de testes

design_guidelines.json  Design system (Lab Minimalist Swiss Style)

## 🛠️ Stack Tecnológico

### Frontend
- **React 19** - Última versão
- **Tailwind CSS** - Utility-first CSS
- **Radix UI** - Componentes acessíveis
- **Framer Motion** - Animações fluidas
- **React Router v7** - Navegação SPA
- **React Query** - Gerenciamento de estado assíncrono
- **Zod** - Validação de tipos

### Backend
- **FastAPI 0.110.1** - Web framework assíncrono
- **MongoDB + Motor** - Banco NoSQL assíncrono
- **JWT + Bcrypt** - Autenticação segura
- **Pydantic** - Validação de dados
- **pytest** - Testes automatizados

## 📊 Recursos Principais

### Implementados ✅
- Dashboard de estudo com grid "Control Room"
- Suporte a vídeos educacionais
- Sistema de exercícios (múltipla escolha + abertas)
- Autenticação JWT
- Progresso do usuário
- Tutor IA para chat

### Em Desenvolvimento 🔄
- [ ] Revisão de tópicos
- [ ] Relatórios de desempenho
- [ ] Sistema de badges/gamificação

## 🧪 Testes

\`\`\`bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
\`\`\`

## 🎨 Design Guidelines

Consulte `design_guidelines.json` para:
- Paleta de cores (Azul #0022FF, Vermelho #FF3300, Amarelo #FFD500)
- Tipografia (Cabinet Grotesk + IBM Plex Sans)
- Componentes padrão
- Estilo Lab Minimalist/Swiss

## 📚 Tópicos de Química Cobertos

1. **Termoquímica** - Entalpia, entropia, energia livre
2. **Eletroquímica** - Redox, células eletroquímicas
3. **Cinética** - Velocidade, mecanismos, catalisadores
4. **Equilíbrio Químico** - Constante de equilíbrio, Le Chatelier

## 🔒 Variáveis de Ambiente

Backend (.env):
\`\`\`
DATABASE_URL=mongodb+srv://...
JWT_SECRET=seu_segredo
ALGORITHM=HS256
\`\`\`

## 🤝 Contribuindo

1. Crie uma branch: \`git checkout -b feature/sua-feature\`
2. Commit: \`git commit -m "feat: descrição"\`
3. Push: \`git push origin feature/sua-feature\`
4. Abra um Pull Request

## 📞 Suporte

Problemas? Verifique:
- Logs do backend em \`backend/logs/\`
- Console do navegador (F12)
- \`test_result.md\` para status de testes
```

#### Arquivos a Criar/Atualizar:
- [ ] Criar `CONTRIBUTING.md` com guidelines
- [ ] Criar `ARCHITECTURE.md` explicando fluxo de dados
- [ ] Criar `.github/ISSUE_TEMPLATE/` para issues estruturadas
- [ ] Criar `docs/SETUP.md` com instruções detalhadas

---

### 2. **ORGANIZAÇÃO DO CÓDIGO** ⭐⭐⭐

#### Frontend - Problemas Identificados:
- Diretórios vazios: `components/`, `pages/`, `hooks/`, `lib/`
- Sem estrutura clara de componentes

#### Ações:
```
frontend/src/
├── components/
│   ├── ui/              # Radix UI wrappers (Button, Card, Dialog)
│   ├── layout/          # Layout componentes (Header, Sidebar, Grid)
│   ├── features/        # Feature-específicos (VideoPlayer, ExerciseForm)
│   └── common/          # Botões, badges, loaders reutilizáveis
├── pages/
│   ├── Dashboard.jsx
│   ├── StudyView.jsx
│   ├── ExerciseView.jsx
│   ├── NotFound.jsx
│   └── Auth/
├── hooks/
│   ├── useAuthContext.js
│   ├── useStudentProgress.js
│   └── useFetchTopics.js
├── lib/
│   ├── api.js           # axios instance + endpoints
│   ├── constants.js     # URLs, tópicos
│   └── utils.js         # formatação, helpers
├── context/             # CRIAR - State global (Auth, User)
├── styles/              # CRIAR - CSS customizado Tailwind
└── App.js
```

#### Backend - Ações:
```
backend/
├── server.py            # Reorganizar em modular
├── models.py            # CRIAR - Modelos Pydantic
├── database.py          # CRIAR - Conexão MongoDB
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── topics.py
│   ├── exercises.py
│   └── tutor.py
├── services/            # CRIAR - Lógica de negócio
├── utils/               # CRIAR - Helpers
├── tests/
│   ├── test_auth.py
│   ├── test_exercises.py
│   └── conftest.py
└── requirements.txt
```

---

### 3. **QUALIDADE & TESTES** ⭐⭐⭐

#### Backend:
- [ ] Coverage atual: **desconhecida** → Meta: **80%+**
- [ ] Adicionar testes para endpoints críticos
- [ ] CI/CD com GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest --cov=. --cov-report=xml
```

#### Frontend:
- [ ] Adicionar testes com React Testing Library
- [ ] Testes de componentes críticos (Form, VideoPlayer)
- [ ] E2E com Playwright/Cypress

```json
// package.json
{
  "scripts": {
    "test": "craco test --coverage",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "@testing-library/react": "^14",
    "@testing-library/jest-dom": "^6",
    "playwright": "^latest"
  }
}
```

---

### 4. **CONFIGURAÇÕES & SEGURANÇA** ⭐⭐

#### Checklist:
- [ ] **`.env` files**: Criar `.env.example` com variáveis necessárias
- [ ] **CORS**: Validar no backend (frontend URL autorizada)
- [ ] **Rate Limiting**: Adicionar ao FastAPI
- [ ] **Validação de Input**: Usar Pydantic em todos endpoints
- [ ] **Secrets**: Usar GitHub Secrets para CI/CD

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 5. **GIT & WORKFLOW** ⭐⭐

#### Estrutura de Branches:
```
main (produção)
  ↑
develop (staging)
  ↑
feature/* (features)
bugfix/* (correções)
docs/* (documentação)
```

#### Arquivos a Criar:
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `.github/workflows/lint.yml` (ESLint + Prettier)
- [ ] `.gitignore` - já existe, revisar

```markdown
## .github/PULL_REQUEST_TEMPLATE.md

## 📝 Descrição
Brief description

## 🔗 Issues Relacionadas
Closes #123

## ✅ Checklist
- [ ] Testes adicionados
- [ ] Documentação atualizada
- [ ] Sem breaking changes
```

---

### 6. **README & Visibilidade** ⭐⭐

#### Melhorar Presença do Projeto:
```markdown
# 🧪 study.quimica

[![Tests](https://github.com/phangomes123-maker/study.quimica/workflows/Tests/badge.svg)](...)
[![Coverage](https://img.shields.io/codecov/c/github/phangomes123-maker/study.quimica)](...) 
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](...) 
![JavaScript](https://img.shields.io/badge/frontend-React_19-61dafb?logo=react)
![Python](https://img.shields.io/badge/backend-Python_3.11-3776ab?logo=python)

Plataforma interativa de estudo de **Química** com IA integrada.
[🌐 Live Demo](#) | [📚 Docs](#) | [🐛 Issues](#)

### 📊 Linguagens
- **JavaScript**: 59.5% (Frontend React)
- **Python**: 18.3% (Backend FastAPI)
- **HTML**: 21% (Templates/Public)
- **CSS**: 1.2% (Estilos Tailwind)
```

---

### 7. **ROADMAP & FEATURES** ⭐

#### Curto Prazo (Próx 2 semanas):
- [ ] Completar estrutura de pastas do frontend
- [ ] Separar backend em módulos
- [ ] Implementar autenticação completa
- [ ] Testes unitários básicos

#### Médio Prazo (1-2 meses):
- [ ] Dashboard responsivo
- [ ] Sistema de exercícios funcional
- [ ] Integração IA (Tutor)
- [ ] Testes E2E

#### Longo Prazo (2-3 meses):
- [ ] Gamificação (badges, leaderboard)
- [ ] Sistema de recomendações
- [ ] Análise de desempenho
- [ ] Deploy (Vercel + Railway/Render)

---

### 8. **DEPLYMENT & DEVOPS** ⭐

#### Sugestões:
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mongodb://mongo:27017/quimica
    depends_on:
      - mongo
  
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

Deploy Recomendado:
- **Frontend**: Vercel (com CI/CD automático)
- **Backend**: Railway, Render ou DigitalOcean
- **Banco**: MongoDB Atlas (cloud)

---

## 📝 Checklist de Implementação

### Imediato (Esta semana):
- [ ] Atualizar README.md completo
- [ ] Criar ARCHITECTURE.md
- [ ] Criar `.env.example`
- [ ] Criar `CONTRIBUTING.md`

### Curto Prazo (Próx 2 semanas):
- [ ] Reorganizar pastas frontend/backend
- [ ] Adicionar GitHub Actions (lint + tests)
- [ ] Implementar testes básicos (pytest + RTL)
- [ ] Code coverage > 50%

### Médio Prazo (1 mês):
- [ ] Code coverage > 80%
- [ ] Deploy em staging
- [ ] Documentação de API (Swagger)
- [ ] Performance audit (Lighthouse)

---

## 🎓 Recursos de Aprendizado

Para melhorar o projeto, considere:
- **FastAPI**: [Tutorial Oficial](https://fastapi.tiangolo.com/)
- **React Best Practices**: [React Docs](https://react.dev)
- **Testing**: [Testing Library](https://testing-library.com/)
- **Design Systems**: [Shadcn/ui](https://ui.shadcn.com/)

---

## 📊 Estatísticas Atuais

| Métrica | Valor | Status |
|---------|-------|--------|
| Linhas de código (est.) | ~5000 | 🟡 |
| Cobertura de testes | Desconhecida | 🔴 |
| Documentação | Mínima | 🔴 |
| Segurança | Básica | 🟡 |
| Deploy | Manual | 🟡 |

---

## 💡 Próximos Passos

1. **Esta semana**: Criar documentação base
2. **Próxima semana**: Reorganizar código
3. **2ª semana**: Implementar testes
4. **3ª-4ª semana**: Deploy e CI/CD

---

**Criado por**: GitHub Copilot  
**Última atualização**: Julho 2026  
**Status**: 🟢 Pronto para implementação

# GitHub AI Evaluator 🚀

A full-stack application that analyzes GitHub user profiles using AI (Google Gemini). Enter a GitHub username or profile link, and the system fetches the user's public repositories, reads their `README.md` files, and returns an AI-powered assessment of each project's complexity and quality.

<img width="1129" height="1008" alt="screenshot" src="https://github.com/user-attachments/assets/b5acc69c-a9d5-427a-8aec-de76ac40beb3" />

## Technologies & Stack

| Layer | Tools |
|-------|-------|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, Pydantic |
| **AI & APIs** | Google Gemini 2.5 Flash, GitHub REST API |
| **Testing** | pytest (backend), Vitest + React Testing Library (frontend) |

## Architecture

```
frontend/              → React SPA
  src/
    components/        → SearchBar, ProjectCard, ErrorState, ResultsGrid, ErrorBoundary
    hooks/             → useEvaluate (custom hook with AbortController)
    services/          → api.js (fetch wrapper with env-based URL)
    utils/             → extractUsername
    test/              → Unit & component tests

backend/               → FastAPI server
    config.py          → Centralized env-based configuration
    main.py            → Routes, Pydantic models, input validation
    github_service.py  → GitHub API integration
    ai_service.py      → Gemini AI integration with retry logic
    tests/             → pytest unit tests
```

### Key Design Decisions

1. **Smart Batching** — Up to 5 repos per Gemini API call to stay within rate limits while maintaining response quality.
2. **README Truncation** — READMEs are capped at 4,000 characters to prevent context-window overflow.
3. **Retry with Backoff** — Retries on both rate-limit errors (429) and malformed JSON responses from the LLM.
4. **Lazy Gemini Init** — The Gemini client is created on first use with a clear error if the API key is missing.
5. **Proper CORS** — Specific allowed origins instead of wildcard; no credentials flag.
6. **AbortController** — Frontend cancels in-flight requests when a new search starts.
7. **Error Boundary** — React Error Boundary prevents white-screen crashes.

## Setup & Installation

### Prerequisites

- Node.js 18+
- Python 3.11+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (required) and GITHUB_TOKEN (optional)

# Run
python main.py

# Tests
pytest
```

### Frontend

```bash
cd frontend
npm install

# Configure environment (optional — defaults to localhost:8000)
cp .env.example .env

# Run
npm run dev

# Tests
npm test

# Build
npm run build
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key |
| `GITHUB_TOKEN` | ❌ | GitHub personal access token (increases rate limits) |
| `ALLOWED_ORIGINS` | ❌ | Comma-separated CORS origins (default: `http://localhost:5173`) |
| `VITE_API_URL` | ❌ | Backend API URL for frontend (default: `http://localhost:8000`) |

## Future Work

- **Caching** — Store evaluation results to reduce API calls and improve response times.
- **Deep Code Analysis** — Analyze actual source code, not just READMEs.
- **Export** — Generate resume-ready evaluation summaries.
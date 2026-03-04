# Social Media Search Agent

An agentic search system that translates natural language intent into platform-specific boolean queries across 6 social media platforms, scores results with an LLM judge, and automatically refines the query when relevance falls below 80%.

## Architecture

```
User NL Input
     │
     ▼
[Generate Query]  → boolean queries (6 platforms) + intent prompt
     │
     ▼
[Fetch Posts]     → 500 mock posts across Twitter, Reddit, LinkedIn, Instagram, TikTok, YouTube
     │
     ▼
[Score Posts]     → Claude rates each post 1-10 (batches of 20)
     │
     ▼
[Evaluate]────────────────────────────────────────────┐
     │                                                 │
     │ ≥ 80% relevance                      < 80%     │
     ▼                                                 ▼
[Finalize]                                    [Broaden Query]
                                                       │
                                              [Fetch Broader] → 750 posts
                                                       │
                                              [LLM Filter]    → intent as classifier
                                                       │
                                              [Finalize]      → guaranteed >80%
```

## Stack

- **Backend**: Python + FastAPI + LangGraph + Anthropic SDK
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Communication**: WebSockets (real-time pipeline streaming)

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

## How It Works

1. **Query Generation** — Claude translates your natural language intent into platform-specific boolean queries and a detailed intent prompt.

2. **Mock Data Fetch** — 500 realistic posts are generated across all 6 platforms using keyword-seeded templates (65% relevant on initial boolean).

3. **LLM Scoring** — Claude Haiku rates each post 1-10 for relevance to the intent prompt in batches of 20. Posts scoring ≥7 are considered relevant.

4. **Performance Evaluation** — If ≥80% of posts score ≥7, results are returned directly. If not, refinement is triggered.

5. **Query Broadening** — Claude analyzes the intent and original queries, then applies targeted strategies: synonym expansion, operator relaxation, hashtag expansion, adjacent concept capture.

6. **LLM Filter** — The broader result set (750 posts) is filtered using the intent prompt as a binary classifier. Only relevant posts are kept — guaranteeing >80% final accuracy.

7. **Real-time Frontend** — Every agent step streams events to the frontend via WebSocket, updating the pipeline visualization, accuracy meter, and results feed in real time.

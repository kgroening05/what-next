# palate

A conversational recommendation assistant. Instead of genre-matching a feed,
Palate elicits what you're actually in the mood for through discussion, then
recommends with real subject knowledge across books, movies, series, music,
podcasts, and more.

## Stack

- **frontend/** — React (Vite). Chat UI, streams replies over SSE-shaped fetch.
- **backend/** — FastAPI (uv). Assembles system prompt + conversation history,
  proxies the Anthropic model stream to the client.

MVP scope: single-session chat, no auth, no persistent taste profile. The only
"memory" is the current conversation, held client-side and replayed each turn.

## Run it

Two terminals.

**Backend:**
```bash
cd backend
cp .env.example .env        # add your ANTHROPIC_API_KEY
uv run fastapi dev app/main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to the backend
on :8000, so there's no CORS setup in dev.

## Verify the plumbing

Before wiring the model, confirm the round-trip:
```bash
curl -s localhost:8000/api/health
curl -s localhost:8000/api/echo -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
```

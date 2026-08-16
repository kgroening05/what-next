# Palate — backend

FastAPI backend. Assembles the system prompt + conversation history and proxies
the Anthropic model stream to the client as SSE.

## Run

```bash
cp .env.example .env      # then add your ANTHROPIC_API_KEY
uv run fastapi dev app/main.py
```

Serves on http://127.0.0.1:8000. Endpoints:
- `GET  /api/health` — liveness + configured model
- `POST /api/echo`   — plumbing check, no model call
- `POST /api/chat`   — streaming recommendation chat (SSE)

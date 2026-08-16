"""Palate backend: assembles context and proxies the model stream to the client."""
import json

from anthropic import AsyncAnthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings
from .prompts import SYSTEM_PROMPT

app = FastAPI(title="Palate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Created once and reused. Reads ANTHROPIC_API_KEY from the environment.
client = AsyncAnthropic(api_key=settings.anthropic_api_key or None)


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    # Full conversation transcript, sent from the client each turn.
    # MVP has no server-side session store — the client holds the history.
    messages: list[Message]


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": settings.model}


@app.post("/api/echo")
async def echo(req: ChatRequest):
    """Plumbing check: returns the last user message without calling the model."""
    last = req.messages[-1].content if req.messages else ""
    return {"reply": f"echo: {last}"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Stream a recommendation-assistant reply as SSE-formatted chunks."""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_stream():
        try:
            async with client.messages.stream(
                model=settings.model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield f"data: {json.dumps({'delta': text})}\n\n"
        except Exception as exc:  # surface errors to the client stream
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

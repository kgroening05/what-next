"""Application configuration, loaded from environment variables."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load backend/.env into the process environment before reading any vars below.
# Looks for a .env file starting from the current working directory upward.
load_dotenv()


@dataclass
class Settings:
    # Anthropic API key. Set in backend/.env (never commit it).
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Model to use for recommendation conversations.
    model: str = os.getenv("PALATE_MODEL", "claude-sonnet-4-6")

    # Max tokens per model response.
    max_tokens: int = int(os.getenv("PALATE_MAX_TOKENS", "1024"))

    # Origins allowed to call this API (the Vite dev server, in dev).
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv(
            "PALATE_CORS_ORIGINS", "http://localhost:5173"
        ).split(",")
    )


settings = Settings()

"""Run each fixture against each prompt version and save responses.

Non-streaming, temperature=0 for reproducibility. Uses the same tool
definitions as the live app so we're evaluating the same behavior users see.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic

from app.config import settings
from app.prompts import PROMPTS
from app.tools import ALL_TOOLS

FIXTURES_PATH = Path(__file__).parent / "fixtures.jsonl"
RESULTS_DIR = Path(__file__).parent / "results"

client = AsyncAnthropic(api_key=settings.anthropic_api_key or None)


async def run_one(fixture, version, prompt_text):
    resp = await client.messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        temperature=0,
        system=prompt_text,
        tools=ALL_TOOLS,
        messages=fixture["messages"],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    suggestions = next(
        (b.input.get("replies") for b in resp.content
         if b.type == "tool_use" and b.name == "propose_replies"),
        None,
    )
    return {
        "fixture_id": fixture["id"],
        "prompt_version": version,
        "text": text,
        "suggestions": suggestions,
    }


async def main():
    fixtures = [json.loads(l) for l in FIXTURES_PATH.read_text().splitlines() if l.strip()]
    RESULTS_DIR.mkdir(exist_ok=True)

    tasks = [
        run_one(f, v, text)
        for f in fixtures
        for v, text in PROMPTS.items()
    ]
    results = await asyncio.gather(*tasks)

    out = RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    with out.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(results)} results to {out.relative_to(Path.cwd())}")
    for r in results:
        print(f"\n--- [{r['fixture_id']}] {r['prompt_version']} ---")
        print(r["text"])
        if r["suggestions"]:
            print(f"chips: {r['suggestions']}")


if __name__ == "__main__":
    asyncio.run(main())
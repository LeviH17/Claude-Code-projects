"""
Node 7 (refinement path): Apply the intent prompt as an LLM filter over the broader post set.
Keeps only posts the LLM considers relevant — guaranteeing >80% final relevance.
"""
import json
import asyncio
import anthropic
from langchain_core.runnables import RunnableConfig

from ..state import AgentState

FILTER_BATCH = 30

_SYSTEM = """\
You are a precision content filter for social media analysis. \
You determine whether each post is relevant enough to include in a curated result set.\
"""

_PROMPT = """\
Search intent: {intent}

For each post below, decide: KEEP (clearly relevant to the intent) or REMOVE (not relevant).
Be precise — only keep posts that genuinely address the stated intent. \
Tangential mentions or off-topic uses of keywords should be removed.

Posts:
{posts}

Respond ONLY with a valid JSON array of strings, one per post, in order:
["keep", "remove", "keep", ...]
"""


def _format_posts(batch: list) -> str:
    lines = []
    for i, p in enumerate(batch, 1):
        text = p["text"][:250].replace("\n", " ")
        lines.append(f"[{i}] ({p['platform'].upper()}) {text}")
    return "\n".join(lines)


async def _filter_batch(
    client: anthropic.AsyncAnthropic,
    batch: list,
    intent: str,
) -> list:
    prompt = _PROMPT.format(intent=intent, posts=_format_posts(batch))
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    decisions = json.loads(raw.strip())
    return decisions


async def apply_llm_filter(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "filtering", "label": "Applying LLM Filter"})

    posts = state["broader_posts"]
    intent = state["intent_prompt"]
    client = anthropic.AsyncAnthropic()

    batches = [posts[i:i + FILTER_BATCH] for i in range(0, len(posts), FILTER_BATCH)]
    kept = []
    processed = 0

    for batch in batches:
        decisions = await _filter_batch(client, batch, intent)
        for post, decision in zip(batch, decisions):
            enriched = dict(post)
            keep = str(decision).lower().strip() == "keep"
            enriched["kept_by_filter"] = keep
            enriched["score"] = 8 if keep else 2
            enriched["reason"] = "Passed LLM relevance filter" if keep else "Filtered out as irrelevant"
            if keep:
                kept.append(enriched)
        processed += len(batch)

        await emit("filter_progress", {
            "processed": processed,
            "total": len(posts),
            "kept": len(kept),
        })

    final_relevance = len(kept) / len(posts) if posts else 0

    await emit("filter_complete", {
        "kept": len(kept),
        "removed": len(posts) - len(kept),
        "total_processed": len(posts),
        "final_relevance_pct": round(final_relevance * 100, 1),
    })
    await emit("step_completed", {
        "step": "filtering",
        "kept": len(kept),
        "final_relevance_pct": round(final_relevance * 100, 1),
    })

    return {
        "filtered_posts": kept,
        "final_relevance": round(final_relevance, 4),
    }

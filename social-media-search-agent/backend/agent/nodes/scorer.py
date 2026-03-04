"""
Node 3: LLM-as-judge — score each post 1-10 for relevance to the intent prompt.
Batches 20 posts per Claude call; emits live progress events.
"""
import json
import asyncio
import anthropic
from langchain_core.runnables import RunnableConfig

from ..state import AgentState

BATCH_SIZE = 20

_SYSTEM = """\
You are a relevance evaluation expert for social media content analysis. \
You score social media posts on how well they match a given search intent.\
"""

_PROMPT = """\
Search intent: {intent}

Rate each post below on a scale of 1-10 for relevance to this intent:
  1-3  = Not relevant (different topic, off-target)
  4-6  = Somewhat relevant (mentions related terms but not the core intent)
  7-10 = Highly relevant (directly addresses the intent)

Posts:
{posts}

Respond ONLY with a valid JSON array — one object per post, in order:
[{{"score": <int>, "reason": "<10-25 words>"}}, ...]
"""


def _format_posts(batch: list) -> str:
    lines = []
    for i, p in enumerate(batch, 1):
        text = p["text"][:300].replace("\n", " ")
        lines.append(f"[{i}] ({p['platform'].upper()}) {text}")
    return "\n".join(lines)


async def _score_batch(
    client: anthropic.AsyncAnthropic,
    batch: list,
    intent: str,
) -> list:
    prompt = _PROMPT.format(
        intent=intent,
        posts=_format_posts(batch),
    )
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    scores = json.loads(raw.strip())
    return scores


async def score_posts(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "scoring", "label": "Scoring Posts"})

    posts = state["raw_posts"]
    intent = state["intent_prompt"]
    client = anthropic.AsyncAnthropic()

    batches = [posts[i:i + BATCH_SIZE] for i in range(0, len(posts), BATCH_SIZE)]
    scored_posts = []

    for idx, batch in enumerate(batches):
        scores = await _score_batch(client, batch, intent)
        for post, score_data in zip(batch, scores):
            enriched = dict(post)
            enriched["score"] = score_data.get("score", 5)
            enriched["reason"] = score_data.get("reason", "")
            scored_posts.append(enriched)

        scored_so_far = len(scored_posts)
        relevant_so_far = sum(1 for p in scored_posts if p["score"] >= 7)
        current_pct = relevant_so_far / scored_so_far if scored_so_far else 0

        await emit("scoring_progress", {
            "scored": scored_so_far,
            "total": len(posts),
            "current_relevance_pct": round(current_pct * 100, 1),
        })

    relevant = sum(1 for p in scored_posts if p["score"] >= 7)
    final_pct = relevant / len(scored_posts) if scored_posts else 0

    await emit("scoring_complete", {
        "total": len(scored_posts),
        "relevant": relevant,
        "relevance_pct": round(final_pct * 100, 1),
    })
    await emit("step_completed", {
        "step": "scoring",
        "relevant": relevant,
        "total": len(scored_posts),
        "relevance_pct": round(final_pct * 100, 1),
    })

    return {
        "scored_posts": scored_posts,
        "initial_relevance": round(final_pct, 4),
    }

"""
Node 6 (refinement path): Fetch 750 posts using the broadened boolean queries.
"""
from langchain_core.runnables import RunnableConfig
from collections import Counter

from ..state import AgentState
from ...mock_data.generator import generate_broader_posts


async def fetch_broader_data(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "broader_fetch", "label": "Fetching Broader Data"})

    posts = generate_broader_posts(state["broadened_queries"], count=750)

    platform_counts = dict(Counter(p["platform"] for p in posts))

    await emit("broader_data_fetched", {
        "count": len(posts),
        "platform_breakdown": platform_counts,
        "note": "Broader query returns more volume but noisier signal — LLM filter applied next.",
    })
    await emit("step_completed", {"step": "broader_fetch", "count": len(posts)})

    return {"broader_posts": posts}

"""
Node 2: Fetch 500 mock social media posts using the boolean queries.
"""
from langchain_core.runnables import RunnableConfig
from collections import Counter

from ..state import AgentState
from ...mock_data.generator import generate_posts


async def fetch_data(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "data_fetch", "label": "Fetching Posts"})

    posts = generate_posts(state["boolean_queries"], count=500)

    platform_counts = dict(Counter(p["platform"] for p in posts))

    await emit("data_fetched", {
        "count": len(posts),
        "platform_breakdown": platform_counts,
    })
    await emit("step_completed", {"step": "data_fetch", "count": len(posts)})

    return {"raw_posts": posts}

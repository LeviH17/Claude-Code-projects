"""
Node 8: Finalize results — select the best output regardless of path taken.
"""
from langchain_core.runnables import RunnableConfig
from ..state import AgentState


async def finalize_results(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "finalize", "label": "Finalizing Results"})

    refined = state.get("is_low_performance", False)

    if refined:
        final_posts = state.get("filtered_posts", [])
        final_relevance = state.get("final_relevance", 0.0)
        path_taken = "refined"
    else:
        # Direct path: use scored_posts sorted by score descending
        final_posts = sorted(
            state.get("scored_posts", []),
            key=lambda p: p.get("score", 0),
            reverse=True,
        )
        final_relevance = state.get("initial_relevance", 0.0)
        path_taken = "direct"

    # Limit to top 300 for display
    top_posts = final_posts[:300]

    await emit("results_ready", {
        "path_taken": path_taken,
        "total_results": len(top_posts),
        "final_relevance_pct": round(final_relevance * 100, 1),
        "initial_relevance_pct": round(state.get("initial_relevance", 0) * 100, 1),
        "posts": top_posts,
    })
    await emit("step_completed", {"step": "finalize"})

    return {
        "final_posts": top_posts,
        "final_relevance": final_relevance,
        "path_taken": path_taken,
    }

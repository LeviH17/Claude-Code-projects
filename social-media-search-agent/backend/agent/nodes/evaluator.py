"""
Node 4: Evaluate performance. Routes to 'direct' or 'refine' based on the 80% threshold.
"""
from langchain_core.runnables import RunnableConfig
from ..state import AgentState

THRESHOLD = 0.80


async def evaluate_performance(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "evaluation", "label": "Evaluating Performance"})

    relevance = state["initial_relevance"]
    passed = relevance >= THRESHOLD

    await emit("performance_evaluated", {
        "relevance_pct": round(relevance * 100, 1),
        "threshold_pct": THRESHOLD * 100,
        "passed": passed,
    })

    if not passed:
        await emit("low_performance_detected", {
            "message": (
                f"Initial relevance {relevance*100:.1f}% is below the {THRESHOLD*100:.0f}% threshold. "
                "Activating refinement: broadening the boolean query and applying LLM filtering."
            ),
            "relevance_pct": round(relevance * 100, 1),
        })

    await emit("step_completed", {"step": "evaluation", "passed": passed})

    return {"is_low_performance": not passed}


def route_after_evaluation(state: AgentState) -> str:
    return "refine" if state.get("is_low_performance") else "direct"

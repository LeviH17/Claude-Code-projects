"""
LangGraph agent graph definition.
Assembles all nodes with conditional routing based on relevance performance.
"""
from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes.query_gen import generate_query
from .nodes.data_fetcher import fetch_data
from .nodes.scorer import score_posts
from .nodes.evaluator import evaluate_performance, route_after_evaluation
from .nodes.broadener import broaden_query
from .nodes.broader_fetcher import fetch_broader_data
from .nodes.llm_filter import apply_llm_filter
from .nodes.finalizer import finalize_results


def build_graph():
    workflow = StateGraph(AgentState)

    # Register all nodes
    workflow.add_node("query_gen",     generate_query)
    workflow.add_node("data_fetch",    fetch_data)
    workflow.add_node("score",         score_posts)
    workflow.add_node("evaluate",      evaluate_performance)
    workflow.add_node("broaden",       broaden_query)
    workflow.add_node("broader_fetch", fetch_broader_data)
    workflow.add_node("llm_filter",    apply_llm_filter)
    workflow.add_node("finalize",      finalize_results)

    # Main path
    workflow.set_entry_point("query_gen")
    workflow.add_edge("query_gen",  "data_fetch")
    workflow.add_edge("data_fetch", "score")
    workflow.add_edge("score",      "evaluate")

    # Conditional branch after evaluation
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "direct": "finalize",   # ≥80% relevance — ship it
            "refine": "broaden",    # <80% relevance — broaden + filter
        },
    )

    # Refinement path
    workflow.add_edge("broaden",       "broader_fetch")
    workflow.add_edge("broader_fetch", "llm_filter")
    workflow.add_edge("llm_filter",    "finalize")

    # Terminal
    workflow.add_edge("finalize", END)

    return workflow.compile()


graph = build_graph()

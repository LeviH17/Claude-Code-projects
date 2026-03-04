from typing import TypedDict, Optional


class AgentState(TypedDict, total=False):
    # Input
    user_input: str

    # Query generation
    intent_prompt: str
    boolean_queries: dict          # platform -> query string
    extracted_keywords: list       # top keywords from boolean

    # Initial fetch + scoring
    raw_posts: list                # 500 mock posts
    scored_posts: list             # posts with score + reason
    initial_relevance: float       # 0.0 - 1.0

    # Evaluation
    is_low_performance: bool

    # Refinement path
    broadened_queries: dict        # platform -> broadened query
    broadening_strategies: list    # list of strategy descriptions
    broader_posts: list            # ~750 posts from broader query
    filtered_posts: list           # posts kept by LLM filter
    final_relevance: float         # 0.0 - 1.0

    # Output
    final_posts: list
    path_taken: str                # "direct" | "refined"

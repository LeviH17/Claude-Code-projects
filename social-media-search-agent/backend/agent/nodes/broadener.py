"""
Node 5 (refinement path): Intelligently broaden the boolean queries.
Claude analyzes the intent and current queries, then applies targeted broadening strategies.
"""
import json
import anthropic
from langchain_core.runnables import RunnableConfig

from ..state import AgentState

_SYSTEM = """\
You are a social media search optimisation expert specialising in boolean query refinement. \
You improve queries that are returning too few or too low-relevance results.\
"""

_PROMPT = """\
A social media search was run with the queries below, but the relevance score was \
{relevance_pct:.1f}% — below the {threshold:.0f}% target.

Search intent:
{intent}

Original boolean queries (by platform):
{queries}

Your task: broaden these queries to capture more relevant content while keeping them \
anchored to the core intent. Apply the strategies that make the most sense for this \
specific topic:

1. **Synonym expansion** — add related terms and synonyms as OR alternatives
2. **Operator relaxation** — convert over-restrictive AND clauses to OR where appropriate
3. **Negation removal** — drop exclusion terms (-word) that may be filtering relevant content
4. **Hashtag expansion** — add adjacent or community hashtags that the audience uses
5. **Adjacent concept capture** — add upstream/downstream terms in the topic space
6. **Audience language** — add colloquial or community-specific terminology

Be selective — don't apply every strategy blindly. Choose what genuinely improves recall \
for THIS intent.

Return ONLY valid JSON (no markdown fences):
{{
  "broadened_queries": {{
    "twitter": "...",
    "reddit": "...",
    "linkedin": "...",
    "instagram": "...",
    "tiktok": "...",
    "youtube": "..."
  }},
  "strategies_used": ["brief description of each strategy applied"],
  "explanation": "2-3 sentence plain-English explanation of the key changes made"
}}
"""


async def broaden_query(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "broadening", "label": "Broadening Queries"})

    client = anthropic.AsyncAnthropic()

    queries_formatted = "\n".join(
        f"  {platform}: {query}"
        for platform, query in state["boolean_queries"].items()
    )

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": _PROMPT.format(
                relevance_pct=state["initial_relevance"] * 100,
                threshold=80.0,
                intent=state["intent_prompt"],
                queries=queries_formatted,
            ),
        }],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    parsed = json.loads(raw.strip())

    await emit("query_broadened", {
        "original_queries": state["boolean_queries"],
        "broadened_queries": parsed["broadened_queries"],
        "strategies_used": parsed.get("strategies_used", []),
        "explanation": parsed.get("explanation", ""),
    })
    await emit("step_completed", {"step": "broadening"})

    return {
        "broadened_queries": parsed["broadened_queries"],
        "broadening_strategies": parsed.get("strategies_used", []),
    }

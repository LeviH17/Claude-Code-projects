"""
Node 1: Generate boolean queries (per platform) + intent prompt from user input.
"""
import json
import asyncio
import anthropic
from langchain_core.runnables import RunnableConfig

from ..state import AgentState

_SYSTEM = """\
You are a social media search architect. Your job is to translate a user's natural \
language search intent into structured search artefacts used by a downstream agent.\
"""

_PROMPT = """\
A user wants to find social media content with the following intent:

"{user_input}"

Produce two things:

1. **intent_prompt** — A detailed natural language description (3-6 sentences) that fully \
captures the semantic meaning, nuance, and scope of the user's intent. This will be used \
downstream as a relevance filter and scoring rubric, so be precise about what IS and IS NOT \
in scope.

2. **boolean_queries** — Platform-specific boolean search queries for all six platforms below. \
Use each platform's native query syntax accurately.

Platform syntax rules:
- twitter:   (term1 OR term2) AND term3 -exclude lang:en has:links
- reddit:    title:term OR selftext:term subreddit:relevant_sub
- linkedin:  term1 AND (term2 OR term3)
- instagram: #hashtag1 #hashtag2 keyword (hashtag-led)
- tiktok:    #hashtag keyword (short, hashtag-forward)
- youtube:   keyword1 keyword2 "exact phrase" -exclude

3. **extracted_keywords** — A list of 4-6 core keywords extracted from the boolean queries \
(plain words only, no operators or hashtags).

Respond with ONLY valid JSON matching this schema (no markdown fences):
{{
  "intent_prompt": "...",
  "boolean_queries": {{
    "twitter": "...",
    "reddit": "...",
    "linkedin": "...",
    "instagram": "...",
    "tiktok": "...",
    "youtube": "..."
  }},
  "extracted_keywords": ["kw1", "kw2", "..."]
}}
"""


async def generate_query(state: AgentState, config: RunnableConfig) -> dict:
    emit = config.get("configurable", {}).get("emit")

    await emit("step_started", {"step": "query_gen", "label": "Generating Queries"})

    client = anthropic.AsyncAnthropic()

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": _PROMPT.format(user_input=state["user_input"]),
        }],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if Claude adds them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    parsed = json.loads(raw.strip())

    await emit("query_generated", {
        "intent_prompt": parsed["intent_prompt"],
        "boolean_queries": parsed["boolean_queries"],
        "extracted_keywords": parsed.get("extracted_keywords", []),
    })
    await emit("step_completed", {"step": "query_gen"})

    return {
        "intent_prompt": parsed["intent_prompt"],
        "boolean_queries": parsed["boolean_queries"],
        "extracted_keywords": parsed.get("extracted_keywords", []),
    }

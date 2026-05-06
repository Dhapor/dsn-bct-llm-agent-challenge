"""
Task B — Agentic Recommendation Engine.

Multi-step agentic workflow using Claude tool use:
  Tool 1: search_items(query, category, limit) → retrieves candidates from vector store
  Tool 2: get_item_details(item_id) → fetches full item metadata
  Tool 3: score_item(item_id, reasons) → logs agent's scoring rationale

The agent reasons across multiple turns before producing a final ranked list.
Handles: cold-start (no history), cross-domain, and multi-turn conversation.
"""

import os
import sys
import json
from typing import Any

import anthropic

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from shared.user_profiler import build_user_profile, profile_to_prompt_context
from shared.nigerian_adapter import get_nigerian_persona_prompt, get_nigerian_recommendation_context
from shared.vector_store import ItemVectorStore
from shared.sample_catalog import get_all_items, get_item_by_id

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"

# Initialise vector store once at module load
_store = ItemVectorStore()
_store.add_items(get_all_items())


# --- Tool definitions for the agent ---

TOOLS = [
    {
        "name": "search_items",
        "description": (
            "Search the item catalog for candidates matching a query. "
            "Returns a ranked list of items. Use this to retrieve candidates "
            "based on the user's stated preferences, history, or inferred interests."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query describing what the user might like",
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter: restaurant, book, movie, electronics, music, household",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of results to return (default 10, max 20)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_item_details",
        "description": "Get full metadata for a specific item by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The item ID to retrieve",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "finalize_recommendations",
        "description": (
            "Submit the final ranked list of recommendations. Call this ONCE when you have "
            "reasoned through the candidates and are ready to produce the final output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "description": "Ordered list of recommendations (best first)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "score": {
                                "type": "number",
                                "description": "Relevance score 0-1",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Personalised explanation in the user's voice/context (1-2 sentences)",
                            },
                        },
                        "required": ["item_id", "name", "score", "reason"],
                    },
                },
                "overall_reasoning": {
                    "type": "string",
                    "description": "2-3 sentence summary of recommendation strategy for this user",
                },
                "cold_start_strategy": {
                    "type": "string",
                    "description": "If cold-start (no history): describe what signals were used instead",
                },
            },
            "required": ["recommendations", "overall_reasoning"],
        },
    },
]


# --- Tool execution ---

def _execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "search_items":
        query = tool_input["query"]
        category = tool_input.get("category")
        limit = min(int(tool_input.get("limit", 10)), 20)
        results = _store.search(query, top_k=limit, category_filter=category)
        simplified = [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "category": r.get("category"),
                "description": r.get("description", "")[:120],
                "avg_rating": r.get("avg_rating"),
                "tags": r.get("tags", []),
            }
            for r in results
        ]
        return json.dumps(simplified, indent=2)

    elif tool_name == "get_item_details":
        item_id = tool_input["item_id"]
        item = get_item_by_id(item_id)
        if item:
            return json.dumps(item, indent=2)
        return json.dumps({"error": f"Item {item_id} not found"})

    elif tool_name == "finalize_recommendations":
        # This is a signal tool — the agent's output is extracted from this call
        return json.dumps({"status": "recommendations_received"})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


# --- Main agent loop ---

def get_recommendations(
    user_persona: dict[str, Any],
    context: dict[str, Any] | None = None,
    num_recommendations: int = 5,
    conversation_history: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Agentic recommendation with multi-turn support.
    conversation_history: list of {role, content} dicts for multi-turn.
    """
    profile = build_user_profile(user_persona)
    user_context = profile_to_prompt_context(profile)
    nigerian_ctx = get_nigerian_persona_prompt(profile["location"], profile["uses_pidgin"])
    nigerian_rec_ctx = get_nigerian_recommendation_context(profile["location"])

    is_cold_start = profile["review_count"] == 0

    system_prompt = f"""{nigerian_ctx}

You are an expert recommendation agent for a Nigerian user.

{nigerian_rec_ctx}

Your task is to deliver highly personalised recommendations using an agentic search-and-reason workflow:
1. ANALYSE the user profile to understand their preferences, style, and context
2. SEARCH for candidates using the search_items tool (run multiple searches across domains if helpful)
3. REASON about fit — how well does each candidate match this specific user?
4. FINALISE by calling finalize_recommendations with your top {num_recommendations} picks, ranked

{'COLD START: This user has no review history. Use location, stated preferences, and demographic signals.' if is_cold_start else ''}

Be specific in your reasoning. Generic recommendations are penalised. Reference the user's actual preferences.
Think cross-domain — a user who likes Afrobeats music might enjoy certain restaurants with live music."""

    user_message = f"""USER PROFILE:
{user_context}

CONTEXT/REQUEST:
{json.dumps(context or {}, indent=2)}

Please search for and recommend {num_recommendations} items this user would genuinely enjoy.
Use multiple tool calls to explore different categories and angles before finalising."""

    messages: list[dict[str, Any]]
    if conversation_history:
        messages = conversation_history + [{"role": "user", "content": user_message}]
    else:
        messages = [{"role": "user", "content": user_message}]

    final_recommendations = None
    tool_calls_log = []
    max_iterations = 8

    for iteration in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            messages=messages,
        )

        # Append assistant response to message history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_calls_log.append({"tool": tool_name, "input": tool_input})

                    result = _execute_tool(tool_name, tool_input)

                    # Capture finalize call
                    if tool_name == "finalize_recommendations":
                        final_recommendations = tool_input

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

            if final_recommendations:
                break

    if not final_recommendations:
        # Fallback: extract from last text response
        final_recommendations = _fallback_recommendations(profile, num_recommendations)

    return {
        "recommendations": final_recommendations.get("recommendations", []),
        "overall_reasoning": final_recommendations.get("overall_reasoning", ""),
        "cold_start_strategy": final_recommendations.get("cold_start_strategy", ""),
        "is_cold_start": is_cold_start,
        "tool_calls": tool_calls_log,
        "user_profile_summary": {
            "name": profile["name"],
            "location": profile["location"],
            "avg_rating": profile["avg_rating"],
            "top_categories": profile["top_categories"],
        },
        "updated_conversation": messages,
    }


def _fallback_recommendations(profile: dict[str, Any], n: int) -> dict[str, Any]:
    """Keyword-based fallback if the agent loop doesn't produce structured output."""
    query = " ".join(profile["top_categories"] + profile["stated_preferences"] + [profile["location"]])
    results = _store.search(query or "popular nigerian", top_k=n)
    recs = [
        {
            "item_id": r.get("id", ""),
            "name": r.get("name", ""),
            "category": r.get("category", ""),
            "score": 0.5,
            "reason": f"Matches your interest in {r.get('category', 'this category')}.",
        }
        for r in results
    ]
    return {
        "recommendations": recs,
        "overall_reasoning": "Fallback keyword-based recommendations based on user profile.",
    }

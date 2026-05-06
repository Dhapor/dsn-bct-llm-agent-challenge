"""
Core agent for Task A: User Modeling.
Generates a simulated review (text + star rating) for a given user and item.

Agentic workflow:
  1. Build user profile from history
  2. Inject Nigerian cultural context
  3. Call Claude to reason about the user's likely experience
  4. Extract structured output (rating + review text)
"""

import os
import re
import sys
import json
from typing import Any

import anthropic

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from shared.user_profiler import build_user_profile, profile_to_prompt_context
from shared.nigerian_adapter import get_nigerian_persona_prompt

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"


SYSTEM_PROMPT_TEMPLATE = """{nigerian_context}

You are simulating a specific user writing an online review. Your job is to produce an authentic,
behaviorally faithful review that matches this user's real voice, rating patterns, and preferences.

Key principles:
- The rating should be consistent with their historical avg ({avg_rating:.1f}/5) unless the item clearly
  warrants deviation
- Match the user's typical review length (~{review_length} words)
- Capture their tone exactly — do not genericise
- If the item has characteristics the user specifically likes/dislikes, that drives the rating
- Nigerian cultural nuance and references should feel organic, never forced

Output ONLY valid JSON in this exact format:
{{
  "rating": <float 1.0-5.0, one decimal place>,
  "review": "<review text>",
  "reasoning": "<2-3 sentences explaining why this rating and tone were chosen>"
}}
"""


def generate_review(
    user_persona: dict[str, Any],
    product_details: dict[str, Any],
) -> dict[str, Any]:
    """
    Main entry point for Task A.
    Returns: {rating, review, reasoning, user_profile_summary}
    """
    profile = build_user_profile(user_persona)
    user_context = profile_to_prompt_context(profile)
    nigerian_ctx = get_nigerian_persona_prompt(
        user_location=profile["location"],
        uses_pidgin=profile["uses_pidgin"],
    )

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        nigerian_context=nigerian_ctx,
        avg_rating=profile["avg_rating"],
        review_length=profile["avg_review_length"],
    )

    item_description = _format_item(product_details)

    user_message = f"""USER PROFILE:
{user_context}

ITEM TO REVIEW:
{item_description}

Generate a review this user would write for this item. Remember: simulate their authentic voice,
not a generic reviewer. Output only JSON."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # Cache system prompt
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    result = _parse_json_output(raw)
    result["user_profile_summary"] = {
        "avg_rating": profile["avg_rating"],
        "uses_pidgin": profile["uses_pidgin"],
        "location": profile["location"],
        "review_count": profile["review_count"],
    }
    return result


def _format_item(product: dict[str, Any]) -> str:
    lines = []
    for key in ["name", "category", "cuisine", "description", "price_range", "location", "avg_rating", "tags"]:
        val = product.get(key)
        if val:
            lines.append(f"  {key}: {val}")
    return "\n".join(lines) if lines else str(product)


def _parse_json_output(text: str) -> dict[str, Any]:
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    try:
        data = json.loads(text)
        # Validate and clamp rating
        rating = float(data.get("rating", 3.0))
        rating = max(1.0, min(5.0, round(rating * 2) / 2))  # Round to nearest 0.5
        data["rating"] = rating
        return data
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # Fallback: extract rating with regex
        rating_match = re.search(r'"rating"\s*:\s*([0-9.]+)', text)
        review_match = re.search(r'"review"\s*:\s*"([^"]+)"', text)
        reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]+)"', text)
        return {
            "rating": float(rating_match.group(1)) if rating_match else 3.0,
            "review": review_match.group(1) if review_match else text[:500],
            "reasoning": reasoning_match.group(1) if reasoning_match else "Could not parse structured output.",
            "parse_error": str(e),
        }

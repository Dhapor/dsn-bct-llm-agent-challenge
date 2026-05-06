"""
Builds a structured user profile from review history.
Used by both Task A (review generation) and Task B (recommendations).
"""

from typing import Any
import statistics


def build_user_profile(persona: dict[str, Any]) -> dict[str, Any]:
    """
    Derives tone, rating tendencies, and preference signals from a user persona dict.
    Expects persona to have: name, location, review_history (list of dicts), preferences (optional).
    """
    history = persona.get("review_history", [])

    ratings = [r["rating"] for r in history if "rating" in r]
    avg_rating = round(statistics.mean(ratings), 2) if ratings else 3.0
    rating_std = round(statistics.stdev(ratings), 2) if len(ratings) > 1 else 0.5

    # Derive vocabulary style from existing reviews
    all_reviews = " ".join(r.get("review", "") for r in history)
    word_count = len(all_reviews.split()) if all_reviews else 0
    avg_review_length = round(word_count / len(history), 0) if history else 80

    # Detect if user already writes in Nigerian Pidgin/slang
    nigerian_markers = ["abeg", "oga", "e don", "sharp sharp", "na wa", "nawa", "chai", "mehn", "omo", "wahala"]
    uses_pidgin = any(marker in all_reviews.lower() for marker in nigerian_markers)

    # Category preferences
    categories = [r.get("category", "") for r in history if r.get("category")]
    category_counts: dict[str, int] = {}
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
    top_categories = sorted(category_counts, key=category_counts.get, reverse=True)[:5]  # type: ignore

    return {
        "user_id": persona.get("user_id", "unknown"),
        "name": persona.get("name", "User"),
        "location": persona.get("location", "Nigeria"),
        "avg_rating": avg_rating,
        "rating_std": rating_std,
        "avg_review_length": int(avg_review_length),
        "uses_pidgin": uses_pidgin,
        "top_categories": top_categories,
        "stated_preferences": persona.get("preferences", []),
        "review_count": len(history),
        "sample_reviews": history[-3:],  # last 3 reviews as style reference
    }


def profile_to_prompt_context(profile: dict[str, Any]) -> str:
    """Converts a user profile into a concise prompt-ready context string."""
    lines = [
        f"User: {profile['name']} from {profile['location']}",
        f"Review history: {profile['review_count']} reviews",
        f"Average rating they give: {profile['avg_rating']:.1f}/5 (std: {profile['rating_std']:.1f})",
        f"Typical review length: ~{profile['avg_review_length']} words",
        f"Top categories: {', '.join(profile['top_categories']) if profile['top_categories'] else 'general'}",
        f"Stated preferences: {', '.join(profile['stated_preferences']) if profile['stated_preferences'] else 'none specified'}",
    ]
    if profile["uses_pidgin"]:
        lines.append("Writing style: Uses Nigerian Pidgin English naturally")
    if profile["sample_reviews"]:
        lines.append("Sample past reviews:")
        for rev in profile["sample_reviews"]:
            lines.append(f"  - [{rev.get('rating', '?')}/5] {rev.get('item', 'item')}: \"{rev.get('review', '')}\"")
    return "\n".join(lines)

"""
RAG-based AI explainer using OpenRouter (via the OpenAI-compatible API).

Flow:
  1. Retrieve  — top songs are already scored and retrieved by recommender.py
  2. Augment   — those songs are formatted into a prompt as context
  3. Generate  — the LLM reads the context and writes a personalized explanation
"""

import logging
import os
from typing import Dict, List, Tuple

from openai import OpenAI

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL    = "openai/gpt-oss-120b:free"


def _format_song_context(songs_with_scores: List[Tuple]) -> str:
    """Format retrieved songs into a readable block for the prompt."""
    lines = []
    for i, (song, score, _) in enumerate(songs_with_scores, 1):
        lines.append(
            f"{i}. \"{song['title']}\" by {song['artist']} "
            f"(Genre: {song['genre']}, Mood: {song['mood']}, "
            f"Energy: {song['energy']:.2f}, Acousticness: {song['acousticness']:.2f}, "
            f"Match score: {score:.2f}/7.0)"
        )
    return "\n".join(lines)


def get_ai_explanation(user_prefs: Dict, songs_with_scores: List[Tuple]) -> str:
    """
    Send retrieved songs + user preferences to GPT and return a
    conversational explanation of why the songs are a good fit.

    Args:
        user_prefs: dict with keys genre, mood, energy, likes_acoustic
        songs_with_scores: list of (song_dict, score, reasons) tuples

    Returns:
        AI-generated explanation string, or a fallback message on error.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable is not set")
        return "AI explanation unavailable: OPENROUTER_API_KEY is not configured."

    try:
        client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
    except Exception as e:
        logger.error("Failed to initialize OpenRouter client: %s", e)
        return "AI explanation unavailable: could not connect to OpenRouter."

    acoustic_label = (
        "yes" if user_prefs.get("likes_acoustic") is True
        else "no" if user_prefs.get("likes_acoustic") is False
        else "no preference"
    )

    song_context = _format_song_context(songs_with_scores)

    prompt = (
        "You are a friendly music recommendation assistant.\n\n"
        "A user described their music taste:\n"
        f"  - Favorite genre: {user_prefs.get('genre', 'any')}\n"
        f"  - Favorite mood: {user_prefs.get('mood', 'any')}\n"
        f"  - Energy level: {user_prefs.get('energy', 0.5):.2f} "
        "(0.0 = very calm, 1.0 = very energetic)\n"
        f"  - Likes acoustic music: {acoustic_label}\n\n"
        "Based on those preferences, the system retrieved these songs:\n"
        f"{song_context}\n\n"
        "Write 2-3 friendly sentences explaining why these songs are a great match. "
        "Reference specific features (genre, mood, energy, acousticness) to justify the picks. "
        "Keep the tone warm and concise."
    )

    logger.info(
        "Sending %d retrieved songs to OpenAI for user prefs: %s",
        len(songs_with_scores),
        user_prefs,
    )

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        logger.info("OpenRouter response received successfully")
        return response.choices[0].message.content
    except Exception as e:
        logger.error("OpenRouter API call failed: %s", e)
        return "AI explanation unavailable. See rule-based reasons above."

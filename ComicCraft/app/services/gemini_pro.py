from __future__ import annotations

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_STORY_MODEL
from app.schemas import ComicStory


def _client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=GEMINI_API_KEY)


def _mock_story(outline: list[dict]) -> list[dict]:
    result = []
    for p in outline:
        result.append(
            {
                "panel": p["panel"],
                "title": p["title"],
                "scene_description": p["scene_description"],
                "caption": "The moment hangs in the air as the adventure moves forward.",
                "narration": p["scene_description"] + " The character gathers courage and keeps moving.",
                "dialogue": '“I can do this.”',
                "image_prompt": p["image_prompt"],
            }
        )
    return result


def generate_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    """Expand the outline into panel-by-panel narration and dialogue."""
    if not GEMINI_API_KEY:
        return _mock_story(outline)

    prompt = f"""
You are the lead comic-book writer.
Main character: {character_name}
Tone: {tone}

Expand the following panel outline into a polished five-panel comic.
For every panel provide:
- panel number and title
- scene description
- short atmospheric caption
- narration in comic-book prose
- concise character dialogue
- the original image prompt, improved only when needed for visual consistency

Keep continuity between panels. Dialogue must be natural and concise.
Do not put markdown headings around the response; return only structured data.

OUTLINE:
{outline}
"""
    client = _client()
    response = client.models.generate_content(
        model=GEMINI_STORY_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicStory,
            temperature=0.85,
        ),
    )
    story = ComicStory.model_validate_json(response.text)
    return [panel.model_dump() for panel in story.panels]

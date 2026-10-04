from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_OUTLINE_MODEL, MAX_PANELS
from app.schemas import ComicOutline


def _client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=GEMINI_API_KEY)


def _mock_outline(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> list[dict[str, Any]]:
    beats = [
        ("The Beginning", f"{character_name} discovers an unexpected clue in {setting}."),
        ("The Challenge", f"A difficult obstacle appears, forcing {character_name} to act."),
        ("The Turning Point", f"{character_name} finds a clever way through the problem."),
        ("The Choice", f"A final decision changes the direction of the adventure."),
        ("The New Dawn", f"{character_name} reaches a meaningful ending and looks toward what comes next."),
    ]
    return [
        {
            "panel": i + 1,
            "title": title,
            "scene_description": description,
            "image_prompt": (
                f"Comic panel, {art_style}, {tone} mood, {setting}. Main character {character_name}. "
                f"Story idea: {story_prompt}. Scene: {description}. Cinematic composition, expressive character, "
                "clean linework, detailed background, no text, no speech bubbles."
            ),
        }
        for i, (title, description) in enumerate(beats)
    ]


def generate_outline(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> list[dict[str, Any]]:
    """Generate a strict five-panel outline using Gemini structured output."""
    if not GEMINI_API_KEY:
        return _mock_outline(story_prompt, character_name, setting, tone, art_style)

    prompt = f"""
Create exactly {MAX_PANELS} sequential comic panels.
Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Make the story coherent from panel 1 through panel {MAX_PANELS}.
- Each panel must have a short title, vivid scene description, and a production-ready image prompt.
- Keep the same main character visually consistent across panels.
- Do not put written dialogue or captions inside the image prompt.
- Return only the requested structured data.
"""

    client = _client()
    response = client.models.generate_content(
        model=GEMINI_OUTLINE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
            temperature=0.9,
        ),
    )
    data = ComicOutline.model_validate_json(response.text)
    panels = data.panels[:MAX_PANELS]
    if len(panels) != MAX_PANELS:
        raise ValueError(f"Gemini returned {len(panels)} panels; expected {MAX_PANELS}.")
    return [panel.model_dump() for panel in panels]

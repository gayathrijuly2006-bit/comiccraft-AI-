from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=4000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=1, max_length=200)
    tone: str = Field(..., min_length=1, max_length=100)
    art_style: str = Field(..., min_length=1, max_length=150)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value


class PanelOutline(BaseModel):
    panel: int = Field(..., ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[PanelOutline]


class PanelStory(BaseModel):
    panel: int = Field(..., ge=1, le=5)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicStory(BaseModel):
    panels: List[PanelStory]

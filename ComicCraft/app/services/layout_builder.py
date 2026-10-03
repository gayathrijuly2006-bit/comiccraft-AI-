from __future__ import annotations


def build_comic_layout(image_paths: list[str], story: list[dict], outline: list[dict]) -> list[dict]:
    """Join image URLs with the corresponding panel story and metadata."""
    layout = []
    for index, panel in enumerate(story):
        outline_item = outline[index] if index < len(outline) else {}
        layout.append(
            {
                "panel": panel.get("panel", index + 1),
                "title": panel.get("title") or outline_item.get("title", f"Panel {index + 1}"),
                "image_path": image_paths[index] if index < len(image_paths) else "",
                "scene_description": panel.get("scene_description", outline_item.get("scene_description", "")),
                "caption": panel.get("caption", ""),
                "narration": panel.get("narration", ""),
                "dialogue": panel.get("dialogue", ""),
                "image_prompt": panel.get("image_prompt", outline_item.get("image_prompt", "")),
            }
        )
    return layout

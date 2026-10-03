from __future__ import annotations

import hashlib
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import (
    HF_PROVIDER,
    HF_TOKEN,
    IMAGE_BACKEND,
    IMAGE_HEIGHT,
    IMAGE_MODEL,
    IMAGE_WIDTH,
    LOCAL_IMAGE_MODEL,
    PANELS_DIR,
)


def sanitize_filename(value: str, max_len: int = 60) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return (cleaned[:max_len] or "panel")


def _mock_image(prompt: str, path: Path) -> None:
    """Create a deterministic placeholder so the app is testable without AI keys."""
    digest = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "#eef2ff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((35, 35, IMAGE_WIDTH - 35, IMAGE_HEIGHT - 35), outline="#334155", width=5)
    draw.text((60, 70), "COMICCRAFT DEMO PANEL", fill="#0f172a")
    wrapped = prompt[:450]
    draw.multiline_text((60, 130), wrapped, fill="#334155", spacing=8)
    draw.text((60, IMAGE_HEIGHT - 90), f"Demo image • {digest[:10]}", fill="#64748b")
    img.save(path, format="PNG")


def _hf_image(prompt: str) -> Image.Image:
    from huggingface_hub import InferenceClient

    client = InferenceClient(provider=HF_PROVIDER, api_key=HF_TOKEN)
    return client.text_to_image(prompt=prompt, model=IMAGE_MODEL)


def _local_image(prompt: str) -> Image.Image:
    from diffusers import StableDiffusionPipeline
    import torch

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(LOCAL_IMAGE_MODEL, torch_dtype=dtype)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    return pipe(prompt).images[0]


def generate_image(prompt: str, filename: str | None = None) -> str:
    """Generate an illustration and return a browser-relative static path."""
    if not filename:
        filename = sanitize_filename(prompt) + ".png"
    elif not filename.lower().endswith(".png"):
        filename += ".png"

    output_path = PANELS_DIR / filename
    backend = IMAGE_BACKEND

    if backend == "mock" or (backend == "hf" and not HF_TOKEN):
        _mock_image(prompt, output_path)
    elif backend == "hf":
        image = _hf_image(prompt)
        image.save(output_path, format="PNG")
    elif backend == "local":
        image = _local_image(prompt)
        image.save(output_path, format="PNG")
    else:
        raise ValueError("IMAGE_BACKEND must be one of: hf, local, mock")

    return f"/static/panels/{output_path.name}"

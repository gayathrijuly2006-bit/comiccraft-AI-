from __future__ import annotations

import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, MAX_PANELS
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _generate_comic(payload: PromptRequest) -> tuple[list[dict], str]:
    outline = generate_outline(
        payload.story_prompt,
        payload.character_name,
        payload.setting,
        payload.tone,
        payload.art_style,
    )
    story = generate_story(outline, payload.character_name, payload.tone)
    image_paths = []
    for panel in story:
        prompt = panel.get("image_prompt") or outline[len(image_paths)].get("image_prompt", "")
        image_paths.append(generate_image(prompt, f"panel_{len(image_paths) + 1}.png"))
    layout = build_comic_layout(image_paths, story, outline)
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"max_panels": MAX_PANELS})


@router.post("/generate", response_class=HTMLResponse)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout, pdf_path = _generate_comic(payload)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": layout, "pdf_path": pdf_path, "request_data": payload.model_dump()},
        )
    except Exception as exc:
        logger.exception("Comic generation failed")
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        layout, pdf_path = _generate_comic(payload)
        return JSONResponse({"success": True, "layout": layout, "pdf_path": pdf_path})
    except Exception as exc:
        logger.exception("JSON comic generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/test-image")
async def test_image(prompt: str = "A heroic fox exploring an enchanted forest, comic book art"):
    try:
        image_path = generate_image(prompt, "test_panel.png")
        return {"success": True, "image_path": image_path, "prompt": prompt}
    except Exception as exc:
        logger.exception("Image test failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = "/static/exports/latest.pdf"):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_path": pdf_path},
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}

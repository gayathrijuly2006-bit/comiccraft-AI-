# ComicCraft — AI Comic Generator

ComicCraft turns a short story idea into a five-panel comic with structured story planning, narration/dialogue, AI illustrations and a downloadable PDF.

## Architecture

Browser → FastAPI → Gemini outline → Gemini story → Hugging Face image generation → layout builder → FPDF PDF export.

The source documentation specifies FastAPI/Uvicorn, Jinja2, Gemini Flash/Pro, Hugging Face Diffusers/Stable Diffusion and FPDF. This implementation keeps that architecture while using the current `google-genai` SDK and configurable current model IDs. It also includes a mock mode so the full application can be tested without API keys.

## Quick start (Windows / VS Code)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

If PowerShell blocks activation, you do not need to activate the environment: the commands above invoke the venv Python directly.

## AI configuration

For a real generation run, put a Gemini API key in `GEMINI_API_KEY` and a Hugging Face token in `HF_TOKEN`.

- `IMAGE_BACKEND=hf`: hosted Hugging Face text-to-image.
- `IMAGE_BACKEND=local`: local Diffusers pipeline; install `requirements-local-diffusion.txt` and expect a large model download.
- `IMAGE_BACKEND=mock`: deterministic placeholder images for development/testing.
- `USE_MOCK_AI=auto`: Gemini is used when configured; otherwise deterministic story content is used.

## API endpoints

- `GET /` — homepage
- `POST /generate` — HTML form generation
- `POST /generate-comic/json` — JSON API generation
- `GET /test-image?prompt=...` — image-generation test
- `GET /export-success` — export confirmation page
- `GET /health` — health check
- `GET /docs` — Swagger UI

## Testing

With the server running:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

Then test the JSON endpoint from Swagger UI or PowerShell. Without API keys, set `IMAGE_BACKEND=mock` in `.env`; the complete workflow still runs and produces a PDF.

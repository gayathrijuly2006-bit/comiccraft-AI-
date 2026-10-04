# ComicCraft AI

Five-panel AI comic generator using Streamlit and Google Gemini.

## Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m streamlit run streamlit_app.py
```

Put a NEW Gemini API key in `.env`. Never commit `.env`.

## Streamlit Cloud

Main file: `ComicCraft/streamlit_app.py`

Secrets:

```toml
GEMINI_API_KEY = "YOUR_NEW_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
```

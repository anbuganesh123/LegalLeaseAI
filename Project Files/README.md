# LegalEase — AI-Powered Legal Document Generator

LegalEase is the FastAPI + Streamlit + Google Gemini application described in the supplied project documentation. It accepts document type, parties, terms and effective-date details, generates a legal draft, lets the user edit it, previews it with formatting, and exports TXT, DOCX and PDF.

## Frontend update

The frontend no longer exposes backend URL details or a **Check Backend** control. The FastAPI service remains an internal application component because the supplied architecture calls for Streamlit → FastAPI → Gemini. Users only interact with the LegalEase workspace.

The document preview now renders `**bold**`, `*italic*`, headings, lists and numbered clauses correctly. DOCX and PDF exports also apply inline bold/italic formatting instead of leaving Markdown markers visible. TXT exports remove Markdown markers for clean plain text.

## Gemini configuration

The included `.env` is intentionally present. There is **no `.env.example` and no `.gitignore`** in this package.

Set your Google AI Studio / Gemini API key in `.env`:

```env
GEMINI_API_KEY=YOUR_REAL_GEMINI_API_KEY
GEMINI_MODEL=auto
GEMINI_FALLBACK_MODELS=gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.8-flash
DEMO_MODE=false
BACKEND_URL=http://127.0.0.1:8000
```

`GEMINI_MODEL=auto` makes the backend select from configured/current accessible models instead of depending on the retired Gemini 1.5 model from the older source document.

## VS Code — final terminal steps

Open the extracted `LegalEase` folder in VS Code.

### Terminal 1 — FastAPI backend

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Streamlit frontend

VS Code → **Terminal → New Terminal**

```powershell
.\\.venv\\Scripts\\Activate.ps1
python -m streamlit run frontend/app.py
```

Then open:

```text
http://localhost:8501
```

The backend remains at `http://127.0.0.1:8000`, but its URL/check controls are intentionally hidden from the frontend user interface.

## Test

```powershell
python -m pytest -q
```

## Project structure

```text
LegalEase/
├── .env
├── .streamlit/
│   └── config.toml
├── assets/
│   └── logo.png
├── backend/
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── config.py
│   ├── ai_core/
│   │   └── gemini_generator.py
│   ├── services/
│   │   ├── docx_formatter.py
│   │   ├── pdf_formatter.py
│   │   ├── txt_formatter.py
│   │   └── exporters.py
│   └── utils/
│       └── text.py
├── frontend/
│   └── app.py
├── tests/
├── requirements.txt
├── Dockerfile
├── Procfile
├── run_backend.bat
├── run_backend.sh
├── run_frontend.bat
└── run_frontend.sh
```

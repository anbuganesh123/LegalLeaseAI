from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .ai_core.gemini_generator import GeminiDocumentGenerator
from .config import settings
from .schemas import DocumentRequest, DocumentResponse

router = APIRouter(tags=["LegalEase"])
generator = GeminiDocumentGenerator()


@router.get("/", summary="API home")
def home() -> dict[str, str]:
    return {
        "message": "LegalEase AI Legal Document Generator API is running",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health", summary="Health check")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "demo_mode": settings.demo_mode,
        "gemini_configured": bool(
            settings.gemini_api_key
            and settings.gemini_api_key != "PASTE_YOUR_GEMINI_API_KEY_HERE"
        ),
        "model": settings.gemini_model,
        "fallback_models": list(settings.gemini_fallback_models),
        "configured_primary": settings.gemini_model,
    }


@router.post("/generate", response_model=DocumentResponse, summary="Generate a legal document")
def generate_document(request: DocumentRequest) -> DocumentResponse:
    try:
        if settings.demo_mode:
            document = generator.demo_document(
                request.document_type,
                request.parties,
                request.terms,
                request.dates,
            )
            return DocumentResponse(
                document=document,
                document_type=request.document_type,
                demo_mode=True,
                model=None,
            )

        document = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
        return DocumentResponse(
            document=document,
            document_type=request.document_type,
            demo_mode=False,
            model=generator.last_model_used or settings.gemini_model,
        )
    except Exception as exc:  # noqa: BLE001 - expose provider error to UI as API detail
        raise HTTPException(status_code=502, detail=str(exc)) from exc

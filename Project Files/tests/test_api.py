from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend import routes
from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"].startswith("LegalEase")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model"]
    assert isinstance(body["fallback_models"], list)


def test_validation_rejects_blank_fields():
    response = client.post(
        "/generate",
        json={"document_type": "", "parties": "x", "terms": "y", "dates": "z"},
    )
    assert response.status_code == 422


def test_demo_generation(monkeypatch):
    original = routes.settings
    demo_settings = SimpleNamespace(
        app_name=original.app_name,
        app_version=original.app_version,
        gemini_api_key=original.gemini_api_key,
        gemini_model=original.gemini_model,
        gemini_fallback_models=original.gemini_fallback_models,
        demo_mode=True,
        backend_url=original.backend_url,
        max_document_type=original.max_document_type,
        max_parties=original.max_parties,
        max_terms=original.max_terms,
        max_dates=original.max_dates,
    )
    monkeypatch.setattr(routes, "settings", demo_settings)

    response = client.post(
        "/generate",
        json={
            "document_type": "Non-Disclosure Agreement",
            "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
            "terms": "Confidentiality; Return materials within 30 days; 15 days termination notice",
            "dates": "September 23, 2026",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "Non-Disclosure Agreement"
    assert "Non-Disclosure Agreement" in body["document"]
    assert body["demo_mode"] is True

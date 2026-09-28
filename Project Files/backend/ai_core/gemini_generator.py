from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

from ..config import settings
from ..utils.text import sanitize_text, terms_to_list

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None


@dataclass
class GeminiDocumentGenerator:
    """Generate LegalEase drafts using the current Google GenAI SDK.

    The generator deliberately avoids hard-coding retired/legacy Gemini models.
    It first checks which configured text-generation models are actually exposed
    to the user's API key, then retries temporary 429/503 provider errors before
    falling back to another accessible model.
    """

    api_key: str | None = None
    model_name: str | None = None
    fallback_models: tuple[str, ...] | None = None
    retry_count: int = 2

    # Current stable text-generation models documented by Google.
    # Ordering favors generally available Flash models and keeps a more capable
    # model available when the API key has access to it.
    DEFAULT_MODEL_CANDIDATES = (
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
    )

    def __post_init__(self) -> None:
        self.api_key = (self.api_key or settings.gemini_api_key).strip()
        self.model_name = (self.model_name or settings.gemini_model).strip()
        self.fallback_models = tuple(self.fallback_models or settings.gemini_fallback_models)
        self._client = None
        self.last_model_used: str | None = None
        self.last_attempts: list[str] = []

    def _client_or_raise(self):
        if not self.api_key or self.api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Put your real Google Gemini API key in the project's .env file."
            )
        if genai is None:
            raise RuntimeError(
                "The current Google GenAI SDK is not installed. Run 'python -m pip install -r requirements.txt'."
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @staticmethod
    def build_prompt(document_type: str, parties: str, terms: str, dates: str) -> str:
        term_list = terms_to_list(terms)
        terms_block = "\n".join(f"- {item}" for item in term_list) or "- [INSERT AGREED TERMS]"
        return f"""You are LegalEase, an AI-powered legal document generator.

Create a comprehensive professional draft of the requested legal document using only the supplied information.
Do not invent names, addresses, payment amounts, dates, duties, governing law, or any other material facts.
When information is missing, use a clear placeholder in square brackets instead of guessing.
Use formal legal language, clear headings, numbered clauses, and signature blocks where appropriate.
Preserve every user-requested term and incorporate it into a coherent document.

DOCUMENT TYPE:
{sanitize_text(document_type)}

PARTIES INVOLVED:
{sanitize_text(parties)}

EFFECTIVE DATE / DATE DETAILS:
{sanitize_text(dates)}

TERMS & CONDITIONS:
{terms_block}

OUTPUT REQUIREMENTS:
1. Start with the document title as a Markdown H1.
2. Use Markdown H2 headings for major sections.
3. Use numbered clauses where suitable.
4. Include definitions, obligations, confidentiality, payment, term/termination, dispute or governing-law provisions only when relevant and supported by the provided facts; otherwise use placeholders.
5. Include signature sections for the relevant parties.
6. End with a short 'Review Notes' section identifying material missing information or placeholders.
7. Return only the document draft. Do not discuss these instructions.
""".strip()

    def _configured_candidates(self) -> Iterable[str]:
        seen: set[str] = set()
        configured = [self.model_name, *self.fallback_models]
        for name in configured:
            model = (name or "").strip()
            if model and model.lower() != "auto" and model not in seen:
                seen.add(model)
                yield model

    def _available_generate_models(self) -> set[str] | None:
        """Return accessible generateContent model IDs when the API can list them.

        Some API-key configurations may restrict model listing. In that case we
        return None and let direct generation attempts decide model availability.
        """
        client = self._client_or_raise()
        try:
            available: set[str] = set()
            pager = client.models.list()
            for model in pager:
                name = str(getattr(model, "name", "") or "")
                methods = getattr(model, "supported_actions", None)
                if methods is None:
                    methods = getattr(model, "supported_generation_methods", None)
                method_names = {str(item).lower() for item in (methods or [])}
                if name.startswith("models/"):
                    short_name = name.split("/", 1)[1]
                else:
                    short_name = name
                if short_name and (not method_names or "generatecontent" in method_names):
                    available.add(short_name)
            return available or None
        except Exception:
            return None

    def _candidate_models(self) -> list[str]:
        configured = list(self._configured_candidates())
        if not configured:
            configured = list(self.DEFAULT_MODEL_CANDIDATES)

        # If the project is set to auto, use Google's currently exposed models.
        if (self.model_name or "").lower() == "auto":
            configured = list(self.DEFAULT_MODEL_CANDIDATES)

        available = self._available_generate_models()
        if not available:
            return configured

        accessible = [name for name in configured if name in available]

        # Add current stable candidates that are accessible even if the .env list
        # is stale. This is what prevents a new user from getting stuck on retired
        # or account-restricted models.
        for name in self.DEFAULT_MODEL_CANDIDATES:
            if name in available and name not in accessible:
                accessible.append(name)

        return accessible or configured

    @staticmethod
    def _is_temporary_provider_error(exc: Exception) -> bool:
        text = str(exc).lower()
        return any(token in text for token in ("503", "service unavailable", "high demand", "429", "rate limit", "resource exhausted"))

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        client = self._client_or_raise()
        prompt = self.build_prompt(document_type, parties, terms, dates)
        failures: list[str] = []
        self.last_attempts = []

        config = types.GenerateContentConfig(
            temperature=0.25,
            max_output_tokens=8192,
            system_instruction=(
                "You draft professional legal documents from user-supplied facts. "
                "Never fabricate material facts; use bracketed placeholders for missing information."
            ),
        )

        for model_name in self._candidate_models():
            for attempt in range(self.retry_count + 1):
                self.last_attempts.append(f"{model_name} (attempt {attempt + 1})")
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )
                    content = getattr(response, "text", None)
                    if content and content.strip():
                        self.last_model_used = model_name
                        return sanitize_text(content)
                    failures.append(f"{model_name}: empty response")
                    break
                except Exception as exc:  # provider errors vary by SDK/API version
                    if self._is_temporary_provider_error(exc) and attempt < self.retry_count:
                        time.sleep(1.5 * (2**attempt))
                        continue
                    failures.append(f"{model_name}: {exc}")
                    break

        raise RuntimeError(
            "Gemini generation failed. No currently accessible configured model returned content. "
            + " | ".join(failures)
            + " | Remove retired/restricted model IDs from .env, or set GEMINI_MODEL=auto."
        )

    @staticmethod
    def demo_document(document_type: str, parties: str, terms: str, dates: str) -> str:
        term_list = terms_to_list(terms)
        party_lines = [part.strip() for part in sanitize_text(parties).split(",") if part.strip()]
        party_text = ", ".join(party_lines) or "[INSERT PARTIES]"
        bullets = "\n".join(f"- {term}" for term in term_list) or "- [INSERT AGREED TERMS]"
        return sanitize_text(
            f"""# {sanitize_text(document_type)}

## 1. Parties
{party_text}

## 2. Effective Date
{sanitize_text(dates)}

## 3. Purpose
This draft records the principal terms supplied by the parties for the {sanitize_text(document_type)}.

## 4. Terms & Conditions
{bullets}

## 5. Additional Provisions
The parties should add all provisions required for their transaction and applicable jurisdiction, including any notices, representations, warranties, remedies, intellectual-property provisions, and dispute-resolution terms that are not specified above.

## 6. Signatures

Party 1: ______________________________    Date: __________________

Party 2: ______________________________    Date: __________________

## Review Notes
This is a local demonstration draft. Replace placeholders and review the document carefully before signing or relying on it.
"""
        )

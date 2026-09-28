from __future__ import annotations

from ..utils.text import sanitize_text, strip_markdown


def format_txt(text: str) -> bytes:
    return (strip_markdown(sanitize_text(text)) + "\n").encode("utf-8")

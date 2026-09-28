from __future__ import annotations

import html
import re
import unicodedata

SMART_REPLACEMENTS = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u2026": "...",
        "\u2022": "-",
        "\u00a9": "(c)",
        "\u00ae": "(r)",
        "\u2122": "(tm)",
    }
)

INLINE_MARKDOWN_RE = re.compile(r"(\*\*.+?\*\*|__.+?__|\*[^*\n]+?\*|_[^_\n]+?_|`[^`\n]+?`)")


def sanitize_text(text: str | None) -> str:
    """Clean text for legal-document rendering without changing its structure."""
    if text is None:
        return ""
    value = str(text).translate(SMART_REPLACEMENTS)
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\x00", "")
    value = re.sub(r"[\u0001-\u0008\u000B\u000C\u000E-\u001F\u007F]", "", value)
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{4,}", "\n\n\n", value)
    return value.strip()


def terms_to_list(terms: str | None) -> list[str]:
    """Convert semicolon-separated input into a clean list of terms."""
    if not terms:
        return []
    return [item for item in (sanitize_text(p) for p in terms.split(";")) if item]


def safe_filename(value: str, fallback: str = "legalease_document") -> str:
    cleaned = sanitize_text(value).lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")
    return cleaned or fallback


def strip_markdown(text: str) -> str:
    """Return clean text suitable for plain-text exports."""
    value = sanitize_text(text)
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", value)
    value = re.sub(r"__(.+?)__", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"\1", value)
    value = re.sub(r"(?<!_)_([^_\n]+?)_(?!_)", r"\1", value)
    value = re.sub(r"`([^`\n]+?)`", r"\1", value)
    return value


def markdown_to_runs(text: str) -> list[tuple[str, bool, bool, bool]]:
    """Parse simple inline Markdown into (text, bold, italic, code) runs."""
    value = sanitize_text(text)
    runs: list[tuple[str, bool, bool, bool]] = []
    last = 0
    for match in INLINE_MARKDOWN_RE.finditer(value):
        if match.start() > last:
            runs.append((value[last:match.start()], False, False, False))
        token = match.group(0)
        if token.startswith("**") and token.endswith("**"):
            runs.append((token[2:-2], True, False, False))
        elif token.startswith("__") and token.endswith("__"):
            runs.append((token[2:-2], True, False, False))
        elif token.startswith("*") and token.endswith("*"):
            runs.append((token[1:-1], False, True, False))
        elif token.startswith("_") and token.endswith("_"):
            runs.append((token[1:-1], False, True, False))
        elif token.startswith("`") and token.endswith("`"):
            runs.append((token[1:-1], False, False, True))
        last = match.end()
    if last < len(value):
        runs.append((value[last:], False, False, False))
    return runs or [(value, False, False, False)]


def markdown_to_html(text: str) -> str:
    """Render the supported Markdown subset safely for the browser preview."""
    escaped = html.escape(sanitize_text(text), quote=False)
    escaped = re.sub(r"`([^`\n]+?)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"__(.+?)__", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(r"(?<!_)_([^_\n]+?)_(?!_)", r"<em>\1</em>", escaped)
    return escaped


def format_html_preview(text: str) -> str:
    """Render headings, lists, numbered clauses and inline Markdown safely."""
    lines = sanitize_text(text).splitlines()
    output: list[str] = []
    in_list = False
    list_kind = None

    def close_list() -> None:
        nonlocal in_list, list_kind
        if in_list:
            output.append(f"</{list_kind}>")
            in_list = False
            list_kind = None

    for raw in lines:
        line = raw.strip()
        if not line:
            close_list()
            output.append("<div class='preview-spacer'></div>")
            continue
        if line.startswith("### "):
            close_list()
            output.append(f"<h3>{markdown_to_html(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            close_list()
            output.append(f"<h2>{markdown_to_html(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            close_list()
            output.append(f"<h1>{markdown_to_html(line[2:])}</h1>")
            continue
        if re.match(r"^[-*] ", line):
            if not in_list or list_kind != "ul":
                close_list()
                output.append("<ul>")
                in_list = True
                list_kind = "ul"
            output.append(f"<li>{markdown_to_html(line[2:])}</li>")
            continue
        if re.match(r"^\d+[.)] ", line):
            close_list()
            prefix, body = re.match(r"^(\d+[.)])\s+(.*)$", line).groups()
            output.append(f"<p class='numbered'><span class='clause-number'>{html.escape(prefix)}</span> {markdown_to_html(body)}</p>")
            continue
        close_list()
        output.append(f"<p>{markdown_to_html(line)}</p>")

    close_list()
    return "\n".join(output)

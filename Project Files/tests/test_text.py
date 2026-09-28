from backend.utils.text import format_html_preview, safe_filename, sanitize_text, terms_to_list


def test_sanitize_text():
    assert sanitize_text("Hello — “world”\x00") == 'Hello - "world"'


def test_terms_to_list():
    assert terms_to_list("A; B ; ; C") == ["A", "B", "C"]


def test_safe_filename():
    assert safe_filename("Employment Contract 2026") == "employment_contract_2026"


def test_html_preview_escapes_html():
    html = format_html_preview("# Title\n\n<script>alert(1)</script>")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_html_preview_renders_bold_markdown():
    html = format_html_preview("This is **bold** and *italic* text.")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html

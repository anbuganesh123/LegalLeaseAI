from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").strip().rstrip("/")
LOGO_PATH = PROJECT_ROOT / "assets" / "logo.png"

st.set_page_config(
    page_title="LegalEase | AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #0f172a;
        --muted: #64748b;
        --line: #e2e8f0;
        --surface: #ffffff;
        --soft: #f8fafc;
        --brand: #1d4ed8;
        --brand-dark: #153eaa;
        --accent: #0f766e;
        --success: #15803d;
    }
    .stApp { background: linear-gradient(180deg, #f8fbff 0%, #f5f7fb 48%, #ffffff 100%); }
    .block-container { max-width: 1280px; padding-top: 1rem; padding-bottom: 4rem; }
    [data-testid="stSidebar"] { background: #0b1220; border-right: 1px solid #172033; }
    [data-testid="stSidebar"] * { color: #e5edf8 !important; }
    [data-testid="stSidebar"] .stCaption { color: #9fb0c8 !important; }
    .brand-row { display:flex; align-items:center; gap:14px; margin: 4px 0 26px; }
    .brand-mark { width:42px; height:42px; border-radius:13px; display:flex; align-items:center; justify-content:center; background:#ffffff; box-shadow:0 8px 24px rgba(15,23,42,.12); overflow:hidden; }
    .brand-mark img { width:100%; height:100%; object-fit:cover; }
    .brand-name { font-size:1.18rem; font-weight:750; letter-spacing:-.02em; }
    .brand-sub { color:#93a4bd; font-size:.8rem; margin-top:2px; }
    .hero { background: radial-gradient(circle at top right, rgba(29,78,216,.12), transparent 34%), linear-gradient(135deg, #ffffff, #f8fbff); border:1px solid #e3eaf3; border-radius:26px; padding:34px 38px 30px; box-shadow:0 18px 60px rgba(15,23,42,.07); margin-bottom:24px; }
    .eyebrow { display:inline-flex; align-items:center; gap:8px; padding:7px 11px; border:1px solid #dbe5f2; background:#ffffff; border-radius:999px; color:#334155; font-size:.76rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    .eyebrow-dot { width:7px; height:7px; border-radius:50%; background:#10b981; box-shadow:0 0 0 5px rgba(16,185,129,.12); }
    .hero h1 { margin:15px 0 7px; color:var(--ink); font-size:clamp(2rem,4vw,3.3rem); line-height:1.04; letter-spacing:-.04em; }
    .hero p { margin:0; max-width:780px; color:#64748b; font-size:1.02rem; line-height:1.7; }
    .feature-strip { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:24px; }
    .feature { padding:14px 16px; border:1px solid #e5eaf1; background:rgba(255,255,255,.74); border-radius:15px; }
    .feature b { display:block; color:#0f172a; font-size:.88rem; margin-bottom:3px; }
    .feature span { color:#7a8799; font-size:.78rem; }
    .section-card { background:var(--surface); border:1px solid var(--line); border-radius:20px; padding:22px 22px 18px; box-shadow:0 10px 36px rgba(15,23,42,.045); margin-bottom:18px; }
    .section-title { color:#0f172a; font-size:1.1rem; font-weight:750; margin-bottom:3px; }
    .section-help { color:#7a8799; font-size:.8rem; margin-bottom:16px; }
    .field-label { font-size:.78rem; font-weight:750; color:#334155; margin:2px 0 7px; }
    .mini-badge { display:inline-block; margin-bottom:10px; padding:5px 9px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:.72rem; font-weight:700; }
    .generate-wrap { margin-top:2px; }
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button { border-radius:12px; min-height:48px; font-weight:750; letter-spacing:.01em; box-shadow:0 10px 20px rgba(29,78,216,.17); }
    div.stButton > button:not([kind="primary"]) { border-radius:11px; }
    .preview-shell { background:#0b1220; border:1px solid #1c2a42; border-radius:22px; padding:22px; box-shadow:inset 0 1px 0 rgba(255,255,255,.03), 0 12px 36px rgba(15,23,42,.13); }
    .preview-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
    .preview-label { color:#f8fafc; font-weight:750; }
    .preview-chip { color:#9fb0c8; font-size:.72rem; padding:5px 9px; border:1px solid #263654; border-radius:999px; }
    .preview-card { color:#e8eef8; max-height:660px; overflow-y:auto; padding:10px 12px 14px 6px; line-height:1.75; font-family: Georgia, 'Times New Roman', serif; }
    .preview-card h1 { text-align:center; font-size:1.8rem; color:#ffffff; margin:4px 0 17px; letter-spacing:-.02em; }
    .preview-card h2 { color:#dbeafe; font-size:1.22rem; margin:1.35rem 0 .52rem; padding-bottom:5px; border-bottom:1px solid #24324a; }
    .preview-card h3 { color:#bfdbfe; font-size:1.04rem; margin:1rem 0 .35rem; }
    .preview-card p { margin:.48rem 0; color:#d9e2ef; }
    .preview-card ul { margin:.45rem 0 .7rem 1.15rem; }
    .preview-card li { margin:.28rem 0; color:#dbe5f1; }
    .preview-card strong { color:#ffffff; font-weight:800; }
    .preview-card em { color:#cbd5e1; }
    .preview-card code { background:#17233a; color:#bae6fd; padding:2px 5px; border-radius:5px; font-family:'SFMono-Regular',Consolas,monospace; font-size:.88em; }
    .preview-card .numbered { padding-left:4px; }
    .preview-card .clause-number { display:inline-flex; min-width:29px; color:#93c5fd; font-weight:800; }
    .preview-spacer { height:.28rem; }
    .doc-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:0 0 14px; }
    .stat { background:#f8fafc; border:1px solid #e9eef5; border-radius:14px; padding:12px 13px; }
    .stat-value { font-size:1.08rem; font-weight:800; color:#0f172a; }
    .stat-label { font-size:.72rem; color:#7a8799; margin-top:2px; }
    .empty-state { text-align:center; padding:48px 20px; border:1px dashed #cbd5e1; border-radius:18px; background:linear-gradient(180deg,#ffffff,#f8fafc); }
    .empty-icon { font-size:2.1rem; margin-bottom:8px; }
    .empty-state h3 { margin:0 0 5px; color:#0f172a; }
    .empty-state p { margin:0; color:#7a8799; }
    .sidebar-note { color:#9fb0c8; font-size:.77rem; line-height:1.65; }
    .step { display:flex; gap:10px; align-items:flex-start; margin:12px 0; }
    .step-no { min-width:24px; height:24px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#14213a; color:#93c5fd; font-size:.72rem; font-weight:800; }
    .step-text { font-size:.77rem; line-height:1.5; color:#c4d1e2; }
    .footer-note { color:#94a3b8; font-size:.76rem; text-align:center; padding:20px 0 4px; }
    @media (max-width:900px) { .feature-strip { grid-template-columns:1fr; } .hero { padding:26px 22px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# Professional sidebar — backend mechanics are intentionally hidden from the user.
with st.sidebar:
    logo_html = ""
    if LOGO_PATH.exists():
        import base64
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        logo_html = f"<img src='data:image/png;base64,{encoded}' />"
    st.markdown(
        f"<div class='brand-row'><div class='brand-mark'>{logo_html or '⚖️'}</div><div><div class='brand-name'>LegalEase</div><div class='brand-sub'>AI-powered legal drafting</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("**Workspace**")
    st.markdown(
        "<div class='sidebar-note'>Create a structured legal draft from the facts you provide. Review, edit, and export the finished draft from one workspace.</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**How it works**")
    for number, text in (
        ("1", "Describe the document, parties, date, and agreed terms."),
        ("2", "Generate a structured draft with clear clauses and placeholders."),
        ("3", "Review or edit the draft, then export it as TXT, DOCX, or PDF."),
    ):
        st.markdown(f"<div class='step'><div class='step-no'>{number}</div><div class='step-text'>{text}</div></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div class='sidebar-note'><b>Important:</b> LegalEase creates AI-assisted drafts. Review legal requirements, missing facts, and jurisdiction-specific terms before signing or relying on a document.</div>",
        unsafe_allow_html=True,
    )

if "document" not in st.session_state:
    st.session_state.document = ""
if "document_type" not in st.session_state:
    st.session_state.document_type = ""
if "generation_meta" not in st.session_state:
    st.session_state.generation_meta = {}
if "editing" not in st.session_state:
    st.session_state.editing = False
if "party_text" not in st.session_state:
    st.session_state.party_text = ""
if "terms_text" not in st.session_state:
    st.session_state.terms_text = ""
if "date_text" not in st.session_state:
    st.session_state.date_text = ""

st.markdown(
    "<div class='hero'><div class='eyebrow'><span class='eyebrow-dot'></span> AI LEGAL DRAFTING WORKSPACE</div><h1>Turn your terms into a professional legal draft.</h1><p>Generate structured agreements, contracts, NDAs, leases, and more — then refine the language and export the final draft in the format you need.</p><div class='feature-strip'><div class='feature'><b>Structured drafting</b><span>Clear sections, clauses, placeholders and signatures.</span></div><div class='feature'><b>Editable by design</b><span>Review and modify the generated wording before export.</span></div><div class='feature'><b>Ready to export</b><span>Download clean TXT, DOCX and branded PDF files.</span></div></div></div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-card'><div class='section-title'>Create legal document</div><div class='section-help'>Provide the essential facts. Use semicolons between individual terms.</div>", unsafe_allow_html=True)

with st.form("document_form", clear_on_submit=False):
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='field-label'>Document type</div>", unsafe_allow_html=True)
        document_kind = st.selectbox(
            "Document type",
            [
                "Employment Contract",
                "Non-Disclosure Agreement (NDA)",
                "Lease Agreement",
                "Employment Offer Letter",
                "Freelance Work Contract",
                "Service Agreement",
                "Consulting Agreement",
                "Partnership Agreement",
                "General Contract / Agreement",
                "Other / Custom",
            ],
            label_visibility="collapsed",
            index=0,
        )
        custom_type = ""
        if document_kind == "Other / Custom":
            custom_type = st.text_input("Custom document type", placeholder="e.g. Software License Agreement")
        st.markdown("<div class='field-label'>Parties involved</div>", unsafe_allow_html=True)
        parties = st.text_area(
            "Parties involved",
            value=st.session_state.party_text,
            height=145,
            placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
            label_visibility="collapsed",
        )
    with c2:
        st.markdown("<div class='field-label'>Effective date</div>", unsafe_allow_html=True)
        dates = st.text_input(
            "Effective date",
            value=st.session_state.date_text,
            placeholder="April 15, 2025",
            label_visibility="collapsed",
        )
        st.markdown("<div class='field-label'>Terms & conditions</div>", unsafe_allow_html=True)
        terms = st.text_area(
            "Terms & conditions",
            value=st.session_state.terms_text,
            height=145,
            placeholder="Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
            label_visibility="collapsed",
        )

    document_type = custom_type.strip() if document_kind == "Other / Custom" else document_kind
    st.markdown("<div class='mini-badge'>Required information</div><div style='color:#748196;font-size:.8rem;margin-bottom:10px;'>Document type · parties · effective date · terms & conditions</div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Generate Document  →", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    missing = []
    for label, value in (
        ("Document Type", document_type),
        ("Parties Involved", parties),
        ("Terms & Conditions", terms),
        ("Effective Date", dates),
    ):
        if not value.strip():
            missing.append(label)

    if missing:
        st.warning("Please complete: " + ", ".join(missing))
    else:
        st.session_state.party_text = parties
        st.session_state.terms_text = terms
        st.session_state.date_text = dates
        payload = {"document_type": document_type, "parties": parties, "terms": terms, "dates": dates}
        with st.spinner("LegalEase is drafting your document…"):
            try:
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=180)
                response.raise_for_status()
                data = response.json()
                st.session_state.document = data["document"]
                st.session_state.document_type = data.get("document_type") or document_type
                st.session_state.generation_meta = data
                st.session_state.editing = False
                st.toast("Document generated successfully", icon="✅")
                st.rerun()
            except requests.RequestException as exc:
                detail = ""
                if getattr(exc, "response", None) is not None:
                    try:
                        detail = exc.response.json().get("detail", "")
                    except Exception:
                        detail = getattr(exc.response, "text", "")[:700]
                st.error(f"Generation failed. {detail or exc}")

if not st.session_state.document:
    st.markdown(
        "<div class='empty-state'><div class='empty-icon'>⚖️</div><h3>Your document will appear here</h3><p>Fill in the details above and generate a draft to unlock preview, editing and downloads.</p></div>",
        unsafe_allow_html=True,
    )
else:
    from backend.services.exporters import format_docx, format_pdf, format_txt
    from backend.utils.text import format_html_preview, safe_filename, strip_markdown

    meta = st.session_state.generation_meta
    word_count = len(strip_markdown(st.session_state.document).split())
    clause_count = sum(1 for line in st.session_state.document.splitlines() if line.strip().startswith(("## ", "### ")))
    term_count = len([x for x in st.session_state.terms_text.split(";") if x.strip()])

    st.markdown("<div class='section-card'><div class='section-title'>Your generated document</div><div class='section-help'>Review the draft carefully. You can switch between a formatted preview and an editable version.</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='doc-stats'><div class='stat'><div class='stat-value'>{word_count:,}</div><div class='stat-label'>Words</div></div><div class='stat'><div class='stat-value'>{clause_count:,}</div><div class='stat-label'>Sections</div></div><div class='stat'><div class='stat-value'>{term_count:,}</div><div class='stat-label'>Input terms</div></div></div>",
        unsafe_allow_html=True,
    )
    if meta.get("demo_mode"):
        st.info("Demo mode is active. Set DEMO_MODE=false in .env and add your Gemini API key for live AI generation.")
    elif meta.get("model"):
        st.caption(f"Generated with Gemini • {meta['model']}")

    preview_tab, edit_tab = st.tabs(["Preview", "Edit document"])
    with preview_tab:
        styled_html = format_html_preview(st.session_state.document)
        st.markdown(
            f"<div class='preview-shell'><div class='preview-top'><div class='preview-label'>{st.session_state.document_type}</div><div class='preview-chip'>Formatted preview</div></div><div class='preview-card'>{styled_html}</div></div>",
            unsafe_allow_html=True,
        )
    with edit_tab:
        st.markdown("**Edit the draft below**")
        edited_text = st.text_area(
            "Editable document",
            st.session_state.document,
            height=620,
            key="edit_document_box",
            label_visibility="collapsed",
        )
        if edited_text != st.session_state.document:
            st.session_state.document = edited_text
            st.caption("Unsaved edits are held in this session and are used by the download buttons.")
        else:
            st.caption("Markdown formatting is supported. For bold text, use **double asterisks** around the words you want bold.")

    st.markdown("### Download / save")
    base_name = safe_filename(st.session_state.document_type)
    d1, d2, d3 = st.columns(3, gap="medium")
    with d1:
        st.download_button("Download .TXT", data=format_txt(st.session_state.document), file_name=f"{base_name}.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("Download .DOCX", data=format_docx(st.session_state.document, st.session_state.document_type, st.session_state.terms_text), file_name=f"{base_name}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with d3:
        st.download_button("Download .PDF", data=format_pdf(st.session_state.document, st.session_state.document_type, st.session_state.terms_text), file_name=f"{base_name}.pdf", mime="application/pdf", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>LegalEase is an AI-assisted drafting tool. Review generated content and jurisdiction-specific requirements before use.</div>", unsafe_allow_html=True)

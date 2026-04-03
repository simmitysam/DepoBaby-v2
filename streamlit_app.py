import streamlit as st
import anthropic
import pdfplumber
import io
import json
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DepoBaby",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #F4F1EA; color: #1E293B; }

/* Header text must be high contrast on dark background */
.depobaby-header, .depobaby-header * {
    color: #C9A84C !important;
}
.depobaby-title {
    color: #C9A84C !important;
}
.depobaby-sub {
    color: #C9A84C !important;
}

/* Ensure buttons are legible in all states */
.stButton > button,
.stButton > button:focus,
.stButton > button:active,
div[data-testid="stButton"] button,
div[data-testid="stButton"] button:focus,
div[data-testid="stButton"] button:active {
    color: #C9A84C !important;
    background: #0F1623 !important;
    border-color: #C9A84C !important;
    box-shadow: none !important;
}
.stButton > button span,
.stButton > button:focus span,
.stButton > button:active span,
div[data-testid="stButton"] button span,
div[data-testid="stButton"] button:focus span,
div[data-testid="stButton"] button:active span {
    color: #C9A84C !important;
}
.stButton > button:hover,
div[data-testid="stButton"] button:hover {
    color: #0F1623 !important;
    background: #C9A84C !important;
}
.stButton > button:hover span,
div[data-testid="stButton"] button:hover span {
    color: #0F1623 !important;
}

.stButton > button[disabled],
div[data-testid="stButton"] button[disabled] {
    color: rgba(255,255,255,0.8) !important;
    background: rgba(15,22,35,0.8) !important;
}

.stButton > button[disabled] span,
div[data-testid="stButton"] button[disabled] span {
    color: rgba(255,255,255,0.8) !important;
}

.depobaby-header {
    background: #0F1623;
    border-bottom: 3px solid #C9A84C;
    padding: 16px 32px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: baseline;
    gap: 14px;
}
.depobaby-title {
    font-family: 'EB Garamond', serif;
    font-size: 2rem;
    font-weight: 600;
    color: #C9A84C !important;
    letter-spacing: 0.04em;
    margin: 0;
}
.depobaby-sub {
    font-size: 0.68rem;
    color: #C9A84C !important;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.section-title {
    font-family: 'EB Garamond', serif;
    font-size: 1.2rem;
    font-weight: 500;
    color: #0F1623;
    border-bottom: 2px solid #C9A84C;
    padding-bottom: 5px;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}
.matter-banner {
    background: #0F1623;
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 6px;
    padding: 14px 20px;
    margin-bottom: 20px;
}
.pill-red    { background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; border-radius:3px; padding:2px 8px; font-size:0.65rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; display:inline-block; }
.pill-amber  { background:#FEF3C7; color:#78350F; border:1px solid #FDE68A; border-radius:3px; padding:2px 8px; font-size:0.65rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; display:inline-block; }
.pill-green  { background:#D1FAE5; color:#065F46; border:1px solid #6EE7B7; border-radius:3px; padding:2px 8px; font-size:0.65rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; display:inline-block; }
.pill-navy   { background:#0F1623; color:#C9A84C; border:1px solid rgba(201,168,76,0.3); border-radius:3px; padding:2px 8px; font-size:0.65rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; display:inline-block; }
.pill-gray   { background:#F3F4F6; color:#374151; border:1px solid #D1D5DB; border-radius:3px; padding:2px 8px; font-size:0.65rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; display:inline-block; }

.timeline-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
.timeline-table th { background:#0F1623; color:#C9A84C; padding:9px 12px; text-align:left; font-size:0.66rem; letter-spacing:0.1em; text-transform:uppercase; font-weight:500; }
.timeline-table td { padding:9px 12px; border-bottom:1px solid #EEE9E0; vertical-align:top; line-height:1.5; color: #2D3748; }
.timeline-table tr:nth-child(even) td { background:#FAFAF7; }

.party-card { background:#fff; border:1px solid #DDD8CE; border-radius:6px; padding:14px 16px; margin-bottom:10px; }
.party-name { font-family:'EB Garamond',serif; font-size:1.05rem; font-weight:500; color:#0F1623; margin-top:6px; }
.party-type { font-size: 0.72rem; color:#4A5568; margin-top:2px; }
.party-desc { font-size: 0.82rem; color:#2D3748; margin-top:8px; line-height:1.55; }

.disc-item { border-left:3px solid #C9A84C; padding:8px 12px; margin-bottom:7px; background:#FAFAF7; border-radius:0 4px 4px 0; }
.disc-cat  { font-size:0.62rem; font-weight:700; letter-spacing:0.11em; text-transform:uppercase; color:#C9A84C; margin-bottom:3px; }
.disc-text { font-size:0.83rem; line-height:1.5; color: #2D3748; }
.disc-bas  { font-size:0.72rem; color:#4A5568; margin-top:4px; font-style:italic; }

.gap-item  { display:flex; gap:8px; padding:9px 12px; border-radius:4px; margin-bottom:6px; color: #2D3748; }
.gap-crit  { background:#FEE2E2; border:1px solid #FCA5A5; }
.gap-sig   { background:#FEF3C7; border:1px solid #FDE68A; }
.gap-min   { background:#F4F1EA; border:1px solid #DDD8CE; }

/* ── Buttons ── */
.stButton > button,
.stButton > button:focus,
.stButton > button:active {
    background: #0F1623 !important;
    color: #C9A84C !important;
    border: 1.5px solid #C9A84C !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.78rem !important;
    padding: 10px 28px !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #C9A84C !important;
    color: #0F1623 !important;
}

/* Strong header text override */
.depobaby-header,
.depobaby-header > .depobaby-title,
.depobaby-header > .depobaby-sub,
.depobaby-header * {
    color: #C9A84C !important;
    -webkit-text-fill-color: #C9A84C !important;
}

/* Enforce button text contrast for the API key continue button */
.stButton button,
.stButton button span,
div[data-testid="stButton"] button,
div[data-testid="stButton"] button span {
    color: #C9A84C !important;
    background: #0F1623 !important;
}

.stButton button:hover,
.stButton button:focus,
.stButton button:active,
div[data-testid="stButton"] button:hover,
div[data-testid="stButton"] button:focus,
div[data-testid="stButton"] button:active {
    color: #0F1623 !important;
    background: #C9A84C !important;
}

/* Keep header rule continuing */
    opacity: 1 !important;
}

/* ── Field labels ── */
label, .stTextInput label, .stSelectbox label,
.stTextArea label, .stFileUploader label,
.stRadio label, p.st-emotion-cache-10trblm {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #2D3748 !important;
}

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea {
    border: 1px solid #DDD8CE !important;
    border-radius: 4px !important;
    background: #fff !important;
    color: #1C1C22 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border: 1px solid #DDD8CE !important;
    border-radius: 4px !important;
    background: #fff !important;
    color: #1C1C22 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}
.stSelectbox > div > div > div { color: #1C1C22 !important; }
.stSelectbox svg { fill: #4A5568 !important; }

/* ── Selectbox dropdown options ── */
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="menu"] li {
    color: #1C1C22 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Radio buttons ── */
.stRadio > div { flex-direction: row !important; gap: 16px !important; }
.stRadio label { color: #1C1C22 !important; font-size: 0.85rem !important; font-weight: 400 !important; text-transform: none !important; letter-spacing: 0 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #1C1C22 !important; }

/* ── File uploader ── */
.stFileUploader > div {
    border: 1.5px dashed #DDD8CE !important;
    border-radius: 6px !important;
    background: #FAFAF7 !important;
}
.stFileUploader label { color: #2D3748 !important; }
[data-testid="stFileUploaderDropzone"] { background: #FAFAF7 !important; }
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p { color: #2D3748 !important; }

/* ── Spinner / info / success messages ── */
.stSpinner p, .stAlert p, .stSuccess p, .stInfo p, .stWarning p {
    color: #1C1C22 !important;
}

/* ── Metric labels & values ── */
[data-testid="stMetricLabel"] { color: #4A5568 !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #0F1623 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #0F1623;
    border-radius: 4px 4px 0 0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(201,168,76,0.7);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 12px 22px;
}
.stTabs [aria-selected="true"] {
    color: #C9A84C !important;
    border-bottom: 2px solid #C9A84C !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #fff;
    border: 1px solid rgba(201,168,76,0.2);
    border-top: none;
    padding: 22px;
    border-radius: 0 0 4px 4px;
}
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}

/* ── Ensure all text has proper contrast ── */
.stApp p, .stApp span, .stApp div, .stApp li {
    color: #2D3748 !important;
}

/* Override any light text that might appear */
.stMarkdown p, .stText p {
    color: #2D3748 !important;
}

/* Ensure success/info/warning messages are visible */
.stSuccess, .stInfo, .stWarning {
    color: #2D3748 !important;
}
.stSuccess p, .stInfo p, .stWarning p {
    color: #2D3748 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="depobaby-header">
    <span class="depobaby-title">⚖ DepoBaby</span>
    <span class="depobaby-sub">Complaint Analysis &amp; Discovery Intelligence</span>
</div>
""", unsafe_allow_html=True)

# ── Screen 0: API Key ────────────────────────────────────────────────────────
if "api_key_stored" not in st.session_state:
    st.session_state["api_key_stored"] = ""

if not st.session_state["api_key_stored"]:
    st.markdown("""
    <div style="max-width:480px;margin:60px auto 0;background:#fff;border:1px solid #DDD8CE;border-radius:8px;padding:36px 40px;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
        <div style="font-family:'EB Garamond',serif;font-size:1.5rem;font-weight:500;color:#0F1623;margin-bottom:6px;">Welcome to DepoBaby</div>
        <div style="font-size:0.8rem;color:#888;margin-bottom:24px;line-height:1.6;">Enter your Anthropic API key to get started.<br>Your key is stored only in your browser session and never saved to disk.</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        entered_key = st.text_input(
            "Anthropic API Key",
            placeholder="sk-ant-api03-...",
            key="api_key_input",
            label_visibility="collapsed",
        )
        st.markdown("<div style='font-size:0.72rem;color:#888;margin-top:4px;text-align:center'>Get your key at console.anthropic.com</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("→  Continue", use_container_width=True):
            key = entered_key.strip()
            if key.startswith("sk-ant") and len(key) > 40:
                st.session_state["api_key_stored"] = key
                st.rerun()
            else:
                st.error("That doesn't look like a valid Anthropic key. It should start with sk-ant-api03-")
    st.stop()

api_key = st.session_state["api_key_stored"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_pdf_text(file_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n\n"
    except Exception as e:
        st.error(f"PDF extraction error: {e}")
    return text.strip()


def call_claude(complaint_text, filing_date, case_type, api_key=None):
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("No API key provided")
    client = anthropic.Anthropic(api_key=api_key)

    system = (
        "You are a senior California litigation associate specializing in breach-of-contract matters. "
        "Extract structured data from complaints. "
        "Respond ONLY with a single valid JSON object — no preamble, no markdown fences, no text outside the JSON."
    )

    prompt = f"""Analyze this complaint and return ONE JSON object with exactly three keys: "timeline", "parties", "discovery".

"timeline": array where each item has:
{{"date":string, "event":string, "source":string,
  "significance":"CONTRACT|BREACH|NOTICE|PAYMENT|TERMINATION|PROCEDURAL|PERFORMANCE|OTHER",
  "flag":"CLEAN|AMBIGUOUS|MISSING DATE|KEY DATE|NEEDS VERIFICATION",
  "flag_note":string}}

"parties":
{{"plaintiff":{{"name":string,"type":string,"description":string}},
  "defendant":{{"name":string,"type":string,"description":string}},
  "additional_defendants":[{{"name":string,"type":string,"description":string}}],
  "named_individuals":[{{"name":string,"role":string,"affiliation":string,"discovery_relevance":string}}],
  "third_parties":[{{"name":string,"role":string,"relevance":string}}],
  "causes_of_action":[string],
  "claims_summary":string}}

"discovery":
{{"document_requests":[{{"category":string,"description":string,"basis":string}}],
  "interrogatory_topics":[{{"topic":string,"description":string,"basis":string}}],
  "key_witnesses":[{{"role":string,"relevance":string,"priority":"HIGH|MEDIUM|LOW"}}],
  "factual_gaps":[{{"gap":string,"severity":"CRITICAL|SIGNIFICANT|MINOR","implication":string,"source_para":string}}],
  "case_themes":[string]}}

COMPLAINT (filing date: {filing_date}, case type: {case_type}):
{complaint_text[:4000]}

Return ONLY the raw JSON object."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # Try to find the outermost JSON object even if truncated
        # Find opening brace
        start = cleaned.find('{')
        if start == -1:
            raise ValueError("No JSON object found in response")
        # Walk backwards from end to find valid JSON
        end = len(cleaned)
        while end > start:
            try:
                return json.loads(cleaned[start:end])
            except Exception:
                end -= 1
                # Skip back to last } or ] for efficiency
                prev_brace = max(cleaned.rfind('}', start, end+1), cleaned.rfind(']', start, end+1))
                if prev_brace > start:
                    end = prev_brace + 1
                else:
                    break
        raise ValueError(f"Could not parse JSON. Response length: {len(cleaned)}. Start: {cleaned[start:start+200]}")


def flag_pill(flag):
    mapping = {
        "CLEAN": ("pill-green", "CLEAN"),
        "KEY DATE": ("pill-green", "KEY DATE"),
        "AMBIGUOUS": ("pill-amber", "AMBIGUOUS"),
        "MISSING DATE": ("pill-red", "MISSING DATE"),
        "NEEDS VERIFICATION": ("pill-amber", "NEEDS VERIFICATION"),
    }
    cls, label = mapping.get(flag, ("pill-gray", flag or "—"))
    return f'<span class="{cls}">{label}</span>'


SIG_EMOJI = {
    "CONTRACT": "📝", "BREACH": "⚠️", "NOTICE": "📬", "PAYMENT": "💰",
    "TERMINATION": "🚫", "PROCEDURAL": "⚖️", "PERFORMANCE": "✅", "OTHER": "·",
}

GAP_CLASS = {"CRITICAL": "gap-item gap-crit", "SIGNIFICANT": "gap-item gap-sig", "MINOR": "gap-item gap-min"}
GAP_ICON  = {"CRITICAL": "🔴", "SIGNIFICANT": "🟡", "MINOR": "⚪"}
WIT_PILL  = {"HIGH": "pill-red", "MEDIUM": "pill-amber", "LOW": "pill-gray"}

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["results", "matter_info", "analyzed"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "analyzed" else False

# ── INTAKE ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Matter Intake</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    matter_name = st.text_input("Matter Name", placeholder="e.g. Johnson v. ABC Corp")
with c2:
    side = st.selectbox("Side Represented", ["Plaintiff", "Defendant", "Neutral / Research"])
with c3:
    case_type = st.selectbox("Case Type", [
        "Breach of Contract — Services Agreement",
        "Breach of Contract — Non-Payment",
        "Breach of Contract — Real Property",
        "Breach of Contract",
        "Fraud",
        "Common Counts",
        "Mixed / Other",
    ])

c4, c5 = st.columns([1, 2])
with c4:
    filing_date = st.text_input("Complaint Filed", placeholder="e.g. February 28, 2024")
with c5:
    court = st.text_input("Court", placeholder="e.g. San Diego Superior Court")

st.markdown('<div class="section-title">Complaint Input</div>', unsafe_allow_html=True)

input_method = st.radio(
    "Input Method",
    ["📎 Upload PDF", "📋 Paste Text"],
    horizontal=True,
    label_visibility="collapsed",
)

complaint_text = ""

if input_method == "📎 Upload PDF":
    uploaded = st.file_uploader("Upload complaint PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded:
        with st.spinner("Extracting text from PDF…"):
            complaint_text = extract_pdf_text(uploaded.read())
        if complaint_text:
            st.success(f"✓ Extracted {len(complaint_text):,} characters from **{uploaded.name}**")
            with st.expander("Preview extracted text"):
                st.text(complaint_text[:2000] + ("…" if len(complaint_text) > 2000 else ""))
        else:
            st.warning("Could not extract text — PDF may be scanned. Try pasting the text instead.")
else:
    complaint_text = st.text_area(
        "Paste complaint text",
        height=260,
        placeholder="Paste the full text of the complaint here…",
        label_visibility="collapsed",
    )

st.markdown("")
_, btn_col, _ = st.columns([1, 1, 3])
with btn_col:
    run = st.button("⚡  Analyze Complaint", use_container_width=True)

# ── RUN ───────────────────────────────────────────────────────────────────────
if run:
    if not complaint_text or len(complaint_text.strip()) < 100:
        st.warning("Please provide complaint text before analyzing.")
    else:
        st.session_state.matter_info = {
            "matter": matter_name or "Untitled Matter",
            "side": side,
            "case_type": case_type,
            "filing_date": filing_date or "Not provided",
            "court": court or "Not specified",
        }
        with st.spinner("Analyzing complaint — this usually takes 20–40 seconds…"):
            try:
                st.session_state.results = call_claude(
                    complaint_text,
                    filing_date or "Not provided",
                    case_type,
                    api_key=api_key,
                )
                st.session_state.analyzed = True
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.results:
    mi = st.session_state.matter_info
    r  = st.session_state.results
    tl = r.get("timeline", [])
    pa = r.get("parties", {})
    di = r.get("discovery", {})

    # Matter banner
    st.markdown(f"""
    <div class="matter-banner">
        <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:center;">
            <div>
                <div style="font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:rgba(201,168,76,.6);margin-bottom:2px">Matter</div>
                <div style="font-family:'EB Garamond',serif;font-size:1.05rem;color:#C9A84C;">{mi['matter']}</div>
            </div>
            <div>
                <div style="font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:rgba(201,168,76,.6);margin-bottom:2px">Side</div>
                <div style="font-size:.85rem;color:rgba(255,255,255,.8);">{mi['side']}</div>
            </div>
            <div>
                <div style="font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:rgba(201,168,76,.6);margin-bottom:2px">Case Type</div>
                <div style="font-size:.85rem;color:rgba(255,255,255,.8);">{mi['case_type']}</div>
            </div>
            <div>
                <div style="font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:rgba(201,168,76,.6);margin-bottom:2px">Filed</div>
                <div style="font-size:.85rem;color:rgba(255,255,255,.8);">{mi['filing_date']}</div>
            </div>
            <div>
                <div style="font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:rgba(201,168,76,.6);margin-bottom:2px">Court</div>
                <div style="font-size:.85rem;color:rgba(255,255,255,.8);">{mi['court']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["  📅  Timeline  ", "  👥  Parties & Claims  ", "  🔍  Discovery Focus  "])

    # ── TIMELINE ──────────────────────────────────────────────────────────────
    with tab1:
        if not tl:
            st.info("No timeline events extracted.")
        else:
            rows = ""
            for ev in tl:
                emoji = SIG_EMOJI.get(ev.get("significance", "OTHER"), "·")
                note  = f'<div style="font-size:.7rem;color:#888;font-style:italic;margin-top:2px">{ev.get("flag_note","")}</div>' if ev.get("flag_note") else ""
                rows += f"""<tr>
                    <td style="white-space:nowrap;font-weight:500;font-size:.8rem">{ev.get('date','—')}</td>
                    <td>{emoji} {ev.get('event','—')}{note}</td>
                    <td style="white-space:nowrap;font-size:.74rem;color:#888">{ev.get('source','—')}</td>
                    <td style="font-size:.7rem;color:#888;white-space:nowrap">{ev.get('significance','—')}</td>
                    <td>{flag_pill(ev.get('flag','CLEAN'))}</td>
                </tr>"""

            st.markdown(f"""
            <table class="timeline-table">
                <thead><tr><th>Date</th><th>Event</th><th>Source</th><th>Type</th><th>Flag</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)

            fc = {}
            for ev in tl:
                f = ev.get("flag", "CLEAN")
                fc[f] = fc.get(f, 0) + 1

            st.markdown("")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Total Events", len(tl))
            s2.metric("🔴 Missing Dates", fc.get("MISSING DATE", 0))
            s3.metric("🟡 Ambiguous", fc.get("AMBIGUOUS", 0))
            s4.metric("✅ Clean / Key", fc.get("CLEAN", 0) + fc.get("KEY DATE", 0))

    # ── PARTIES ───────────────────────────────────────────────────────────────
    with tab2:
        if not pa:
            st.info("No party information extracted.")
        else:
            pc1, pc2 = st.columns(2)

            pl = pa.get("plaintiff", {})
            de = pa.get("defendant", {})

            with pc1:
                st.markdown('<div class="section-title">Plaintiff</div>', unsafe_allow_html=True)
                if pl:
                    st.markdown(f"""
                    <div class="party-card">
                        <span class="pill-navy">Plaintiff</span>
                        <div class="party-name">{pl.get('name','—')}</div>
                        <div class="party-type">{pl.get('type','')}</div>
                        <div class="party-desc">{pl.get('description','')}</div>
                    </div>""", unsafe_allow_html=True)

            with pc2:
                st.markdown('<div class="section-title">Defendant</div>', unsafe_allow_html=True)
                if de:
                    st.markdown(f"""
                    <div class="party-card">
                        <span class="pill-red">Defendant</span>
                        <div class="party-name">{de.get('name','—')}</div>
                        <div class="party-type">{de.get('type','')}</div>
                        <div class="party-desc">{de.get('description','')}</div>
                    </div>""", unsafe_allow_html=True)

            add_defs = pa.get("additional_defendants", [])
            if add_defs:
                st.markdown('<div class="section-title">Additional Defendants</div>', unsafe_allow_html=True)
                for d in add_defs:
                    st.markdown(f'<div class="party-card" style="padding:10px 14px"><span class="pill-gray">{d.get("type","Unknown")}</span> <strong>{d.get("name","—")}</strong><span style="color:#888;font-size:.8rem"> — {d.get("description","")}</span></div>', unsafe_allow_html=True)

            named = pa.get("named_individuals", [])
            if named:
                st.markdown('<div class="section-title">Named Individuals & Agents</div>', unsafe_allow_html=True)
                for ind in named:
                    st.markdown(f'<div class="party-card" style="padding:10px 14px"><span class="pill-navy">{ind.get("role","—")}</span> <strong style="font-size:.9rem">{ind.get("name","—")}</strong><span style="color:#888;font-size:.78rem"> · {ind.get("affiliation","")}</span><div style="font-size:.78rem;color:#555;margin-top:4px">{ind.get("discovery_relevance","")}</div></div>', unsafe_allow_html=True)

            thirds = pa.get("third_parties", [])
            if thirds:
                st.markdown('<div class="section-title">Third Parties</div>', unsafe_allow_html=True)
                for tp in thirds:
                    st.markdown(f'<div class="party-card" style="padding:10px 14px;border-left:3px solid #C9A84C"><strong>{tp.get("name","—")}</strong><span style="color:#888;font-size:.8rem"> — {tp.get("role","")}</span><div style="font-size:.78rem;color:#555;margin-top:3px">{tp.get("relevance","")}</div></div>', unsafe_allow_html=True)

            coa = pa.get("causes_of_action", [])
            if coa:
                st.markdown('<div class="section-title">Causes of Action</div>', unsafe_allow_html=True)
                pills = " ".join([f'<span class="pill-navy">{c}</span>' for c in coa])
                st.markdown(f'<div style="padding:8px 0">{pills}</div>', unsafe_allow_html=True)

            summary = pa.get("claims_summary", "")
            if summary:
                st.markdown('<div class="section-title">Claims Summary</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-family:\'EB Garamond\',serif;font-size:1rem;line-height:1.8;font-style:italic;color:#555;background:#FAFAF7;padding:14px 16px;border-left:3px solid #C9A84C;border-radius:0 4px 4px 0">{summary}</div>', unsafe_allow_html=True)

    # ── DISCOVERY ─────────────────────────────────────────────────────────────
    with tab3:
        if not di:
            st.info("No discovery analysis available.")
        else:
            themes = di.get("case_themes", [])
            if themes:
                st.markdown('<div class="section-title">Central Case Themes</div>', unsafe_allow_html=True)
                chips = " ".join([f'<span style="display:inline-block;background:rgba(201,168,76,.1);color:#5A442A;border:1px solid rgba(201,168,76,.25);border-radius:3px;padding:3px 9px;font-size:.75rem;margin:0 4px 5px 0">{t}</span>' for t in themes])
                st.markdown(chips, unsafe_allow_html=True)

            dc1, dc2 = st.columns(2)

            with dc1:
                st.markdown('<div class="section-title">Document Requests (RFPs)</div>', unsafe_allow_html=True)
                for dr in di.get("document_requests", []):
                    st.markdown(f'<div class="disc-item"><div class="disc-cat">{dr.get("category","")}</div><div class="disc-text">{dr.get("description","")}</div><div class="disc-bas">Basis: {dr.get("basis","")}</div></div>', unsafe_allow_html=True)

            with dc2:
                st.markdown('<div class="section-title">Interrogatory Topics</div>', unsafe_allow_html=True)
                for rog in di.get("interrogatory_topics", []):
                    st.markdown(f'<div class="disc-item"><div class="disc-cat">{rog.get("topic","")}</div><div class="disc-text">{rog.get("description","")}</div><div class="disc-bas">Basis: {rog.get("basis","")}</div></div>', unsafe_allow_html=True)

            witnesses = di.get("key_witnesses", [])
            if witnesses:
                st.markdown('<div class="section-title">Deposition Targets</div>', unsafe_allow_html=True)
                for w in witnesses:
                    priority = w.get("priority", "MEDIUM")
                    pcls = WIT_PILL.get(priority, "pill-gray")
                    st.markdown(f'<div class="party-card" style="padding:10px 14px;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px"><div><strong style="font-size:.88rem">{w.get("role","—")}</strong><div style="font-size:.78rem;color:#555;margin-top:3px">{w.get("relevance","")}</div></div><span class="{pcls}">Priority: {priority}</span></div>', unsafe_allow_html=True)

            gaps = di.get("factual_gaps", [])
            if gaps:
                st.markdown('<div class="section-title">Factual Gaps & Ambiguities</div>', unsafe_allow_html=True)
                for g in gaps:
                    sev  = g.get("severity", "MINOR")
                    cls  = GAP_CLASS.get(sev, "gap-item gap-min")
                    icon = GAP_ICON.get(sev, "⚪")
                    st.markdown(f'<div class="{cls}"><div style="font-size:14px;flex-shrink:0;margin-top:2px">{icon}</div><div><div style="font-size:.85rem;font-weight:600">{g.get("gap","—")}</div><div style="font-size:.78rem;color:#555;margin-top:3px;line-height:1.45">{g.get("implication","")}</div></div></div>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("↩  New Analysis"):
        st.session_state.analyzed = False
        st.session_state.results  = None
        st.session_state.matter_info = None
        st.rerun()
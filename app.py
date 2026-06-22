import re
import streamlit as st
import requests
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsureWise AI",
    page_icon="🌿",
    layout="centered",
)

# ── Inject the original CSS so it looks identical ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --bg:#F0F7FF; --bg-dim:#DCE9FA; --paper:#FFFFFF;
  --ink:#0F172A; --ink-soft:#64748B; --line:rgba(37,99,235,0.16);
  --pine:#2563EB; --pine-dark:#1D4ED8; --pine-soft:#E0F2FE;
  --marigold:#0D9488; --marigold-soft:#CCFBF1;
  --brick:#DC2626; --brick-soft:#FEE2E2;
  --shadow:rgba(15,23,42,0.10); --radius:14px;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"] { display: none; }
footer { display: none; }
#MainMenu { display: none; }

.brand {
  display: flex; align-items: center; gap: 10px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700; font-size: 18px; color: var(--ink);
  padding: 18px 0 6px;
}
.brand-dot {
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--pine); display: inline-flex;
  align-items: center; justify-content: center;
}
.brand-dot::after {
  content: ''; width: 6px; height: 6px;
  border-radius: 50%; background: var(--marigold); display: block;
}

.disclaimer-box {
  background: var(--brick-soft); border: 1px solid #FCA5A5;
  border-radius: 10px; padding: 12px 16px;
  font-size: 13px; color: #7F1D1D; margin-bottom: 20px;
  font-family: 'Inter', sans-serif;
}

.chat-bubble-bot {
  background: var(--pine-soft); color: var(--ink);
  border-radius: 13px; border-top-left-radius: 4px;
  padding: 12px 16px; margin: 6px 0; font-size: 15px;
  max-width: 85%; font-family: 'Inter', sans-serif;
  line-height: 1.5;
}
.chat-bubble-user {
  background: var(--marigold); color: #FFFFFF;
  border-radius: 13px; padding: 12px 16px;
  margin: 6px 0 6px auto; font-size: 15px;
  max-width: 85%; text-align: right;
  font-family: 'Inter', sans-serif; line-height: 1.5;
}
.chat-row-bot { display: flex; gap: 10px; margin-bottom: 4px; }
.chat-row-user { display: flex; justify-content: flex-end; margin-bottom: 4px; }
.chat-dot {
  width: 11px; height: 11px; border-radius: 50%;
  margin-top: 14px; flex-shrink: 0;
}
.chat-dot-bot { background: var(--pine); }
.chat-dot-user { background: var(--marigold); }

.summary-card {
  background: var(--paper); border: 1px solid var(--line);
  border-radius: 13px; padding: 22px; margin-top: 10px;
  font-family: 'Inter', sans-serif; font-size: 14.5px;
  line-height: 1.6;
}
.summary-card h4 {
  font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px;
  text-transform: uppercase; letter-spacing: .06em;
  color: var(--pine-dark); margin: 18px 0 6px;
}
.summary-card h4:first-child { margin-top: 0; }
.summary-card ul, .summary-card ol {
  margin: 0 0 10px; padding-left: 20px;
}
.summary-card li { margin-bottom: 6px; }
.summary-disclaimer {
  font-size: 12px; color: var(--brick);
  background: var(--brick-soft); border-radius: 8px;
  padding: 9px 12px; margin-top: 14px;
}
.progress-bar-wrap {
  background: var(--bg-dim); border-radius: 4px;
  height: 6px; margin-bottom: 18px; overflow: hidden;
}
.progress-bar-fill {
  height: 100%; background: var(--pine);
  border-radius: 4px; transition: width .35s ease;
}
.step-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; color: var(--ink-soft); margin-bottom: 6px;
}
.stButton > button {
  background: var(--pine) !important; color: #fff !important;
  border: none !important; border-radius: 999px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important; font-size: 14px !important;
  padding: 8px 20px !important; margin: 4px 4px 4px 0 !important;
  transition: background .15s !important;
}
.stButton > button:hover { background: var(--pine-dark) !important; }
.stTextInput > div > div > input {
  border: 1.5px solid var(--line) !important;
  border-radius: 999px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14.5px !important; padding: 10px 18px !important;
  background: #fff !important; color: var(--ink) !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--pine) !important;
  box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── API key from Streamlit secrets ────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")

# ── Markdown-ish text -> HTML for the summary card ────────────────────────────
# Handles **bold** section headings, **bold** inline text (any number of spans
# per line, not just one), and turns consecutive "1. ..." lines into a real
# <ol> list instead of a wall of separate paragraphs.
def markdown_to_html(text: str) -> str:
    def inline_bold(s: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    parts = []
    in_list = False
    for raw_line in text.split("\n"):
        line = raw_line.strip()

        if not line:
            if in_list:
                parts.append("</ol>")
                in_list = False
            continue

        # A line that is ENTIRELY "**Heading**" -> section heading
        if line.startswith("**") and line.endswith("**") and len(line) > 4:
            if in_list:
                parts.append("</ol>")
                in_list = False
            parts.append(f"<h4>{line.strip('*')}</h4>")
            continue

        # "1. text" or "1) text" -> grouped into an <ol>
        m = re.match(r"^\d+[\.\)]\s+(.*)", line)
        if m:
            if not in_list:
                parts.append("<ol>")
                in_list = True
            parts.append(f"<li>{inline_bold(m.group(1))}</li>")
            continue

        if in_list:
            parts.append("</ol>")
            in_list = False
        parts.append(f"<p style='margin:0 0 8px'>{inline_bold(line)}</p>")

    if in_list:
        parts.append("</ol>")
    return "".join(parts)

# ── Gemini call ───────────────────────────────────────────────────────────────
# Current GA flagship as of mid-2026, free tier, no announced shutdown date.
# Gemini 1.0 and 1.5 are fully retired and will 404 on every request.
# If this ever 404s again, run:
#   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
# to see exactly which model IDs your key can currently call.
GEMINI_MODEL = "gemini-3.5-flash"

def call_gemini(answers: dict) -> str:
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API key not found. Add GEMINI_API_KEY to your Streamlit secrets."

    priorities = answers.get("priorities", "Not specified")
    if isinstance(priorities, list):
        priorities = ", ".join(priorities) if priorities else "No strong preference"

    prompt = f"""You are InsureWise AI — a warm, knowledgeable assistant that helps Americans navigate public health insurance programs. A user has shared the following about their situation:

- Currently has insurance: {answers.get("coverage", "Unknown")}
- Household size: {answers.get("household", "Unknown")}
- Children under 19 at home: {answers.get("kids", "Unknown")}
- Employment status: {answers.get("employment", "Unknown")}
- Monthly household income (before taxes): {answers.get("income", "Unknown")}
- Age group: {answers.get("age", "Unknown")}
- Military / veteran connection: {answers.get("military", "Unknown")}
- State: {answers.get("location", "Unknown")}
- Coverage priorities: {priorities}

Please respond with three clearly labeled sections using these exact headings:

**Programs You May Qualify For**
List 2–3 real public programs or plan types (e.g. Medicaid, CHIP, ACA Marketplace Silver plan, Medicare, VA Health). For each, write 1–2 sentences in plain language explaining WHY this person likely qualifies and what it covers.

**Your Action Checklist**
A short numbered list (1. 2. 3.): documents to gather (proof of income, residency, etc.) and exactly where to apply (real website or agency name, e.g. healthcare.gov, their state Medicaid agency).

**One Thing Most People Miss**
One sentence about a deadline, rule, or tip that surprises people in this exact situation.

Keep the tone friendly and clear — no jargon without explanation. Do not include any closing disclaimer sentence — the app displays its own disclaimer separately."""

    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        data = resp.json()

        if "error" in data:
            return f"Gemini error: {data['error'].get('message', 'Unknown error')}"

        candidates = data.get("candidates") or []
        if not candidates:
            reason = data.get("promptFeedback", {}).get("blockReason")
            if reason:
                return f"Gemini didn't return a result (blocked: {reason}). Try rephrasing one of your answers."
            return "Gemini didn't return a result. Please try again."

        parts_out = candidates[0].get("content", {}).get("parts", [])
        text_out = "".join(p.get("text", "") for p in parts_out).strip()
        return text_out or "Gemini returned an empty response. Please try again."

    except requests.exceptions.Timeout:
        return "The request to Gemini timed out. Please try again."
    except Exception as e:
        return f"Something went wrong: {str(e)}"

# ── Question steps ────────────────────────────────────────────────────────────
STEPS = [
    {"id": "coverage",    "question": "Do you currently have any health insurance?",
     "options": ["No, I don't have any", "Yes, through my job", "Yes, my own plan", "Not sure"]},
    {"id": "household",   "question": "How many people are in your household, including you?",
     "options": ["Just me", "2", "3", "4 or more"]},
    {"id": "kids",        "question": "Do you have any children under 19 living with you?",
     "options": ["Yes", "No"]},
    {"id": "employment",  "question": "What's your current employment situation?",
     "options": ["Employed full-time", "Employed part-time", "Self-employed", "Unemployed", "Retired"]},
    {"id": "income",      "question": "Roughly, what's your household's monthly income before taxes?",
     "options": ["Under $1,500", "$1,500–$3,000", "$3,000–$5,000", "Over $5,000"]},
    {"id": "age",         "question": "What's your age group?",
     "options": ["Under 26", "26–49", "50–64", "65 or older"]},
    {"id": "military",    "question": "Have you or an immediate family member served in the U.S. military?",
     "options": ["I'm a veteran", "I'm active duty", "Immediate family served", "Not applicable"]},
    {"id": "location",    "question": "Which state do you live in?",
     # "Other" used to be a dead-end chip that recorded the literal text
     # "Other — I'll type it" as the answer. The free-text box below every
     # question already covers any state not listed, so it's removed here.
     "options": ["Texas", "California", "Florida", "New York"]},
    {"id": "priorities",  "question": "What matters most to you in a plan? (pick all that apply)",
     "options": ["Low monthly cost", "Low deductible", "Keeping my current doctor",
                 "Prescription coverage", "Mental health coverage", "Dental & vision"],
     "multi": True},
]

# ── Session state init ────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "history" not in st.session_state:
    st.session_state.history = []  # list of (role, text)
if "result" not in st.session_state:
    st.session_state.result = None
if "disclaimer_done" not in st.session_state:
    st.session_state.disclaimer_done = False

# ── Brand header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand">
  <span class="brand-dot"></span>
  InsureWise AI
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
if not st.session_state.disclaimer_done:
    st.markdown("""
    <div class="disclaimer-box">
      <strong>Before you continue:</strong> Every provider and plan name in this demo is
      synthetic — built for the USAII Global AI Hackathon 2026. Nothing here is a real
      insurance offer or a guarantee of eligibility. For real enrollment, visit
      <a href="https://healthcare.gov" target="_blank">healthcare.gov</a> or your state Medicaid agency.
    </div>
    """, unsafe_allow_html=True)
    if st.button("I understand — let's get started →"):
        st.session_state.disclaimer_done = True
        st.rerun()
    st.stop()

# ── Done — show result ────────────────────────────────────────────────────────
if st.session_state.result is not None:
    # Replay chat history
    for role, text in st.session_state.history:
        if role == "bot":
            st.markdown(f'<div class="chat-row-bot"><div class="chat-dot chat-dot-bot"></div><div class="chat-bubble-bot">{text}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-row-user"><div class="chat-bubble-user">{text}</div></div>', unsafe_allow_html=True)

    formatted = markdown_to_html(st.session_state.result)

    st.markdown(f"""
    <div class="summary-card">
      {formatted}
      <div class="summary-disclaimer">
        This is guidance, not a guarantee — verify eligibility at
        <a href="https://healthcare.gov" target="_blank">healthcare.gov</a>
        or your state Medicaid agency. Sessions are not stored.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("↩ Start over"):
        for key in ["step", "answers", "history", "result"]:
            del st.session_state[key]
        st.rerun()
    st.stop()

# ── Progress bar ──────────────────────────────────────────────────────────────
total = len(STEPS)
current = st.session_state.step
pct = int((current / total) * 100)
st.markdown(f'<div class="step-label">Step {min(current+1, total)} of {total}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

# ── Replay history ────────────────────────────────────────────────────────────
for role, text in st.session_state.history:
    if role == "bot":
        st.markdown(f'<div class="chat-row-bot"><div class="chat-dot chat-dot-bot"></div><div class="chat-bubble-bot">{text}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-row-user"><div class="chat-bubble-user">{text}</div></div>', unsafe_allow_html=True)

# ── Current question ──────────────────────────────────────────────────────────
step = STEPS[current]
st.markdown(f'<div class="chat-row-bot"><div class="chat-dot chat-dot-bot"></div><div class="chat-bubble-bot">{step["question"]}</div></div>', unsafe_allow_html=True)
st.write("")

is_multi = step.get("multi", False)

if is_multi:
    selected = st.multiselect("Pick all that apply:", step["options"], label_visibility="collapsed")
    if st.button("Send →"):
        answer = selected if selected else []
        display = ", ".join(answer) if answer else "No strong preference"
        st.session_state.history.append(("bot", step["question"]))
        st.session_state.history.append(("user", display))
        st.session_state.answers[step["id"]] = answer
        st.session_state.step += 1
        # Last step — call Gemini
        if st.session_state.step >= total:
            with st.spinner("Checking your options with InsureWise AI..."):
                st.session_state.result = call_gemini(st.session_state.answers)
        st.rerun()
else:
    # Show chips as buttons in columns
    cols = st.columns(2)
    for i, opt in enumerate(step["options"]):
        if cols[i % 2].button(opt, key=f"opt_{current}_{i}"):
            st.session_state.history.append(("bot", step["question"]))
            st.session_state.history.append(("user", opt))
            st.session_state.answers[step["id"]] = opt
            st.session_state.step += 1
            if st.session_state.step >= total:
                with st.spinner("Checking your options with InsureWise AI..."):
                    st.session_state.result = call_gemini(st.session_state.answers)
            st.rerun()

    # Or type it
    st.write("")
    with st.form(key=f"text_form_{current}", clear_on_submit=True):
        typed = st.text_input("Or type your own answer:", placeholder="Type here...", label_visibility="collapsed")
        submitted = st.form_submit_button("Send")
        if submitted and typed.strip():
            st.session_state.history.append(("bot", step["question"]))
            st.session_state.history.append(("user", typed.strip()))
            st.session_state.answers[step["id"]] = typed.strip()
            st.session_state.step += 1
            if st.session_state.step >= total:
                with st.spinner("Checking your options with InsureWise AI..."):
                    st.session_state.result = call_gemini(st.session_state.answers)
            st.rerun()

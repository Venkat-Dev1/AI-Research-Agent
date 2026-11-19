"""Streamlit UI for the AI Research Agent (LangGraph pipeline).

Run:  streamlit run app.py
"""

import io
import re
import traceback
from contextlib import redirect_stdout
from datetime import datetime

import streamlit as st

from pipeline import run_research_pipeline

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
      .block-container {max-width: 1000px; padding-top: 2rem;}
      .hero h1 {margin-bottom: 0.2rem;}
      .hero p {color: #8b8fa3; margin-top: 0;}
      div[data-testid="stTabs"] button {font-size: 1rem; font-weight: 600;}
      .report-box {padding: 0.5rem 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Helpers ----------
def as_text(value) -> str:
    """Normalise LangChain outputs (str / AIMessage / list blocks) to plain text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    content = getattr(value, "content", value)
    if isinstance(content, list):
        return "\n".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return str(content)


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s|)\]>]+", text)
    seen, unique = set(), []
    for u in urls:
        u = u.rstrip(".,;")
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def run_pipeline_safely(topic: str):
    """Run the pipeline, capturing console logs. Returns (state, logs, error)."""
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            state = run_research_pipeline(topic)
        return state, buffer.getvalue(), None
    except Exception:
        return None, buffer.getvalue(), traceback.format_exc()


# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <h1>🔎 AI Research Agent</h1>
      <p>Search → Read → Write → Critique. Enter a topic and get a structured research report.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("research_form", clear_on_submit=False):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of generative AI on software engineering jobs",
    )
    submitted = st.form_submit_button("Run research", type="primary", use_container_width=True)

# ---------- Execution ----------
if submitted:
    topic = topic.strip()
    if not topic:
        st.warning("Please enter a research topic.")
    else:
        with st.status("Running research pipeline...", expanded=True) as status:
            st.write("🔍 Searching, 📖 reading sources, ✍️ drafting, 🧐 reviewing. This can take a minute.")
            state, logs, error = run_pipeline_safely(topic)
            if error:
                status.update(label="Pipeline failed", state="error")
            else:
                status.update(label="Research complete", state="complete", expanded=False)

        if error:
            st.error("The pipeline hit an error. Details below.")
            st.code(error, language="python")
            if logs:
                with st.expander("Execution logs"):
                    st.code(logs)
        else:
            st.session_state["result"] = {
                "topic": topic,
                "state": state,
                "logs": logs,
                "time": datetime.now().strftime("%d %b %Y, %H:%M"),
            }

# ---------- Results ----------
result = st.session_state.get("result")
if result:
    state = result["state"]
    report = as_text(state.get("report"))
    feedback = as_text(state.get("feedback"))
    search_results = as_text(state.get("search_agent_response"))
    scraped = as_text(state.get("Scrapped_content"))
    sources = state.get("urls") or extract_urls(search_results)

    st.divider()
    head, action = st.columns([4, 1])
    with head:
        st.subheader(result["topic"])
        st.caption(f"Generated on {result['time']}")
    with action:
        safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", result["topic"]).strip("_")[:50] or "report"
        st.download_button(
            "⬇ Download report",
            data=report,
            file_name=f"{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    m1, m2, m3 = st.columns(3)
    m1.metric("Sources found", len(sources))
    m2.metric("Report words", len(report.split()))
    m3.metric("Page scraped", "Yes" if scraped.strip() else "No")

    tab_report, tab_review, tab_sources, tab_raw = st.tabs(
        ["📄 Report", "🧐 Critic Review", "🔗 Sources", "🛠 Raw Data"]
    )

    with tab_report:
        if report.strip():
            st.markdown(f'<div class="report-box">', unsafe_allow_html=True)
            st.markdown(report)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No report was generated.")

    with tab_review:
        if feedback.strip():
            if feedback.startswith("Critic failed"):
                st.error(feedback)
            else:
                st.markdown(feedback)
        else:
            st.info("No critic feedback available.")

    with tab_sources:
        if sources:
            for i, url in enumerate(sources, 1):
                st.markdown(f"{i}. [{url}]({url})")
        else:
            st.info("No source URLs were detected in the search results.")
        with st.expander("Search agent output"):
            st.markdown(search_results or "_Empty_")

    with tab_raw:
        with st.expander("Scraped content"):
            st.text(scraped or "No content scraped.")
        with st.expander("Execution logs"):
            st.code(result["logs"] or "No logs captured.")
from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
ANALYSIS = ROOT / "outputs" / "review_analysis.json"
PULSE = ROOT / "outputs" / "weekly_product_pulse.md"
FEE = ROOT / "outputs" / "fee_explainer.md"
CSV = ROOT / "data" / "reviews.csv"

st.set_page_config(page_title="Milestone 5 Review Pulse", page_icon="📊", layout="wide")
st.title("📊 ChatGPT Review Pulse")
st.caption("Milestone 5 · Evidence-based review analysis dashboard")
st.info("This dashboard displays the output of your local pipeline. It does not create reviews or invent evidence.")

with st.sidebar:
    st.header("Project controls")
    st.write("1. Collect reviews in the VS Code terminal.")
    st.code("python collect_reviews.py", language="bash")
    st.write("2. Run the analysis pipeline.")
    st.code("python run_pipeline.py", language="bash")
    if st.button("Refresh dashboard", type="primary"):
        st.rerun()
    st.caption("After rerunning the pipeline, click Refresh dashboard.")

if not ANALYSIS.exists():
    st.warning("No analysis report found yet.")
    st.markdown("**First:** run `python collect_reviews.py`, then `python run_pipeline.py` in your VS Code terminal.")
    st.markdown("When `outputs/review_analysis.json` exists, refresh this page.")
    st.stop()

try:
    report = json.loads(ANALYSIS.read_text(encoding="utf-8"))
except Exception as exc:
    st.error(f"Could not read the analysis report: {exc}")
    st.stop()

count = int(report.get("review_count", 0))
date_range = report.get("date_range", {})
c1, c2, c3 = st.columns(3)
c1.metric("Usable reviews", count)
c2.metric("First review date", date_range.get("start", "—"))
c3.metric("Last review date", date_range.get("end", "—"))
st.caption(f"Report generated: {report.get('generated_date', 'unknown')} · Method: {report.get('method', 'not specified')}")

st.subheader("Theme overview")
theme_counts = {x.get("theme","Theme"): x.get("review_count",0) for x in report.get("theme_clusters", [])}
if theme_counts and any(int(v) > 0 for v in theme_counts.values()):
    chart_df = pd.DataFrame({"Theme": list(theme_counts.keys()), "Review matches": [int(v) for v in theme_counts.values()]})
    st.bar_chart(chart_df.set_index("Theme"))
    st.dataframe(chart_df.sort_values("Review matches", ascending=False), use_container_width=True, hide_index=True)
else:
    st.warning("No theme matches were found. Check the collected reviews and keyword rules.")

st.subheader("Top 3 theme candidates")
top = report.get("top_3_themes", [])
if top:
    cols = st.columns(len(top))
    for col, item in zip(cols, top):
        col.metric(item.get("theme", "Theme"), item.get("review_count", 0), help="Reviews assigned to this automatically generated cluster.")
else:
    st.write("No top themes available.")

st.subheader("Three recent review quotes")
quotes = report.get("three_real_review_quotes", [])
if quotes:
    for i, item in enumerate(quotes, start=1):
        with st.expander(f"Review {i} · {item.get('date', 'date unknown')} · Rating: {item.get('rating', 'unknown')}"):
            st.write(item.get("quote", ""))
            if item.get("source_url"):
                st.markdown(f"[Open original review]({item['source_url']})")
else:
    st.write("No quotes available yet.")

st.subheader("Billing / fee confusion evidence")
st.write(report.get("fee_issue_status", "No fee status available."))
fee_items = report.get("fee_issue_candidates", [])
if fee_items:
    for i, item in enumerate(fee_items, start=1):
        with st.expander(f"Candidate {i} · {item.get('date', 'date unknown')}"):
            st.write(item.get("quote", ""))
            if item.get("source_url"):
                st.markdown(f"[Open original review]({item['source_url']})")
else:
    st.write("No billing-related review candidates found. Do not invent a recurring issue.")

left, right = st.columns(2)
with left:
    st.subheader("Weekly Product Pulse")
    if PULSE.exists():
        st.markdown(PULSE.read_text(encoding="utf-8"))
    else:
        st.warning("Pulse not generated yet. Run `python run_pipeline.py`.")
with right:
    st.subheader("Fee Explainer")
    if FEE.exists():
        st.markdown(FEE.read_text(encoding="utf-8"))
    else:
        st.warning("Fee explainer not generated yet. Run `python run_pipeline.py`.")

st.divider()
st.subheader("MCP approval gate")
st.warning("External actions are BLOCKED until you preview the outputs and explicitly approve them in the MCP client.")
st.code("preview_outputs → approve_outputs('APPROVE MILESTONE 5 OUTPUTS') → append_to_google_doc / create_gmail_draft")
st.caption("The Gmail action creates a draft only; it never sends the email. Google Docs and Gmail require your Google OAuth credentials.")
st.caption("Method: automated clustering on the collected review sample. Verify public quotes and official policy sources before submission.")

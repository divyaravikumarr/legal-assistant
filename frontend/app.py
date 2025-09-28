import json
import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# --- Page config ---
st.set_page_config(
    page_title="⚖️ SME LegalSync",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #F9FAFB;
    }
    .stApp {
        background: linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
    }
    .main-header p {
        color: #DBEAFE;
        font-size: 1.1rem;
        text-align: center;
        margin: 0.5rem 0 0;
    }
    .sidebar .sidebar-content {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background: #1E3A8A;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #3B82F6;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .stTabs [role="tab"] {
        font-weight: 600;
        color: #1E3A8A;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: #DBEAFE;
        color: #1E3A8A;
    }
    .stTabs [role="tab"]:hover {
        background: #EFF6FF;
    }
    .stMetric {
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stExpander {
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .stExpander:hover {
        border-color: #3B82F6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- App Header ---
st.markdown(
    """
    <div class="main-header">
        <h1>⚖️ SME LegalSync</h1>
        <p>Empowering Small Businesses with Smart Contract Insights</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar controls ---
st.sidebar.header("⚙️ Control Panel")
backend = st.sidebar.text_input("Backend URL", "http://localhost:8000", help="Enter the backend API URL")
lang = st.sidebar.selectbox("Language", ["English", "Hindi"], index=0, help="Select explanation language")
max_pages = st.sidebar.slider("Max Pages", 5, 30, 20, help="Maximum pages to analyze")
time_budget = st.sidebar.slider("Analysis Time (sec)", 5, 30, 15, help="Time budget for analysis")
use_llm = st.sidebar.checkbox("Enable AI Insights", value=True, help="Use LLM for deeper analysis")

if st.sidebar.button("🔗 Test Connection"):
    try:
        r = requests.get(f"{backend}/health", timeout=10)
        r.raise_for_status()
        st.sidebar.success("✅ Backend Connected")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed: {e}")

# --- Tabs Layout ---
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Contract", "📊 Risk Dashboard", "📜 Clause Insights", "⬇️ Export Reports"])

# --- Session state init ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
    st.session_state.report_pdf = None

with tab1:
    st.header("📤 Upload Your Contract")
    st.markdown("Upload a PDF, DOCX, or TXT file to analyze contract risks.")
    uploaded = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    if st.button("🚀 Analyze Contract", type="primary", use_container_width=True):
        if not uploaded:
            st.error("Please upload a contract file.")
        else:
            try:
                files = {"file": (uploaded.name, uploaded.getvalue())}
                options = {
                    "lang": lang,
                    "max_pages": int(max_pages),
                    "time_budget_sec": int(time_budget),
                    "use_llm": bool(use_llm),
                }
                data = {"options": json.dumps(options)}

                with st.spinner("Analyzing your contract..."):
                    r = requests.post(f"{backend}/analyze", files=files, data=data, timeout=180)
                    r.raise_for_status()
                    st.session_state.analysis_result = r.json()
                st.success("✅ Analysis Complete! View results in the Risk Dashboard.")
            except Exception as e:
                st.error(f"❌ Analysis Failed: {e}")

with tab2:
    st.header("📊 Risk Dashboard")
    res = st.session_state.analysis_result
    if not res:
        st.info("Upload a contract in the **Upload Contract** tab to see insights.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", f"{res.get('overall_score',0)}/10", delta="Higher is riskier")
        col2.metric("Risk Level", res.get("bucket", "-"), delta_color="off")
        col3.metric("Analysis Time", f"{res.get('duration_ms',0)} ms")

        # --- Risk Distribution Pie ---
        clauses = res.get("clauses", [])
        df = pd.DataFrame([{"title": c["title"], "risk": c["risk"]} for c in clauses])

        if not df.empty:
            def risk_level(r):
                if r == 0: return "Safe"
                elif r <= 3: return "Low"
                elif r <= 6: return "Medium"
                return "High"
            df["level"] = df["risk"].apply(risk_level)

            pie = px.pie(df, names="level", title="Clause Risk Breakdown", color="level",
                         color_discrete_map={"Safe":"green","Low":"lightgreen","Medium":"orange","High":"red"},
                         hole=0.3)
            pie.update_layout(title_x=0.5, margin=dict(t=50, b=20))
            st.plotly_chart(pie, use_container_width=True)

            # --- Top Risks Bar ---
            top_risks = res.get("top_risks", [])
            if top_risks:
                risk_df = pd.DataFrame(top_risks)
                bar = px.bar(risk_df, x="title", y="score", color="score", title="Top Risky Clauses",
                             color_continuous_scale="RdYlGn_r", text_auto=True)
                bar.update_layout(title_x=0.5, xaxis_title="", yaxis_title="Risk Score", margin=dict(t=50, b=20))
                st.plotly_chart(bar, use_container_width=True)

with tab3:
    st.header("📜 Clause Insights")
    res = st.session_state.analysis_result
    if not res:
        st.info("No analysis available. Upload a contract to view clause details.")
    else:
        for c in res["clauses"]:
            title = c.get("title","Clause")
            risk = c.get("risk",0)

            if risk == 0:
                risk_label = f"🟢 Safe (0/10)"
            elif risk <= 3:
                risk_label = f"🟢 Low ({risk}/10)"
            elif risk <= 6:
                risk_label = f"🟡 Medium ({risk}/10)"
            else:
                risk_label = f"🔴 High ({risk}/10)"

            with st.expander(f"{title} — {risk_label}", expanded=False):
                st.markdown(f"**Clause Text:** {c.get('text','No text available')}")
                if c.get("rule_hits"):
                    st.caption("**Rules Triggered:** " + ", ".join(c["rule_hits"]))
                if c.get("entities"):
                    st.caption("**Entities Detected:** " + ", ".join(c["entities"]))
                if c.get("llm"):
                    st.markdown("**AI Insights:**")
                    if c["llm"].get("explanation"):
                        st.info(c["llm"]["explanation"])
                    if c["llm"].get("issue"):
                        st.warning(f"⚠️ {c['llm']['issue']}")
                    if c["llm"].get("alt_clause"):
                        st.code(c["llm"]["alt_clause"], language="markdown")

with tab4:
    st.header("⬇️ Export Reports")
    res = st.session_state.get("analysis_result")

    if not res:
        st.info("Run an analysis in the **Upload Contract** tab to enable exports.")
    else:
        # Markdown Export
        with st.expander("📝 Markdown Report", expanded=True):
            if st.button("📥 Generate Markdown", use_container_width=True):
                with st.spinner("Generating Markdown report..."):
                    try:
                        rr = requests.post(f"{backend}/report", json=res, timeout=60)
                        rr.raise_for_status()
                        st.download_button(
                            "Download report.md",
                            data=rr.text,
                            file_name="contract_analysis.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"❌ Could not generate report: {e}")

        # PDF Export
        with st.expander("📄 PDF Report", expanded=False):
            if st.button("📄 Generate PDF", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    try:
                        rr = requests.post(f"{backend}/report/pdf", json=res, timeout=90)
                        rr.raise_for_status()
                        st.session_state.report_pdf = rr.content
                        st.success("✅ PDF report generated. Download below.")
                    except Exception as e:
                        st.error(f"❌ Could not generate PDF: {e}")

            if st.session_state.get("report_pdf"):
                st.download_button(
                    "📥 Download report.pdf",
                    data=st.session_state.report_pdf,
                    file_name="contract_analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
"""
MediScript AI — Complete Streamlit Frontend
Pakistan's First AI Prescription Analyzer
HackData V1 | GDGoC CUI Wah
Project Idea: Hamza Ali | Team: Muhammad Umair Malik | Shahzaib Shoaib Rathore
"""

import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediScript AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0A0F1E 0%, #0D1B2A 50%, #0A1628 100%);
    min-height: 100vh;
}

/* Header Banner */
.mediscript-header {
    background: linear-gradient(90deg, #001A2C 0%, #003348 50%, #001A2C 100%);
    border: 1px solid #00BCD4;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.mediscript-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00BCD4, #00E5FF, #00BCD4, transparent);
}
.header-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #00E5FF;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0;
    line-height: 1.1;
}
.header-sub {
    color: #607D8B;
    font-size: 0.95rem;
    margin: 0;
}
.header-tagline {
    color: #00BCD4;
    font-size: 0.85rem;
    margin: 8px 0 0 0;
    font-family: 'JetBrains Mono', monospace;
}

/* Drug Cards */
.drug-card {
    background: linear-gradient(135deg, #0F2030, #142840);
    border: 1px solid #1E3A4F;
    border-left: 3px solid #00BCD4;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    transition: border-color 0.2s;
}
.drug-card:hover { border-left-color: #00E5FF; }
.drug-name {
    color: #00E5FF;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 8px 0;
}
.drug-meta {
    color: #8FA8B8;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Interaction Badges */
.badge-severe {
    background: rgba(255,77,109,0.15);
    border: 1px solid #FF4D6D;
    color: #FF4D6D;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-moderate {
    background: rgba(255,215,0,0.15);
    border: 1px solid #FFD700;
    color: #FFD700;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-mild {
    background: rgba(0,200,83,0.15);
    border: 1px solid #00C853;
    color: #00C853;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #0F2030, #142840);
    border: 1px solid #1E3A4F;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #00E5FF;
    line-height: 1;
}
.metric-label {
    color: #607D8B;
    font-size: 0.8rem;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Auth Forms */
.auth-container {
    max-width: 420px;
    margin: 0 auto;
    background: linear-gradient(135deg, #0F2030, #0D1B2A);
    border: 1px solid #1E3A4F;
    border-radius: 20px;
    padding: 40px;
}
.auth-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #00E5FF;
    text-align: center;
    margin-bottom: 8px;
}
.auth-sub {
    color: #607D8B;
    text-align: center;
    font-size: 0.9rem;
    margin-bottom: 28px;
}

/* Explanation Boxes */
.explain-en {
    background: rgba(0,188,212,0.08);
    border: 1px solid rgba(0,188,212,0.3);
    border-radius: 12px;
    padding: 20px;
    color: #B0D4E0;
    line-height: 1.8;
    font-size: 0.95rem;
}
.explain-ur {
    background: rgba(0,200,83,0.08);
    border: 1px solid rgba(0,200,83,0.3);
    border-radius: 12px;
    padding: 20px;
    color: #A8D5B8;
    line-height: 1.8;
    font-size: 0.95rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0D1B2A;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #607D8B;
    border-radius: 8px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #1E3A4F !important;
    color: #00E5FF !important;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00BCD4, #00E5FF);
    color: #0A0F1E;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 1rem;
    letter-spacing: 0.5px;
    transition: opacity 0.2s;
}
.stButton > button[kind="primary"]:hover { opacity: 0.9; }

/* Input fields */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus {
    background: #0F2030;
    border-color: #1E3A4F;
    color: #E0F0F8;
    border-radius: 8px;
}

/* File uploader */
.stFileUploader > div {
    background: #0F2030;
    border: 2px dashed #1E3A4F;
    border-radius: 12px;
    transition: border-color 0.2s;
}
.stFileUploader > div:hover { border-color: #00BCD4; }

/* Expanders */
.streamlit-expanderHeader {
    background: #0F2030;
    border-radius: 8px;
    color: #00BCD4;
}

/* Divider */
hr {
    border-color: #1E3A4F;
}

/* Section labels */
.section-label {
    color: #607D8B;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

/* Sidebar */
.css-1d391kg, section[data-testid="stSidebar"] {
    background: #0A0F1E;
    border-right: 1px solid #1E3A4F;
}

/* Warning / info / success overrides */
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Session State Defaults ────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state["user"] = None
if "result" not in st.session_state:
    st.session_state["result"] = None
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"


# ── Helper Functions ──────────────────────────────────────────────────────────
def backend_get(endpoint: str, params: dict = None) -> dict:
    try:
        r = requests.get(f"{BACKEND}{endpoint}", params=params, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def backend_post(endpoint: str, json_data: dict = None) -> dict:
    try:
        r = requests.post(f"{BACKEND}{endpoint}", json=json_data, timeout=15)
        return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def severity_badge(sev: str) -> str:
    cls_map = {"SEVERE": "badge-severe", "MODERATE": "badge-moderate", "MILD": "badge-mild"}
    return f'<span class="{cls_map.get(sev, "badge-mild")}">{sev}</span>'


# ── Auth Pages ────────────────────────────────────────────────────────────────
def show_auth_page():
    st.markdown("""
    <div class="mediscript-header">
        <p class="header-title">💊 MediScript AI</p>
        <p class="header-sub">Pakistan's First AI Prescription Analyzer</p>
        <p class="header-tagline">// HackData V1 | GDGoC CUI Wah | Project by Hamza Ali</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1.4, 1])
    with col_b:
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])

        with tab_login:
            st.markdown("#### Welcome back")
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Login →", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        result = backend_post("/auth/login", {"email": email, "password": password})
                    if result.get("success"):
                        st.session_state["user"] = result["user"]
                        st.success(f"Welcome back, {result['user']['username']}!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Login failed"))
            st.markdown("---")
            st.caption("💡 Don't have an account? Use the Sign Up tab above.")

        with tab_signup:
            st.markdown("#### Create your account")
            full_name = st.text_input("Full Name", key="su_name", placeholder="Muhammad Umair")
            su_email = st.text_input("Email", key="su_email", placeholder="you@example.com")
            su_username = st.text_input("Username", key="su_user", placeholder="umair123")
            su_pass = st.text_input("Password", type="password", key="su_pass", placeholder="••••••••")
            su_pass2 = st.text_input("Confirm Password", type="password", key="su_pass2", placeholder="••••••••")
            if st.button("Create Account →", type="primary", use_container_width=True):
                if su_pass != su_pass2:
                    st.error("Passwords do not match.")
                elif not su_email or not su_username or not su_pass:
                    st.error("All fields are required.")
                else:
                    with st.spinner("Creating account..."):
                        result = backend_post("/auth/signup", {
                            "email": su_email,
                            "username": su_username,
                            "password": su_pass,
                            "full_name": full_name,
                        })
                    if result.get("success"):
                        st.session_state["user"] = result["user"]
                        st.success("Account created! Welcome to MediScript AI! 🎉")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Signup failed"))

    # Features preview
    st.markdown("<br>", unsafe_allow_html=True)
    feat_cols = st.columns(4)
    features = [
        ("🔬", "AI Vision", "Gemini reads any prescription"),
        ("⚕️", "500K+ Records", "FDA drug interaction database"),
        ("🌐", "Bilingual", "English + Roman Urdu"),
        ("📊", "Reports", "Download PDF reports"),
    ]
    for col, (icon, title, desc) in zip(feat_cols, features):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:2rem">{icon}</div>
                <div style="color:#00E5FF;font-weight:600;margin:8px 0 4px">{title}</div>
                <div style="color:#607D8B;font-size:0.8rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Main App (Logged In) ──────────────────────────────────────────────────────
def show_main_app():
    user = st.session_state["user"]

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0 8px">
            <div style="font-size:2.5rem">💊</div>
            <div style="color:#00E5FF;font-weight:700;font-size:1.1rem">MediScript AI</div>
            <div style="color:#607D8B;font-size:0.75rem">HackData V1</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        st.markdown(f"""
        <div style="background:#0F2030;border:1px solid #1E3A4F;border-radius:10px;padding:12px 16px;margin-bottom:12px">
            <div style="color:#607D8B;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px">Logged in as</div>
            <div style="color:#00E5FF;font-weight:600;margin-top:2px">{user['username']}</div>
            <div style="color:#607D8B;font-size:0.8rem">{user.get('email','')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Navigation**")
        nav = st.radio("", ["🔬 Analyze", "📊 Dashboard", "📋 My Scans", "ℹ️ Help"], label_visibility="collapsed")

        st.divider()
        st.caption("**Team MediScript AI**")
        st.caption("💡 Idea: Hamza Ali")
        st.caption("👨‍💻 Muhammad Umair Malik")
        st.caption("👨‍💻 Shahzaib Shoaib Rathore")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["result"] = None
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="mediscript-header">
        <p class="header-title">💊 MediScript AI</p>
        <p class="header-sub">Pakistan's First AI Prescription Analyzer — Upload • Analyze • Understand</p>
        <p class="header-tagline">// HackData V1 | GDGoC CUI Wah | Powered by Google Gemini (Anti-Gravity) + OpenFDA + RxNorm</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Route to page ─────────────────────────────────────────────────────────
    if "Analyze" in nav:
        show_analyze_page(user)
    elif "Dashboard" in nav:
        show_dashboard_page(user)
    elif "Scans" in nav:
        show_history_page(user)
    elif "Help" in nav:
        show_help_page()


# ── Analyze Page ──────────────────────────────────────────────────────────────
def show_analyze_page(user: dict):
    col_left, col_right = st.columns([1, 1.1], gap="large")

    with col_left:
        st.markdown("### 📤 Upload Prescription")
        uploaded_file = st.file_uploader(
            "Take a photo or upload prescription image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Works with handwritten or printed prescriptions. For best results use a clear, well-lit photo.",
            label_visibility="collapsed",
        )

        if uploaded_file:
            st.image(uploaded_file, caption="📄 Your Prescription", use_container_width=True)
            st.caption(f"File: {uploaded_file.name} | Size: {round(uploaded_file.size/1024,1)} KB")

            if st.button("🔬 Analyze Prescription", type="primary", use_container_width=True):
                with st.status("Analyzing prescription...", expanded=True) as status:
                    st.write("📸 Enhancing image quality...")
                    try:
                        headers = {}
                        if user.get("id"):
                            headers["X-User-Id"] = user["id"]

                        st.write("🤖 Calling Gemini Vision AI (Anti-Gravity)...")
                        resp = requests.post(
                            f"{BACKEND}/analyze",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")},
                            headers=headers,
                            timeout=90,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get("success"):
                                st.write("⚕️ Checking FDA drug interactions...")
                                st.write("🌐 Generating bilingual explanation...")
                                st.write("✅ Analysis complete!")
                                status.update(label="✅ Analysis Complete!", state="complete")
                                st.session_state["result"] = data
                            else:
                                status.update(label="⚠️ Could not extract drugs", state="error")
                                st.error(data.get("error", "Analysis failed"))
                                if data.get("raw_text"):
                                    with st.expander("Raw text from image"):
                                        st.text(data["raw_text"])
                        else:
                            status.update(label="❌ Error", state="error")
                            st.error(f"Backend error: {resp.text[:300]}")
                    except requests.exceptions.ConnectionError:
                        status.update(label="❌ Connection Error", state="error")
                        st.error("Cannot connect to backend. Make sure backend is running.")
                    except Exception as e:
                        status.update(label="❌ Error", state="error")
                        st.error(f"Error: {str(e)}")
        else:
            st.markdown("""
            <div style="background:#0F2030;border:2px dashed #1E3A4F;border-radius:12px;
                        padding:40px;text-align:center;margin-top:12px">
                <div style="font-size:3rem;margin-bottom:12px">📋</div>
                <div style="color:#00BCD4;font-weight:600;margin-bottom:8px">Upload a prescription photo</div>
                <div style="color:#607D8B;font-size:0.85rem">Supports JPG, PNG, WEBP<br>Handwritten or printed prescriptions</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        if st.session_state.get("result"):
            show_results(st.session_state["result"])
        else:
            st.markdown("""
            <div style="padding:60px 0;text-align:center">
                <div style="font-size:4rem;opacity:0.3">💊</div>
                <div style="color:#1E3A4F;font-size:1.1rem;margin-top:12px">Results will appear here</div>
            </div>
            """, unsafe_allow_html=True)


def show_results(data: dict):
    """Display full analysis results."""
    drugs_info = data.get("drugs", {})
    drug_list = drugs_info.get("drug_list", [])
    interactions = data.get("interactions", [])
    explanation = data.get("explanation", {})
    recommendations = data.get("recommendations", {})
    double_check = data.get("double_check", {})

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(drug_list)}</div>
            <div class="metric-label">Drugs Found</div></div>""", unsafe_allow_html=True)
    with m2:
        sev_color = "#FF4D6D" if interactions else "#00C853"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{sev_color}">{len(interactions)}</div>
            <div class="metric-label">Interactions</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(explanation.get('warnings', []))}</div>
            <div class="metric-label">Warnings</div></div>""", unsafe_allow_html=True)
    with m4:
        confidence = double_check.get("confidence", "—")
        conf_color = {"high": "#00C853", "medium": "#FFD700", "low": "#FF4D6D"}.get(confidence, "#607D8B")
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{conf_color};font-size:1.6rem">{confidence.upper()}</div>
            <div class="metric-label">AI Confidence</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Summary
    if explanation.get("summary"):
        st.info(f"📝 **Summary:** {explanation['summary']}")

    # Doctor / Patient info
    if drugs_info.get("doctor_name") or drugs_info.get("date"):
        with st.expander("📋 Prescription Details"):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Doctor:** {drugs_info.get('doctor_name', 'Unknown')}")
            c2.write(f"**Patient:** {drugs_info.get('patient_name', 'Unknown')}")
            c3.write(f"**Date:** {drugs_info.get('date', 'Unknown')}")
            if drugs_info.get("diagnosis"):
                st.write(f"**Diagnosis/Notes:** {drugs_info.get('diagnosis', '')}")

    # Drug cards
    if drug_list:
        st.markdown("#### 💊 Medications Found")
        for drug in drug_list:
            name = drug.get("name", "Unknown Drug")
            dosage = drug.get("dosage", "?")
            freq = drug.get("frequency_readable", drug.get("frequency", "?"))
            duration = drug.get("duration", "?")
            route = drug.get("route", "oral")
            instructions = drug.get("instructions", "")
            generic = drug.get("generic_name", "")

            st.markdown(f"""
            <div class="drug-card">
                <div class="drug-name">💊 {name}
                    {'<span style="color:#607D8B;font-size:0.8rem;font-weight:400"> / ' + generic + '</span>' if generic and generic != name else ''}
                </div>
                <div class="drug-meta">
                    🔹 Dose: {dosage} &nbsp;|&nbsp; ⏰ {freq} &nbsp;|&nbsp; 📅 {duration} &nbsp;|&nbsp; 🩺 {route}
                    {'<br>📌 ' + instructions if instructions and instructions not in ('unclear', '') else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Double-check results
    if double_check.get("issues"):
        with st.expander("🔍 AI Double-Check Results"):
            issues = double_check.get("issues", [])
            if issues:
                for issue in issues:
                    sev = issue.get("severity", "info")
                    if sev == "critical":
                        st.error(f"🚨 {issue.get('drug', '?')}: {issue.get('issue', '')}")
                    elif sev == "warning":
                        st.warning(f"⚠️ {issue.get('drug', '?')}: {issue.get('issue', '')}")
                    else:
                        st.info(f"ℹ️ {issue.get('drug', '?')}: {issue.get('issue', '')}")
            # Dosage checks table
            checks = double_check.get("dosage_checks", [])
            if checks:
                df_checks = pd.DataFrame(checks)
                st.dataframe(df_checks, use_container_width=True, hide_index=True)

    # Interactions
    st.markdown("#### ⚕️ Drug Interactions")
    if interactions:
        for ix in interactions:
            sev = ix.get("severity", "MODERATE")
            desc = ix.get("description", "")
            source = ix.get("source", "")
            badge = severity_badge(sev)
            fn = st.error if sev == "SEVERE" else st.warning if sev == "MODERATE" else st.info
            fn(f"**{ix['drug1']}** + **{ix['drug2']}** — {desc} *(Source: {source})*")

        # Plotly chart
        labels = [f"{x['drug1']} + {x['drug2']}" for x in interactions]
        sev_scores = [3 if x["severity"] == "SEVERE" else 2 if x["severity"] == "MODERATE" else 1 for x in interactions]
        bar_colors = ["#FF4D6D" if s == 3 else "#FFD700" if s == 2 else "#00C853" for s in sev_scores]
        text_labels = ["SEVERE" if s == 3 else "MODERATE" if s == 2 else "MILD" for s in sev_scores]

        fig = go.Figure(go.Bar(
            x=labels, y=sev_scores,
            marker_color=bar_colors,
            text=text_labels, textposition="auto",
            hovertemplate="%{x}<br>Severity: %{text}<extra></extra>",
        ))
        fig.update_layout(
            title="Interaction Severity Chart",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,27,42,0.8)",
            height=280,
            margin=dict(t=40, b=20, l=0, r=0),
            yaxis=dict(
                tickvals=[1, 2, 3],
                ticktext=["MILD", "MODERATE", "SEVERE"],
                gridcolor="#1E3A4F",
            ),
            xaxis=dict(gridcolor="#1E3A4F"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No dangerous drug interactions detected!")

    # Bilingual explanations
    st.markdown("#### 🌐 Bilingual Explanation")
    tab_en, tab_ur = st.tabs(["🇬🇧 English", "🇵🇰 Roman Urdu"])
    with tab_en:
        st.markdown(f"""<div class="explain-en">{explanation.get('english', 'Not available')}</div>""",
                    unsafe_allow_html=True)
    with tab_ur:
        st.markdown(f"""<div class="explain-ur">{explanation.get('urdu', 'Not available')}</div>""",
                    unsafe_allow_html=True)

    # Warnings
    warnings = explanation.get("warnings", [])
    if warnings:
        st.markdown("#### ⚠️ Warnings")
        for w in warnings:
            st.warning(f"⚠️ {w}")

    # Tips
    tips = explanation.get("tips", [])
    if tips:
        with st.expander("💡 Tips for Safe Use"):
            for tip in tips:
                st.success(f"✓ {tip}")

    # Recommendations
    if recommendations:
        with st.expander("🩺 Doctor Recommendations & Lifestyle Advice"):
            urgency = recommendations.get("urgency", "normal")
            if urgency == "urgent":
                st.error("🚨 **URGENT:** Please consult your doctor immediately.")
            elif urgency == "consult_soon":
                st.warning("⚠️ Please consult your doctor at your earliest convenience.")

            dietary = recommendations.get("dietary", [])
            if dietary:
                st.markdown("**Dietary:**")
                for d in dietary:
                    st.write(f"• {d}")

            lifestyle = recommendations.get("lifestyle", [])
            if lifestyle:
                st.markdown("**Lifestyle:**")
                for l in lifestyle:
                    st.write(f"• {l}")

            alternatives = recommendations.get("alternatives", [])
            if alternatives:
                st.markdown("**Possible Alternatives (consult doctor first):**")
                for a in alternatives:
                    st.write(f"• **{a['original']}** → {a['alternative']}: {a['reason']}")

            supplements = recommendations.get("supplements", [])
            if supplements:
                st.markdown("**Recommended Supplements:**")
                for s in supplements:
                    st.write(f"• **{s['name']}** ({s['dose']}): {s['purpose']}")

    # PDF Download
    st.markdown("---")
    if st.button("📄 Generate & Download PDF Report", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                from utils.report_generator import generate_pdf_report
                pdf_bytes = generate_pdf_report(
                    drugs=data.get("drugs", {}),
                    interactions=data.get("interactions", []),
                    explanation=data.get("explanation", {}),
                    recommendations=data.get("recommendations", {}),
                    double_check=data.get("double_check", {}),
                    scan_id=data.get("scan_id", ""),
                )
                if pdf_bytes:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name="mediscript_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.info("PDF generation requires ReportLab (pip install reportlab)")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")


# ── Dashboard Page ────────────────────────────────────────────────────────────
def show_dashboard_page(user: dict):
    st.markdown("### 📊 Analytics Dashboard")

    col_refresh = st.columns([5, 1])
    with col_refresh[1]:
        refresh = st.button("🔄 Refresh", use_container_width=True)

    # Stats
    stats = backend_get("/dashboard", params={"user_id": user.get("id")})
    user_stats = stats.get("stats", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{user_stats.get('total_scans', 0)}</div>
            <div class="metric-label">Total Scans</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#FF4D6D">{user_stats.get('total_interactions', 0)}</div>
            <div class="metric-label">Interactions Found</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{user_stats.get('total_drugs', 0)}</div>
            <div class="metric-label">Total Drugs Analyzed</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analytics charts
    analytics = backend_get("/analytics")
    if analytics:
        df_analytics = pd.DataFrame(analytics)

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_bar = px.bar(
                df_analytics.head(10),
                x="drug_name", y="scan_count",
                title="Top 10 Most Scanned Drugs",
                template="plotly_dark",
                color="scan_count",
                color_continuous_scale=["#1E3A4F", "#00BCD4"],
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,27,42,0.8)",
                height=320,
                margin=dict(t=40, b=60, l=0, r=0),
                coloraxis_showscale=False,
                xaxis=dict(tickangle=-30),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            if len(df_analytics) > 0:
                fig_pie = px.pie(
                    df_analytics.head(8),
                    names="drug_name", values="scan_count",
                    title="Drug Distribution",
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.ice,
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=320,
                    margin=dict(t=40, b=0, l=0, r=0),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

    # Activity log
    activity = backend_get(f"/user/{user['id']}/activity", params={"limit": 10})
    if activity:
        st.markdown("#### 🕐 Recent Activity")
        for act in activity:
            created = act.get("created_at", "")[:16].replace("T", " ")
            action = act.get("action", "")
            icon_map = {"login": "🔑", "signup": "📝", "scan": "🔬", "report_download": "📄"}
            icon = icon_map.get(action, "•")
            st.markdown(
                f'<div style="color:#607D8B;font-size:0.85rem;padding:4px 0">'
                f'{icon} <span style="color:#8FA8B8">{action}</span> — {created}</div>',
                unsafe_allow_html=True,
            )


# ── History Page ──────────────────────────────────────────────────────────────
def show_history_page(user: dict):
    st.markdown("### 📋 My Prescription Scans")

    history = backend_get("/history", params={"limit": 50, "user_id": user.get("id")})

    if not history:
        st.info("No scans yet. Upload your first prescription in the Analyze tab!")
        return

    st.caption(f"Found **{len(history)}** scan(s)")

    for scan in history:
        created = scan.get("created_at", "")[:16].replace("T", " ")
        drug_count = scan.get("drug_count", 0)
        has_ix = scan.get("has_interaction", False)
        scan_id = scan.get("id", "")[:8]
        summary = scan.get("summary", "")

        badge_html = (
            '<span style="color:#FF4D6D;font-size:0.75rem">⚠ Interactions</span>'
            if has_ix
            else '<span style="color:#00C853;font-size:0.75rem">✓ Safe</span>'
        )

        with st.expander(f"📋 Scan {scan_id} | {drug_count} drugs | {created} | {badge_html}", expanded=False):
            # Parse drug list
            try:
                drugs = json.loads(scan.get("drug_list", "[]"))
                if drugs:
                    st.markdown("**Medications:**")
                    for d in drugs:
                        st.write(f"• {d.get('name','?')} — {d.get('dosage','?')} | {d.get('frequency','?')}")
            except Exception:
                pass

            if summary:
                st.info(f"📝 {summary}")

            # Show English explanation
            explanation_en = scan.get("explanation_en", "")
            if explanation_en:
                with st.expander("English Explanation"):
                    st.write(explanation_en)

            # Show Urdu
            explanation_ur = scan.get("explanation_ur", "")
            if explanation_ur:
                with st.expander("Roman Urdu Explanation"):
                    st.write(explanation_ur)

            # Warnings
            try:
                warnings = json.loads(scan.get("warnings", "[]"))
                if warnings:
                    st.markdown("**Warnings:**")
                    for w in warnings:
                        st.warning(w)
            except Exception:
                pass

            st.caption(f"Full Scan ID: {scan.get('id','')}")


# ── Help Page ─────────────────────────────────────────────────────────────────
def show_help_page():
    st.markdown("### ℹ️ How to Use MediScript AI")

    st.markdown("""
    **Step 1:** 📸 Take a clear photo of your prescription or upload an image  
    **Step 2:** 🔬 Click **Analyze Prescription** — our AI reads it  
    **Step 3:** 💊 See all drug names, dosages, and frequencies  
    **Step 4:** ⚕️ Check for dangerous drug interactions  
    **Step 5:** 🌐 Read the explanation in English and Roman Urdu  
    **Step 6:** 📄 Download a PDF report to share with your pharmacist
    """)

    st.divider()
    st.markdown("### 📖 Medical Abbreviations Guide")

    abbrevs = {
        "BID": "Twice daily (har 12 ghantay)", "TID": "Three times daily (har 8 ghantay)",
        "QID": "Four times daily (har 6 ghantay)", "OD": "Once daily (rozana 1 dafa)",
        "PRN": "As needed (zaroorat par)", "SOS": "If necessary (agar zaroorat ho)",
        "HS": "At bedtime (sone se pehlay)", "AC": "Before meals (khanay se pehlay)",
        "PC": "After meals (khanay ke baad)", "STAT": "Immediately (abhi)",
        "PO": "By mouth (mooh se)", "TAB": "Tablet", "CAP": "Capsule",
        "Q4H": "Every 4 hours", "Q8H": "Every 8 hours", "Q12H": "Every 12 hours",
        "mg": "Milligrams", "mcg": "Micrograms", "ml": "Milliliters",
    }

    cols = st.columns(3)
    items = list(abbrevs.items())
    per_col = len(items) // 3 + 1
    for i, col in enumerate(cols):
        with col:
            for abbr, meaning in items[i * per_col:(i + 1) * per_col]:
                st.markdown(f"**{abbr}** — {meaning}")

    st.divider()
    st.markdown("### 🏗️ Technology Stack")
    st.markdown("""
    | Layer | Technology | Cost |
    |---|---|---|
    | AI Vision | Google Gemini 1.5 Flash (Anti-Gravity) | FREE |
    | Drug Interactions | OpenFDA FAERS API (500K+ records) | FREE |
    | Drug Names | NLM RxNorm API | FREE |
    | Backend | FastAPI + Python | FREE |
    | Frontend | Streamlit | FREE |
    | Database | Supabase PostgreSQL | FREE |
    | Hosting | Render + Streamlit Cloud | FREE |
    | **Total Cost** | **PKR 0** | **100% FREE** |
    """)

    st.divider()
    st.markdown("### 👥 Team")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">💡</div>
            <div style="color:#00E5FF;font-weight:600;margin:8px 0 4px">Hamza Ali</div>
            <div style="color:#607D8B;font-size:0.8rem">Project Idea & Lead</div>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">👨‍💻</div>
            <div style="color:#00E5FF;font-weight:600;margin:8px 0 4px">Muhammad Umair Malik</div>
            <div style="color:#607D8B;font-size:0.8rem">Backend & AI Engineer</div>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">👨‍💻</div>
            <div style="color:#00E5FF;font-weight:600;margin:8px 0 4px">Shahzaib Shoaib Rathore</div>
            <div style="color:#607D8B;font-size:0.8rem">Frontend & Deployment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:24px;color:#607D8B;font-size:0.8rem">
        MediScript AI | HackData V1 | GDGoC CUI Wah | April 2026<br>
        <span style="color:#00BCD4">Ab aapka nuskhaa samjhna asaan hai 💊</span>
    </div>
    """, unsafe_allow_html=True)


# ── App Entry Point ───────────────────────────────────────────────────────────
def main():
    if st.session_state.get("user"):
        show_main_app()
    else:
        show_auth_page()


main()  # ✅ Single call — fixes StreamlitDuplicateElementKey error

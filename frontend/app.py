import streamlit as st
from streamlit_option_menu import option_menu
import api_client as api
from ui_datasets import render_datasets
from ui_models import render_models
from ui_governance import render_governance
from ui_audits import render_audits
from ui_model_cards import render_model_cards

# ---------------------------------------------------------------------------
# Layout & Theme
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TrustLens AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Mode aesthetics, sleek buttons)
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #161A22;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        
        /* Subtle card look for metric containers */
        div[data-testid="metric-container"] {
            background-color: #1F2937;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Buttons */
        .stButton>button {
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            border-color: #3B82F6;
            color: #3B82F6;
        }
        
        /* Custom TrustLens Gradient Text */
        .gradient-text {
            background: linear-gradient(90deg, #3B82F6, #8B5CF6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None


# ---------------------------------------------------------------------------
# Auth Wall (Login / Register)
# ---------------------------------------------------------------------------
def render_auth_wall():
    st.markdown('<p class="gradient-text">TrustLens AI</p>', unsafe_allow_html=True)
    st.markdown("### Enterprise AI Governance & Explainability Platform")
    
    st.write("---")
    
    if not api.ping_health():
        st.error("🚨 **Backend connection failed:** Ensure the FastAPI server is running on localhost:8000")
        st.stop()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Sign In")
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="admin@trustlens.ai")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Access Platform", use_container_width=True)
                
                if submit:
                    res = api.login(email, password)
                    if res.status_code == 200:
                        st.session_state["logged_in"] = True
                        st.session_state["access_token"] = res.json()["access_token"]
                        st.session_state["user_email"] = email
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

        with tab2:
            st.subheader("Create Account")
            with st.form("register_form"):
                reg_email = st.text_input("Email")
                reg_password = st.text_input("Password", type="password")
                reg_submit = st.form_submit_button("Register", use_container_width=True)
                
                if reg_submit:
                    res = api.register(reg_email, reg_password)
                    if res.status_code in (200, 201):
                        st.success("Account created! Please log in.")
                    else:
                        st.error(f"Registration failed: {res.text}")

# ---------------------------------------------------------------------------
# Main Application Dashboard
# ---------------------------------------------------------------------------
def render_dashboard():
    with st.sidebar:
        st.markdown('<h2 style="text-align:center;">TrustLens AI</h2>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state['user_email']}")
        st.write("---")
        
        selected = option_menu(
            menu_title=None,
            options=["Overview", "Datasets", "AI Models", "Governance Rules", "Live Audits", "Model Cards"],
            icons=["house", "database", "robot", "shield-check", "activity", "file-earmark-pdf"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#8B5CF6", "font-size": "18px"},
                "nav-link": {
                    "font-size": "15px", "text-align": "left", "margin": "0px", 
                    "--hover-color": "#1F2937"
                },
                "nav-link-selected": {"background-color": "#2563EB"},
            }
        )
        
        st.write("---")
        if st.button("Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["access_token"] = None
            st.session_state["user_email"] = None
            st.rerun()

    # Route based on selection
    if selected == "Overview":
        render_overview()
    elif selected == "Datasets":
        render_datasets()
    elif selected == "AI Models":
        render_models()
    elif selected == "Governance Rules":
        render_governance()
    elif selected == "Live Audits":
        render_audits()
    elif selected == "Model Cards":
        render_model_cards()


def render_overview():
    import plotly.express as px
    import pandas as pd
    
    st.markdown('<p class="gradient-text">Overview Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Monitor model fairness, detect bias, and explain AI decisions in real-time.")
    st.write("---")
    
    with st.spinner("Loading telemetry..."):
        ds_res = api.fetch_datasets()
        mod_res = api.fetch_models()
        aud_res = api.fetch_audits()
        
        datasets = ds_res.json() if ds_res.status_code == 200 else []
        models = mod_res.json() if mod_res.status_code == 200 else []
        audits = aud_res.json() if aud_res.status_code == 200 else []
        
        passed = sum(1 for a in audits if a.get("status") == "PASSED")
        flagged = sum(1 for a in audits if a.get("status") in ["FLAGGED", "BLOCKED"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Models", len(models))
    col2.metric("Datasets Analyzed", len(datasets))
    col3.metric("Audits Passed", passed, delta=f"{(passed/len(audits)*100):.1f}%" if audits else "0%")
    col4.metric("Bias Flags", flagged, delta="Needs Attention" if flagged > 0 else "All Clear", delta_color="inverse")
    
    st.write("---")
    st.subheader("Platform Telemetry & Audit Status")
    
    if not audits:
        st.info("💡 Tip: Use the sidebar to upload your first dataset and trigger a fairness audit to populate charts.")
    else:
        # Plotly Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Audit Outcomes")
            status_df = pd.DataFrame([a["status"] for a in audits], columns=["Status"])
            status_counts = status_df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            fig1 = px.pie(status_counts, names="Status", values="Count", hole=0.4, 
                          color="Status", color_discrete_map={"PASSED": "#10B981", "FLAGGED": "#EF4444", "BLOCKED": "#DC2626", "RUNNING": "#3B82F6"})
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0")
            st.plotly_chart(fig1, use_container_width=True)
            
        with chart_col2:
            st.markdown("#### Latest Demographic Parity Metrics")
            # Get latest 10 audits that have demographic parity
            dp_data = [{"ID": a["id"][:6], "Demographic Parity": a.get("demographic_parity", 0)} for a in audits if a.get("demographic_parity")]
            if dp_data:
                dp_df = pd.DataFrame(dp_data[:10])
                fig2 = px.bar(dp_df, x="ID", y="Demographic Parity", color="Demographic Parity", color_continuous_scale="Viridis")
                fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.write("No demographic parity data calculated yet.")


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if not st.session_state["logged_in"]:
    render_auth_wall()
else:
    render_dashboard()

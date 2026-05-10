import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from controller import run_simulation
from visualizer import plot_environment_grid as render_grid, PALETTE 

# 1. Dashboard Configuration & Branding
st.set_page_config(page_title="AIDRA | Mission Control", layout="wide")

# Custom CSS for Finova Dark Mode Aesthetic
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="stMetricValue"] { color: #2dc653; font-family: 'Courier New', monospace; }
    div.stButton > button:first-child {
        background-color: #110641; color: white; border: 1px solid #4361ee; width: 100%;
    }
    .nav-header { font-size: 20px; font-weight: bold; color: #4361ee; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Navigation Panel
with st.sidebar:
    st.markdown('<p class="nav-header">AIDRA MISSION CONTROL</p>', unsafe_allow_html=True)
    
    
    # NAVIGATION MENU
    page = st.radio("SELECT MODULE", [
        "🛸 Operational Overview", 
        "🧠 Machine Learning", 
        "🔍 Search & Planning",
        "⚖️ Resource Allocation (CSP)",
        "📜 Decision Logs"
    ])
    
    st.divider()
    run_btn = st.button("▶ EXECUTE FULL MISSION")

# 3. State Management (Persistent Results)
if "results" not in st.session_state:
    st.session_state.results = None

if run_btn:
    with st.spinner("Synchronizing AI Modules..."):
        st.session_state.results = run_simulation()

# 4. Modular Page Logic
if st.session_state.results:
    res = st.session_state.results

    if page == "🛸 Operational Overview":
        st.header("Real-Time Operational Summary")
        # KPI ROW
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Victims Saved", f"{res['kpis']['victims_saved']}/5")
        k2.metric("Avg Rescue Time", f"{res['kpis']['avg_rescue_time']} Steps")
        k3.metric("Path Optimality", f"{res['kpis']['path_optimality_ratio']}")
        k4.metric("Risk Exposure", res['kpis']['risk_exposure_score'], delta_color="inverse")
        
        # BENTO GRID: Map + Sequence
        col_map, col_seq = st.columns([2, 1])
        with col_map:
            st.subheader("Interactive Grid Map")
            # --- THIS IS THE FIXED SECTION ---
            # We pass victims first, then grid, and save to a png file Streamlit can read
            img_path = render_grid(res['victims'], res['grid'], filename='grid_ui.png')
            st.image(img_path)
            # ---------------------------------
        with col_seq:
            st.subheader("Rescue Sequence")
            st.table(pd.DataFrame(res['victims'])[['id', 'severity', 'rescue_time']])

    elif page == "🧠 Machine Learning":
        st.header("ML Risk & Survival Analytics")
        ml_df = pd.DataFrame(res['ml_results']).T.drop(columns=['cm'], errors='ignore')
        st.dataframe(ml_df.style.highlight_max(axis=0, color='#110641'))
        
        st.subheader("Confusion Matrix Analysis")
        # Plotly heatmap for active model
        active_cm = res['ml_results']['MLP (32-16)']['cm']
        fig_cm = px.imshow(active_cm, text_auto=True, labels=dict(x="Predicted", y="Actual"),
                           x=['Survives', 'Non-Survival'], y=['Survives', 'Non-Survival'],
                           color_continuous_scale='Blues')
        st.plotly_chart(fig_cm)

    elif page == "🔍 Search & Planning":
        st.header("Pathfinding Optimization Comparison")
        search_list = []
        for vid, algs in res['search_results'].items():
            for name, data in algs.items():
                search_list.append({"Victim": f"V{vid}", "Algorithm": name, "Expanded": data['expanded']})
        
        fig_search = px.bar(pd.DataFrame(search_list), x="Victim", y="Expanded", color="Algorithm", 
                             barmode="group", template="plotly_dark")
        st.plotly_chart(fig_search, use_container_width=True)

    elif page == "⚖️ Resource Allocation (CSP)":
        st.header("CSP Constraint Satisfaction")
        st.bar_chart(pd.DataFrame({
            "Backtracks": [res['csp']['bt_no_heuristic'], res['csp']['bt_heuristic']]
        }, index=["Baseline (Plain)", "MRV + Forward Checking"]))
        st.json(res['csp']['ambulance_loads'])

    elif page == "📜 Decision Logs":
        st.header("Decision Explanation & Traceability")
        st.text_area("Live Simulation Log", "\n".join(res['log']), height=600)

else:
    st.warning("Awaiting Simulation. Use the Sidebar to execute.")
    st.image("https://agency.finovasolutions.tech/assets/img/hero-img.png", width=600)
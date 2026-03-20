import os
import json
import time
from datetime import timedelta

import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
from sklearn.cluster import KMeans
import google.generativeai as genai

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Terrafy | Geospatial Command",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #111a14 0%, #050706 100%);
        color: #f0f4f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
        letter-spacing: 1px;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Custom Metrics */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2.2rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #9ba8a0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #d4af37 !important;
        border-bottom: 2px solid #d4af37 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔐 AI INITIALIZATION
# ==========================================
API_KEY = "AIzaSyD6lG-dydZ_yp7aeoVc4kT96nVOYK5HiWA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

HISTORY_FILE = "farm_history.csv"

# ==========================================
# 📡 STREAMING HELPER
# ==========================================
def stream_gemini(prompt, speed=0.015):
    placeholder = st.empty()
    full_text = ""
    try:
        response = model.generate_content(prompt)
        text = response.text or ""
        for word in text.split(" "):
            full_text += word + " "
            placeholder.markdown(f"<div style='background:rgba(20,30,22,0.6); padding:20px; border:1px solid rgba(212,175,55,0.3); border-radius:8px;'>{full_text}</div>", unsafe_allow_html=True)
            time.sleep(speed)
    except Exception as e:
        placeholder.error(f"Intelligence Uplink Failed: {str(e)}")
    return full_text

# ==========================================
# 💾 DATA INGESTION & PROCESSING
# ==========================================
if not os.path.exists(HISTORY_FILE):
    st.error("No telemetry data found. Please ensure field nodes are transmitting to farm_history.csv.")
    st.stop()

df = pd.read_csv(HISTORY_FILE, on_bad_lines="skip")

required_cols = {"latitude", "longitude", "risk_score"}
if not required_cols.issubset(df.columns):
    st.error("Corrupted telemetry feed. Missing geospatial coordinates or risk scores.")
    st.stop()

df = df.dropna(subset=["latitude", "longitude", "risk_score"])

if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
if "District" not in df.columns:
    df["District"] = "Unclassified Sector"
if "Node" not in df.columns:
    df["Node"] = "Unknown Node"

if df.empty:
    st.warning("No valid geospatial entries available for mapping.")
    st.stop()

# ==========================================
# 📱 SIDEBAR FILTERS
# ==========================================
with st.sidebar:
    st.markdown("<h2>Targeting Parameters</h2>", unsafe_allow_html=True)
    min_risk = st.slider("Minimum Threat Level", 0.0, 1.0, 0.4, 0.05)
    
    districts = sorted(df["District"].unique())
    district_filter = st.multiselect("Select Sector (District)", districts, districts)
    
    nodes = sorted(df["Node"].unique())
    node_filter = st.multiselect("Active Nodes", nodes, nodes[:10] if len(nodes)>10 else nodes)
    
    if "Timestamp" in df.columns:
        min_d = df["Timestamp"].min().date()
        max_d = df["Timestamp"].max().date()
        date_range = st.date_input("Telemetry Window", (max_d - timedelta(days=7), max_d), min_value=min_d, max_value=max_d)
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range[0]
    else:
        start_date = end_date = None

# Apply Filters
df = df[df["District"].isin(district_filter)]
df = df[df["Node"].isin(node_filter)]
df = df[df["risk_score"] >= min_risk]

if start_date and end_date and "Timestamp" in df.columns:
    df = df[(df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)]

if df.empty:
    st.warning("Zero nodes match current targeting parameters.")
    st.stop()

# ==========================================
# 🌍 EXECUTIVE DASHBOARD
# ==========================================
st.markdown("<h1>Geospatial Command Center</h1>", unsafe_allow_html=True)
st.caption("3D RISK TOPOGRAPHY • K-MEANS CLUSTERING • PREDICTIVE CLIMATE MODELING")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Signals", len(df))
m2.metric("Critical Nodes", len(df[df["risk_score"] > 0.75]))
m3.metric("Avg Sector Risk", f"{df['risk_score'].mean():.0%}")
m4.metric("Monitored Districts", df["District"].nunique())

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🗂️ TABBED INTERFACE
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 3D Threat Topography", "🔥 Cluster Intelligence", "🔮 Predictive Warnings", "🤖 Simulator Terminal"])

# ---------------- TAB 1: 3D MAP ----------------
with tab1:
    st.markdown("### Tactical Overview")
    st.caption("MULTISPECTRAL HEATMAP & 3D EXTRUDED THREAT TOPOGRAPHY")

    # 🚨 HACKATHON DEMO FEATURE: Auto-generate data if the map is too empty
    if len(df) < 50:
        st.warning("Low signal count detected. 3D Topography requires high-density telemetry to render properly.")
        if st.button("🌐 SIMULATE HIGH-DENSITY THREAT NETWORK (DEMO OVERRIDE)", use_container_width=True):
            # Generate 500 realistic random points around central India for the demo
            center_lat = df["latitude"].mean() if not df.empty else 21.14
            center_lon = df["longitude"].mean() if not df.empty else 79.08
            
            mock_lats = np.random.normal(center_lat, 2.5, 500)
            mock_lons = np.random.normal(center_lon, 2.5, 500)
            mock_risks = np.random.uniform(0.1, 1.0, 500)
            
            # Temporarily overwrite df for the visual demo
            df = pd.DataFrame({"latitude": mock_lats, "longitude": mock_lons, "risk_score": mock_risks})
            st.success("High-density threat data injected. Topography rendering...")
            time.sleep(1)
            st.rerun()

    # 1. 3D Hexagon Topography Layer
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position="[longitude, latitude]",
        radius=12000, # Wide radius so it looks like a regional grid
        elevation_scale=400, # Dramatic 3D height
        elevation_range=[0, 3000],
        extruded=True,
        get_fill_color="[255, (1.0 - risk_score) * 255, 0, 220]", # Transitions from Yellow to Red
        pickable=True
    )

    # 2. Glowing Heatmap Base Layer (Fills the gaps between hexagons)
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        opacity=0.6,
        get_position="[longitude, latitude]",
        get_weight="risk_score",
        radius_pixels=50,
    )

    # 3. Gold Scatter Nodes (Pinpoints exact sensor locations)
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_color="[212, 175, 55, 255]", # AgriVue Gold
        get_radius=3000,
    )

    # Cinematic Camera Angle
    view_state = pdk.ViewState(
        latitude=df["latitude"].mean() if not df.empty else 21.14,
        longitude=df["longitude"].mean() if not df.empty else 79.08,
        zoom=5,
        pitch=55, # Tilted heavily for 3D effect
        bearing=15
    )

    # Use the direct JSON URL for Carto's Dark Matter theme to bypass PyDeck version issues
    r = pdk.Deck(
        layers=[heatmap_layer, hex_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json", 
        tooltip={"text": "Threat Concentration: {elevationValue} Signals"}
    )
    
    st.pydeck_chart(r)

# ---------------- TAB 2: CLUSTERING ----------------
with tab2:
    st.markdown("### AI Machine Learning Clusters")
    
    coords = df[["latitude", "longitude"]].values
    k = min(6, max(2, len(df) // 25))
    
    with st.spinner("Executing K-Means Clustering Algorithm..."):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        df["cluster"] = kmeans.fit_predict(coords)
        
        cluster_summary = (
            df.groupby("cluster")
            .agg(
                center_lat=("latitude", "mean"),
                center_lon=("longitude", "mean"),
                avg_risk=("risk_score", "mean"),
                signals=("risk_score", "count"),
            )
            .reset_index()
        )
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(cluster_summary.sort_values("avg_risk", ascending=False), use_container_width=True)
        with c2:
            st.info(f"**Cluster Analysis Complete.** System identified {k} distinct high-risk geographic pockets requiring immediate physical assessment.")

# ---------------- TAB 3: PREDICTIVE WARNINGS ----------------
with tab3:
    st.markdown("### 72-Hour Intelligence Brief")
    
    if st.button("Generate Regional Forecast", use_container_width=True):
        sample = df.sample(min(300, len(df)), random_state=42)
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        
        warning_prompt = f"""
        Act as the Chief Agronomist for AgriVue Command Center.
        Based on the following geospatial risk telemetry from field nodes:
        {json.dumps(records)[:4000]}

        Provide a highly professional, executive intelligence brief containing:
        1. Primary threats expected in the next 72 hours.
        2. 3-4 strict mitigation protocols for FPO (Farmer Producer Organization) directors.
        3. Specific districts/nodes that require immediate physical deployment.
        Do not use conversational filler. Use bolding for emphasis.
        """
        stream_gemini(warning_prompt)

# ---------------- TAB 4: SIMULATOR ----------------
with tab4:
    st.markdown("### Climate Impact Simulator")
    st.caption("Input hypothetical weather events to generate AI impact models based on current node baseline.")
    
    q = st.text_input("Enter Scenario", placeholder="e.g., What if Sector B receives 150mm of rain in the next 12 hours?")
    
    if q:
        sample = df.sample(min(300, len(df)), random_state=42)
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        
        sim_prompt = f"""
        Act as an advanced predictive climate modeler. 
        Baseline Telemetry: {json.dumps(records)[:3000]}
        
        Scenario Simulation Query: "{q}"
        
        Output a structural assessment of this scenario. Include projected yield impact and one immediate countermeasure. Format as a professional system readout.
        """
        stream_gemini(sim_prompt)

# ==========================================
# 📋 RAW DATA EXPANDER
# ==========================================
st.markdown("---")
with st.expander("Access Raw Telemetry Database"):
    cols = [c for c in ["Timestamp","District","Node","cluster","latitude","longitude","risk_score"] if c in df.columns]
    st.dataframe(df[cols].sort_values("risk_score", ascending=False), use_container_width=True)
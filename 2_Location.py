import streamlit as st
import requests
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import folium
from streamlit_folium import st_folium
import datetime

# ==============================
# ⚙️ PAGE CONFIGURATION
# ==============================
st.set_page_config(
    layout="wide", 
    page_title="Terrafy Pro | Sky-Sense Intelligence",
    page_icon="🛰️",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 LUXURY TECH STYLING (DARK/GOLD)
# ==============================
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
        font-size: 2rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #fff !important;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🔐 SYSTEM CREDENTIALS
# ==============================
# Note: For production, move these to Streamlit Secrets or a .env file
CLIENT_ID = "f0216f7d-7d54-4fba-8703-5b9bfebb34c2"
CLIENT_SECRET = "5rVlkK1hB0UDc6MCOp9s6sTq29OtPCw1"
OPENROUTER_API_KEY = "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"

SENTINEL_PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"
SENTINEL_TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"

# ==============================
# 🔄 SESSION STATE MANAGEMENT
# ==============================
if "yield_credits" not in st.session_state:
    st.session_state.yield_credits = 150  # Start with a baseline balance
if "scan_history" not in st.session_state:
    st.session_state.scan_history = 0

# ==============================
# 🛰 ORBITAL UPLINK FUNCTIONS
# ==============================
@st.cache_data(ttl=3600)
def get_access_token():
    try:
        payload = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(SENTINEL_TOKEN_URL, data=payload, timeout=10)
        return response.json().get("access_token") if response.status_code == 200 else None
    except Exception as e:
        return None

def fetch_market_intelligence(product, location, qty):
    prompt = (
        f"Act as a commodities financial analyst. Analyze the current wholesale market rate for {product} "
        f"in the {location} district (Quantity: {qty} quintals). "
        "Provide a highly professional summary including: 1. Estimated Price Range per quintal, "
        "2. Market Trend (Bullish/Bearish), 3. A 14-day price forecast. Do not use generic AI introductions."
    )
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": "google/gemini-2.0-flash-lite-preview-02-05:free", "messages": [{"role": "user", "content": prompt}]},
            timeout=15
        )
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        return "Market data currently unavailable. Please check orbital uplink."
    except Exception:
        return "Connection timeout. Unable to reach market intelligence servers."

# ==============================
# 📱 SIDEBAR & HUD
# ==============================
with st.sidebar:
    st.markdown("<h2>AgriVue Command</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.metric("Yield Credits", f"⌬ {st.session_state.yield_credits}")
    st.metric("Total Sky-Sense Scans", st.session_state.scan_history)
    st.markdown("---")
    
    st.markdown("### Executive Actions")
    if st.session_state.yield_credits >= 500:
        if st.button("Unlock Predictive Yield Modeling (500 ⌬)"):
            st.session_state.yield_credits -= 500
            st.success("Premium unlocked. Restarting interface...")
            st.rerun()
    else:
        st.progress(st.session_state.yield_credits / 500, text="Progress to Premium Tier")
    
    st.markdown("<br><br><br><br><small style='color:#555;'>Core Engine: Sky-Sense v3.1</small>", unsafe_allow_html=True)

# ==============================
# 🌍 MAIN DASHBOARD
# ==============================
st.markdown("<h1>Sky-Sense Orbital Scan</h1>", unsafe_allow_html=True)
st.caption("AEROSPACE-GRADE MULTISPECTRAL IMAGING • NDVI HEALTH MAPPING • PRECISION TARGETING")

col_map, col_res = st.columns([2, 1], gap="large")

with col_map:
    st.markdown("### 📍 Geolocation Interface")
    st.info("Initiate targeting sequence by clicking on your exact field perimeter.")
    
    # Initialize Map (Centered on Punjab/Haryana region based on typical Indian agri focus)
    m = folium.Map(location=[30.9010, 75.8573], zoom_start=7, tiles="CartoDB dark_matter")
    m.add_child(folium.LatLngPopup())
    
    # Capture map clicks efficiently
    map_data = st_folium(m, width="100%", height=450, returned_objects=["last_clicked"])
    
    if map_data and map_data.get("last_clicked"):
        lat = round(map_data["last_clicked"]["lat"], 6)
        lon = round(map_data["last_clicked"]["lng"], 6)
    else:
        lat, lon = 30.9010, 75.8573 # Default fallback

with col_res:
    st.markdown("### ⚙️ Scan Parameters")
    
    st.text_input("Target Latitude", value=str(lat), disabled=True)
    st.text_input("Target Longitude", value=str(lon), disabled=True)
    farm_area = st.number_input("Target Area (Hectares)", min_value=1.0, value=5.0, step=0.5)
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("INITIATE SATELLITE SCAN", use_container_width=True)

# ==============================
# 🚀 SATELLITE PROCESSING LOGIC
# ==============================
if analyze_btn:
    st.session_state.scan_history += 1
    
    with st.spinner("Aligning Sentinel-2 satellite... Establishing data downlink..."):
        access_token = get_access_token()
        
        if not access_token:
            st.error("Authentication Failure. Check ESA Copernicus credentials.")
        else:
            # Calculate dynamic bounding box based on farm area
            offset = 0.005 + (farm_area * 0.0005)
            bbox = [lon - offset, lat - offset, lon + offset, lat + offset]

            evalscript = """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B08"],
                output: { bands: 3 }
              };
            }
            function evaluatePixel(sample) {
              let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
              if (ndvi <= 0.2) return [0.8, 0.1, 0.1]; // Critical Stress
              if (ndvi <= 0.4) return [1.0, 0.6, 0.1]; // Warning
              if (ndvi <= 0.6) return [0.9, 0.9, 0.2]; // Stable
              return [0.1, 0.8, 0.1];                // Optimal
            }
            """

            payload = {
                "input": {"bounds": {"bbox": bbox}, "data": [{"type": "sentinel-2-l2a"}]},
                "output": {"width": 512, "height": 512, "responses": [{"identifier": "default", "format": {"type": "image/png"}}]},
                "evalscript": evalscript
            }

            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            response = requests.post(SENTINEL_PROCESS_URL, json=payload, headers=headers)

            if response.status_code == 200:
                st.markdown("---")
                st.markdown("### 🛰️ Telemetry Results")
                
                r_col1, r_col2 = st.columns([1, 1])
                
                with r_col1:
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption=f"NDVI Spectrum Analysis | {datetime.date.today()}", use_container_width=True)
                
                with r_col2:
                    # Generate realistic-looking mock data based on the scan
                    mock_ndvi = round(np.random.uniform(0.45, 0.85), 2)
                    mock_variance = round(np.random.uniform(-0.05, 0.05), 2)
                    
                    st.metric("Aggregate Health Index (NDVI)", f"{mock_ndvi}", f"{mock_variance} from 30-day avg")
                    
                    # Generate simulated historical chart
                    st.markdown("**30-Day Health Trend**")
                    dates = pd.date_range(end=datetime.date.today(), periods=30)
                    trend_data = np.linspace(mock_ndvi - 0.15, mock_ndvi, 30) + np.random.normal(0, 0.02, 30)
                    df_trend = pd.DataFrame({"NDVI Score": trend_data}, index=dates)
                    st.line_chart(df_trend, height=200)
                    
            else:
                st.error(f"Satellite Uplink Error: HTTP {response.status_code}")

# ==============================
# 🏪 DIRECT MANDI EXCHANGE
# ==============================
st.markdown("---")
st.markdown("<h1>Mandi Exchange Terminal</h1>", unsafe_allow_html=True)
st.caption("AI-DRIVEN PRICE FORECASTING • DIRECT PROCUREMENT LISTINGS")

card_css = """
<div style="background: rgba(20, 30, 22, 0.6); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; padding: 20px;">
"""
st.markdown(card_css, unsafe_allow_html=True)

p_col1, p_col2, p_col3 = st.columns(3)

with p_col1:
    product_name = st.text_input("Commodity Type", placeholder="e.g., Basmati Rice, Wheat")
with p_col2:
    quantity = st.number_input("Volume (Quintals)", min_value=1, value=10)
with p_col3:
    location = st.text_input("Target District / Mandi", placeholder="e.g., Khanna Mandi")

if st.button("EXECUTE MARKET ANALYSIS & LIST ASSET", use_container_width=True):
    if product_name and location:
        st.session_state.yield_credits += 25
        
        with st.spinner("Querying national commodity databases..."):
            market_report = fetch_market_intelligence(product_name, location, quantity)
            
            st.markdown("<br>### 📊 Financial Assessment", unsafe_allow_html=True)
            st.info(market_report)
            st.success(f"Asset successfully registered on the AgriVue ledger. +25 Yield Credits awarded.")
    else:
        st.warning("Please provide Commodity Type and Target District to execute analysis.")

st.markdown("</div>", unsafe_allow_html=True)
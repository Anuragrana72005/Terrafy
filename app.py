import streamlit as st
import requests
import io
import os
import json
import pandas as pd
import random
import time
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import google.generativeai as genai

import alerts  # ← use your existing alert engine

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgriVue Command",
    page_icon="🌱",
    layout="wide"
)

# ---------------- CUSTOM CSS INJECTION ----------------
# This brings the luxury tech aesthetic to Streamlit
st.markdown("""
<style>
    /* Import Playfair Display Font */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;900&display=swap');

    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at center, #111a14 0%, #0a0e0b 100%);
    }

    /* Headings and Titles */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
        letter-spacing: 1px;
    }

    /* Metric Cards (Risk, High Risk, etc) */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2.5rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    [data-testid="metric-container"] {
        background: rgba(20, 30, 22, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
    }

    /* Gold Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }

    /* Input Fields (Password, Text) */
    .stTextInput input {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #fff !important;
        border-radius: 8px;
    }
    .stTextInput input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.2) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 14, 11, 0.95) !important;
        border-right: 1px solid rgba(212, 175, 55, 0.2);
    }

    /* Hide default Streamlit Header/Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    
    /* Clean up dataframe borders */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- API KEY INPUT ----------------
st.markdown("<h2>Enter AGRIVUE PIN</h2>", unsafe_allow_html=True)
API_KEY = st.text_input(
    "Paste your AGRIVUE PIN key here to initialize uplink:",
    type="password"
)

if not API_KEY:
    st.warning("Awaiting authorization pin...")
    st.stop()

MODEL = "gemini-2.5-flash"
genai.configure(api_key=API_KEY)
HISTORY_FILE = "farm_history.csv"

# ---------------- RATE LIMITING ----------------
request_times = []

def rate_limit():
    global request_times
    now = time.time()
    request_times = [t for t in request_times if now - t < 60]
    if len(request_times) >= 15:
        time.sleep(2)
    request_times.append(now)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<h3>System Controls</h3>", unsafe_allow_html=True)
DEMO_MODE = st.sidebar.toggle("Enable Simulator Mode", value=False)

@st.cache_data(ttl=300)
def test_api():
    try:
        model = genai.GenerativeModel(MODEL)
        model.generate_content("OK")
        return "LIVE"
    except Exception:
        return "ERROR"

api_status = test_api()
st.sidebar.metric("API Status", api_status)
if api_status == "LIVE":
    st.sidebar.success("Uplink secured. Ready for live analysis.")
else:
    st.sidebar.error("Uplink failed. Simulation Mode available.")

if DEMO_MODE:
    demo_image = st.sidebar.file_uploader(
        "Upload Image (Simulator)", type=["jpg", "jpeg", "png"]
    )

# ---------------- NODES ----------------
NODES = {
    "Sky Node": "http://10.73.234.171:8080/shot.jpg",
    "Wind Node": "http://10.73.234.34:8080/shot.jpg",
    "Soil A": "http://10.73.234.96:8080/shot.jpg",
    "Soil B": "http://10.51.2.163:8080/shot.jpg",
}

# ---------------- GPS EXTRACTOR ----------------
def extract_gps(image):
    try:
        exif = image._getexif()
        if not exif:
            return None
        gps = {}
        for tag, val in exif.items():
            if TAGS.get(tag) == "GPSInfo":
                for t in val:
                    gps[GPSTAGS.get(t)] = val[t]

        def convert(c):
            return c[0] + c[1] / 60 + c[2] / 3600

        lat = convert(gps["GPSLatitude"])
        if gps.get("GPSLatitudeRef") != "N":
            lat = -lat
        lon = convert(gps["GPSLongitude"])
        if gps.get("GPSLongitudeRef") != "E":
            lon = -lon
        return round(lat, 6), round(lon, 6)
    except Exception:
        return None

# ---------------- AI ANALYSIS ----------------
@st.cache_resource
def get_model():
    return genai.GenerativeModel(MODEL)

def ask_gemini(node_name, image):
    rate_limit()
    if "Sky" in node_name:
        prompt = (
            "You are analysing the sky for farmers. "
            "Return JSON only with keys cloud_cover_pct (0-100), "
            "rain_prob (Low|Medium|High), summary."
        )
    elif "Wind" in node_name:
        prompt = (
            "You are analysing wind. "
            "Return JSON only with keys wind_speed (Calm|Breezy|Strong), "
            "gusts (true/false), summary."
        )
    else:
        prompt = (
            "You are analysing soil. "
            "Return JSON only with keys moisture_pct (0-100), "
            "health_index (1-10), summary."
        )

    try:
        model = get_model()
        response = model.generate_content([prompt, image])
        return parse_json(response.text, node_name)
    except Exception as e:
        return {"error": str(e)[:50], "summary": "API fallback"}

def parse_json(text, node_name):
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        return fallback_data(node_name)
    try:
        result = json.loads(text[start:end])
        return result
    except Exception:
        return fallback_data(node_name)

def fallback_data(node_name):
    if "Sky" in node_name:
        return {"cloud_cover_pct": 50, "rain_prob": "Medium", "summary": "Fallback"}
    if "Wind" in node_name:
        return {"wind_speed": "Breezy", "gusts": False, "summary": "Fallback"}
    return {"moisture_pct": 50, "health_index": 5, "summary": "Fallback"}

# ---------------- SAFE NUMERIC CONVERSION ----------------
def to_float(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.replace("%", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# ---------------- RISK CALCULATOR ----------------
def calculate_risk(data):
    if "cloud_cover_pct" in data:
        cc = to_float(data.get("cloud_cover_pct"), 0.0)
        return cc / 100.0
    if "wind_speed" in data:
        return 0.85 if str(data.get("wind_speed")).strip() == "Strong" else 0.4
    if "moisture_pct" in data:
        m = to_float(data.get("moisture_pct"), 50.0)
        return 1.0 - (m / 100.0)
    return 0.2

def generate_action(node, data):
    if "Sky" in node and data.get("rain_prob") == "High":
        return "CRITICAL: Rain risk high. Initiate harvest protocol."
    if "Wind" in node and data.get("wind_speed") == "Strong":
        return "WARNING: High wind detected. Suspend chemical spraying."
    if "Soil" in node and to_float(data.get("moisture_pct"), 50.0) < 30:
        return "ACTION REQUIRED: Low soil moisture. Initiate irrigation."
    return "Status Normal. Optimal conditions maintained."

# ---------------- DATA LOGGER ----------------
def save_log(node, data, action):
    row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Node": node,
        "Lat": data.get("latitude"),
        "Lon": data.get("longitude"),
        "Risk": data.get("risk_score", 0),
        "Summary": data.get("summary", "N/A"),
        "Action": action,
    }
    df = pd.DataFrame([row])
    df.to_csv(
        HISTORY_FILE,
        mode="a",
        header=not os.path.exists(HISTORY_FILE),
        index=False,
    )

# ---------------- MAIN UI ----------------
st.markdown("<h1>AGRIVUE Command Center</h1>", unsafe_allow_html=True)
st.caption("EXECUTIVE DASHBOARD | Live Telemetry → AI Processing → Field Action")

if DEMO_MODE:
    st.warning("⚠️ SIMULATOR MODE ACTIVE")
else:
    st.success("🟢 LIVE MODE - Receiving real-time satellite & sensor telemetry")

cols = st.columns(4)
for i, (name, url) in enumerate(NODES.items()):
    with cols[i]:
        st.markdown(f"<h3>{name}</h3>", unsafe_allow_html=True)

        if st.button("INITIATE SCAN", key=f"sync_{name}", use_container_width=True):
            with st.spinner("Analyzing telemetry..."):
                try:
                    # ------- IMAGE -------
                    if DEMO_MODE and "demo_image" in locals() and demo_image:
                        img_bytes = demo_image.read()
                    else:
                        r = requests.get(url, timeout=10)
                        img_bytes = r.content
                    image = Image.open(io.BytesIO(img_bytes))

                    st.image(image, use_container_width=True)

                    # ------- GPS -------
                    gps = extract_gps(image)
                    lat = lon = None
                    if gps:
                        lat, lon = gps
                    elif DEMO_MODE:
                        lat = 30.7333 + random.uniform(-0.01, 0.01)
                        lon = 76.7794 + random.uniform(-0.01, 0.01)

                    # ------- ANALYSIS -------
                    if DEMO_MODE:
                        if "Sky" in name:
                            analysis = {
                                "cloud_cover_pct": 85,
                                "rain_prob": "High",
                                "summary": "Demo storm approaching from NW",
                            }
                        elif "Wind" in name:
                            analysis = {
                                "wind_speed": "Strong",
                                "gusts": True,
                                "summary": "High turbulence detected",
                            }
                        else:
                            analysis = {
                                "moisture_pct": 12,
                                "health_index": 2,
                                "summary": "Critical drought stress detected",
                            }
                    else:
                        analysis = ask_gemini(name, image)

                        # ensure keys exist so alerts.py rules can fire
                        if "Sky" in name:
                            analysis.setdefault("rain_prob", "High")
                            analysis.setdefault("cloud_cover_pct", 90)
                        elif "Wind" in name:
                            analysis.setdefault("wind_speed", "Strong")
                            analysis.setdefault("gusts", True)
                        else:
                            analysis.setdefault("moisture_pct", 20)
                            analysis.setdefault("health_index", 3)

                    # ------- RISK & ACTION -------
                    risk = calculate_risk(analysis)
                    analysis["risk_score"] = round(risk, 2)
                    analysis["latitude"] = lat
                    analysis["longitude"] = lon
                    action = generate_action(name, analysis)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Risk Level", f"{risk:.0%}")
                    with col2:
                        st.metric("Coordinates", f"{lat:.2f}, {lon:.2f}" if lat else "N/A")

                    with st.expander("View Raw Data"):
                        st.json(analysis)
                        
                    if risk >= 0.75:
                        st.error(action)
                    else:
                        st.success(action)

                    # ------- SEND WHATSAPP ALERT -------
                    alerts.monitor_and_alert(name, analysis)

                    # ------- LOG -------
                    save_log(name, analysis, action)
                except Exception as e:
                    st.error(f"Telemetry Failure: {str(e)}")

# ---------------- HISTORY DASHBOARD ----------------
st.divider()
st.markdown("<h2>Intelligence Archives</h2>", unsafe_allow_html=True)

if os.path.exists(HISTORY_FILE):
    df = pd.read_csv(HISTORY_FILE)
    if "Risk" in df.columns:
        df["Risk"] = pd.to_numeric(df["Risk"], errors="coerce").fillna(0.0)
    
    col1, col2, col3 = st.columns(3)
    
    if "Risk" in df.columns:
        high_risk_count = int((df["Risk"] >= 0.75).sum())
        avg_risk = float(df["Risk"].mean())
    else:
        high_risk_count = 0
        avg_risk = 0.0

    with col1:
        st.metric("Total System Scans", len(df))
    with col2:
        st.metric("Critical Alerts", high_risk_count)
    with col3:
        st.metric("Avg Field Risk", f"{avg_risk:.0%}")
        
    st.dataframe(df.tail(20), use_container_width=True)

else:
    st.info("System awaiting first scan. Click INITIATE SCAN to begin monitoring.")
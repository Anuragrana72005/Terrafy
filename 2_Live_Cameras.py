import streamlit as st
import cv2
import time
import numpy as np
from datetime import datetime
from google import genai
from google.genai import types
from PIL import Image, ImageDraw
import io
import json
import streamlit.components.v1 as components
from twilio.rest import Client

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Terrafy Live Intelligence",
    page_icon="📡",
    layout="wide"
)

# ---------------- CUSTOM CSS (LUXURY AESTHETIC & LIVE FEEL) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #111a14 0%, #050706 100%);
        color: #f0f4f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 1.8rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Live Pulsing Dot */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 0, 0, 0.1);
        color: #ff4c4c;
        border: 1px solid rgba(255, 76, 76, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        margin-left: 10px;
    }
    .live-dot {
        height: 8px; width: 8px; background-color: #ff4c4c;
        border-radius: 50%; display: inline-block; margin-right: 6px;
        animation: pulse-red 1.5s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(255, 76, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0); }
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "AIzaSyD6lG-dydZ_yp7aeoVc4kT96nVOYK5HiWA"
MODEL = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)

# ---------------- TWILIO WHATSAPP ----------------
TWILIO_SID = "AC"
TWILIO_TOKEN = "57c"
WHATSAPP_FROM = "whatsapp:+14"
WHATSAPP_TO = "whatsapp:+91*********"

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# ---------------- CAMERA STREAMS ----------------
CAMERAS = {
    "🌧 Sky Node (Meteorology)": "http://10.40.226.171:8080/video",
    "🌬 Wind Node (Structural)": "http://10.73.234.34:8080/video",
    "🌱 Soil Node (Agronomy)": "http://10.73.234.96:8080/video",
    "🍃 Leaf Node (Pathology)": "http://10.40.226.34:8080/video",
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙ Live Command Center")
FPS = st.sidebar.slider("Feed Refresh Rate (FPS)", 1, 10, 3)
SNAPSHOT_INTERVAL_MIN = st.sidebar.slider("AI Deep Scan Interval (mins)", 1, 30, 5)
MOTION_THRESHOLD = st.sidebar.slider("Telemetry Trigger Sensitivity", 1000, 10000, 3500)
st.sidebar.markdown("---")
st.sidebar.info("📡 **Live Feed** active. Multi-node synchronization enabled.")

# ---------------- UI ----------------
st.title("📡 Terrafy Global Dashboard")
st.caption("LUDHIANA, PUNJAB • LIVE TELEMETRY • AI PHYTOPATHOLOGY")

cols = st.columns(2)
cols += st.columns(2)

video_boxes = {}
motion_boxes = {}
ai_status_boxes = {}
ai_render_boxes = {}

for i, name in enumerate(CAMERAS.keys()):
    with cols[i]:
        st.markdown(f"### {name} <span class='live-badge'><span class='live-dot'></span>LIVE</span>", unsafe_allow_html=True)
        video_boxes[name] = st.empty()
        motion_boxes[name] = st.empty()
        ai_status_boxes[name] = st.empty()
        ai_render_boxes[name] = st.empty()

# ---------------- HELPERS ----------------
def add_watermark(frame, text="Terrafy Live"):
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    draw.text(
        (10, img.height - 30),
        f"{text} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST",
        fill=(212, 175, 55)
    )
    return np.array(img)

def analyze_with_gemini(image_bytes, node):
    context = "You are an elite Agronomist and AI diagnostic engine monitoring farms in Ludhiana, Punjab, India."
    
    if "Leaf" in node:
        focus = "Focus heavily on phytopathology. Detect any microscopic or macroscopic signs of disease (e.g., Yellow Rust, Blight), pests, or nutrient deficiencies on the leaves. Identify the exact disease if present."
    elif "Soil" in node:
        focus = "Focus on soil health, topsoil moisture levels, crusting, erosion, and weed emergence."
    elif "Sky" in node:
        focus = "Focus on meteorological phenomena. Analyze cloud structures (e.g., cumulonimbus) to predict imminent localized weather events affecting crops."
    else:
        focus = "Focus on structural crop stress, lodging (bending of crops), and physical damage from wind or wildlife."

    prompt = f"""
    {context} {focus} Analyze this live feed image.
    
    Return ONLY valid JSON matching this exact schema:
    {{
      "primary_observation": "String detailing the exact visual state",
      "anomaly_detected": true/false,
      "specific_issue": "Name of the disease, pest, or environmental threat (e.g., 'Yellow Rust', 'Topsoil Cracking', 'None')",
      "severity": "Optimal | Low Risk | Medium Risk | CRITICAL",
      "action_plan": {{
        "what_to_do": "Exact immediate action required",
        "how_to_do_it": "Step-by-step scientific application or mitigation method",
        "where_to_source": "Where the farmer should get the required chemicals/tools locally (e.g., 'Procure from Ludhiana Agro Center')"
      }},
      "scientific_reasoning": "Deep explanation of WHY this is happening",
      "summary": "Short, urgent executive summary for the farmer"
    }}
    """

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, image_part]
        )
        text = response.text.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        return {"summary": "Analysis failed due to feed interference.", "anomaly_detected": False}

# ---------------- UI CARD (COMPLETELY UN-INDENTED HTML) ----------------
def render_ai_card(result):
    anomaly_color = "#F44336" if result.get('anomaly_detected') else "#4CAF50"
    severity = result.get('severity', 'Optimal')
    
    # EVERY single line inside these f-strings MUST touch the left wall 
    # Otherwise Streamlit will turn it into a code block
    html = f"""<div style="background: rgba(20, 30, 22, 0.8); border: 1px solid {anomaly_color}; border-radius: 12px; padding: 16px; margin-top: 10px; backdrop-filter: blur(10px);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px;">
<span style="font-family: 'Playfair Display', serif; color: #d4af37; font-size: 1.1rem;">Deep Diagnostic</span>
<span style="background: {anomaly_color}40; border: 1px solid {anomaly_color}; color: {anomaly_color}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{severity}</span>
</div>
<div style="color: #f0f4f1; font-size: 0.95rem; margin-bottom: 10px;">
<strong>Detected State:</strong> {result.get('primary_observation', 'Clear')}
</div>"""

    if result.get('anomaly_detected') and result.get('action_plan'):
        action = result['action_plan']
        html += f"""
<div style="background: rgba(244, 67, 54, 0.1); padding: 10px; border-left: 3px solid #F44336; margin-bottom: 10px; font-size: 0.85rem;">
<strong style="color:#F44336;">🚨 THREAT: {result.get('specific_issue', 'Unknown')}</strong><br><br>
<strong style="color:#d4af37;">WHAT TO DO:</strong> {action.get('what_to_do')}<br>
<strong style="color:#d4af37;">HOW TO EXECUTE:</strong> {action.get('how_to_do_it')}<br>
<strong style="color:#d4af37;">LOGISTICS:</strong> {action.get('where_to_source')}
</div>
<div style="font-size: 0.8rem; color: #9ba8a0; font-style: italic;">
<strong>Science:</strong> {result.get('scientific_reasoning', '')}
</div>"""
    else:
        html += f"""
<div style="font-size: 0.85rem; color: #4CAF50;">
✅ Parameters nominal. No immediate intervention required. 
</div>"""

    html += "</div>"
    return html

# ---------------- WHATSAPP MESSAGE ----------------
def send_whatsapp(node, result):
    if not result.get('anomaly_detected'):
        return

    action = result.get('action_plan', {})
    message = (
        f"🚨 TERRAFY CRITICAL ALERT 🚨\n\n"
        f"📍 Node: {node}\n"
        f"⚠️ Threat: {result.get('specific_issue')}\n"
        f"📈 Severity: {result.get('severity')}\n\n"
        f"🛠 WHAT TO DO:\n{action.get('what_to_do')}\n\n"
        f"📋 HOW:\n{action.get('how_to_do_it')}\n\n"
        f"🛒 PROCURE:\n{action.get('where_to_source')}\n\n"
        f"🧠 SUMMARY:\n{result.get('summary')}"
    )

    try:
        twilio_client.messages.create(
            from_=WHATSAPP_FROM,
            to=WHATSAPP_TO,
            body=message
        )
    except Exception as e:
        print(f"Twilio error: {e}")

# ---------------- STATE ----------------
last_snapshot = {k: 0.0 for k in CAMERAS}
prev_gray = {}
snapshot_interval_sec = SNAPSHOT_INTERVAL_MIN * 60

# ---------------- MAIN LOOP ----------------
while True:
    for node, url in CAMERAS.items():
        with video_boxes[node]:
            components.html(f'<img src="{url}" width="100%" style="border-radius: 8px; border: 1px solid rgba(212,175,55,0.3);">', height=320)

        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = add_watermark(frame, node)

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        motion = 0
        if node in prev_gray:
            motion = int(np.sum(cv2.absdiff(prev_gray[node], gray)))
        prev_gray[node] = gray

        motion_pct = min(100, motion // 500)
        motion_boxes[node].progress(motion_pct / 100.0, text=f"Kinetic Telemetry: {motion_pct}%")

        now = time.time()
        if now - last_snapshot[node] > snapshot_interval_sec or motion > MOTION_THRESHOLD:
            last_snapshot[node] = now
            buf = io.BytesIO()
            Image.fromarray(frame).save(buf, format="JPEG")

            ai_status_boxes[node].info("🧠 Executing Deep Diagnostic Scan...")
            result = analyze_with_gemini(buf.getvalue(), node)

            ai_status_boxes[node].empty()
            ai_render_boxes[node].markdown(render_ai_card(result), unsafe_allow_html=True)
            send_whatsapp(node, result)

    time.sleep(1 / FPS)

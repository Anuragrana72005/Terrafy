import streamlit as st
import qrcode
from PIL import Image
import hashlib
import json
from datetime import datetime, timedelta
import io
import time
import pydeck as pdk
import pandas as pd
import numpy as np
import altair as alt
from fpdf import FPDF

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Terrafy | Provenance Ledger",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp { background: radial-gradient(circle at top, #111a14 0%, #050706 100%); color: #f0f4f1; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #d4af37 !important; letter-spacing: 1px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {background: transparent !important;}

    [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 2rem !important; font-family: 'Playfair Display', serif !important; }
    [data-testid="stMetricLabel"] { color: #9ba8a0 !important; text-transform: uppercase; letter-spacing: 1px; }

    .glass-card { background: rgba(20, 30, 22, 0.6); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 12px; padding: 20px; backdrop-filter: blur(10px); margin-bottom: 20px; }
    .hash-string { font-family: 'Courier New', Courier, monospace; color: #4CAF50; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 6px; word-break: break-all; font-size: 0.85rem; border: 1px solid rgba(76, 175, 80, 0.3); text-align: center; }
    .terminal-box { font-family: 'Courier New', Courier, monospace; color: #00ff00; background: #0a0a0a; padding: 15px; border-radius: 8px; border: 1px solid #333; height: 300px; overflow-y: auto; font-size: 0.85rem; }
    .live-dot { height: 10px; width: 10px; background-color: #ff4c4c; border-radius: 50%; display: inline-block; animation: pulse-red 1.5s infinite; margin-right: 8px; }
    
    /* Custom Timeline CSS Restored */
    .timeline { border-left: 2px solid rgba(212, 175, 55, 0.5); padding-left: 20px; margin-left: 10px; margin-top: 15px; }
    .timeline-item { position: relative; margin-bottom: 25px; }
    .timeline-item::before {
        content: ''; position: absolute; left: -27px; top: 0; width: 12px; height: 12px;
        background-color: #d4af37; border-radius: 50%; box-shadow: 0 0 10px #d4af37;
    }
    .timeline-date { font-size: 0.85rem; color: #9ba8a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
    .timeline-title { font-size: 1.1rem; font-weight: 600; color: #f0f4f1; margin-bottom: 4px; }
    .timeline-desc { font-size: 0.9rem; color: #b0bec5; }

    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 76, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 76, 76, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📦 ENHANCED MOCK DATABASE
# ==========================================
batches = {
    "BATCH-AV-9942": {
        "crop": "Premium Basmati Rice", "farm_location": "Ludhiana, Punjab", "farmer": "Sardar Jagjeet Singh",
        "health_index": 94, "pesticides": "0.0% (Organic)", "carbon_saved": "1.2 Tons", "carbon_payout": "₹ 3,450",
        "planted": "2025-11-12", "harvested": "2026-02-25", "status": "In Transit to Export Hub",
        "storage_temp": 18.2, "storage_hum": 62, "base_spoilage_risk": 2.4,
        "origin_coords": [75.8573, 30.9010], "dest_coords": [70.2100, 21.0200]
    },
    "BATCH-AV-8810": {
        "crop": "Sharbati Wheat", "farm_location": "Karnal, Haryana", "farmer": "Anurag Rana",
        "health_index": 88, "pesticides": "0.2% (Safe limits)", "carbon_saved": "0.8 Tons", "carbon_payout": "₹ 2,100",
        "planted": "2025-10-05", "harvested": "2026-02-20", "status": "Warehoused (ITC Procurement)",
        "storage_temp": 22.0, "storage_hum": 45, "base_spoilage_risk": 5.1,
        "origin_coords": [76.9900, 29.6800], "dest_coords": [72.8300, 18.9400]
    }
}

with st.sidebar:
    st.markdown("<h2>🔗 Master Ledger</h2>", unsafe_allow_html=True)
    selected_batch = st.selectbox("Select Asset Batch", list(batches.keys()))
    st.markdown("---")
    st.info("🟢 **Blockchain Node: SYNCED**\n\nVerifying cryptographic signatures across Terrafy nodes.")

batch_data = batches[selected_batch]
data_string = json.dumps(batch_data, sort_keys=True).encode('utf-8')
crypto_hash = hashlib.sha256(data_string).hexdigest()
asset_grade = "AAA (Exceptional)" if batch_data["health_index"] >= 90 else "A (Standard Premium)"

# ==========================================
# 📄 PDF GENERATION LOGIC
# ==========================================
def generate_certificate(batch_id, data, hash_val):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(1)
    pdf.rect(5, 5, 200, 287)
    
    pdf.set_font("Times", "B", 24)
    pdf.set_text_color(20, 30, 22)
    pdf.cell(0, 20, "TERRAFY ENTERPRISE", ln=True, align="C")
    
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Cryptographic Certificate of Provenance", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(50, 50, 50)
    reason_text = "This document serves as immutable cryptographic proof of origin, quality, and environmental compliance for the specified agricultural asset. The data herein has been verified by decentralized IoT oracles and is permanently sealed on the Terrafy Ledger."
    pdf.multi_cell(0, 8, reason_text, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, " ASSET PASSPORT DATA", ln=True, fill=True)
    
    pdf.set_font("Arial", "", 12)
    details = [
        f"Batch Identifier: {batch_id}",
        f"Commodity Class: {data['crop']}",
        f"Origin Farm: {data['farm_location']} (Operated by {data['farmer']})",
        f"Harvest Date: {data['harvested']}",
        f"Chemical Profile: {data['pesticides']}",
        f"Carbon Offset Yield: {data['carbon_saved']}"
    ]
    for detail in details:
        pdf.cell(0, 8, f"  {detail}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 15, f"TERRAFY GLOBAL RANKING: {asset_grade}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Courier", "B", 10)
    pdf.cell(0, 10, "ON-CHAIN SHA-256 SIGNATURE:", ln=True, align="L")
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 6, hash_val)
    pdf.ln(10)
    
    pdf.set_font("Arial", "I", 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    pdf.cell(0, 10, f"Issued Date & Time: {timestamp}", ln=True)
    pdf.cell(0, 10, "Authorized by: Terrafy Automated Smart Contract System", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# ==========================================
# 🌍 EXECUTIVE DASHBOARD
# ==========================================
st.markdown("<h1>Terrafy Blockchain Ledger</h1>", unsafe_allow_html=True)
st.caption("FARM-TO-FORK TRACEABILITY • IMMUTABLE SMART CONTRACTS • EXPORT VERIFICATION")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Commodity Class", batch_data["crop"])
m2.metric("Terrafy Asset Grade", asset_grade)
m3.metric("Chemical Verification", batch_data["pesticides"])
m4.metric("Carbon Monetization", batch_data["carbon_payout"])
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🗺️ Live Routing & Timeline", "📊 Spoilage Risk Predictor", "📜 Blockchain Terminal"])

# ---------------- TAB 1: DYNAMIC MAP & EXPORT ----------------
with tab1:
    col1, col2 = st.columns([1.5, 1], gap="large")
    
    with col1:
        st.markdown("### 📍 Live Spatial Telemetry")
        
        arc_data = pd.DataFrame({
            "inbound_lon": [batch_data["origin_coords"][0]], "inbound_lat": [batch_data["origin_coords"][1]],
            "outbound_lon": [batch_data["dest_coords"][0]], "outbound_lat": [batch_data["dest_coords"][1]],
        })
        nodes_data = pd.DataFrame({
            "lon": [batch_data["origin_coords"][0], batch_data["dest_coords"][0]],
            "lat": [batch_data["origin_coords"][1], batch_data["dest_coords"][1]],
            "name": ["Origin (Farm)", "Destination (Port)"],
            "color": [[212, 175, 55, 255], [76, 175, 80, 255]]
        })

        view_state = pdk.ViewState(
            latitude=(batch_data["origin_coords"][1] + batch_data["dest_coords"][1]) / 2,
            longitude=(batch_data["origin_coords"][0] + batch_data["dest_coords"][0]) / 2,
            zoom=5, pitch=50, bearing=-15
        )

        st.pydeck_chart(pdk.Deck(
            layers=[
                pdk.Layer("ArcLayer", data=arc_data, get_source_position=["inbound_lon", "inbound_lat"], get_target_position=["outbound_lon", "outbound_lat"], get_source_color=[212, 175, 55, 200], get_target_color=[76, 175, 80, 200], get_width=6, auto_highlight=True),
                pdk.Layer("ScatterplotLayer", data=nodes_data, get_position=["lon", "lat"], get_color="color", get_radius=20000, radius_scale=1, radius_min_pixels=5, radius_max_pixels=15, pickable=True)
            ], 
            initial_view_state=view_state, map_provider="carto", map_style="dark", tooltip={"text": "{name}"}
        ))
        
        # RESTORED: Agronomic Lifecycle Timeline
        st.markdown("<br>### ⏳ Agronomic Lifecycle", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card">
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-date">{batch_data['planted']}</div>
                    <div class="timeline-title">🌱 Seed Sowing & Geotagging</div>
                    <div class="timeline-desc">Coordinates locked: {batch_data['farm_location']}. Optimal moisture levels confirmed via sensors.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-date">Mid-Season (Continuous)</div>
                    <div class="timeline-title">🛰️ Orbital Health Verification</div>
                    <div class="timeline-desc">Maintained {batch_data['health_index']} health index. Zero unapproved chemical treatments detected.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-date">{batch_data['harvested']}</div>
                    <div class="timeline-title">🚜 Yield Securitization</div>
                    <div class="timeline-desc">Harvest logged. Quality grade assessed and data permanently hashed to ledger.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🔐 Digital Passport")
        
        # RESTORED: Visual QR Code Generation and Display
        verification_url = f"https://terrafy-ledger.com/verify?batch={selected_batch}&hash={crypto_hash[:16]}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(verification_url)
        qr.make(fit=True)
        buf = io.BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
        
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 15px;">
            <h4 style="color:#d4af37; margin-top:0; font-size: 1.2rem;">{selected_batch}</h4>
            <p style="color:#9ba8a0; font-size:0.8rem; margin-bottom:10px;">Scan to verify origin authenticity</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Rendering the QR Code to the screen
        st.markdown("<div style='display: flex; justify-content: center; background: white; padding: 15px; border-radius: 12px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.image(buf.getvalue(), width=200) 
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Cryptographic Signature")
        st.markdown(f"<div class='hash-string'>0x{crypto_hash}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 📜 Export Compliance")
        st.markdown(f"""
        <div class="glass-card">
            <p style="margin: 0; padding: 5px 0;">✅ FDA Import Safety Compliant</p>
            <p style="margin: 0; padding: 5px 0;">✅ EU Organic Standard Met</p>
            <p style="margin: 0; padding: 5px 0;">✅ Carbon Offset Audited</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Generation Button
        pdf_bytes = generate_certificate(selected_batch, batch_data, crypto_hash)
        st.download_button(
            label="📄 DOWNLOAD OFFICIAL CERTIFICATE",
            data=pdf_bytes,
            file_name=f"Terrafy_Certificate_{selected_batch}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# ---------------- TAB 2: AI DEEP ANALYTICS ----------------
with tab2:
    st.markdown("### 🧠 AI Spoilage & Risk Prediction")
    st.latex(r"Risk\_Score = \sum_{t=0}^{T} \left( \alpha(\Delta Temp_t)^2 + \beta(\Delta Hum_t) \right) \times e^{-\gamma \cdot HealthIndex}")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        np.random.seed(int(crypto_hash[:8], 16) % 10000)
        hours = pd.date_range(end=datetime.now(), periods=72, freq='H')
        df_telemetry = pd.DataFrame({
            'Time': hours, 
            'Temperature (°C)': np.random.normal(loc=batch_data['storage_temp'], scale=0.8, size=72), 
            'Humidity (%)': np.random.normal(loc=batch_data['storage_hum'], scale=2.5, size=72)
        }).melt('Time', var_name='Metric', value_name='Value')
        
        st.altair_chart(alt.Chart(df_telemetry).mark_line().encode(
            x='Time:T', y='Value:Q', color='Metric:N', tooltip=['Time', 'Metric', 'Value']
        ).properties(height=300).interactive(), use_container_width=True)

    with c2:
        st.markdown(f"### <span class='live-dot'></span>Live Environment", unsafe_allow_html=True)
        st.metric("Container Temp", f"{batch_data['storage_temp']} °C", "+0.2 °C (Stable)", delta_color="inverse")
        st.metric("Relative Humidity", f"{batch_data['storage_hum']}%", "-1.2% (Stable)")
        st.metric("Predicted Spoilage Risk", f"{batch_data['base_spoilage_risk']}%", "Nominal")

# ---------------- TAB 3: SMART CONTRACT AUDIT ----------------
with tab3:
    st.markdown("### 📜 On-Chain Execution Logs")
    log_output = f"""[SYSTEM] Node connection established... OK
[BLOCKCHAIN] Retrieving contract history for address 0x8F9a...34e2
[INFO] Contract Standard: ERC-1155 (Multi-Token Provenance)
[EVENT] {batch_data['planted']} | MINT: Genesis token minted. 
        -> Lat/Lon Geofence locked: {batch_data['origin_coords']}
[EVENT] {batch_data['harvested']} | UPDATE: Yield logged. Health index {batch_data['health_index']} verified by Oracle.
[EVENT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SYNC: Live telemetry node heartbeat received.
[CRYPTO] Current Block Hash: 0x{crypto_hash}"""

    st.markdown(f'<div class="terminal-box"><pre>{log_output}</pre></div>', unsafe_allow_html=True)
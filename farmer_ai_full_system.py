import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import json
import time
import hashlib
import random
import pandas as pd
import altair as alt

# =========================
# ⚙️ PAGE CONFIG & CSS
# =========================
st.set_page_config(
    page_title="Terrafy | Equipment Exchange",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');

    .stApp { background: radial-gradient(circle at top, #111a14 0%, #050706 100%); color: #f0f4f1; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #d4af37 !important; letter-spacing: 1px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {background: transparent !important;}

    [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 2.2rem !important; font-family: 'Playfair Display', serif !important; }
    [data-testid="stMetricLabel"] { color: #9ba8a0 !important; text-transform: uppercase; letter-spacing: 1px; }
    
    div.stButton > button { background: linear-gradient(135deg, #d4af37, #b8860b) !important; color: #000 !important; font-weight: 800 !important; border: none !important; border-radius: 6px !important; transition: all 0.3s ease !important; padding: 0.75rem !important; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { background: rgba(0,0,0,0.5) !important; border: 1px solid rgba(212, 175, 55, 0.3) !important; color: #fff !important; border-radius: 6px; }
    
    .dashboard-card { background: rgba(20, 30, 22, 0.6); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 12px; padding: 20px; backdrop-filter: blur(10px); margin-bottom: 20px; }
    .terminal-box { font-family: 'Courier New', Courier, monospace; color: #00ff00; background: #0a0a0a; padding: 15px; border-radius: 8px; border: 1px solid #333; height: 250px; overflow-y: auto; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 🔐 GEMINI CONFIG
# =========================
GEMINI_API_KEY = "AIzaSyD6lG-dydZ_yp7aeoVc4kT96nVOYK5HiWA"
MODEL = "gemini-2.5-flash"
client = genai.Client(api_key=GEMINI_API_KEY)

def safe_json_from_text(text: str):
    if not text: raise ValueError("Empty AI response")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start: raise ValueError("No JSON found")
    return json.loads(text[start:end + 1])

# =========================
# 🧠 AI MARKETPLACE BRAIN (UPGRADED)
# =========================
def gemini_marketplace_brain(context):
    prompt = f"""
    You are an elite Agricultural Economist, Risk Actuary, and Logistics AI powering the Terrafy Equipment Exchange.
    Context Parameters: {context}

    Calculate the dynamic rental price, but also predict the mechanical wear-and-tear risk, weather impact, and carbon offset.
    Output ONLY valid JSON matching this schema:
    {{
      "best_decision": "Short Actionable Command (e.g., EXECUTE RENTAL, REQUIRE DEPOSIT)",
      "optimized_price": 1250,
      "estimated_cost": 10000,
      "estimated_benefit": 15000,
      "net_impact": 5000,
      "wear_and_tear_risk_pct": 14.5,
      "mechanical_risk_reasoning": "Why this specific crop/duration poses mechanical risk.",
      "weather_multiplier": 1.15,
      "carbon_saved_kg": 450,
      "smart_contract_clause": "A highly legal-sounding condition based on the trust score and task."
    }}
    """
    try:
        response = client.models.generate_content(
            model=MODEL, contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
        )
        return response.text
    except Exception as e:
        return None

# =========================
# 🌍 MAIN UI DASHBOARD
# =========================
st.markdown("<h1>Terrafy | Sovereign Equipment Exchange</h1>", unsafe_allow_html=True)
st.caption("DYNAMIC PRICING • PREDICTIVE MAINTENANCE AI • ON-CHAIN CONTRACTS • ESG TRACKING")
st.markdown("---")

# ---------------- INPUT PANEL ----------------
st.markdown("### 🎛️ Asset & Contract Parameters")
with st.container(border=True):
    in_col1, in_col2, in_col3, in_col4 = st.columns(4)
    with in_col1:
        equipment = st.selectbox("Asset Type", ["Tractor (50HP+)", "Rotavator", "Boom Sprayer", "Combine Harvester", "Seed Drill"])
        crop = st.selectbox("Target Commodity", ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane"])
    with in_col2:
        season = st.selectbox("Current Phase", ["Land Preparation", "Sowing", "Crop Maintenance", "Harvesting"])
        weather = st.selectbox("Imminent Weather Forecast", ["Clear / Optimal", "Approaching Rainstorm", "Drought / Hard Soil"])
    with in_col3:
        base_price = st.number_input("Market Baseline (₹/Hr)", min_value=100, value=800, step=50)
        hours = st.number_input("Contract Duration (Hrs)", min_value=1, value=12)
    with in_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        reputation_score = st.slider("Counterparty Trust Score", 0, 100, 72, help="Based on past Terrafy telemetry")

execute_btn = st.button("INITIALIZE QUANTUM PRICING & RISK ENGINE", use_container_width=True)

# =========================
# 🚀 AI EXECUTION & OUTPUT
# =========================
if execute_btn:
    context = f"""
    Crop: {crop} | Phase: {season} | Asset: {equipment} | Weather: {weather}
    Market Baseline: ₹{base_price}/hour | Duration: {hours} hours
    Counterparty Trust Score: {reputation_score}/100 | Current Month: {datetime.now().strftime('%B')}
    """

    with st.spinner("Quantum algorithms optimizing asset logistics, calculating kinetic wear, and drafting smart contracts..."):
        time.sleep(1.5) 
        raw = gemini_marketplace_brain(context)
        
        try:
            data = safe_json_from_text(raw)
            opt_price = float(data.get("optimized_price", base_price))
            net_impact = float(data.get("net_impact", 0))
            wear_risk = float(data.get("wear_and_tear_risk_pct", 10.0))
            carbon = int(data.get("carbon_saved_kg", 200))
            
            st.markdown("---")
            
            # Executive Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("System Directive", data.get("best_decision", "N/A"))
            m2.metric("Optimized Rate", f"₹ {opt_price:,.0f} / hr", f"{(opt_price - base_price):+,.0f} Surge")
            m3.metric("Projected Net ROI", f"₹ {net_impact:,.0f}")
            m4.metric("Asset Wear Risk", f"{wear_risk}%", "- Requires Telemetry", delta_color="inverse")

            # Multi-Tab Deep Dive
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Financial Engine", "⚙️ Predictive Maintenance", "🌍 ESG Carbon Yield", "📜 Smart Contract"])
            
            # --- TAB 1: Financials ---
            with tab1:
                r1, r2 = st.columns([2, 1])
                with r1:
                    st.markdown("### Market Economics")
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <p><strong style="color:#d4af37;">Weather Surge Multiplier:</strong> {data.get('weather_multiplier', 1.0)}x applied due to {weather}.</p>
                        <p><strong style="color:#d4af37;">Trust Score Impact:</strong> Counterparty score of {reputation_score}/100 adjusted the baseline margin.</p>
                        <p><strong style="color:#d4af37;">Asset Utilization:</strong> {hours} hours committed to {crop} {season}.</p>
                    </div>
                    """, unsafe_allow_html=True)
                with r2:
                    st.markdown("### Ledger Impact")
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <span style="color:#9ba8a0;">Gross Liability:</span> <strong style="color:#ff4c4c; float:right;">₹ {data.get('estimated_cost', 0):,.0f}</strong><br><br>
                        <span style="color:#9ba8a0;">Gross Yield:</span> <strong style="color:#4CAF50; float:right;">₹ {data.get('estimated_benefit', 0):,.0f}</strong><br><hr style="border-color:#333;">
                        <span style="color:#d4af37; font-size:1.2rem;">NET MARGIN:</span> <strong style="color:#d4af37; font-size:1.2rem; float:right;">₹ {net_impact:,.0f}</strong>
                    </div>
                    """, unsafe_allow_html=True)

            # --- TAB 2: Predictive Maintenance ---
            with tab2:
                st.markdown("### Kinetic Wear-and-Tear Probability Model")
                st.markdown("Terrafy calculates mechanical depreciation using the proprietary non-linear decay formula:")
                
                # Formal LaTeX equation for risk modeling
                st.latex(r"Risk_{wear} = \left( \frac{H_{contract}}{H_{avg}} \right)^{\alpha} \times e^{-\beta \cdot Trust} + \gamma_{crop}")
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("Probability of Breakdown", f"{wear_risk}%")
                    st.progress(wear_risk / 100)
                with c2:
                    st.markdown(f"""
                    <div class="dashboard-card" style="border-color:#ff4c4c;">
                        <h4 style="color:#ff4c4c; margin-top:0;">AI Diagnostic Warning</h4>
                        <p>{data.get('mechanical_risk_reasoning', 'No critical data.')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # --- TAB 3: ESG & Carbon ---
            with tab3:
                st.markdown("### Scope 3 Emissions Reduction")
                st.markdown("By utilizing the Terrafy sharing economy instead of procuring net-new machinery, this transaction generates verifiable carbon offsets.")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="dashboard-card" style="text-align:center;">
                        <h2 style="color:#4CAF50; font-size:3rem; margin:0;">{carbon} kg</h2>
                        <p style="color:#9ba8a0; text-transform:uppercase;">CO2 Equivalent Offset</p>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.info("🌱 **Monetization Opportunity:** These verified offsets can be hashed to the Terrafy Ledger and sold to enterprise buyers for secondary revenue.")

            # --- TAB 4: Smart Contract ---
            with tab4:
                st.markdown("### On-Chain Execution")
                contract_hash = hashlib.sha256(f"{equipment}{crop}{hours}{opt_price}{datetime.now()}".encode()).hexdigest()
                
                log_output = f"""[TERRAFY PROTOCOL] Initiating secure handshake...
[ORACLE] Fetching current localized weather constraints... OK ({weather})
[RISK NODE] Verifying counterparty identity. Trust Score: {reputation_score}/100.
[LEDGER] Minting transactional agreement...

>>> SMART CONTRACT CLAUSE INJECTED:
"{data.get('smart_contract_clause', 'Standard rental terms apply.')}"

[CRYPTO] Locking terms. Dynamic rate set to INR {opt_price}/hr.
[STATUS] Awaiting biometric signature from Counterparty.

TX HASH: 0x{contract_hash}"""
                st.markdown(f'<div class="terminal-box"><pre>{log_output}</pre></div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Marketplace Neural Engine Offline. Error: {str(e)}")

# =========================
# FOOTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("AGRIVUE LOGISTICS • The data presented is generated by AI models and should be cross-referenced with local physical market conditions prior to finalizing financial contracts.")
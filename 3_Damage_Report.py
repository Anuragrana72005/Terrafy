import streamlit as st
import io
import json
import random
import textwrap
from PIL import Image
from datetime import datetime
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import alerts

# ==============================
# ⚙️ PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Terrafy | Loss Adjustment",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 LUXURY TECH STYLING
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
API_KEY = "Gemini API key"
client = genai.Client(api_key=API_KEY)

# ==============================
# 📱 SIDEBAR & HUD
# ==============================
st.sidebar.markdown("<h2>Claim Parameters</h2>", unsafe_allow_html=True)

DEMO_MODE = st.sidebar.toggle("Simulated Assessor Mode", value=False)

st.sidebar.markdown("### Asset Details")
crop_name = st.sidebar.text_input("Commodity Type", value="Wheat")
total_area_ha = st.sidebar.number_input("Total Insured Area (Hectares)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

st.sidebar.markdown("### Financial Baselines")
expected_yield_q_per_ha = st.sidebar.number_input("Expected Yield (Quintal/Ha)", min_value=1.0, max_value=200.0, value=35.0, step=1.0)
expected_price_rs_per_q = st.sidebar.number_input("Market Rate (₹/Quintal)", min_value=100.0, max_value=10000.0, value=2200.0, step=50.0)

# ==============================
# 🌍 MAIN DASHBOARD
# ==============================
st.markdown("<h1>Automated Loss Adjustment</h1>", unsafe_allow_html=True)
st.caption("AI DAMAGE QUANTIFICATION • FINANCIAL IMPACT MODELING • PMFBY COMPLIANCE")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Pre-Event Baseline")
    before_img = st.file_uploader("Upload BEFORE Damage Image", type=["jpg", "jpeg", "png"], key="before")

with col2:
    st.markdown("### 2. Post-Event Assessment")
    after_img = st.file_uploader("Upload AFTER Damage Image", type=["jpg", "jpeg", "png"], key="after")

def metric_row(label, value, help_text=None):
    st.markdown(f"**{label}:** <span style='color:#d4af37;'>{value}</span>", unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)

# ==============================
# 🧠 AI PROCESSING ENGINE
# ==============================
if before_img and after_img:
    before_bytes = before_img.getvalue()
    after_bytes = after_img.getvalue()

    before_image = Image.open(io.BytesIO(before_bytes))
    after_image = Image.open(io.BytesIO(after_bytes))

    st.markdown("---")
    st.subheader("Visual Evidence Verification")
    c1, c2 = st.columns(2)
    c1.image(before_image, caption="Verified Baseline", use_container_width=True)
    c2.image(after_image, caption="Reported Damage", use_container_width=True)

    with st.spinner("Executing structural damage analysis via Terrafy AI..."):

        if DEMO_MODE:
            damage_pct = random.randint(30, 85)
            damage_data = {
                "damage_type": "Severe Waterlogging/Lodging",
                "damage_severity_pct": damage_pct,
                "salvageable": damage_pct < 55,
                "estimated_area_affected_ha": round(total_area_ha * damage_pct / 100.0, 2),
                "likely_cause": "Intense localized precipitation leading to structural crop failure and canopy collapse. Soil saturation exceeded 95% threshold.",
                "risk_of_secondary_issues": "High risk of fungal rot and pest infestation due to prolonged moisture exposure.",
                "recommended_farmer_actions": [
                    "Isolate the affected area by digging temporary drainage trenches immediately.",
                    "Document all angles of the field using the Terrafy mobile application.",
                    "Do not harvest or clear the field until the official adjuster physically verifies the claim."
                ],
                "required_documents_for_claim": [
                    "Aadhaar Card & Bank Passbook",
                    "Khasra/Khatauni (Land Ownership Records)",
                    "Crop Sowing Certificate (Issued by Patwari)",
                    "Premium Deduction Receipt (Bank Statement)"
                ],
                "followup_next_7_days": "Monitor root integrity. If soil remains saturated for 72+ hours, assume 100% yield loss in affected sectors.",
                "summary": "Critical structural failure detected in crop canopy. High probability of yield loss exceeding insurance thresholds requiring immediate intervention."
            }
        else:
            try:
                schema = {
                    "type": "object",
                    "properties": {
                        "damage_type": {"type": "string"},
                        "damage_severity_pct": {"type": "number"},
                        "salvageable": {"type": "boolean"},
                        "estimated_area_affected_ha": {"type": "number"},
                        "likely_cause": {"type": "string"},
                        "risk_of_secondary_issues": {"type": "string"},
                        "recommended_farmer_actions": {"type": "array", "items": {"type": "string"}},
                        "required_documents_for_claim": {"type": "array", "items": {"type": "string"}},
                        "followup_next_7_days": {"type": "string"},
                        "summary": {"type": "string"}
                    },
                    "required": ["damage_type", "damage_severity_pct", "salvageable", "estimated_area_affected_ha", "likely_cause", "risk_of_secondary_issues", "recommended_farmer_actions", "required_documents_for_claim", "followup_next_7_days", "summary"]
                }

                prompt = f"""
                You are a senior, highly analytical Crop Insurance Adjuster for the PMFBY.
                The asset is {crop_name} spanning {total_area_ha} hectares.

                Compare the BEFORE (baseline) and AFTER (post-event) images.
                Provide a highly professional, clinical assessment of the damage. 
                Estimate the severity percentage strictly based on visual canopy/structural degradation.
                Your tone must be objective, financial, and executive.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, before_image, after_image],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    ),
                )
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                damage_data = json.loads(clean_json)

            except Exception as e:
                st.error(f"Neural processing failure: {e}")
                st.stop()

    # ---------------- YIELD & FINANCIAL CALCULATIONS ----------------
    damage_pct = float(damage_data.get("damage_severity_pct", 0))
    damage_fraction = max(0.0, min(damage_pct / 100.0, 1.0))
    damaged_area_ha = min(damage_data.get("estimated_area_affected_ha", total_area_ha * damage_fraction), total_area_ha)

    normal_yield_q = total_area_ha * expected_yield_q_per_ha
    expected_income_rs = normal_yield_q * expected_price_rs_per_q
    estimated_yield_loss_q = normal_yield_q * damage_fraction
    estimated_income_loss_rs = estimated_yield_loss_q * expected_price_rs_per_q

    if damage_pct < 20:
        insurance_eligible = "Unlikely (Below Threshold)"
        claim_urgency = "Standard Monitoring"
        badge_color = colors.HexColor("#4CAF50") # Green
        suggested_claim_window_days = 7
    elif damage_pct < 50:
        insurance_eligible = "Probable (Requires Audit)"
        claim_urgency = "Elevated"
        badge_color = colors.HexColor("#FF9800") # Orange
        suggested_claim_window_days = 3
    else:
        insurance_eligible = "Highly Probable (Exceeds Threshold)"
        claim_urgency = "CRITICAL"
        badge_color = colors.HexColor("#F44336") # Red
        suggested_claim_window_days = 2

    claim_id = f"TRF-{random.randint(10000, 99999)}-{datetime.now().strftime('%y%m')}"

    damage_data.update({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estimated_income_loss_rs": estimated_income_loss_rs,
        "estimated_yield_loss_q": estimated_yield_loss_q,
        "insurance_eligible": insurance_eligible,
        "claim_urgency": claim_urgency,
        "damaged_area_ha_final": round(damaged_area_ha, 2),
        "claim_id": claim_id
    })

    # ---------------- UI DASHBOARD RENDER ----------------
    st.markdown("---")
    st.markdown("<h2>Executive Damage Report</h2>", unsafe_allow_html=True)
    
    st.info(f"**Terrafy AI Summary:** {damage_data.get('summary', 'Analysis completed.')}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Structural Damage", f"{damage_pct}%")
    m2.metric("Affected Area", f"{damaged_area_ha:.2f} Ha")
    m3.metric("Est. Yield Loss", f"{estimated_yield_loss_q:.1f} Qtl")
    m4.metric("Financial Exposure", f"₹ {estimated_income_loss_rs:,.0f}")

    # ---------------- PDF GENERATION (ULTRA-RICH FORMAT) ----------------
    def generate_pdf(data: dict, badge_col) -> str:
        filename = "Terrafy_Official_Loss_Report.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # --- Helper for text wrapping ---
        def draw_wrapped_text(c, text, x, y, max_width=90, line_height=14):
            lines = textwrap.wrap(text, width=max_width)
            for line in lines:
                c.drawString(x, y, line)
                y -= line_height
            return y

        yield_loss = data.get('estimated_yield_loss_q', 0.0)
        income_loss = data.get('estimated_income_loss_rs', 0.0)
        
        # --- TOP HEADER (Dark Luxury Box) ---
        c.setFillColor(colors.HexColor("#111a14"))
        c.rect(0, height - 80, width, 80, fill=1, stroke=0)
        
        c.setFillColor(colors.HexColor("#d4af37")) # Gold text
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, height - 40, "TERRAFY ENTERPRISE")
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 60, "Official AI Loss Adjustment & Causal Analysis Report")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - 40, height - 40, f"CLAIM ID: {data['claim_id']}")
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 40, height - 60, f"Date: {data.get('timestamp')}")
        
        # --- SEVERITY BADGE ---
        c.setFillColor(badge_col)
        c.roundRect(40, height - 120, 150, 25, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(55, height - 112, f"STATUS: {data['claim_urgency']}")

        # Reset text color to black for body
        c.setFillColor(colors.black)
        
        # --- SECTION 1: ASSET & FINANCIALS ---
        y_pos = height - 150
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#d4af37"))
        c.drawString(40, y_pos, "1. ASSET & FINANCIAL EXPOSURE")
        c.setFillColor(colors.black)
        
        y_pos -= 20
        c.setFont("Helvetica", 11)
        c.drawString(40, y_pos, f"Commodity Assessed: {crop_name}")
        c.drawString(300, y_pos, f"Total Insured Area: {total_area_ha} Hectares")
        y_pos -= 20
        c.drawString(40, y_pos, f"Estimated Yield Loss: {yield_loss:.1f} Quintals")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(300, y_pos, f"Financial Exposure: INR {income_loss:,.2f}")
        
        # --- SECTION 2: AI CAUSAL ANALYSIS ---
        y_pos -= 40
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#d4af37"))
        c.drawString(40, y_pos, "2. DIAGNOSTIC & CAUSAL ANALYSIS")
        c.setFillColor(colors.black)
        
        y_pos -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, f"Primary Damage Vector: {data.get('damage_type', 'N/A')}")
        c.drawString(300, y_pos, f"Severity Index: {data.get('damage_severity_pct', 0)}% Structural Loss")
        
        y_pos -= 25
        c.drawString(40, y_pos, "Why This Happened (AI Diagnosis):")
        c.setFont("Helvetica", 10)
        y_pos -= 15
        y_pos = draw_wrapped_text(c, data.get("likely_cause", "N/A"), 40, y_pos, 100)

        y_pos -= 10
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, "Executive Summary:")
        c.setFont("Helvetica", 10)
        y_pos -= 15
        y_pos = draw_wrapped_text(c, data.get("summary", "N/A"), 40, y_pos, 100)

        # --- SECTION 3: MITIGATION & NEXT STEPS ---
        y_pos -= 20
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#d4af37"))
        c.drawString(40, y_pos, "3. MITIGATION & REQUIRED NEXT STEPS")
        c.setFillColor(colors.black)
        
        y_pos -= 25
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, "Immediate Actions Required by Farmer/Agent:")
        c.setFont("Helvetica", 10)
        y_pos -= 15
        for action in data.get("recommended_farmer_actions", []):
            y_pos = draw_wrapped_text(c, f"• {action}", 50, y_pos, 95)
            y_pos -= 5
            
        y_pos -= 10
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_pos, "Mandatory Compliance Window:")
        c.setFont("Helvetica", 10)
        c.drawString(220, y_pos, f"Must formally file within {suggested_claim_window_days} Days")
        
        # --- FOOTER ---
        c.setFillColor(colors.HexColor("#111a14"))
        c.rect(0, 0, width, 50, fill=1, stroke=0)
        
        c.setFillColor(colors.HexColor("#d4af37"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, 25, "TERRAFY SUPPORT: 1-800-TERRAFY (1-800-837-7239)")
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 8)
        c.drawString(40, 12, "This document is AI-generated for pre-assessment purposes. Subject to physical adjuster verification.")

        c.save()
        return filename

    st.markdown("<br>", unsafe_allow_html=True)
    pdf_file = generate_pdf(damage_data, badge_color)

    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            "📄 DOWNLOAD TERRAFY PDF REPORT",
            data=open(pdf_file, "rb").read(),
            file_name=f"{claim_id}_Loss_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # ---------------- WHATSAPP ALERT ----------------
    try:
        alerts.monitor_and_alert(
            "Loss Adjustment Module",
            {
                "rain_prob": "Low",
                "wind_speed": "Calm",
                "moisture_pct": 50,
                "summary": (
                    f"TERRAFY CLAIM INITIATED: {claim_id}\n"
                    f"Commodity: {crop_name} | Damage: {damage_pct}%\n"
                    f"Financial Exposure: INR {estimated_income_loss_rs:,.0f}\n"
                    f"Eligibility: {insurance_eligible}\n"
                    f"Action: Submit official Terrafy PDF report to local FPO."
                )
            }
        )
        st.success("📲 Executive summary successfully routed via Twilio Secure Network.")
    except Exception as e:
        st.error("Could not transmit WhatsApp alert. Ensure Twilio server is online.")

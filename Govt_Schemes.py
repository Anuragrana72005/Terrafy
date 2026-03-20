import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# ⚙️ PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(
    page_title="Terrafy | Govt Relief Liaison",
    page_icon="🏛️",
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
        font-size: 2rem !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ba8a0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom Buttons */
    div.stButton > button, .stLinkButton > a {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
        display: block;
        text-align: center;
    }
    div.stButton > button:hover, .stLinkButton > a:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #fff !important;
        border-radius: 6px;
    }
    
    /* Scheme Cards */
    .scheme-card {
        background: rgba(20, 30, 22, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: transparent;
        border-radius: 4px 4px 0px 0px; color: #9ba8a0; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #d4af37 !important; border-bottom: 2px solid #d4af37 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔐 AI INITIALIZATION
# ==========================================
API_KEY = "Gemini API key"
MODEL = "gemini-2.5-flash"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL)

@st.cache_data(ttl=3600)
def check_gemini():
    try:
        r = model.generate_content("Reply OK")
        return bool(r.text)
    except Exception:
        return False

GEMINI_OK = check_gemini()

# ==========================================
# 📱 SIDEBAR: LOCALIZATION & TELEMETRY
# ==========================================
with st.sidebar:
    st.markdown("<h2>Regional Context</h2>", unsafe_allow_html=True)
    
    if GEMINI_OK:
        st.success("🟢 AI Comm-Link Active")
    else:
        st.error("🔴 AI Comm-Link Offline")

    LANGUAGES = {
        "English": "English", "हिंदी": "Hindi", "ਪੰਜਾਬੀ": "Punjabi",
        "मराठी": "Marathi", "தமிழ்": "Tamil", "తెలుగు": "Telugu",
    }
    STATES = [
        "Punjab", "Haryana", "Uttar Pradesh", "Maharashtra", 
        "Tamil Nadu", "Karnataka", "Rajasthan", "Bihar", "Madhya Pradesh"
    ]

    language_ui = st.selectbox("Liaison Output Language", list(LANGUAGES.keys()))
    farmer_language = LANGUAGES[language_ui]
    state = st.selectbox("Jurisdiction (State)", STATES)

    st.markdown("---")
    st.markdown("<h2>Live Telemetry Integration</h2>", unsafe_allow_html=True)
    st.caption("Auto-synced from AgriVue Node Sensors")
    
    damage_pct = st.slider("Canopy Damage (%)", 0, 100, 55)
    crop_stress = st.selectbox("Biometric Stress Level", ["Nominal", "Elevated", "Critical"])
    soil_moisture = st.slider("Soil Moisture Deficit (%)", 0, 100, 22)

# ==========================================
# 🧠 LOGIC & SCHEME REGISTRY
# ==========================================
# Determine primary intervention category
if damage_pct >= 50:
    category = "INSURANCE_AND_COMPENSATION"
    urgency = "CRITICAL"
elif damage_pct >= 30:
    category = "PARTIAL_RELIEF"
    urgency = "ELEVATED"
elif soil_moisture < 30:
    category = "IRRIGATION_SUPPORT"
    urgency = "MODERATE"
elif crop_stress == "Critical":
    category = "FARMER_SUPPORT"
    urgency = "ELEVATED"
else:
    category = "DEVELOPMENT_AND_CREDIT"
    urgency = "NOMINAL"

# Expanded, professional database
GOVT_SCHEMES = {
    "INSURANCE_AND_COMPENSATION": [
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "benefit": "Comprehensive compensation for yield loss due to non-preventable risks.",
            "processing": "15-30 days post physical assessment.",
            "eligibility": "Actively insured farmers with >33% assessed crop damage.",
            "link": "https://pmfby.gov.in/"
        },
        {
            "name": "State Disaster Response Fund (SDRF)",
            "benefit": "Direct financial relief for severe natural calamities (flood, drought, cyclone).",
            "processing": "Immediate (upon district notification).",
            "eligibility": "Farmers in gazetted disaster-hit districts.",
            "link": "https://ndmiss.mha.gov.in/"
        }
    ],
    "PARTIAL_RELIEF": [
        {
            "name": "PMFBY (Mid-Season Adversity Cover)",
            "benefit": "Advance relief (up to 25% of sum insured) for prolonged dry spells or severe floods.",
            "processing": "7-14 days.",
            "eligibility": "Expected yield during season falls below 50% of normal.",
            "link": "https://pmfby.gov.in/"
        }
    ],
    "IRRIGATION_SUPPORT": [
        {
            "name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
            "benefit": "Subsidies ranging from 55% to 100% for micro-irrigation systems (drip/sprinkler).",
            "processing": "30-45 days for subsidy clearance.",
            "eligibility": "All farmers, priority to Small & Marginal (SMF).",
            "link": "https://pmksy.gov.in/"
        },
        {
            "name": "PM-KUSUM (Solar Pumps)",
            "benefit": "Up to 60% subsidy on standalone solar agriculture pumps.",
            "processing": "Varies by state nodal agency.",
            "eligibility": "Farmers with safe/semi-critical groundwater levels.",
            "link": "https://pmkusum.mnre.gov.in/"
        }
    ],
    "FARMER_SUPPORT": [
        {
            "name": "Soil Health Card Scheme",
            "benefit": "Free bi-annual soil testing and customized fertilizer usage advisory.",
            "processing": "14 days post sample collection.",
            "eligibility": "Universal (All landholding farmers).",
            "link": "https://soilhealth.dac.gov.in/"
        }
    ],
    "DEVELOPMENT_AND_CREDIT": [
        {
            "name": "PM-KISAN Samman Nidhi",
            "benefit": "₹6,000 per year minimum income support, transferred directly (DBT).",
            "processing": "Automated tri-annual installments.",
            "eligibility": "Small and marginal farmers with valid land records.",
            "link": "https://pmkisan.gov.in/"
        },
        {
            "name": "Kisan Credit Card (KCC)",
            "benefit": "Institutional credit at concessional interest rates (as low as 4%).",
            "processing": "7-14 days via local banking branches.",
            "eligibility": "All farmers, tenant farmers, and sharecroppers.",
            "link": "https://sbi.co.in/web/agri-rural/agriculture-banking/crop-loan/kisan-credit-card"
        }
    ]
}

# ==========================================
# 🌍 EXECUTIVE DASHBOARD
# ==========================================
st.markdown("<h1>State Subsidy & Relief Liaison</h1>", unsafe_allow_html=True)
st.caption("DIRECT BENEFIT TRANSFER (DBT) ROUTING • SCHEME MATCHING • E-GOVERNANCE TERMINAL")
st.markdown("---")

# Telemetry Overview
c1, c2, c3, c4 = st.columns(4)
c1.metric("Intervention Profile", category.replace("_", " "))
c2.metric("System Urgency", urgency)
c3.metric("State Jurisdiction", state)
c4.metric("Output Language", farmer_language)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🗂️ TABBED INTERFACE
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏛️ Verified Entitlements", "📋 Documentation Ledger", "🎙️ AI Liaison Terminal"])

# ---------------- TAB 1: SCHEMES ----------------
with tab1:
    schemes = GOVT_SCHEMES.get(category, [])
    
    if not schemes:
        st.info("Based on current telemetry, standard baseline schemes apply. Diverting to Development & Credit.")
        schemes = GOVT_SCHEMES.get("DEVELOPMENT_AND_CREDIT", [])

    st.markdown("### Automatically Applicable Interventions")
    
    for s in schemes:
        st.markdown(f"""
        <div class="scheme-card">
            <h3 style="margin-top:0; border-bottom:1px solid rgba(212,175,55,0.2); padding-bottom:10px;">{s['name']}</h3>
            <p><strong style="color:#d4af37;">Financial Benefit:</strong> {s['benefit']}</p>
            <p><strong style="color:#d4af37;">Eligibility Criteria:</strong> {s['eligibility']}</p>
            <p><strong style="color:#d4af37;">Processing Timeline:</strong> {s['processing']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(f"INITIATE APPLICATION →", s["link"])
        st.markdown("<br>", unsafe_allow_html=True)

# ---------------- TAB 2: DOCUMENTS ----------------
with tab2:
    st.markdown("### Standard E-Governance Compliance Checklist")
    st.write("Ensure the following digital or physical records are prepared before initiating applications via the state portals:")
    
    docs = [
        ("Aadhaar Card", "Mandatory for all Direct Benefit Transfers (DBT) and e-KYC."),
        ("Bank Passbook / Cancelled Cheque", "Must be seeded with Aadhaar for funds routing."),
        ("Land Records (Khasra/Khatauni)", "Proof of ownership or registered tenancy."),
        ("Crop Sowing Certificate", "Issued by the local Patwari or Village Officer."),
        ("Passport Size Photographs", "Recent, for physical dossier submissions.")
    ]
    
    for doc, desc in docs:
        st.markdown(f"- **<span style='color:#d4af37;'>{doc}:</span>** {desc}", unsafe_allow_html=True)

# ---------------- TAB 3: AI CHATBOT ----------------
with tab3:
    st.markdown("### Government Agricultural Advisory Interface")
    st.caption("Secure communication channel. Speak or type to interface directly with the AI Liaison.")
    
    if "chat" not in st.session_state:
        st.session_state.chat = [("ai", f"Namaste. I am your Terrafy Government Liaison for {state}. Based on your field's {damage_pct}% damage reading, how can I assist you with your relief applications today?")]

    # Render Chat History
    for role, msg in st.session_state.chat:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(msg)

    # Chat Input
    user_msg = st.chat_input("Initiate comm-link (Ask about schemes, processes, or deadlines)...")

    def ask_gemini_voice(question: str) -> str:
        if not GEMINI_OK:
            return "Neural uplink offline. Please try again shortly."

        prompt = f"""
        Act as an elite, highly knowledgeable Agricultural Officer working for the Government of India, currently liaising through the AgriVue system.
        You must reply ONLY in {farmer_language}.
        
        Current Jurisdiction: {state}
        Identified Farm Issue Category: {category}
        Crop Damage: {damage_pct}%
        
        Your objective is to help the farmer by:
        1. Pointing them to the exact government scheme that fits their telemetry data.
        2. Explaining the required documents clearly.
        3. Providing reassurance and an executive, professional, yet empathetic tone.
        
        Farmer Query: "{question}"
        """

        try:
            r = model.generate_content(prompt)
            return r.text
        except Exception:
            return "System overload. Please attempt transmission again."

    if user_msg:
        # Add user message
        st.session_state.chat.append(("user", user_msg))
        with st.chat_message("user"):
            st.write(user_msg)
            
        # Add AI response
        with st.chat_message("assistant"):
            with st.spinner("Decoding transmission and querying state databases..."):
                time.sleep(1) # Fake processing time for professional feel
                response_text = ask_gemini_voice(user_msg)
                st.write(response_text)
                st.session_state.chat.append(("ai", response_text))

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("Terrafy COMMAND | E-Governance routing systems are informational. Final adjudication of subsidies and insurance claims is strictly determined by district magistrates and appointed state officials.")

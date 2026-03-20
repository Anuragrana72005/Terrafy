/* ==========================================
   ⚙️ SYSTEM CONFIGURATION
   ========================================== */
const AGRIVUE_URL = "http://localhost:8501";
const GEMINI_API_KEY = "AIzaSyD6lG-dydZ_yp7aeoVc4kT96nVOYK5HiWA";
const GEMINI_MODEL = "gemini-2.5-flash";
const FLASK_BACKEND = "http://127.0.0.1:5000/";

const NEWSDATA_API_KEY = "pub_98d15e002494493f824a036a860f748a";
const NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news";

/* ==========================================
   🌐 AGRIVUE TRANSLATION ENGINE (i18n)
   ========================================== */
const translations = {
    en: {
        nav_product: "Product", nav_intel: "Intelligence", nav_method: "Methodology", nav_eco: "Ecosystem", nav_login: "Login",
        hero_badge: "Intelligence for the Elite Farmer",
        hero_title: "Climate Mastery <br><span>For Every Field</span>",
        hero_sub: "Terrafy transforms live satellite signals into high-precision decisions. Experience the prestige of data-driven farming.",
        btn_diagnosis: "Initiate Field Diagnosis", btn_assistant: "Talk to Assistant",
        hero_helper: "No login required · Results in 30 seconds",
        card_title: "Live Field Status", card_loc: "📍 Location", card_loc_val: "Mohali, Punjab",
        card_rain: "🌧 Rainfall Risk", card_risk_level: "Very Low", card_temp: "🌡 Temperature",
        card_advice_title: "EXPERT ADVICE", card_advice: "Irrigate The Crops Today",
        trust_text: "<span>Built for Bharat</span> • <span>Low-Latency Data</span> • <span>Multi-Dialect Support</span> • <span>Military-Grade Encryption</span>",
        intel_small: "DATA POINTS", intel_h2: "Beyond Weather Forecasting", intel_p: "We monitor 15+ variables to ensure elite-level accuracy.",
        metric1_h4: "NDVI Vegetation Index", metric1_p: "Monitor chlorophyll levels to detect crop stress 7 days before it's visible to the human eye.",
        metric2_h4: "Evapotranspiration", metric2_p: "Precise calculation of water loss to optimize irrigation schedules down to the liter.",
        metric3_h4: "Soil Carbon Mapping", metric3_p: "Satellite-derived insights into soil health and organic matter trends.",
        metric4_h4: "Hyperspectral Imaging", metric4_p: "Differentiating between nutrient deficiency and pest infestation using light frequency.",
        how_small: "THE PROCESS", how_h2: "The Science of Certainty",
        step1_h3: "Sense", step1_p: "Advanced satellite telemetry scans soil moisture and atmospheric pressure from orbit.",
        step2_h3: "Analyze", step2_p: "AI models cross-reference historical yields with real-time, hyperlocal climate risks.",
        step3_h3: "Advise", step3_p: "Receive executive-level recommendations directly to your mobile device, instantly.",
        eco_small: "ECOSYSTEM", eco_h2: "The Terrafy Ecosystem",
        eco_farmer_h3: "For Farmers", eco_f1: "Eliminate 20% input waste", eco_f2: "Premium local weather alerts", eco_f3: "Direct expert consultations",
        eco_fpo_h3: "Command Center for FPOs", eco_fpo_p: "Manage 1,000+ farmers from a single pane of glass. Track aggregate risk, harvest windows, and procurement logistics.",
        ui_l1: "Regional Resilience", ui_l2: "Water Stress Alerts",
        test_quote: '"Terrafy isn\'t just a tool; it\'s our digital agronomist. We\'ve seen a 15% increase in export-quality yield since integrating their satellite alerts."',
        test_cite: "— Sardar Jagjeet Singh, Progressive Farmer, Punjab",
        impact_h2: "The Terrafy Impact", impact_l1: "Fewer Irrigations", impact_l2: "Districts Secured", impact_l3: "Early Warning",
        cta_h2: "Enter the Future of Agriculture", cta_btn: "Enter TERRAFY Mode",
        foot_desc: "The Gold Standard of Climate Intelligence.",
        foot_r_title: "Resources", foot_r1: "Satellite Methodology", foot_r2: "Climate Whitepapers", foot_r3: "API Documentation",
        foot_c_title: "Company", foot_c1: "Our Vision", foot_c2: "Partnerships", foot_c3: "Contact Support",
        foot_copy: "Terrafy © 2026 • Precision Intelligence for Sustainable Growth.",
        foot_l1: "Privacy Policy", foot_l2: "Terms of Service",
        chat_btn: "Terrafy AI", chat_h1: "Terrafy Executive Assistant", chat_sub: "Real-time climate guidance",
        chat_msg: "Greetings. I am your Terrafy Assistant. How can I assist your field today?"
    },
    hi: {
        nav_product: "उत्पाद", nav_intel: "बुद्धिमत्ता", nav_method: "कार्यप्रणाली", nav_eco: "पारिस्थितिकी तंत्र", nav_login: "लॉग इन करें",
        hero_badge: "प्रगतिशील किसान के लिए बुद्धिमत्ता",
        hero_title: "जलवायु पर नियंत्रण <br><span>हर खेत के लिए</span>",
        hero_sub: "एग्रीव्यू लाइव सैटेलाइट सिग्नलों को उच्च-सटीक निर्णयों में बदलता है। डेटा-संचालित खेती की शक्ति का अनुभव करें।",
        btn_diagnosis: "फील्ड निदान प्रारंभ करें", btn_assistant: "सहायक से बात करें",
        hero_helper: "लॉगिन आवश्यक नहीं · 30 सेकंड में परिणाम",
        card_title: "लाइव फील्ड स्थिति", card_loc: "📍 स्थान", card_loc_val: "खन्ना, पंजाब",
        card_rain: "🌧 वर्षा का जोखिम", card_risk_level: "बहुत कम", card_temp: "🌡 तापमान",
        card_advice_title: "विशेषज्ञ की सलाह", card_advice: "आज फसलों की सिंचाई करें",
        trust_text: "<span>भारत के लिए निर्मित</span> • <span>तीव्र डेटा</span> • <span>बहु-भाषी समर्थन</span> • <span>सैन्य-ग्रेड सुरक्षा</span>",
        intel_small: "डेटा बिंदु", intel_h2: "मौसम पूर्वानुमान से परे", intel_p: "सटीकता सुनिश्चित करने के लिए हम 15+ चर की निगरानी करते हैं।",
        metric1_h4: "NDVI वनस्पति सूचकांक", metric1_p: "फसल के तनाव को 7 दिन पहले पहचानने के लिए क्लोरोफिल के स्तर की निगरानी करें।",
        metric2_h4: "वाष्पीकरण (Evapotranspiration)", metric2_p: "सिंचाई कार्यक्रम को अनुकूलित करने के लिए पानी की कमी की सटीक गणना।",
        metric3_h4: "मृदा कार्बन मैपिंग", metric3_p: "मिट्टी के स्वास्थ्य और जैविक पदार्थों के रुझान की सैटेलाइट अंतर्दृष्टि।",
        metric4_h4: "हाइपरस्पेक्ट्रल इमेजिंग", metric4_p: "प्रकाश आवृत्ति का उपयोग करके पोषक तत्वों की कमी और कीट संक्रमण के बीच अंतर करना।",
        how_small: "प्रक्रिया", how_h2: "निश्चितता का विज्ञान",
        step1_h3: "संवेदन (Sense)", step1_p: "उन्नत सैटेलाइट टेलीमेट्री कक्षा से मिट्टी की नमी और वायुमंडलीय दबाव को स्कैन करती है।",
        step2_h3: "विश्लेषण (Analyze)", step2_p: "एआई मॉडल वास्तविक समय के जलवायु जोखिमों के साथ ऐतिहासिक पैदावार का मिलान करते हैं।",
        step3_h3: "सलाह (Advise)", step3_p: "सीधे अपने मोबाइल डिवाइस पर तुरंत कार्यकारी स्तर की सिफारिशें प्राप्त करें।",
        eco_small: "पारिस्थितिकी तंत्र", eco_h2: "एग्रीव्यू इकोसिस्टम",
        eco_farmer_h3: "किसानों के लिए", eco_f1: "20% इनपुट बर्बादी को खत्म करें", eco_f2: "प्रीमियम स्थानीय मौसम अलर्ट", eco_f3: "विशेषज्ञों से सीधा परामर्श",
        eco_fpo_h3: "FPO के लिए कमांड सेंटर", eco_fpo_p: "एक ही स्क्रीन से 1,000+ किसानों का प्रबंधन करें। जोखिम, फसल कटाई के समय और रसद को ट्रैक करें।",
        ui_l1: "क्षेत्रीय लचीलापन", ui_l2: "जल तनाव अलर्ट",
        test_quote: '"एग्रीव्यू सिर्फ एक टूल नहीं है; यह हमारा डिजिटल एग्रोनोमिस्ट है। सैटेलाइट अलर्ट का उपयोग करने के बाद हमारी पैदावार में 15% की वृद्धि हुई है।"',
        test_cite: "— सरदार जगजीत सिंह, प्रगतिशील किसान, पंजाब",
        impact_h2: "एग्रीव्यू का प्रभाव", impact_l1: "कम सिंचाई", impact_l2: "सुरक्षित जिले", impact_l3: "प्रारंभिक चेतावनी",
        cta_h2: "कृषि के भविष्य में प्रवेश करें", cta_btn: "एग्रीव्यू मोड में प्रवेश करें",
        foot_desc: "जलवायु बुद्धिमत्ता का स्वर्ण मानक।",
        foot_r_title: "संसाधन", foot_r1: "सैटेलाइट कार्यप्रणाली", foot_r2: "जलवायु श्वेतपत्र", foot_r3: "API दस्तावेज़ीकरण",
        foot_c_title: "कंपनी", foot_c1: "हमारा दृष्टिकोण", foot_c2: "साझेदारी", foot_c3: "समर्थन से संपर्क करें",
        foot_copy: "एग्रीव्यू © 2026 • सतत विकास के लिए सटीक बुद्धिमत्ता।",
        foot_l1: "गोपनीयता नीति", foot_l2: "सेवा की शर्तें",
        chat_btn: "एग्रीव्यू AI", chat_h1: "एग्रीव्यू कार्यकारी सहायक", chat_sub: "वास्तविक समय जलवायु मार्गदर्शन",
        chat_msg: "नमस्कार। मैं आपका एग्रीव्यू सहायक हूं। आज मैं आपके खेत की क्या सहायता कर सकता हूं?"
    },
    pa: {
        nav_product: "ਉਤਪਾਦ", nav_intel: "ਖੁਫੀਆ ਜਾਣਕਾਰੀ", nav_method: "ਕਾਰਜਪ੍ਰਣਾਲੀ", nav_eco: "ਈਕੋਸਿਸਟਮ", nav_login: "ਲਾਗਇਨ",
        hero_badge: "ਅਗਾਂਹਵਧੂ ਕਿਸਾਨ ਲਈ ਖੁਫੀਆ ਜਾਣਕਾਰੀ",
        hero_title: "ਜਲਵਾਯੂ ਨਿਯੰਤਰਣ <br><span>ਹਰ ਖੇਤ ਲਈ</span>",
        hero_sub: "ਐਗਰੀਵਿਊ ਲਾਈਵ ਸੈਟੇਲਾਈਟ ਸਿਗਨਲਾਂ ਨੂੰ ਉੱਚ-ਸਟੀਕ ਫੈਸਲਿਆਂ ਵਿੱਚ ਬਦਲਦਾ ਹੈ। ਡੇਟਾ-ਸੰਚਾਲਿਤ ਖੇਤੀ ਦਾ ਅਨੁਭਵ ਕਰੋ।",
        btn_diagnosis: "ਫੀਲਡ ਨਿਦਾਨ ਸ਼ੁਰੂ ਕਰੋ", btn_assistant: "ਸਹਾਇਕ ਨਾਲ ਗੱਲ ਕਰੋ",
        hero_helper: "ਕੋਈ ਲਾਗਇਨ ਲੋੜੀਂਦਾ ਨਹੀਂ · 30 ਸਕਿੰਟਾਂ ਵਿੱਚ ਨਤੀਜੇ",
        card_title: "ਲਾਈਵ ਫੀਲਡ ਸਥਿਤੀ", card_loc: "📍 ਸਥਾਨ", card_loc_val: "ਖੰਨਾ, ਪੰਜਾਬ",
        card_rain: "🌧 ਮੀਂਹ ਦਾ ਜੋਖਮ", card_risk_level: "ਬਹੁਤ ਘੱਟ", card_temp: "🌡 ਤਾਪਮਾਨ",
        card_advice_title: "ਮਾਹਰ ਦੀ ਸਲਾਹ", card_advice: "ਅੱਜ ਫਸਲਾਂ ਦੀ ਸਿੰਚਾਈ ਕਰੋ",
        trust_text: "<span>ਭਾਰਤ ਲਈ ਬਣਾਇਆ ਗਿਆ</span> • <span>ਤੇਜ਼ ਡੇਟਾ</span> • <span>ਬਹੁ-ਭਾਸ਼ਾਈ ਸਹਾਇਤਾ</span> • <span>ਮਿਲਟਰੀ-ਗ੍ਰੇਡ ਸੁਰੱਖਿਆ</span>",
        intel_small: "ਡੇਟਾ ਪੁਆਇੰਟ", intel_h2: "ਮੌਸਮ ਦੀ ਭਵਿੱਖਬਾਣੀ ਤੋਂ ਪਰੇ", intel_p: "ਸਟੀਕਤਾ ਨੂੰ ਯਕੀਨੀ ਬਣਾਉਣ ਲਈ ਅਸੀਂ 15+ ਵੇਰੀਏਬਲਾਂ ਦੀ ਨਿਗਰਾਨੀ ਕਰਦੇ ਹਾਂ।",
        metric1_h4: "NDVI ਬਨਸਪਤੀ ਸੂਚਕਾਂਕ", metric1_p: "ਫਸਲ ਦੇ ਤਣਾਅ ਨੂੰ 7 ਦਿਨ ਪਹਿਲਾਂ ਪਛਾਣਨ ਲਈ ਕਲੋਰੋਫਿਲ ਦੇ ਪੱਧਰਾਂ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ।",
        metric2_h4: "ਵਾਸ਼ਪੀਕਰਨ (Evapotranspiration)", metric2_p: "ਸਿੰਚਾਈ ਕਾਰਜਕ੍ਰਮ ਨੂੰ ਅਨੁਕੂਲ ਬਣਾਉਣ ਲਈ ਪਾਣੀ ਦੇ ਨੁਕਸਾਨ ਦੀ ਸਹੀ ਗਣਨਾ।",
        metric3_h4: "ਮਿੱਟੀ ਕਾਰਬਨ ਮੈਪਿੰਗ", metric3_p: "ਮਿੱਟੀ ਦੀ ਸਿਹਤ ਅਤੇ ਜੈਵਿਕ ਪਦਾਰਥਾਂ ਦੇ ਰੁਝਾਨਾਂ ਦੀ ਸੈਟੇਲਾਈਟ ਸਮਝ।",
        metric4_h4: "ਹਾਈਪਰਸਪੈਕਟਰਲ ਇਮੇਜਿੰਗ", metric4_p: "ਪ੍ਰਕਾਸ਼ ਬਾਰੰਬਾਰਤਾ ਦੀ ਵਰਤੋਂ ਕਰਦੇ ਹੋਏ ਪੌਸ਼ਟਿਕ ਤੱਤਾਂ ਦੀ ਕਮੀ ਅਤੇ ਕੀੜਿਆਂ ਦੇ ਹਮਲੇ ਵਿਚਕਾਰ ਫਰਕ ਕਰਨਾ।",
        how_small: "ਪ੍ਰਕਿਰਿਆ", how_h2: "ਯਕੀਨ ਦਾ ਵਿਗਿਆਨ",
        step1_h3: "ਸੈਂਸ (Sense)", step1_p: "ਉੱਨਤ ਸੈਟੇਲਾਈਟ ਟੈਲੀਮੈਟਰੀ ਪੁਲਾੜ ਤੋਂ ਮਿੱਟੀ ਦੀ ਨਮੀ ਅਤੇ ਵਾਯੂਮੰਡਲ ਦੇ ਦਬਾਅ ਨੂੰ ਸਕੈਨ ਕਰਦੀ ਹੈ।",
        step2_h3: "ਵਿਸ਼ਲੇਸ਼ਣ (Analyze)", step2_p: "AI ਮਾਡਲ ਅਸਲ-ਸਮੇਂ ਦੇ ਜਲਵਾਯੂ ਜੋਖਮਾਂ ਦੇ ਨਾਲ ਇਤਿਹਾਸਕ ਝਾੜ ਦਾ ਮੇਲ ਕਰਦੇ ਹਨ।",
        step3_h3: "ਸਲਾਹ (Advise)", step3_p: "ਸਿੱਧੇ ਆਪਣੇ ਮੋਬਾਈਲ ਡਿਵਾਈਸ 'ਤੇ ਤੁਰੰਤ ਕਾਰਜਕਾਰੀ ਪੱਧਰ ਦੀਆਂ ਸਿਫ਼ਾਰਸ਼ਾਂ ਪ੍ਰਾਪਤ ਕਰੋ।",
        eco_small: "ਈਕੋਸਿਸਟਮ", eco_h2: "ਐਗਰੀਵਿਊ ਈਕੋਸਿਸਟਮ",
        eco_farmer_h3: "ਕਿਸਾਨਾਂ ਲਈ", eco_f1: "20% ਇਨਪੁਟ ਬਰਬਾਦੀ ਨੂੰ ਖਤਮ ਕਰੋ", eco_f2: "ਪ੍ਰੀਮੀਅਮ ਸਥਾਨਕ ਮੌਸਮ ਅਲਰਟ", eco_f3: "ਮਾਹਰਾਂ ਨਾਲ ਸਿੱਧਾ ਸਲਾਹ-ਮਸ਼ਵਰਾ",
        eco_fpo_h3: "FPO ਲਈ ਕਮਾਂਡ ਸੈਂਟਰ", eco_fpo_p: "ਇੱਕ ਸਕ੍ਰੀਨ ਤੋਂ 1,000+ ਕਿਸਾਨਾਂ ਦਾ ਪ੍ਰਬੰਧਨ ਕਰੋ। ਜੋਖਮ, ਵਾਢੀ ਦੇ ਸਮੇਂ ਅਤੇ ਲੌਜਿਸਟਿਕਸ ਨੂੰ ਟ੍ਰੈਕ ਕਰੋ।",
        ui_l1: "ਖੇਤਰੀ ਲਚਕੀਲਾਪਣ", ui_l2: "ਪਾਣੀ ਦੇ ਤਣਾਅ ਸੰਬੰਧੀ ਚੇਤਾਵਨੀਆਂ",
        test_quote: '"ਐਗਰੀਵਿਊ ਸਿਰਫ਼ ਇੱਕ ਸਾਧਨ ਨਹੀਂ ਹੈ; ਇਹ ਸਾਡਾ ਡਿਜੀਟਲ ਐਗਰੋਨੋਮਿਸਟ ਹੈ। ਸੈਟੇਲਾਈਟ ਅਲਰਟ ਦੀ ਵਰਤੋਂ ਕਰਨ ਤੋਂ ਬਾਅਦ ਸਾਡੀ ਪੈਦਾਵਾਰ ਵਿੱਚ 15% ਦਾ ਵਾਧਾ ਹੋਇਆ ਹੈ।"',
        test_cite: "— ਸਰਦਾਰ ਜਗਜੀਤ ਸਿੰਘ, ਅਗਾਂਹਵਧੂ ਕਿਸਾਨ, ਪੰਜਾਬ",
        impact_h2: "ਐਗਰੀਵਿਊ ਦਾ ਪ੍ਰਭਾਵ", impact_l1: "ਘੱਟ ਸਿੰਚਾਈ", impact_l2: "ਸੁਰੱਖਿਅਤ ਜ਼ਿਲ੍ਹੇ", impact_l3: "ਸ਼ੁਰੂਆਤੀ ਚੇਤਾਵਨੀ",
        cta_h2: "ਖੇਤੀਬਾੜੀ ਦੇ ਭਵਿੱਖ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ", cta_btn: "ਐਗਰੀਵਿਊ ਮੋਡ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ",
        foot_desc: "ਜਲਵਾਯੂ ਖੁਫੀਆ ਜਾਣਕਾਰੀ ਦਾ ਸੁਨਹਿਰੀ ਮਿਆਰ।",
        foot_r_title: "ਸਰੋਤ", foot_r1: "ਸੈਟੇਲਾਈਟ ਕਾਰਜਪ੍ਰਣਾਲੀ", foot_r2: "ਜਲਵਾਯੂ ਵ੍ਹਾਈਟਪੇਪਰ", foot_r3: "API ਦਸਤਾਵੇਜ਼",
        foot_c_title: "ਕੰਪਨੀ", foot_c1: "ਸਾਡਾ ਦ੍ਰਿਸ਼ਟੀਕੋਣ", foot_c2: "ਭਾਈਵਾਲੀ", foot_c3: "ਸਹਾਇਤਾ ਨਾਲ ਸੰਪਰਕ ਕਰੋ",
        foot_copy: "ਐਗਰੀਵਿਊ © 2026 • ਟਿਕਾਊ ਵਿਕਾਸ ਲਈ ਸਟੀਕ ਖੁਫੀਆ ਜਾਣਕਾਰੀ।",
        foot_l1: "ਗੋਪਨੀਯਤਾ ਨੀਤੀ", foot_l2: "ਸੇਵਾ ਦੀਆਂ ਸ਼ਰਤਾਂ",
        chat_btn: "ਐਗਰੀਵਿਊ AI", chat_h1: "ਐਗਰੀਵਿਊ ਕਾਰਜਕਾਰੀ ਸਹਾਇਕ", chat_sub: "ਅਸਲ-ਸਮੇਂ ਜਲਵਾਯੂ ਮਾਰਗਦਰਸ਼ਨ",
        chat_msg: "ਨਮਸਕਾਰ। ਮੈਂ ਤੁਹਾਡਾ ਐਗਰੀਵਿਊ ਸਹਾਇਕ ਹਾਂ। ਅੱਜ ਮੈਂ ਤੁਹਾਡੇ ਖੇਤ ਦੀ ਕੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?"
    }
};

// Core Translation Function
function changeLanguage(langCode) {
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[langCode] && translations[langCode][key]) {
            el.innerHTML = translations[langCode][key];
        }
    });

    localStorage.setItem('agrivue_lang', langCode);
}

// Auto-load preferred language & Welcome message on startup
document.addEventListener('DOMContentLoaded', () => {
    // 1. Language Load
    const savedLang = localStorage.getItem('agrivue_lang') || 'en';
    changeLanguage(savedLang);

    // 2. User Welcome Message Load
    const user = localStorage.getItem("agrivueUser");
    const welcome = document.getElementById("welcomeUser");
    if (user && welcome) {
        welcome.innerHTML = "Welcome back, " + user + " 👋";
    }
});


/* ==========================================
   🚀 CORE NAVIGATION & SCAN LAUNCHER
   ========================================== */
function openAgriVue() {
    window.open(AGRIVUE_URL, "_blank");
}

function startScan() {
    const btn = document.querySelector(".btn-primary");
    if (!btn) return;

    btn.innerText = "Analyzing signals...";
    btn.disabled = true;

    setTimeout(() => {
        openAgriVue();
        btn.innerText = "Start Free Climate Scan";
        btn.disabled = false;
    }, 1200);
}

/* ==========================================
   🖱️ UI: STICKY NAVBAR & SCROLL SPY
   ========================================== */
const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
    if (!navbar) return;
    navbar.classList.toggle("scrolled", window.scrollY > 20);
});

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {
    let current = "";

    sections.forEach(section => {
        const top = section.offsetTop - 140;
        if (window.scrollY >= top) current = section.id;
    });

    navLinks.forEach(link => {
        link.classList.toggle(
            "active",
            link.getAttribute("href") === "#" + current
        );
    });
});

/* ==========================================
   📊 UI: COUNT-UP ANIMATIONS
   ========================================== */
const counters = document.querySelectorAll(".count");
let counted = false;

function runCounters() {
    if (counted) return;

    counters.forEach(counter => {
        const target = Number(counter.dataset.target || "0");
        let current = 0;
        const step = Math.max(1, target / 40);

        const update = () => {
            current += step;

            if (current < target) {
                counter.innerText = Math.floor(current);
                requestAnimationFrame(update);
            } else {
                counter.innerText = target;
            }
        };

        update();
    });

    counted = true;
}

const impactSection = document.getElementById("impact");

window.addEventListener("scroll", () => {
    if (!impactSection) return;

    const top = impactSection.getBoundingClientRect().top;
    if (top < window.innerHeight * 0.75) {
        runCounters();
    }
});

/* ==========================================
   ✨ UI: INTERSECTION OBSERVER ANIMATIONS
   ========================================== */
const animatedBlocks = document.querySelectorAll(".section, .impact-row, .impact-cards");

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in-view");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15 }
    );

    animatedBlocks.forEach(el => observer.observe(el));
} else {
    animatedBlocks.forEach(el => el.classList.add("in-view"));
}

/* ==========================================
   🔐 USER AUTHENTICATION
   ========================================== */
function loginUser() {
    const name = document.getElementById("username")?.value;
    const pass = document.getElementById("password")?.value;

    if (!name || !pass) {
        alert("Please enter name and password");
        return;
    }

    localStorage.setItem("agrivueUser", name);
    localStorage.setItem("agrivuePass", pass);

    window.location.href = FLASK_BACKEND;
}

/* ==========================================
   🤖 AGRIVUE AI CHATBOT ENGINE
   ========================================== */
const chatLauncher = document.getElementById("chatLauncher");
const chatPanel = document.getElementById("chatPanel");
const chatClose = document.getElementById("chatClose");
const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");

function openChat() {
    if (chatPanel) {
        chatPanel.style.display = 'flex';
        if (chatLauncher) chatLauncher.style.display = 'none';
    }
}

function closeChat() {
    if (chatPanel) {
        chatPanel.style.display = 'none';
        if (chatLauncher) chatLauncher.style.display = 'flex';
    }
}

if (chatLauncher) chatLauncher.addEventListener("click", openChat);
if (chatClose) chatClose.addEventListener("click", closeChat);

function appendMessage(text, sender = "bot") {
    if (!chatBody) return;

    const msg = document.createElement("div");
    msg.className = "msg " + (sender === "user" ? "msg-user" : "msg-bot");

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.innerHTML = text.replace(/\n/g, "<br>");

    msg.appendChild(bubble);
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendToGemini(prompt) {
    if (!GEMINI_API_KEY) {
        throw new Error("Missing Gemini API key");
    }

    const sysPrompt =
        "You are TERRAFY AI, an agriculture assistant for Indian farmers. " +
        "Answer briefly in 2–4 sentences. Be practical and simple.";

    const body = {
        contents: [
            {
                role: "user",
                parts: [{ text: sysPrompt + "\n\nFarmer: " + prompt }]
            }
        ],
        generationConfig: {
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 256
        }
    };

    const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }
    );

    if (!res.ok) throw new Error("Gemini API error");

    const data = await res.json();
    return (
        data?.candidates?.[0]?.content?.parts?.[0]?.text ||
        "I could not generate a response right now."
    );
}

async function fetchAgriNews(query) {
    if (!NEWSDATA_API_KEY) {
        return "News service not configured.";
    }

    try {
        const agriQuery = "agriculture OR farming OR crops OR farmer OR mandi OR wheat OR rice India";
        const originalURL = `${NEWSDATA_BASE_URL}?apikey=${NEWSDATA_API_KEY}&q=${encodeURIComponent(agriQuery)}&country=in&language=en`;

        // Proxy to fix CORS issues
        const proxyURL = `https://api.allorigins.win/raw?url=${encodeURIComponent(originalURL)}`;

        const res = await fetch(proxyURL);

        if (!res.ok) throw new Error("News API failed");

        const data = await res.json();

        if (!data.results || data.results.length === 0) {
            return "No agriculture news found from India right now.";
        }

        const filtered = data.results.filter(article => {
            const text = ((article.title || "") + " " + (article.description || "")).toLowerCase();
            return (
                text.includes("agri") ||
                text.includes("farm") ||
                text.includes("crop") ||
                text.includes("farmer") ||
                text.includes("mandi") ||
                text.includes("wheat") ||
                text.includes("rice")
            );
        });

        const finalNews = filtered.length > 0 ? filtered : data.results;
        const topNews = finalNews.slice(0, 3);

        let newsText = "🇮🇳 <strong>Latest Agriculture News in India:</strong>\n\n";

        topNews.forEach((article, index) => {
            newsText += `${index + 1}. <a href="${article.link}" target="_blank" style="color:var(--gold-primary); text-decoration:underline;">${article.title}</a>\n`;
        });

        return newsText;

    } catch (error) {
        console.error("News API Error:", error);
        return await sendToGemini("Give me latest agriculture news updates in India.");
    }
}

async function handleSend() {
    if (!chatInput) return;

    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    chatInput.value = "";

    const typing = document.createElement("div");
    typing.className = "msg msg-bot chat-typing";
    typing.innerHTML = '<div class="msg-bubble">TERRAFY AI is thinking…</div>';
    chatBody.appendChild(typing);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        let reply;
        const lowerText = text.toLowerCase();

        if (
            lowerText.includes("news") ||
            lowerText.includes("update") ||
            lowerText.includes("latest") ||
            lowerText.includes("market")
        ) {
            reply = await fetchAgriNews(text);
        } else {
            reply = await sendToGemini(text);
        }

        chatBody.removeChild(typing);
        appendMessage(reply, "bot");

    } catch (e) {
        chatBody.removeChild(typing);
        appendMessage("Sorry, Terrafy AI is not available right now.", "bot");
    }
}

if (chatSend) chatSend.addEventListener("click", handleSend);

if (chatInput) {
    chatInput.addEventListener("keydown", e => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
        }
    });
}
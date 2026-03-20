from flask import Flask, request, send_file
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import json
import os
import logging

# ==========================================
# ⚙️ SYSTEM CONFIGURATION
# ==========================================
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [AGRIVUE WEBHOOK] - %(message)s")

# ⚠️ Gemini Initialization for WhatsApp AI Chat
API_KEY = "AIzaSyC3KJotknWSN2_gYCL2wI_nCzgSehtM648"
genai.configure(api_key=API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================================
# 📂 DIRECTORY & DATABASE SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

DB_FILE = os.path.join(BASE_DIR, "farmers.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==========================================
# 🔊 AUDIO SERVING (TWILIO ENDPOINT)
# ==========================================
@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serves the generated OGG files directly to Twilio's servers."""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        logging.error(f"Audio payload not found: {filename}")
        return "Audio not found", 404

    logging.info(f"Serving audio payload to Twilio: {filename}")
    return send_file(file_path, mimetype="audio/ogg")

# ==========================================
# 🧠 AI CONVERSATION ENGINE
# ==========================================
def ask_agrivue_ai(query, language):
    """Generates an expert agricultural response in the farmer's native language."""
    prompt = f"""
    You are the AgriVue WhatsApp AI Assistant, an elite agricultural expert advising an Indian farmer.
    The farmer is asking: "{query}"
    
    Rules:
    1. Reply ONLY in {language}.
    2. Keep it under 3 short paragraphs (WhatsApp friendly).
    3. Use formatting like *bold* and bullet points.
    4. Be highly practical, scientific, and respectful.
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"AI Generation Failed: {e}")
        return f"⚠️ AgriVue Neural Engine is currently offline. Please try again later."

# ==========================================
# 📲 WHATSAPP WEBHOOK (MAIN LOGIC)
# ==========================================
@app.route("/whatsapp", methods=["POST", "GET"])
def whatsapp_reply():
    """Handles all incoming messages from farmers."""
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "Unknown")

    logging.info(f"Incoming transmission from {from_number}: {incoming_msg}")

    db = load_db()
    user_lang = db.get(from_number, "English") # Default to English
    
    resp = MessagingResponse()
    msg = resp.message()

    # --- COMMAND: START / HELP ---
    if incoming_msg.upper() in ["START", "HELP", "MENU", "HI", "HELLO"]:
        msg.body(
            "🌍 *WELCOME TO TERRAFY COMMAND*\n"
            "_Next-Gen Farm Intelligence_\n\n"
            "Please configure your preferred alert language by replying with a number:\n\n"
            "1️⃣ English\n"
            "2️⃣ हिंदी (Hindi)\n"
            "3️⃣ ਪੰਜਾਬੀ (Punjabi)\n"
            "4️⃣ मराठी (Marathi)\n"
            "5️⃣ தமிழ் (Tamil)\n"
            "6️⃣ తెలుగు (Telugu)\n\n"
            "💡 *Tip:* You can also type any farming question directly into this chat to speak with our AI Agronomist!"
        )
        return str(resp)

    # --- COMMAND: LANGUAGE SELECTION ---
    language_map = {
        "1": "English", "2": "Hindi", "3": "Punjabi", 
        "4": "Marathi", "5": "Tamil", "6": "Telugu"
    }
    
    if incoming_msg in language_map:
        selected_language = language_map[incoming_msg]
        db[from_number] = selected_language
        save_db(db)

        msg.body(
            f"✅ *Language Configuration Secured*\n\n"
            f"Your alerts and AI responses are now set to: *{selected_language}*.\n\n"
            f"You will automatically receive early-warning threat alerts here. Feel free to ask me any farming questions!"
        )
        return str(resp)
        
    # --- COMMAND: STATUS ---
    if incoming_msg.upper() == "STATUS":
        msg.body(
            f"🛡️ *AGRIVUE SYSTEM STATUS*\n\n"
            f"📱 Number: {from_number}\n"
            f"🗣️ Language: {user_lang}\n"
            f"📡 Alert Uplink: ACTIVE\n\n"
            f"We are monitoring your farm telemetry 24/7."
        )
        return str(resp)

    # --- KILLER FEATURE: AI CHAT FALLBACK ---
    # If the message isn't a menu command, pass it to the AgriVue Gemini Engine!
    logging.info(f"Routing query to AI Engine in {user_lang}...")
    ai_answer = ask_agrivue_ai(incoming_msg, user_lang)
    
    msg.body(ai_answer)
    return str(resp)

# ==========================================
# 🚀 SERVER LAUNCH
# ==========================================
if __name__ == "__main__":
    print("===================================================")
    print("🛡️ AGRIVUE WHATSAPP WEBHOOK ACTIVE ON PORT 5000")
    print("⚠️ Ensure Ngrok is running: ngrok http 5000")
    print("===================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
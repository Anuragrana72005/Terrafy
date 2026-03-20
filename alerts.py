from twilio.rest import Client
from translator import translate_text
from voice import generate_voice
import json
import os
import time
import subprocess

# ---------------- TWILIO CONFIG ----------------
TWILIO_SID = "Af"
TWILIO_TOKEN = ""

TWILIO_WHATSAPP = "whatsapp:+6"
YOUR_NUMBER = "whatsapp:+"

# 🔴 MUST MATCH RUNNING NGROK URL
NGROK_BASE_URL = "https://convectional-monte-alarmedly.ngrok-free.dev"

client = Client(TWILIO_SID, TWILIO_TOKEN)

DB_FILE = "farmers.json"
BASE_DIR = os.path.dirname(__file__)
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

# ---------------- HELPERS ----------------
def normalize_whatsapp_number(number):
    if number.startswith("whatsapp:"):
        return number
    return f"whatsapp:{number}"

def get_farmer_language(phone):
    try:
        if not os.path.exists(DB_FILE):
            return "English"
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(phone, "English")
    except Exception:
        return "English"

# ---------------- MP3 → OGG (WHATSAPP FIX) ----------------
def convert_to_whatsapp_voice(mp3_file):
    ogg_file = mp3_file.replace(".mp3", ".ogg")

    mp3_path = os.path.join(AUDIO_DIR, mp3_file)
    ogg_path = os.path.join(AUDIO_DIR, ogg_file)

    command = [
        "ffmpeg",
        "-y",
        "-i", mp3_path,
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "libopus",
        ogg_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return ogg_file

# ---------------- ALERT ENGINE ----------------
def monitor_and_alert(node_name, data):
    """
    data: dict (already parsed JSON from app.py)
    Sends WhatsApp TEXT + VOICE alert
    """

    try:
        print("🔥 ALERT ENGINE HIT")
        print("Node:", node_name)
        print("Data:", data)

        alert_msg = None

        # 🌧️ RAIN ALERT
        if str(data.get("rain_prob", "")).lower() == "high":
            alert_msg = (
                f"*AGRIVUE COMMAND CENTER*\n"
                f"_Live Telemetry Update_\n\n"
                f"🌧️ *PRECIPITATION ALERT*\n"
                f"*Location:* {node_name}\n"
                f"*Status:* Heavy rain forecasted\n"
                f"*Details:* {data.get('summary', 'N/A')}\n\n"
                f"⚠️ _Action Required: Initiate harvest/protection protocols._"
            )

        # 🌬️ WIND ALERT
        elif str(data.get("wind_speed", "")).lower() == "strong":
            alert_msg = (
                f"*AGRIVUE COMMAND CENTER*\n"
                f"_Live Telemetry Update_\n\n"
                f"🌬️ *SEVERE WIND ALERT*\n"
                f"*Location:* {node_name}\n"
                f"*Status:* High turbulence detected\n"
                f"*Details:* {data.get('summary', 'N/A')}\n\n"
                f"⚠️ _Action Required: Suspend chemical spraying immediately._"
            )

        # 🌱 SOIL ALERT
        elif float(data.get("moisture_pct", 100)) <= 25:
            alert_msg = (
                f"*AGRIVUE COMMAND CENTER*\n"
                f"_Live Telemetry Update_\n\n"
                f"🚨 *MOISTURE DEFICIT ALERT*\n"
                f"*Location:* {node_name}\n"
                f"*Soil Moisture:* {data.get('moisture_pct')}%\n"
                f"*Health Index:* {data.get('health_index', 'N/A')}/10\n\n"
                f"⚠️ _Action Required: Initiate immediate irrigation._"
            )

        if not alert_msg:
            print("ℹ️ No alert condition met")
            return False

        # ---------------- LANGUAGE ----------------
        to_number = normalize_whatsapp_number(YOUR_NUMBER)
        language = get_farmer_language(to_number)

        print("🌍 Language selected:", language)

        # Translate the message (Markdown should be preserved by most translation APIs)
        localized_msg = translate_text(alert_msg, language)

        # ================== SEND TEXT ==================
        print("📤 Sending WhatsApp TEXT")

        text_msg = client.messages.create(
            body=localized_msg,
            from_=TWILIO_WHATSAPP,
            to=to_number
        )

        print("✅ WhatsApp TEXT sent | SID:", text_msg.sid)

        # ================== SEND VOICE ==================
               # ================== SEND VOICE ==================
        try:
            print("🎧 Generating voice (MP3)")

            clean_voice_text = localized_msg.replace('*', '').replace('_', '')

            mp3_file = generate_voice(clean_voice_text, language)

            print("🔁 Converting to WhatsApp OGG")
            ogg_file = convert_to_whatsapp_voice(mp3_file)

            voice_url = f"{NGROK_BASE_URL}/audio/{ogg_file}"

            time.sleep(1)

            print("🎙 Sending WhatsApp VOICE:", voice_url)

            voice_msg = client.messages.create(
                from_=TWILIO_WHATSAPP,
                to=to_number,
                media_url=[voice_url]
            )

            print("🎉 WhatsApp VOICE sent | SID:", voice_msg.sid)

        except Exception as ve:
            print("⚠️ Voice failed but TEXT already delivered:", ve)

    except Exception as e:
        print("❌ ALERT ENGINE ERROR:", e)
        return False

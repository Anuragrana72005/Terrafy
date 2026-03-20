from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import edge_tts
import asyncio
import base64
import os
import uuid
from datetime import datetime

# 🔐 Put this in environment variable in production
OPENROUTER_API_KEY = "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"

app = Flask(__name__)
CORS(app)

# ----------------------------
# SERVE FRONTEND
# ----------------------------
@app.route("/")
def home():
    return send_from_directory("../landing", "Kisan.html")

@app.route("/<path:filename>")
def serve_files(filename):
    return send_from_directory("../landing", filename)

# ----------------------------
# SMART LOCAL INTENT HANDLING
# ----------------------------
def handle_local_intents(question, language):
    q = question.lower()

    # Date intent
    if "date" in q or "today" in q:
        today = datetime.now().strftime("%d %B %Y")
        return f"📅 Today's date is {today}."

    # Basic price format intent
    if "price" in q or "rate" in q:
        return None  # Let AI handle structured pricing

    return None


# ----------------------------
# AI ROUTE
# ----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()
    language = data.get("language", "English")

    if not question:
        return jsonify({"answer": "Please ask something."}), 400

    # 🔹 First check local intent (fast response)
    local_reply = handle_local_intents(question, language)
    if local_reply:
        return jsonify({"answer": local_reply, "audio": None})

    # ----------------------------
    # PREMIUM PROMPT ENGINEERING
    # ----------------------------
    system_prompt = f"""
You are Kisan Mitra – India's Smart Agricultural AI Assistant.

Rules:
- Reply only in {language}
- Use clean structured format
- Use emojis carefully
- Farmer-friendly language
- No markdown
- No repetition
- Give price, trend, advice when relevant
- Keep response professional but simple

If user asks crop price:
Format like:

Crop: <name>
Price Range: ₹xx – ₹xx per kg
Market Trend: Stable/Rising/Falling
Updated: <today date>

Advice: Short practical advice.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:5000",
        "X-Title": "Kisan Mitra App"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.4,
        "max_tokens": 350
    }

    # ----------------------------
    # CALL OPENROUTER
    # ----------------------------
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        if response.status_code != 200:
            print("OpenRouter Error:", response.text)
            return jsonify({
                "answer": "⚠️ Unable to fetch market data. Please try again shortly.",
                "audio": None
            }), 500

        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("Server Error:", e)
        return jsonify({
            "answer": "⚠️ Server is temporarily unavailable. Please try again.",
            "audio": None
        }), 500

    # ----------------------------
    # TEXT TO SPEECH
    # ----------------------------
    voice = "hi-IN-MadhurNeural" if language.lower() == "hindi" else "en-IN-PrabhatNeural"
    unique_filename = f"audio_{uuid.uuid4().hex}.mp3"

    async def generate_audio():
        communicate = edge_tts.Communicate(text=answer, voice=voice)
        await communicate.save(unique_filename)

    audio_base64 = None

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_audio())
        loop.close()

        if os.path.exists(unique_filename):
            with open(unique_filename, "rb") as f:
                audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    except Exception as e:
        print("TTS Error:", e)

    finally:
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

    return jsonify({
        "answer": answer,
        "audio": audio_base64
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
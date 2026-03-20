import uuid
import os
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Punjabi": "pa",
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te"
}

def generate_voice(text, language="English"):

    # Prevent empty text error
    if not text or not text.strip():
        print("No text provided for voice generation.")
        return None

    filename = f"voice_{uuid.uuid4().hex}.mp3"
    path = os.path.join(AUDIO_DIR, filename)

    # Get language code safely
    lang_code = LANG_MAP.get(language, "en")

    try:
        # Generate voice (faster response)
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(path)

        print("VOICE GENERATED:", path)
        return filename

    except Exception as e:
        print("Error generating voice:", e)
        return None
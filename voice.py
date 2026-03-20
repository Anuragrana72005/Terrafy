import uuid
import os
import asyncio
import edge_tts

# ==========================================
# ⚙️ DIRECTORY CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ==========================================
# 🎙️ NEURAL VOICE MAPPING (INDIAN ACCENTS)
# ==========================================
# These are premium Microsoft Azure Neural Voices.
# They sound 100% human, with natural breathing and intonation.
LANG_MAP = {
    "English": "en-IN-NeerjaNeural",  # Indian English (Professional Female)
    "Hindi": "hi-IN-SwaraNeural",     # Hindi (Clear Female)
    "Punjabi": "pa-IN-OjasNeural",    # Punjabi (Authoritative Male)
    "Marathi": "mr-IN-AarohiNeural",  # Marathi (Female)
    "Tamil": "ta-IN-PallaviNeural",   # Tamil (Female)
    "Telugu": "te-IN-ShrutiNeural"    # Telugu (Female)
}

# ==========================================
# 🧠 ASYNC AUDIO GENERATION
# ==========================================
async def _generate_voice_async(text, voice, path):
    """Core async function to communicate with Edge Neural TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def generate_voice(text, language="English"):
    """
    Synchronous wrapper so this easily plugs into your existing alerts.py 
    without breaking your code.
    """
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    path = os.path.join(AUDIO_DIR, filename)
    
    # Fallback to English if language is missing
    voice_model = LANG_MAP.get(language, "en-IN-NeerjaNeural")
    
    # Run the async process
    asyncio.run(_generate_voice_async(text, voice_model, path))
    
    print(f"🎙️ [AGRIVUE NEURAL TTS] Voice generated successfully: {filename}")
    return filename
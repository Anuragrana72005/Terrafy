from google import genai

API_KEY = "AIzaSyDnmo_o4zrFdc5wLzjFblyVohw2RZQFfH0"
client = genai.Client(api_key=API_KEY)

def translate_text(text, language):
    # Safe translation stub (no Gemini)
    # You can add real translation later
    return text


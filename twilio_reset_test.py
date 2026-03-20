from twilio.rest import Client

SID = "f"
TOKEN = "d892ee"   # copy fresh from Twilio console

client = Client(SID, TOKEN)

msg = client.messages.create(
    from_="whatsapp:+14",
    to="whatsapp:+91",
    body="✅ AGRIVUE RESET TEST – THIS MUST ARRIVE"
)

print("SID:", msg.sid)

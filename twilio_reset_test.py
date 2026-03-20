from twilio.rest import Client

SID = "AC5fc5c6ad85fb57f5318b0fd5c537d8ff"
TOKEN = "d8964469bce90324a2e5760a26af72ee"   # copy fresh from Twilio console

client = Client(SID, TOKEN)

msg = client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+918872862277",
    body="✅ AGRIVUE RESET TEST – THIS MUST ARRIVE"
)

print("SID:", msg.sid)

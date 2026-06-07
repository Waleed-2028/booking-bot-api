from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
import httpx
import os
import json

load_dotenv()

from bot import get_reply
from sheets import save_booking

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def load_clients() -> dict:
    with open("clients.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params["hub.challenge"])
    return Response(status_code=403)

@app.post("/webhook")
async def receive(request: Request):
    body = await request.json()
    try:
        entry    = body["entry"][0]
        changes  = entry["changes"][0]["value"]
        phone_id = changes["metadata"]["phone_number_id"]
        message  = changes["messages"][0]
        user_id  = message["from"]
        if message.get("type") != "text":
            return {"status": "ok"}
        user_text = message["text"]["body"]
        clients = load_clients()
        client  = clients.get(phone_id)
        if not client:
            return {"status": "unknown_client"}
        reply, booking = get_reply(phone_id, user_id, user_text, client)
        if booking:
            booking["phone"] = user_id
            booking_id = save_booking(client["spreadsheet_id"], booking)
            reply += f"\n\n🆔 رقم حجزك: {booking_id}"
        await send_message(client["wa_token"], phone_id, user_id, reply)
    except (KeyError, IndexError):
        pass
    return {"status": "ok"}

async def send_message(token: str, phone_id: str, to: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    async with httpx.AsyncClient() as client:
        await client.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text}
            }
        )
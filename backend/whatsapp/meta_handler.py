import requests
import os

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")

def send_whatsapp_message(to, message):
    """Send WhatsApp message via Meta Cloud API"""
    if not META_TOKEN or not PHONE_NUMBER_ID:
        raise ValueError("Meta API credentials not set in .env")

    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

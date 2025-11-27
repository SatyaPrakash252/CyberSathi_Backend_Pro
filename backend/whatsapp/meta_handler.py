import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")


# -------------------------------------------------------
# 🚔 NEW: Get nearest police station by user location
# -------------------------------------------------------
def get_nearest_police_station(user_location: str):
    """
    Return nearest police station phone number and name based on user location keyword.
    """
    location_map = {
        "bhubaneswar": {"name": "Bhubaneswar Police Station", "phone": "+916742537777"},
        "cuttack": {"name": "Cuttack Police Station", "phone": "+916712334455"},
        "puri": {"name": "Puri Police Station", "phone": "+916752888777"},
        "rourkela": {"name": "Rourkela Police Station", "phone": "+916616778899"},
        "sambalpur": {"name": "Sambalpur Police Station", "phone": "+916633224466"},
    }

    key = user_location.strip().lower()
    for city in location_map:
        if city in key:
            return location_map[city]
    return {"name": "Local Police Station", "phone": "+91100"}  # fallback if no match


# -------------------------------------------------------
# 💬 Send WhatsApp message
# -------------------------------------------------------
def send_whatsapp_message(to, message):
    """
    Sends a WhatsApp message via Meta Cloud API
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        print("❌ Missing WhatsApp credentials in .env file")
        return

    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": message}
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"📤 Sent to {to}: {message}")
    print(f"Meta Response: {response.status_code} - {response.text}")

    if response.status_code != 200:
        print("⚠️ Failed to send message. Check token or phone ID.")


# -------------------------------------------------------
# 📥 Download media from WhatsApp
# -------------------------------------------------------
def download_media(media_id, file_path="downloads"):
    """
    Downloads a media file from WhatsApp servers and saves it locally.
    """
    try:
        os.makedirs(file_path, exist_ok=True)

        # Step 1: Get the media URL
        url = f"https://graph.facebook.com/v20.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("⚠️ Could not fetch media URL:", response.text)
            return None

        media_url = response.json().get("url")

        # Step 2: Download actual file
        response = requests.get(media_url, headers=headers)
        if response.status_code != 200:
            print("⚠️ Media download failed:", response.text)
            return None

        file_name = f"{file_path}/{media_id}.jpg"
        with open(file_name, "wb") as f:
            f.write(response.content)

        print(f"✅ Media saved to {file_name}")
        return file_name

    except Exception as e:
        print("❌ Error in download_media:", str(e))
        return None

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from backend.init_db import SessionLocal
from backend.models import Complaint
from backend.whatsapp.meta_handler import send_whatsapp_message, download_media, get_nearest_police_station
from uuid import uuid4
import re, os
from backend.utils.grievance_links import get_grievance_link

router = APIRouter()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "cybersathi_verify")
sessions = {}  # Temporary memory for user chat progress

# ---------------- Validation Helpers ----------------
def validate_email(email): return re.match(r"[^@]+@[^@]+\.[^@]+", email)
def validate_phone(phone): return re.match(r"^\+?\d{10,13}$", phone)
def validate_dob(dob): return re.match(r"^\d{2}-\d{2}-\d{4}$", dob)
def validate_pin(pin): return re.match(r"^\d{6}$", pin)
def generate_ticket(): return f"CYB-{str(uuid4())[:8].upper()}"

# ---------------- Webhook Verification ----------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook Verified Successfully!")
        return PlainTextResponse(content=challenge)
    else:
        print("❌ Webhook Verification Failed.")
        return JSONResponse({"error": "Verification failed"}, status_code=403)

# ---------------- Message Handling ----------------
@router.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    db = SessionLocal()

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]["value"]
        message_obj = change["messages"][0]
        sender = message_obj["from"]

        # Detect message type (text / image / document)
        msg_type = message_obj.get("type", "text")
        text = ""
        media_file_path = None

        if msg_type == "text":
            text = message_obj["text"]["body"].strip()
        elif msg_type == "image":
            media_id = message_obj["image"]["id"]
            media_file_path = download_media(media_id, "image")
            text = "[image uploaded]"
        elif msg_type == "document":
            media_id = message_obj["document"]["id"]
            media_file_path = download_media(media_id, "document")
            text = "[document uploaded]"
        else:
            print("⚠️ Unsupported message type:", msg_type)
            return {"status": "unsupported"}

    except Exception as e:
        print("⚠️ Webhook received non-message payload:", e)
        return {"status": "ignored"}

    # ---- New user greeting ----
    if sender not in sessions:
        sessions[sender] = {"stage": "menu"}
        send_whatsapp_message(sender,
            "👋 *Welcome to CyberSathi!* 🚔\n\n"
            "Choose an option:\n"
            "A️⃣ Register New Complaint\n"
            "B️⃣ Check Complaint Status\n"
            "C️⃣ Account Unfreeze Request\n"
            "D️⃣ Other Queries"
        )
        return {"status": "menu sent"}

    user = sessions[sender]

    # ---- Menu ----
    if user["stage"] == "menu":
        choice = text.lower()
        if choice == "a":
            user["stage"] = "name"
            send_whatsapp_message(sender, "Please enter your *Full Name*:")
        elif choice == "b":
            user["stage"] = "status"
            send_whatsapp_message(sender, "Enter your *Phone Number* or *Ticket Number* to check status:")
        elif choice == "c":
            user["stage"] = "unfreeze"
            send_whatsapp_message(sender, "Enter your *Account Number or UPI ID* for unfreeze request:")
        else:
            send_whatsapp_message(sender, "❌ Invalid option. Please type A, B, or C.")
        return {"status": "menu received"}

    # ---------------- Complaint Registration Flow ----------------
    if user["stage"] == "name":
        user["name"] = text
        user["stage"] = "father"
        send_whatsapp_message(sender, "Enter your *Father/Spouse/Guardian Name*:")

    elif user["stage"] == "father":
        user["father_name"] = text
        user["stage"] = "dob"
        send_whatsapp_message(sender, "Enter your *Date of Birth (DD-MM-YYYY)*:")

    elif user["stage"] == "dob":
        if not validate_dob(text):
            send_whatsapp_message(sender, "⚠️ Invalid format. Please use DD-MM-YYYY.")
            return {"status": "retry"}
        user["dob"] = text
        user["stage"] = "phone"
        send_whatsapp_message(sender, "Enter your *Phone Number* (+91XXXXXXXXXX):")

    elif user["stage"] == "phone":
        if not validate_phone(text):
            send_whatsapp_message(sender, "⚠️ Invalid number. Please re-enter (+91XXXXXXXXXX):")
            return {"status": "retry"}
        user["phone"] = text
        user["stage"] = "email"
        send_whatsapp_message(sender, "Enter your *Email ID*:")

    elif user["stage"] == "email":
        if not validate_email(text):
            send_whatsapp_message(sender, "⚠️ Invalid email. Please re-enter:")
            return {"status": "retry"}
        user["email"] = text
        user["stage"] = "village"
        send_whatsapp_message(sender, "Enter your *Village Name*:")

    elif user["stage"] == "village":
        user["village"] = text
        user["stage"] = "post_office"
        send_whatsapp_message(sender, "Enter your *Post Office Name*:")

    elif user["stage"] == "post_office":
        user["post_office"] = text
        user["stage"] = "police_station"
        send_whatsapp_message(sender, "Enter your *Nearest Police Station*:")

    elif user["stage"] == "police_station":
        user["police_station"] = text
        user["stage"] = "district"
        send_whatsapp_message(sender, "Enter your *District Name*:")

    elif user["stage"] == "district":
        user["district"] = text
        user["stage"] = "pincode"
        send_whatsapp_message(sender, "Enter your *PIN Code (6 digits)*:")

    elif user["stage"] == "pincode":
        if not validate_pin(text):
            send_whatsapp_message(sender, "⚠️ Invalid PIN. Please enter a 6-digit number:")
            return {"status": "retry"}
        user["pincode"] = text
        user["stage"] = "fraud"
        send_whatsapp_message(sender,
            "Select Fraud Type:\n"
            "1️⃣ UPI / Banking\n"
            "2️⃣ Social Media\n"
            "3️⃣ Job / Loan App\n"
            "4️⃣ Other"
        )

    elif user["stage"] == "fraud":
        mapping = {"1": "UPI/Banking", "2": "Social Media", "3": "Job/Loan App", "4": "Other"}
        user["fraud"] = mapping.get(text, "Other")
        user["stage"] = "desc"
        send_whatsapp_message(sender,
            "Please describe your issue briefly and upload any related *screenshots, PDFs, or Aadhaar* if available."
        )

    elif user["stage"] == "desc":
        user["desc"] = text
        ticket = generate_ticket()

        complaint = Complaint(
            ticket_number=ticket,
            name=user["name"],
            father_name=user["father_name"],
            dob=user["dob"],
            phone=user["phone"],
            email=user["email"],
            village=user["village"],
            post_office=user["post_office"],
            police_station=user["police_station"],
            district=user["district"],
            pincode=user["pincode"],
            fraud_type=user["fraud"],
            description=text,
            media_files=media_file_path,
            status="Registered"
        )
        db.add(complaint)
        db.commit()

        # ✅ Send confirmation
        send_whatsapp_message(sender,
            f"✅ *Complaint Registered Successfully!*\n\n"
            f"🆔 Ticket No: *{ticket}*\n"
            "Keep this safe for future status checks (Option B)."
        )

        # 🚓 NEW: Add nearest police station call info
        station_info = get_nearest_police_station(user["police_station"])
        station_msg = (
            f"📍 Based on your location, your nearest police station is:\n"
            f"*{station_info['name']}*\n\n"
            f"📞 Call Now: {station_info['phone']}\n\n"
            f"Stay alert and do not share OTP or banking details with anyone. 🚔"
        )
        send_whatsapp_message(sender, station_msg)

        # Suggest grievance portal link
        link_message = get_grievance_link(user["fraud"] + " " + user["desc"])
        send_whatsapp_message(sender, f"📎 You may also visit this link for direct help:\n{link_message}")

        sessions.pop(sender, None)
        return {"status": "complaint registered"}

    # ---------------- Status Check ----------------
    elif user["stage"] == "status":
        record = db.query(Complaint).filter(
            (Complaint.phone == text) | (Complaint.ticket_number == text)
        ).first()

        if record:
            msg = (
                f"📋 *Complaint Status*\n"
                f"👤 Name: {record.name}\n"
                f"🆔 Ticket: {record.ticket_number}\n"
                f"💬 Type: {record.fraud_type}\n"
                f"📍 District: {record.district}\n"
                f"📎 File: {record.media_files or 'No files uploaded'}\n"
                f"📦 Status: {record.status}"
            )
        else:
            msg = "⚠️ No record found for the given details."
        send_whatsapp_message(sender, msg)
        sessions.pop(sender, None)
        return {"status": "status checked"}

    # ---------------- Account Unfreeze ----------------
    elif user["stage"] == "unfreeze":
        send_whatsapp_message(sender, f"🧊 Your unfreeze request for *{text}* has been received. We’ll review it soon.")
        sessions.pop(sender, None)
        return {"status": "unfreeze submitted"}

    # Acknowledge uploads
    if media_file_path:
        send_whatsapp_message(sender, "📎 File received successfully. You can send more or type *done* to finish.")

    return {"status": "done"}

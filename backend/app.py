from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io, csv

# ---- your existing imports ----
from .models import init_db, SessionLocal, Complaint, MessageLog
from . import utils, nlu
from .emotion_model import predict as emo_predict, train_on as emo_train, info as emo_info

# ✅ NEW: import the WhatsApp router
from .whatsapp.whatsapp_router import router as whatsapp_router



app = FastAPI(title="CyberSathi Backend Pro")

app.include_router(whatsapp_router)
# optional: quick health check
@app.get("/")
def health():
    return {"ok": True, "service": "CyberSathi Backend Pro"}

# ---- keep the rest of your code unchanged ----
init_db()

class WebhookMessage(BaseModel):
    from_phone: str
    body: str

class ComplaintIn(BaseModel):
    name: str
    guardian: Optional[str] = ''
    dob: Optional[str] = ''
    phone: str
    email: Optional[str] = ''
    gender: Optional[str] = ''
    village: Optional[str] = ''
    post_office: Optional[str] = ''
    police_station: Optional[str] = ''
    district: Optional[str] = ''
    pincode: Optional[str] = ''
    fraud_text: Optional[str] = ''
    attachments_b64: Optional[List[str]] = None
    source: Optional[str] = 'whatsapp'

class LabelItem(BaseModel):
    id: int
    label: str

class LabelPayload(BaseModel):
    items: List[LabelItem]

def log_message_to_db(from_phone: str, body: str) -> Dict[str, Any]:
    session = SessionLocal()
    intent = nlu.detect_intent(body)
    fraud_cat = nlu.detect_fraud_category(body)
    label, conf = emo_predict(body or "")
    row = MessageLog(
        from_phone=from_phone,
        body=body,
        intent=intent,
        fraud_category=fraud_cat,
        emotion_pred=label,
        emotion_conf=conf,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    rid = row.id
    session.close()
    return {"id": rid, "intent": intent, "fraud_category": fraud_cat, "emotion_pred": label, "emotion_conf": conf}

@app.post("/webhook")
def webhook(msg: WebhookMessage):
    meta = log_message_to_db(msg.from_phone, msg.body)
    reply = "Welcome to CyberSathi. Reply with A for New Complaint, B for Status Check, C for Account Unfreeze, D for Other Queries."
    if meta["intent"] == "new_complaint":
        reply = "To register a complaint, POST to /submit_complaint or continue in WhatsApp guided flow."
    elif meta["intent"] == "status_check":
        reply = "To check status, POST to /status_check with ticket or phone."
    elif meta["intent"] == "account_unfreeze":
        reply = "For account unfreeze, POST to /account_unfreeze with account details."
    return {"reply": reply, **meta}

@app.post("/log_message")
def log_message(msg: WebhookMessage):
    meta = log_message_to_db(msg.from_phone, msg.body)
    return {"message": "logged", **meta}

@app.get("/messages")
def list_messages(q: Optional[str] = None, limit: int = 200):
    session = SessionLocal()
    query = session.query(MessageLog).order_by(MessageLog.created_at.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(MessageLog.body.like(like))
    rows = query.limit(limit).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "from_phone": r.from_phone,
            "body": r.body,
            "intent": r.intent,
            "fraud_category": r.fraud_category,
            "emotion_pred": r.emotion_pred,
            "emotion_conf": r.emotion_conf,
            "human_label": r.human_label,
            "created_at": r.created_at.isoformat()
        })
    session.close()
    return out

@app.get("/export/messages.csv")
def export_messages_csv(limit: int = 5000):
    session = SessionLocal()
    rows = session.query(MessageLog).order_by(MessageLog.created_at.desc()).limit(limit).all()
    session.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","from_phone","body","intent","fraud_category","emotion_pred","emotion_conf","human_label","created_at"])
    for r in rows:
        writer.writerow([r.id, r.from_phone, r.body, r.intent, r.fraud_category, r.emotion_pred, r.emotion_conf, r.human_label, r.created_at])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")

@app.post("/label_messages")
def label_messages(payload: LabelPayload):
    session = SessionLocal()
    updated = 0
    samples = []
    for item in payload.items:
        row = session.query(MessageLog).filter(MessageLog.id == item.id).first()
        if row:
            row.human_label = item.label
            updated += 1
            samples.append((row.body or "", item.label))
    session.commit()
    session.close()
    trained = emo_train(samples)
    return {"updated": updated, **trained}

@app.post("/train_emotion")
def train_emotion(limit: int = 5000):
    session = SessionLocal()
    rows = session.query(MessageLog).filter(MessageLog.human_label.isnot(None)).order_by(MessageLog.created_at.desc()).limit(limit).all()
    session.close()
    samples = [(r.body or "", r.human_label) for r in rows]
    trained = emo_train(samples)
    return {"from_labeled": len(samples), **trained}

@app.get("/model/info")
def model_info():
    return emo_info()

@app.post("/submit_complaint")
def submit_complaint(payload: ComplaintIn):
    errors = []
    if not utils.valid_phone(payload.phone):
        errors.append("Invalid phone number")
    if payload.email and not utils.valid_email(payload.email):
        errors.append("Invalid email")
    if payload.pincode and not utils.valid_pincode(payload.pincode):
        errors.append("Invalid pincode")
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    ticket = utils.gen_ticket()
    session = SessionLocal()
    fraud_cat = nlu.detect_fraud_category(payload.fraud_text or "")
    comp = Complaint(
        ticket=ticket,
        name=payload.name,
        guardian=payload.guardian,
        dob=payload.dob,
        phone=payload.phone,
        email=payload.email,
        gender=payload.gender,
        village=payload.village,
        post_office=payload.post_office,
        police_station=payload.police_station,
        district=payload.district,
        pincode=payload.pincode,
        fraud_category=fraud_cat,
        fraud_subtype="",
        description=payload.fraud_text,
        attachments="[]",
        status="Received"
    )
    session.add(comp)
    session.commit()
    session.refresh(comp)
    session.close()
    return {"message": "Complaint registered", "ticket": ticket}

@app.get("/status_check")
def status_check(ticket: Optional[str] = None, phone: Optional[str] = None):
    session = SessionLocal()
    q = None
    if ticket:
        q = session.query(Complaint).filter(Complaint.ticket == ticket).first()
    elif phone:
        q = session.query(Complaint).filter(Complaint.phone == phone).order_by(Complaint.created_at.desc()).first()
    session.close()
    if not q:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"ticket": q.ticket, "status": q.status, "created_at": q.created_at.isoformat()}

@app.get("/admin/complaints")
def admin_list(limit: int = 100):
    session = SessionLocal()
    items = session.query(Complaint).order_by(Complaint.created_at.desc()).limit(limit).all()
    out = []
    for i in items:
        out.append({
            "ticket": i.ticket,
            "name": i.name,
            "phone": i.phone,
            "fraud_category": i.fraud_category,
            "district": i.district,
            "status": i.status,
            "created_at": i.created_at.isoformat()
        })
    session.close()
    return out

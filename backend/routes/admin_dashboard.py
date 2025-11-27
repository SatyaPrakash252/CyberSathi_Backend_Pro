from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.models import Complaint
from backend.init_db import SessionLocal

router = APIRouter()
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# --- Admin credentials ---
ADMIN_USER = "admin"
ADMIN_PASS = "cybersathi123"

# --- Show login page ---
@router.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# --- Handle login form ---
@router.post("/admin", response_class=HTMLResponse)
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        db = SessionLocal()
        complaints = db.query(Complaint).order_by(Complaint.date_created.desc()).all()
        return templates.TemplateResponse("dashboard.html", {"request": request, "complaints": complaints})
    else:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "❌ Invalid credentials"})

# --- Update status ---
@router.post("/admin/update_status", response_class=HTMLResponse)
async def update_status(request: Request, ticket: str = Form(...), status: str = Form(...)):
    db = SessionLocal()
    complaint = db.query(Complaint).filter(Complaint.ticket_number == ticket).first()
    if complaint:
        complaint.status = status
        db.commit()
    complaints = db.query(Complaint).order_by(Complaint.date_created.desc()).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "complaints": complaints, "message": "✅ Status updated successfully."}
    )

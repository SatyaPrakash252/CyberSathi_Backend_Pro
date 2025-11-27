from fastapi import FastAPI
from backend.init_db import init_db
from backend.routes import admin_dashboard
from backend.whatsapp.whatsapp_router import router as whatsapp_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CyberSathi Backend")

init_db()

# Static file access
app.mount("/image", StaticFiles(directory="image"), name="image")
app.mount("/document", StaticFiles(directory="document"), name="document")

# Routers
app.include_router(whatsapp_router)
app.include_router(admin_dashboard.router)

@app.get("/")
def home():
    return {"message": "🚀 CyberSathi Backend is running!"}

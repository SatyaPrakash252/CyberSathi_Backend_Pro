from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    VERIFY_TOKEN = "cybersathi_verify"

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return JSONResponse(content=int(challenge))
    return JSONResponse(content="Verification failed", status_code=403)

@router.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("📩 Incoming Webhook:", data)
    return JSONResponse(content={"status": "received"}, status_code=200)

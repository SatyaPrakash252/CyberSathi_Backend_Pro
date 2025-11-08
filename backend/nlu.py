# Simple rule-based NLU for intent and fraud type detection
def detect_intent(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["status", "ack", "acknowledgement", "reference", "track"]):
        return "status_check"
    if any(k in t for k in ["unfreeze", "frozen", "freeze", "unlock"]):
        return "account_unfreeze"
    if any(k in t for k in ["fraud", "scam", "hacked", "transaction", "upi", "loan", "card", "apk", "fake"]):
        return "new_complaint"
    return "other"

def detect_fraud_category(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["upi", "imps", "neft", "rtgs", "inb"]):
        return "upi_fraud"
    if any(k in t for k in ["loan app", "loanapp", "instant loan"]):
        return "loan_app"
    if any(k in t for k in ["apk", "downloaded app", "install from link"]):
        return "apk_fraud"
    if any(k in t for k in ["debit card", "credit card", "card"]):
        return "card_fraud"
    if any(k in t for k in ["amazon", "flipkart", "ecommerce", "e-commerce"]):
        return "ecommerce_fraud"
    if any(k in t for k in ["investment", "trading", "ipo", "crypto"]):
        return "investment_fraud"
    if any(k in t for k in ["phish", "fake website", "website"]):
        return "phishing"
    return "other"

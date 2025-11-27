def get_advice(text):
    text_lower = text.lower()
    if "scam" in text_lower or "fraud" in text_lower:
        return "⚠️ Please avoid sharing OTPs or passwords. Report the fraud immediately at cybercrime.gov.in."
    elif "sad" in text_lower or "depress" in text_lower:
        return "💖 It’s okay to feel low sometimes. You are not alone. Please reach out for help or talk to someone you trust."
    elif "angry" in text_lower or "frustrated" in text_lower:
        return "😌 Take a deep breath. Staying calm helps you act wisely — we’re here to support you."
    else:
        return "💬 Thank you for sharing. I’ll make sure your message reaches the CyberSathi team."

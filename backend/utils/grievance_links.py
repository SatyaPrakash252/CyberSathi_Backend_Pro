# backend/utils/grievance_links.py

def get_grievance_link(user_message: str):
    text = user_message.lower()

    if any(word in text for word in ["facebook", "instagram", "meta"]):
        return (
            "🌐 *Meta Grievance Portal*\n"
            "Use this to report hacked or impersonation accounts:\n"
            "👉 https://www.facebook.com/help/contact/1280662443137291"
        )
    elif "twitter" in text or "x.com" in text:
        return (
            "🐦 *Twitter/X Grievance Form*\n"
            "👉 https://help.twitter.com/forms/general"
        )
    elif "telegram" in text:
        return (
            "💬 *Telegram Support*\n"
            "👉 https://telegram.org/support"
        )
    elif "gmail" in text or "google" in text or "youtube" in text:
        return (
            "📧 *Google Account Recovery*\n"
            "👉 https://accounts.google.com/signin/recovery"
        )
    elif "whatsapp" in text:
        return (
            "💚 *WhatsApp India Grievance Channel*\n"
            "👉 https://www.whatsapp.com/contact/noclient/"
        )
    elif "call" in text or "sms" in text or "phone" in text:
        return (
            "📱 *SancharSaathi Fraud Call/SMS Portal*\n"
            "👉 https://www.sancharsaathi.gov.in"
        )
    elif any(word in text for word in ["upi", "bank", "loan", "fraud"]):
        return (
            "🏦 *Cybercrime Financial Fraud Reporting*\n"
            "👉 https://cybercrime.gov.in"
        )
    else:
        return (
            "ℹ️ Please visit the *National Cybercrime Portal* for general issues:\n"
            "👉 https://cybercrime.gov.in"
        )

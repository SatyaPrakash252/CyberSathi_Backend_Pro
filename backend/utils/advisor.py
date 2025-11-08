import random
import requests

def analyze_threat(text: str) -> str:
    """Simple text-based threat analysis."""
    if "http" in text:
        return (
            "⚠️ Suspicious link detected.\n"
            "Avoid opening unknown URLs until verified.\n"
            "You can scan safely using https://www.virustotal.com"
        )
    elif any(ext in text for ext in [".exe", ".apk", ".zip", ".bat"]):
        return (
            "🚫 The file name looks risky and might contain malware.\n"
            "Do not download or share suspicious files."
        )
    return "✅ No immediate threat found. Stay alert!"

def ai_cyber_advisor(text: str) -> str:
    """Give smart cyber-safety tips."""
    advices = [
        "🔒 Change your password and enable 2FA immediately.",
        "⚠️ Never share your OTP or banking PIN with anyone.",
        "💡 If your account was hacked, report at https://cybercrime.gov.in",
        "📞 Contact the Cyber Helpline at 1930 for immediate assistance."
    ]
    return random.choice(advices)

def get_help_info() -> str:
    """Provide helpline contact and awareness."""
    try:
        loc = requests.get("https://ipapi.co/json/").json()
        city = loc.get("city")
        region = loc.get("region")
        return (
            f"📍 Detected Location: {city}, {region}\n"
            "📞 Helpline: 1930\n"
            "👮 Report cybercrime: https://cybercrime.gov.in\n"
            "💬 Odisha Police Cyber Cell is here to help you."
        )
    except:
        return (
            "📞 Emergency Helpline: 1930\n"
            "🌐 cybercrime.gov.in\n"
            "💡 Stay safe online!"
        )

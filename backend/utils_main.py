import re, datetime, random, base64, json, os
from cryptography.fernet import Fernet

KEY_FILE = os.environ.get("CYBERSATHI_FERNET_KEY_FILE", "./fernet_pro.key")

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

FERNET_KEY = load_or_create_key()
fernet = Fernet(FERNET_KEY)

def encrypt_text(plain: str) -> str:
    return fernet.encrypt(plain.encode()).decode()

def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

def valid_phone(phone: str) -> bool:
    import re
    return bool(re.fullmatch(r"[6-9]\d{9}", phone or ""))

def valid_email(email: str) -> bool:
    import re
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""))

def valid_pincode(pin: str) -> bool:
    import re
    return bool(re.fullmatch(r"\d{6}", pin or ""))

def gen_ticket():
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    rand = random.randint(1000, 9999)
    return f"CYB-{today}-{rand}"

def save_attachment_base64(b64str: str, folder="./uploads"):
    os.makedirs(folder, exist_ok=True)
    filename = f"attach_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}.bin"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64str))
    return path

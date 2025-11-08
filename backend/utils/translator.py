# old
# from googletrans import Translator

# new
from deep_translator import GoogleTranslator

def translate_text(text: str, dest: str = "en") -> str:
    try:
        return GoogleTranslator(source="auto", target=dest).translate(text)
    except Exception as e:
        print("Translation error:", e)
        return text

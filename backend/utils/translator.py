from googletrans import Translator

translator_instance = Translator()

def detect_language(text):
    try:
        return translator_instance.detect(text).lang
    except:
        return "en"

def translate_text(text, target_lang="en"):
    try:
        result = translator_instance.translate(text, dest=target_lang)
        return result.text
    except:
        return text

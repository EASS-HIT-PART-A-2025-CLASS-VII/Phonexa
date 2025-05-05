from googletrans import Translator

translator = Translator()

def translate_to_hebrew(text: str) -> str:
    result = translator.translate(text, src='en', dest='he')
    return result.text
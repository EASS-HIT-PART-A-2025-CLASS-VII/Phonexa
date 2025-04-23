import os
import re
import httpx
import aiofiles
from dotenv import load_dotenv

load_dotenv()
MARYTTS_URL = os.getenv("MARYTTS_URL", "http://localhost:59125")
MARYTTS_VOICE = os.getenv("MARYTTS_VOICE", "cmu-slt-hsmm")

# Direct mapping from IPA to X-SAMPA for MaryTTS
# Direct mapping from IPA to X-SAMPA for MaryTTS
IPA_TO_XSAMPA = {
    # Simple vowels
    'i': 'i', 'ɪ': 'I', 'e': 'e', 'ɛ': 'E', 'æ': '{',
    'a': 'a', 'ɑ': 'A', 'ɒ': 'Q', 'ɔ': 'O', 'o': 'o',
    'ʊ': 'U', 'u': 'u', 'ʌ': 'V', 'ə': '@', 'ɜ': '3',
    'ɝ': '3`', 'ɚ': '@`', 'ɐ': '6', 'ᵻ': 'I\\',
    
    # Long vowels - map to same as short vowels (without colon)
    'iː': 'i', 'ɑː': 'A', 'ɔː': 'O', 'uː': 'u',
    
    # Diphthongs
    'eɪ': 'eI', 'aɪ': 'aI', 'ɔɪ': 'OI', 'aʊ': 'aU', 'oʊ': 'oU',
    
    # Rhoticized vowels - also without colons
    'ɑːɹ': 'Ar', 'ɔːɹ': 'Or',
    
    # Basic consonants
    'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 
    'g': 'g', 'f': 'f', 'v': 'v', 'θ': 'T', 'ð': 'D', 
    's': 's', 'z': 'z', 'ʃ': 'S', 'ʒ': 'Z', 'h': 'h',
    'm': 'm', 'n': 'n', 'ŋ': 'N', 'l': 'l', 'r': 'r',
    'j': 'j', 'w': 'w', 'ʔ': '?', 'ɡ': 'g', 'ɹ': 'r\\',
    
    # Affricates
    'tʃ': 'tS', 'dʒ': 'dZ',
    
    # Special cases - syllabic consonants
    'əl': '@l', 'ən': '@n',
    
    # Diacritics and stress marks
    'ˈ': '"', 'ˌ': '%', '.': '.',
    
    # Individual characters for the affricates and diphthongs
    # so they also work when sent character by character
    'ʃ': 'S', 'ʒ': 'Z', 'ɪ': 'I', 'ʊ': 'U',
    
    # Special case - the length marker (colon) should be removed
    'ː': '',
}

def process_sentence_for_tts(sentence: str) -> str:
    s = re.sub(r"<font[^>]*>", "", sentence)
    s = re.sub(r"</font>", "", s)
    return re.sub(r"<[^>]+>", "", s).strip()

def ipa_to_xsampa(ipa: str) -> str:
    """
    Convert IPA string to X-SAMPA using direct mapping.
    Returns X-SAMPA with hyphens between symbols.
    """
    result = []
    for char in ipa:
        # Get the X-SAMPA equivalent or use the original character if not in mapping
        xsampa_char = IPA_TO_XSAMPA.get(char, char)
        result.append(xsampa_char)
    
    # Join with hyphens for MaryXML ph attribute
    return "".join(result)

async def generate_tts_audio(sentence: str):
    sentence = process_sentence_for_tts(sentence)
    output_path = "output.wav"
    try:
        m = re.search(
            r"Try\s+saying\s+([^\s]+)\s+instead\s+of\s+([^\s]+)\.?\s*$",
            sentence, re.IGNORECASE
        )
        if m:
            ipa1, ipa2 = m.group(1), m.group(2)
            # Convert IPA to X-SAMPA using our mapping table
            ph1 = ipa_to_xsampa(ipa1)
            ph2 = ipa_to_xsampa(ipa2)
            print(f"IPA1: {ipa1}, IPA2: {ipa2}")
            print(f"X-SAMPA1: {ph1}, X-SAMPA2: {ph2}")

            maryxml = f"""<?xml version="1.0" encoding="UTF-8"?>
<maryxml xmlns="http://mary.dfki.de/2002/MaryXML" version="0.5" xml:lang="en-US">
  <prosody rate="100%">
    Try saying
    <t ph="{ph1}">{ipa1}</t>
    instead of
    <t ph="{ph2}">{ipa2}</t>.
  </prosody>
</maryxml>"""

            params = {
                "INPUT_TEXT": maryxml,
                "INPUT_TYPE": "RAWMARYXML",
                "OUTPUT_TYPE": "AUDIO",
                "AUDIO": "WAVE_FILE",
                "LOCALE": "en_US",
                "VOICE": MARYTTS_VOICE
            }
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{MARYTTS_URL}/process", params=params, timeout=30.0)
                r.raise_for_status()
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(r.content)
        else:
            # fallback to Edge TTS
            text = sentence
            from edge_tts import Communicate
            comm = Communicate(text=text, voice="en-US-AvaMultilingualNeural")
            await comm.save(output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("TTS output missing or empty")

        return output_path

    except Exception as e:
        print(f"Error in TTS generation: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise
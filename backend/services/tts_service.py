import os
import re



def process_sentence_for_tts(sentence: str) -> str:
    """
    Cleans up a given sentence by removing HTML tags and font-related tags.

    This function performs the following steps:
    1. Removes any opening <font> tags with their attributes.
    2. Removes any closing </font> tags.
    3. Removes any other HTML tags.
    4. Strips leading and trailing whitespace from the resulting string.

    Args:
        sentence (str): The input sentence containing potential HTML tags.

    Returns:
        str: The cleaned sentence with all HTML tags removed.
    """
    s = re.sub(r"<font[^>]*>", "", sentence)
    s = re.sub(r"</font>", "", s)
    return re.sub(r"<[^>]+>", "", s).strip()


async def generate_tts_audio(sentence: str):
    sentence = process_sentence_for_tts(sentence)
    output_path = "output.wav"
            # fallback to Edge TTS
    text = sentence
    from edge_tts import Communicate
    comm = Communicate(text=text, voice="en-US-AvaMultilingualNeural")
    await comm.save(output_path)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("TTS output missing or empty")

    return output_path
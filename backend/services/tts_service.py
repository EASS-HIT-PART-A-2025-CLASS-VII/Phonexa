import os
import re
import edge_tts
import subprocess

def process_sentence_for_tts(sentence: str) -> str:
    """
    Cleans the sentence by removing HTML tags.
    """
    # Step 1: Remove HTML tags
    sentence = re.sub(r"<[^>]+>", "", sentence)
    return sentence

async def generate_tts_audio(sentence: str):
    """
    Generates TTS audio for the given sentence. Uses Edge TTS for standard sentences
    and eSpeak for sentences with IPA phonemes.
    """
    output_path = "output.wav"
    processed_sentence = process_sentence_for_tts(sentence)

    try:
        # Check if the sentence matches the "Try saying ... instead of ..." structure
        match = re.search(r"Try saying ([^ ]+) instead of ([^ ]+)", sentence)
        if match:
            # Use eSpeak for IPA-based sentences
            print("Using eSpeak for TTS.")
            ipa_text = match.group(1)
            # Call eSpeak NG to synthesize IPA to wav
            subprocess.run([
                "espeak-ng",
                "-v", "en",
                "-x",  # Interpret input as IPA
                "-w", output_path,
                ipa_text
            ], check=True)
        else:
            # Use Edge TTS for standard sentences
            print("Using Edge TTS for TTS.")
            communicate = edge_tts.Communicate(
                text=processed_sentence.strip(),
                voice="en-US-AvaMultilingualNeural"
            )
            await communicate.save(output_path)

        return output_path
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e
import os
import re
import edge_tts
import subprocess

def process_sentence_for_tts(sentence: str) -> str:
    """
    Cleans the sentence by removing HTML tags and wrapping IPA words with SSML <phoneme> tags.
    """
    # Step 1: Remove HTML tags
    sentence = re.sub(r"<[^>]+>", "", sentence)

    # Step 2: Wrap IPA words with <phoneme> tags for SSML
    sentence = re.sub(
        r"Try saying ([^ ]+) instead of ([^ ]+)",
        r'Try saying <phoneme alphabet="ipa" ph="\1"></phoneme> instead of <phoneme alphabet="ipa" ph="\2"></phoneme>',
        sentence,
    )

    # Step 3: Wrap the text in a properly formed <speak> tag
    ssml_sentence = (
        f'<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
        f"{sentence}"
        f"</speak>"
    )

    return ssml_sentence.strip()

async def generate_tts_audio(sentence: str):
    """
    Generates TTS audio for the given sentence. Uses Edge TTS for standard sentences
    and eSpeak for sentences with IPA phonemes.
    """
    output_path = "output.wav"

    try:
        # Check if the sentence matches the "Try saying ... instead of ..." structure
        if re.search(r"Try saying ([^ ]+) instead of ([^ ]+)", sentence):
            # Use eSpeak for IPA-based sentences
            print("Using eSpeak for TTS.")
            generate_espeak_audio(sentence, output_path)
        else:
            # Use Edge TTS for standard sentences
            print("Using Edge TTS for TTS.")
            processed_sentence = process_sentence_for_tts(sentence)
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

def generate_espeak_audio(sentence: str, output_path: str):
    """
    Generates TTS audio using eSpeak for sentences with IPA phonemes.

    Parameters:
    sentence (str): The input sentence to convert to audio.
    output_path (str): The path to save the generated audio file.
    """
    try:
        # Remove HTML tags from the sentence
        cleaned_sentence = re.sub(r"<[^>]+>", "", sentence)

        # Use eSpeak to generate the audio
        subprocess.run(
            ["espeak", "-v", "en-us", "-w", output_path, cleaned_sentence],
            check=True
        )
        print(f"eSpeak audio generated at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating eSpeak audio: {e}")
        raise e
import requests
import os
import json


def align_audio_with_gentle(audio_path, transcript_path):
    """
    Aligns a single audio file with its transcript using Gentle.

    Parameters:
    audio_path (str): Path to the audio file.
    transcript_path (str): Path to the transcript file.

    Returns:
    dict: Full JSON response from Gentle API.
    """
    try:
        # Send the audio and transcript to Gentle's API
        url = "http://localhost:8765/transcriptions?async=false"  # Gentle's default API endpoint
        with open(audio_path, "rb") as audio_file, open(transcript_path, "r", encoding="utf-8") as transcript_file:
            files = {
                "audio": audio_file,
                "transcript": (transcript_path, transcript_file.read(), "text/plain"),
            }
            response = requests.post(url, files=files)

        if response.status_code != 200:
            raise RuntimeError(f"Gentle alignment failed: {response.text}")
        
        # Clean up temporary files
        os.remove(audio_path)
        os.remove(transcript_path)

        # Return the full JSON response
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Gentle alignment failed: {e}")
    


def add_ipa_to_gentle_alignment(gentle_json_path, output_path):
    with open(gentle_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
        ARPABET_TO_IPA_PATH = os.path.join(os.path.dirname(__file__), "ARPABET_TO_IPA.json")
        with open(ARPABET_TO_IPA_PATH, "r", encoding="utf-8") as f:
            ARPABET_TO_IPA = json.load(f)
        

    for word in data.get("words", []):
        for phone in word.get("phones", []):
            arpabet = phone["phone"]
            base_arpabet = arpabet.split('_')[0].upper()
            ipa = ARPABET_TO_IPA.get(base_arpabet, "")
            phone["IPAphone"] = ipa

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Example usage:
# add_ipa_to_gentle_alignment(
#     gentle_json_path="gentle_alignment.json",
#     output_path="gentle_alignment_with_ipa.json"
# )
import requests
import os

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
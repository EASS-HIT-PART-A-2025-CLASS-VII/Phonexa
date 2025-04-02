import os
import edge_tts

async def generate_tts_audio(sentence: str):
    output_path = "output.wav"
    try:
        # Use edge-tts to generate the audio file
        communicate = edge_tts.Communicate(text=sentence, voice="en-US-AvaMultilingualNeural")
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e
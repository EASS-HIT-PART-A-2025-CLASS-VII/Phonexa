import os
import torch
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import subprocess

# Load the pre-trained Wav2Vec2 model and processor globally
MODEL_NAME = "facebook/wav2vec2-lv-60-espeak-cv-ft"
print("Loading processor and model...")
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def convert_to_wav(input_path, output_path):
    """
    Converts an audio file to a standard PCM WAV format using FFmpeg.

    Parameters:
    input_path (str): Path to the input audio file.
    output_path (str): Path to save the converted WAV file.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            check=True
        )
        print(f"Converted {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to convert file to WAV: {e}")

async def convert_audio_file(audio):
    """
    Converts an uploaded audio file to phoneme transcription.

    Parameters:
    audio (UploadFile): The uploaded audio file.

    Returns:
    dict: A dictionary containing the phoneme transcription.
    """
    audio_path = f"temp_{audio.filename}"
    wav_path = f"converted_{audio.filename}.wav"
    try:
        print(f"Saving audio file: {audio.filename}")
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

        print(f"Audio file saved at: {audio_path}")

        # Convert to WAV if necessary
        convert_to_wav(audio_path, wav_path)
        phonemes = transcribe_audio_to_phonemes(wav_path)

        print(f"Phoneme transcription: {phonemes}")
        return {"phonemes": phonemes}
    except Exception as e:
        print(f"Error in convert_audio_file: {e}")
        raise
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

def transcribe_audio_to_phonemes(audio_file_path):
    """
    Transcribes an audio file to its phoneme representation using a pre-trained Wav2Vec2 model.

    Parameters:
    audio_file_path (str): Path to the audio file to be transcribed.

    Returns:
    str: Transcribed phoneme sequence.
    """
    try:
        # Load the audio file
        print(f"Loading audio file: {audio_file_path}")
        audio_input, sample_rate = sf.read(audio_file_path)

        # Process the audio input
        input_values = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt").input_values.to(device)

        # Perform inference to get logits
        with torch.no_grad():
            logits = model(input_values).logits

        # Decode the logits to get the predicted phoneme sequence
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        return transcription
    except Exception as e:
        print(f"Error in transcribe_audio_to_phonemes: {e}")
        raise
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

async def convert_audio_file(audio_path):
    """
    Reads the audio file, converts it to WAV if needed, and transcribes to phonemes.
    """
    wav_path = f"converted_{os.path.basename(audio_path)}.wav"
    try:
        print(f"Processing audio file: {audio_path}")

        # Convert to WAV if necessary
        convert_to_wav(audio_path, wav_path)
        print(f"Converted audio file to WAV: {wav_path}")

        # Instead of reading from file again, load the audio data immediately
        print(f"Loading audio from file: {wav_path}")
        audio_input, sample_rate = sf.read(wav_path)
        print("Loaded audio, performing transcription...")

        phonemes = transcribe_audio_to_phonemes_from_array(audio_input, sample_rate)

        return {"phonemes": phonemes}
    except Exception as e:
        print(f"Error in convert_audio_file: {e}")
        raise
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

def transcribe_audio_to_phonemes_from_array(audio_input, sample_rate):
    """
    Transcribes audio (as a numpy array) to its phoneme representation
    using the pre-trained Wav2Vec2 model.

    Parameters:
    audio_input (np.array): Audio signal.
    sample_rate (int): Sampling rate of the audio.

    Returns:
    list: Array of phonemes.
    """
    try:
        # Process the audio input directly
        input_values = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt").input_values.to(device)

        # Perform inference to get logits
        with torch.no_grad():
            logits = model(input_values).logits

        # Decode the logits to get the predicted phoneme sequence
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        # Split the transcription into an array of phonemes
        phonemes = transcription.split()

        return phonemes
    except Exception as e:
        print(f"Error in transcribe_audio_to_phonemes_from_array: {e}")
        raise
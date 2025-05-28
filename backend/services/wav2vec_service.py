import os
import torch
import soundfile as sf
import subprocess
import re
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from services.wav2vec_alignment import tokenize_ipa, align_words_to_phonemes_dp  # Import alignment functions

MODEL_NAME = "facebook/wav2vec2-lv-60-espeak-cv-ft"
MODEL_CACHE = os.environ.get("TRANSFORMERS_CACHE", None)

print(f"Loading processor and model... Cache: {MODEL_CACHE}")
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME, cache_dir=MODEL_CACHE)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME, cache_dir=MODEL_CACHE)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def convert_to_wav(input_path, output_path):
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            check=True
        )
        print(f"Converted {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to convert file to WAV: {e}")

async def convert_audio_file(audio_path, sentenceIPA, sentence):
    wav_path = f"converted_{os.path.basename(audio_path)}.wav"
    try:
        print(f"Processing audio file: {audio_path}")
        convert_to_wav(audio_path, wav_path)
        print(f"Converted audio file to WAV: {wav_path}")
        print(f"Loading audio from file: {wav_path}")
        audio_input, sample_rate = sf.read(wav_path)
        print("Loaded audio, performing transcription...")

        # Process audio using model
        input_values = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt").input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        phonemes = transcription.split()
        # Remove unwanted characters
        sentenceIPA = sentenceIPA.replace("'", "").replace("ˈ", "").replace("ˌ", "").replace(".", "")
        print("Original SentenceIPA:\n", sentenceIPA)
        print("Phonemes from the recording:\n", phonemes)

        ipa_word_phonemes = tokenize_ipa(sentenceIPA)
        print("Tokenized IPA Sentence:\n", ipa_word_phonemes)
        word_alignments = align_words_to_phonemes_dp(ipa_word_phonemes, phonemes)
        sentence_words = [re.sub(r"'", "", w) for w in re.findall(r"\b[\w']+\b", sentence)] # extract the words themselves
        for entry, word in zip(word_alignments, sentence_words):
            entry["user_phonemes"] = ''.join(entry["user_phonemes"])
            entry["word"] = word

        return {
            "sentence": sentence,
            "word_alignments": word_alignments
        }
        
    except Exception as e:
        print(f"Error in transcribe_audio_to_phonemes_from_array: {e}")
        raise
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
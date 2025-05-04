from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import os

MODEL_NAME = "facebook/wav2vec2-lv-60-espeak-cv-ft"
CACHE_DIR = "./model_cache"

os.makedirs(CACHE_DIR, exist_ok=True)
print(f"Downloading model files to {CACHE_DIR}...")

processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

print("Model files downloaded successfully!")
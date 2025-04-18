import os
import torch
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import subprocess
import numpy as np


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

async def convert_audio_file(audio_path, sentenceIPA):
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

        alignment = transcribe_audio_to_phonemes_from_array(audio_input, sample_rate, sentenceIPA)

        return alignment
    except Exception as e:
        print(f"Error in convert_audio_file: {e}")
        raise
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


# Phonetic features implementation based on your model's vocabulary

# Define phonetic features for each IPA symbol
# Format: [type, place/height, manner/backness, voicing/roundedness, length]
# Type: 0=consonant, 1=vowel
# For consonants:
#   Place: bilabial(0), labiodental(1), dental(2), alveolar(3), postalveolar(4), palatal(5), velar(6), glottal(7)
#   Manner: plosive(0), nasal(1), fricative(2), approximant(3), lateral(4)
#   Voicing: unvoiced(0), voiced(1)
# For vowels:
#   Height: high(0), mid-high(1), mid(2), mid-low(3), low(4)
#   Backness: front(0), central(1), back(2)
#   Roundedness: unrounded(0), rounded(1)
#   Length: short(0), long(1)

# Enhanced IPA_FEATURES dictionary with expanded vocabulary
IPA_FEATURES = {
    # Vowels
    'ɪ': [1, 0, 0, 0, 0],  # high front unrounded short (bit)
    'i': [1, 0, 0, 0, 0],  # high front unrounded (alternative notation)
    'iː': [1, 0, 0, 0, 1],  # high front unrounded long (beat)
    'ɛ': [1, 2, 0, 0, 0],  # mid front unrounded (bet)
    'e': [1, 1, 0, 0, 0],  # mid-high front unrounded
    'æ': [1, 3, 0, 0, 0],  # near-low front unrounded (bat)
    'ə': [1, 2, 1, 0, 0],  # mid central unrounded (about)
    'ɚ': [1, 2, 1, 0, 0],  # mid central unrounded r-colored (butter)
    'ɐ': [1, 3, 1, 0, 0],  # near-low central unrounded
    'ʌ': [1, 2, 2, 0, 0],  # mid-low back unrounded (cut)
    'ɑ': [1, 4, 2, 0, 0],  # low back unrounded (short)
    'ɑː': [1, 4, 2, 0, 1],  # low back unrounded long (father)
    'ɔ': [1, 3, 2, 1, 0],  # open-mid back rounded (thought)
    'ɔː': [1, 3, 2, 1, 1],  # open-mid back rounded long
    'ʊ': [1, 0, 2, 1, 0],  # near-high near-back rounded (put)
    'u': [1, 0, 2, 1, 0],  # high back rounded (boot short)
    'uː': [1, 0, 2, 1, 1],  # high back rounded long (boot)
    'ᵻ': [1, 0, 1, 0, 0],  # high central unrounded
    
    # Diphthongs
    'eɪ': [1, 1, 0, 0, 0],  # face
    'aɪ': [1, 4, 0, 0, 0],  # price
    'ɔɪ': [1, 3, 2, 1, 0],  # choice
    'aʊ': [1, 4, 2, 1, 0],  # mouth
    'oʊ': [1, 1, 2, 1, 0],  # goat
    
    # Rhoticized vowels
    'ɑːɹ': [1, 4, 2, 0, 1],  # r-colored low back unrounded long (car)
    'ɔːɹ': [1, 3, 2, 1, 1],  # r-colored open-mid back rounded long (more)
    'ɝ': [1, 2, 1, 0, 0],  # r-colored mid central (fur)
    
    # Consonants
    'p': [0, 0, 0, 0, 0],  # bilabial plosive unvoiced
    'b': [0, 0, 0, 1, 0],  # bilabial plosive voiced
    't': [0, 3, 0, 0, 0],  # alveolar plosive unvoiced
    'd': [0, 3, 0, 1, 0],  # alveolar plosive voiced
    'k': [0, 6, 0, 0, 0],  # velar plosive unvoiced
    'ɡ': [0, 6, 0, 1, 0],  # velar plosive voiced
    'f': [0, 1, 2, 0, 0],  # labiodental fricative unvoiced
    'v': [0, 1, 2, 1, 0],  # labiodental fricative voiced
    'θ': [0, 2, 2, 0, 0],  # dental fricative unvoiced
    'ð': [0, 2, 2, 1, 0],  # dental fricative voiced
    's': [0, 3, 2, 0, 0],  # alveolar fricative unvoiced
    'z': [0, 3, 2, 1, 0],  # alveolar fricative voiced
    'ʃ': [0, 4, 2, 0, 0],  # postalveolar fricative unvoiced
    'ʒ': [0, 4, 2, 1, 0],  # postalveolar fricative voiced
    'h': [0, 7, 2, 0, 0],  # glottal fricative unvoiced
    'm': [0, 0, 1, 1, 0],  # bilabial nasal voiced
    'n': [0, 3, 1, 1, 0],  # alveolar nasal voiced
    'ŋ': [0, 6, 1, 1, 0],  # velar nasal voiced
    'l': [0, 3, 4, 1, 0],  # alveolar lateral voiced
    'ɹ': [0, 3, 3, 1, 0],  # alveolar approximant voiced
    'r': [0, 3, 3, 1, 0],  # alternative notation for 'ɹ'
    'j': [0, 5, 3, 1, 0],  # palatal approximant voiced (yes)
    'w': [0, 0, 3, 1, 0],  # bilabial approximant voiced
    
    # Affricates
    'tʃ': [0, 4, 0, 0, 0],  # postalveolar affricate unvoiced (church)
    'dʒ': [0, 4, 0, 1, 0],  # postalveolar affricate voiced (judge)
    
    # Special cases - syllabic consonants and compounds
    'əl': [1, 2, 1, 0, 0],  # syllabic l (bottle)
    'ən': [1, 2, 1, 0, 0],  # syllabic n (button)
}

def phonetic_distance(a, b):
    """
    Calculate phonetic distance between two IPA symbols based on features.
    
    Returns a value between 0 (identical) and 1 (maximally different)
    """
    # Handle exact matches
    if a == b:
        return 0.0
        
    # Handle unknown symbols
    if a not in IPA_FEATURES or b not in IPA_FEATURES:
        return 1.0
    
    features_a = IPA_FEATURES[a]
    features_b = IPA_FEATURES[b]
    
    # If different types (vowel vs consonant), high penalty
    if features_a[0] != features_b[0]:
        return 0.8
    
    # Calculate weighted feature distance
    weights = [0.0, 0.3, 0.3, 0.2, 0.2]  # Weight for each feature
    total_weight = sum(weights[1:])  # Skip type weight
    
    weighted_diff = 0
    for i in range(1, len(features_a)):
        if features_a[i] != features_b[i]:
            # Scale by the possible range for this feature
            feature_range = 8 if i == 1 and features_a[0] == 0 else \
                            5 if i == 1 and features_a[0] == 1 else \
                            5 if i == 2 and features_a[0] == 0 else \
                            3 if i == 2 and features_a[0] == 1 else \
                            2  # Binary features
            
            # Calculate normalized difference for this feature
            diff = abs(features_a[i] - features_b[i]) / feature_range
            weighted_diff += weights[i] * diff
    
    # Normalize total difference
    distance = weighted_diff / total_weight
    
    # Common phonological processes should have lower penalties:
    # 1. Voicing differences in consonants
    if features_a[0] == 0 and features_b[0] == 0 and features_a[1] == features_b[1] and features_a[2] == features_b[2]:
        if features_a[3] != features_b[3]:  # Only voicing differs
            distance *= 0.7  # Reduce penalty
    
    # 2. Similar vowel heights
    if features_a[0] == 1 and features_b[0] == 1:
        height_diff = abs(features_a[1] - features_b[1])
        if height_diff == 1:  # Adjacent heights
            distance *= 0.8  # Reduce penalty
    
    return min(1.0, distance)  # Cap at 1.0

def levenshtein_with_features(a, b):
    """
    Enhanced Levenshtein distance using phonetic feature distances.
    """
    dp = np.zeros((len(a)+1, len(b)+1), dtype=float)
    for i in range(len(a)+1):
        dp[i][0] = i
    for j in range(len(b)+1):
        dp[0][j] = j
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            # Use phonetic distance for substitution cost
            cost = phonetic_distance(a[i-1], b[j-1])
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution with feature-based cost
            )
    return dp[len(a)][len(b)]

def align_words_to_phonemes_dp(ipa_word_phonemes, predicted_phonemes, beam_width=5):
    """
    Aligns IPA words to predicted phonemes using dynamic programming with beam search.
    
    Parameters:
        ipa_word_phonemes: List of lists, where each inner list contains phonemes of an IPA word
        predicted_phonemes: List of phonemes from model prediction
        beam_width: Number of best candidates to keep at each step
        
    Returns:
        List of word alignments
    """
    N = len(ipa_word_phonemes)
    M = len(predicted_phonemes)
    dp = np.full((N+1, M+1), -np.inf)
    bp = np.full((N+1, M+1), -1, dtype=int)
    dp[0][0] = 0

    for i in range(1, N+1):
        # For each position j
        for j in range(1, M+1):
            # Keep track of candidate start positions and their scores
            candidates = []
            
            # Try all possible previous positions
            for k in range(j):
                # Skip if previous state is unreachable
                if dp[i-1][k] == -np.inf:
                    continue
                    
                ref = ipa_word_phonemes[i-1]
                hyp = predicted_phonemes[k:j]
                
                # Calculate similarity score
                sim = -levenshtein_with_features(ref, hyp)
                score = dp[i-1][k] + sim
                
                # Add to candidates
                candidates.append((score, k))
            
            # If we have candidates, keep only the best beam_width
            if candidates:
                # Sort by score (descending)
                candidates.sort(key=lambda x: x[0], reverse=True)
                
                # Take the best candidate for this position
                best_score, best_k = candidates[0]
                dp[i][j] = best_score
                bp[i][j] = best_k
                
                # We could use other candidates in the beam for more complex 
                # beam search variants, but for basic beam search we just 
                # keep the best one per position

    # Backtracking is the same as before
    if dp[N][M] == -np.inf:
        return "Alignment failed"

    alignment = []
    i, j = N, M
    while i > 0:
        k = bp[i][j]
        alignment.append({
            "IPA_word": ''.join(ipa_word_phonemes[i-1]),
            "user_phonemes": predicted_phonemes[k:j]
        })
        i -= 1
        j = k
    alignment.reverse()
    return alignment

def transcribe_audio_to_phonemes_from_array(audio_input, sample_rate, sentenceIPA):
    """
    Transcribes audio (as a numpy array) to its phoneme representation
    using the pre-trained Wav2Vec2 model, and aligns with the reference IPA using Needleman-Wunsch.
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
        ipa_word_phonemes = tokenize_ipa(sentenceIPA)
        word_alignments = align_words_to_phonemes_dp(ipa_word_phonemes, phonemes)
        return {
            "phonemes": phonemes,
            "word_alignments": word_alignments
        }
        
    except Exception as e:
        print(f"Error in transcribe_audio_to_phonemes_from_array: {e}")
        raise

def tokenize_ipa(ipa_text):
    """
    Properly tokenize IPA text, preserving multi-character phonemes
    """
    # Define multi-character IPA symbols to preserve (add more as needed)
    multi_char_symbols = [
        'ɑː', 'iː', 'uː', 'eɪ', 'aɪ', 'ɔɪ', 'aʊ', 'oʊ', 'ɑːɹ', 'əl',
        'tʃ', 'dʒ', 'ʃ', 'ʒ', 'θ', 'ð', 'ŋ'
    ]
    
    # Sort by length (descending) to prioritize longer matches
    multi_char_symbols.sort(key=len, reverse=True)
    
    # Tokenize the input text
    tokens = []
    words = ipa_text.split()
    for word in words:
        word_tokens = []
        i = 0
        while i < len(word):
            matched = False
            # Try to match multi-character symbols
            for symbol in multi_char_symbols:
                if word[i:].startswith(symbol):
                    word_tokens.append(symbol)
                    i += len(symbol)
                    matched = True
                    break
            # If no multi-character match, take a single character
            if not matched:
                word_tokens.append(word[i])
                i += 1
        tokens.append(word_tokens)
    
    return tokens
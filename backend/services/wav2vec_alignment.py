import numpy as np


# Enhanced IPA_FEATURES dictionary with expanded vocabulary
IPA_FEATURES = {
    # Vowels
    'ɪ': [1, 0, 1, 0, 0],  # Near-close near-front unrounded vowel
    'i': [1, 0, 0, 0, 0],  # Close front unrounded vowel
    'iː': [1, 0, 0, 0, 1], # Long close front unrounded vowel
    'ɛ': [1, 2, 0, 0, 0],  # Open-mid front unrounded vowel
    'e': [1, 1, 0, 0, 0],  # Close-mid front unrounded vowel
    'æ': [1, 3, 0, 0, 0],  # Near-open front unrounded vowel
    'ə': [1, 2, 1, 0, 0],  # Mid central vowel (schwa)
    'ɚ': [1, 2, 1, 0, 1],  # R-colored schwa
    'ɐ': [1, 3, 1, 0, 0],  # Near-open central vowel
    'ʌ': [1, 2, 2, 0, 0],  # Open-mid back unrounded vowel
    'ɑ': [1, 4, 2, 0, 0],  # Open back unrounded vowel
    'ɑː': [1, 4, 2, 0, 1], # Long open back unrounded vowel
    'ɒ': [1, 4, 2, 1, 0],  # Open back rounded vowel
    'ɔ': [1, 3, 2, 1, 0],  # Open-mid back rounded vowel
    'ɔː': [1, 3, 2, 1, 1], # Long open-mid back rounded vowel
    'ʊ': [1, 0, 3, 1, 0],  # Near-close near-back rounded vowel
    'u': [1, 0, 2, 1, 0],  # Close back rounded vowel
    'uː': [1, 0, 2, 1, 1], # Long close back rounded vowel
    'ᵻ': [1, 0, 1, 0, 0],  # Centralized i
    'o': [1, 2, 2, 1, 0],  # Close-mid back rounded vowel
    'a': [1, 4, 0, 0, 0],  # Open front unrounded vowel
    'y': [1, 0, 0, 1, 0],  # Close front rounded vowel
    'ø': [1, 1, 0, 1, 0],  # Close-mid front rounded vowel
    'œ': [1, 2, 0, 1, 0],  # Open-mid front rounded vowel
    'ɯ': [1, 0, 2, 0, 0],  # Close back unrounded vowel
    # Diphthongs
    'eɪ': [1, 1, 0, 0, 3],  # Diphthong type 1
    'aɪ': [1, 4, 0, 0, 3],  # Diphthong type 2
    'ɔɪ': [1, 3, 2, 1, 3],  # Diphthong type 3
    'aʊ': [1, 3, 2, 1, 3],  # Diphthong type 4 - adjusted height to be closer to oʊ
    'oʊ': [1, 2, 2, 1, 3],  # Diphthong type 5 - adjusted height to be closer to aʊ
    'əʊ': [1, 2, 1, 0, 3],  # Diphthong type 6
    # Rhoticized vowels
    'ɑːɹ': [1, 4, 2, 0, 2], # Rhoticized long open back unrounded vowel
    'ɔːɹ': [1, 3, 2, 1, 2], # Rhoticized long open-mid back rounded vowel
    'ɝ': [1, 2, 1, 0, 2],   # Rhoticized mid central vowel
    # Consonants
    'p': [0, 0, 0, 0, 0],
    'b': [0, 0, 0, 1, 0],
    't': [0, 3, 0, 0, 0],
    'd': [0, 3, 0, 1, 0],
    'k': [0, 6, 0, 0, 0],
    'ɡ': [0, 6, 0, 1, 0],
    'g': [0, 6, 0, 1, 0],
    'f': [0, 1, 2, 0, 0],
    'v': [0, 1, 2, 1, 0],
    'θ': [0, 2, 2, 0, 0],
    'ð': [0, 2, 2, 1, 0],
    's': [0, 3, 2, 0, 0],
    'z': [0, 3, 2, 1, 0],
    'ʃ': [0, 4, 2, 0, 0],
    'ʒ': [0, 4, 2, 1, 0],
    'h': [0, 7, 2, 0, 0],
    'm': [0, 0, 1, 1, 0],
    'n': [0, 3, 1, 1, 0],
    'ŋ': [0, 6, 1, 1, 0],
    'l': [0, 3, 4, 1, 0],
    'ɹ': [0, 3, 3, 1, 0],
    'r': [0, 3, 3, 1, 0],
    'j': [0, 5, 3, 1, 0],
    'w': [0, 0, 3, 1, 0],
    # Affricates
    'tʃ': [0, 4, 0, 0, 0],
    'dʒ': [0, 4, 0, 1, 0],
    # Special cases - syllabic consonants and compounds
    'əl': [1, 2, 1, 0, 0],
    'ən': [1, 2, 1, 0, 0],
}

def phonetic_distance(a, b):
    """
    Calculate phonetic distance between two IPA symbols based on features.
    Returns a value between 0 (identical) and 1 (maximally different)
    """
    if a == b:
        return 0.0
    if a not in IPA_FEATURES or b not in IPA_FEATURES:
        return 1.0
    features_a = IPA_FEATURES[a]
    features_b = IPA_FEATURES[b]
    if features_a[0] != features_b[0]:
        return 0.8
    weights = [0.0, 0.3, 0.3, 0.2, 0.2]
    total_weight = sum(weights[1:])
    weighted_diff = 0
    for i in range(1, len(features_a)):
        if features_a[i] != features_b[i]:
            feature_range = 8 if i == 1 and features_a[0] == 0 else \
                            5 if i == 1 and features_a[0] == 1 else \
                            5 if i == 2 and features_a[0] == 0 else \
                            3 if i == 2 and features_a[0] == 1 else 2
            diff = abs(features_a[i] - features_b[i]) / feature_range
            weighted_diff += weights[i] * diff
    distance = weighted_diff / total_weight
    if features_a[0] == 0 and features_b[0] == 0 and features_a[1] == features_b[1] and features_a[2] == features_b[2]:
        if features_a[3] != features_b[3]:
            distance *= 0.7
    if features_a[0] == 1 and features_b[0] == 1:
        height_diff = abs(features_a[1] - features_b[1])
        if height_diff == 1:
            distance *= 0.8
    return min(1.0, distance)

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
            cost = phonetic_distance(a[i-1], b[j-1])
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[len(a)][len(b)]

def align_words_to_phonemes_dp(ipa_word_phonemes, predicted_phonemes, beam_width=5):
    """
    Aligns IPA words to predicted phonemes using dynamic programming with beam search.
    """
    N = len(ipa_word_phonemes)
    M = len(predicted_phonemes)
    dp = np.full((N+1, M+1), -np.inf)
    bp = np.full((N+1, M+1), -1, dtype=int)
    dp[0][0] = 0
    for i in range(1, N+1):
        for j in range(1, M+1):
            candidates = []
            for k in range(j):
                if dp[i-1][k] == -np.inf:
                    continue
                ref = ipa_word_phonemes[i-1]
                hyp = predicted_phonemes[k:j]
                sim = -levenshtein_with_features(ref, hyp)
                score = dp[i-1][k] + sim
                candidates.append((score, k))
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_score, best_k = candidates[0]
                dp[i][j] = best_score
                bp[i][j] = best_k
    if dp[N][M] == -np.inf:
        return [{
            "error": "Alignment failed",
            "IPA_word": "",
            "user_phonemes": [],
        }]
        
    alignment = []
    i, j = N, M
    while i > 0:
        k = bp[i][j]
        ref = ipa_word_phonemes[i-1]
        hyp = predicted_phonemes[k:j]
        
        # Calculate the phonetic distance for this specific word
        distance = levenshtein_with_features(ref, hyp)
        
        # Calculate a similarity score (0-100%) - higher is better
        max_length = max(len(ref), len(hyp))
        similarity = 100 * (1 - (distance / max_length)) if max_length > 0 else 0
        
        alignment.append({
            "IPA_word": ''.join(ref),
            "user_phonemes": hyp,
            "similarity": similarity,
        })
        i -= 1
        j = k
    alignment.reverse()
    return alignment

def tokenize_ipa(ipa_text):
    """
    Properly tokenize IPA text, preserving multi-character phonemes.
    """
    multi_char_symbols = [k for k in IPA_FEATURES.keys() if len(k) > 1]
    multi_char_symbols.sort(key=len, reverse=True)
    tokens = []
    words = ipa_text.split()
    for word in words:
        word_tokens = []
        i = 0
        while i < len(word):
            matched = False
            for symbol in multi_char_symbols:
                if word[i:].startswith(symbol):
                    word_tokens.append(symbol)
                    i += len(symbol)
                    matched = True
                    break
            if not matched:
                word_tokens.append(word[i])
                i += 1
        tokens.append(word_tokens)
    

    return tokens
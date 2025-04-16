import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")
TOGETHERAI_API_KEY = os.getenv("TOGETHER_API_KEY2")

def process_phonemes(sentence: str, sentenceIPA: str, user_phoneme_array, gentle_alignment) -> dict:
    """
    Process the phoneme text by aligning it with the original sentence and passing it to Mistral's LLM.

    Args:
        sentence (str): The original sentence.
        sentenceIPA (str): The IPA transcription of the original sentence.
        phoneme_text (str): The phoneme transcription from the user.

    Returns:
        dict: A dictionary containing the alignment results.
    """
    # Step 1: Split the sentence into words
    sentence_array = sentence.split()  # Example: ["The", "cat", "sat", "on", "the", "mat."]

    # Step 2: Use sentenceIPA directly for sentence_phoneme_array
    sentence_phoneme_array = sentenceIPA.split()  # Example: ["ðə", "kæt", "sæt", "ɔn", "ðə", "mæt"]



    # Step 4: Call Mistral NeMo API for forced alignment
    alignment = align_phonemes_with_mistral(sentence_array, sentence_phoneme_array, user_phoneme_array, gentle_alignment)

    # Step 5: Return the structured data
    return {
        "sentence_array": sentence_array,
        "sentence_phoneme_array": sentence_phoneme_array,
        "user_phoneme_array": user_phoneme_array,
        "alignment": alignment
    }

def align_phonemes_with_mistral(sentence_array, sentence_phoneme_array, user_phoneme_array, gentle_alignment):
    """
    Align the user's phoneme transcription with the original sentence phonemes using Mistral's LLM.

    Args:
        sentence_array (list): List of words in the original sentence.
        sentence_phoneme_array (list): List of IPA phoneme sequences for the original sentence.
        user_phoneme_array (list): List of IPA phoneme groups from the user's transcription.
        gentle_alignment (dict): Alignment data from Gentle.

    Returns:
        list: A list of dictionaries containing the alignment results.
    """
    # Define the system and user prompts
    system_prompt = (
        "You are a forced alignment model. Your task is to align the original sentence words "
        "with the user's phoneme transcription and the Gentle alignment phones. "
        "Return a JSON array where each element maps a word from the original sentence to: "
        "the corresponding phoneme sequence from the original sentence, "
        "the user's phoneme sequence (as a single string), "
        "and the Gentle alignment phones for that word."
    )
    user_prompt = (
        f"Align the following data:\n"
        f"Original Sentence Words: {sentence_array}\n"
        f"Original Sentence Phonemes (IPA): {sentence_phoneme_array}\n"
        f"User's Phonemes (IPA): {user_phoneme_array}\n"
        f"Gentle Alignment Phones: {gentle_alignment}\n"
        "Return ONLY a valid JSON array of objects, where each object has:\n"
        "  - 'word': the word from the original sentence_array\n"
        "  - 'sentence_phoneme': the phoneme sequence from the sentence_phoneme_array\n"
        "  - 'user_phonemes': the user's phonemes for that word, as a single string with NO spaces between phonemes (e.g., 'ðə', not 'ð ə')\n"
        "  - 'gentle_phones': the phones from Gentle alignment for that word\n"
        "Do NOT include any introduction, explanation, or markdown/backticks. Output ONLY the JSON array."
    )

    # Prepare the request payload
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 1.0,
        "stream": False
    }

    # Send the request to Together AI
    together_endpoint = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHERAI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(together_endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            alignment_json = response.json().get("choices", [])[0].get("message", {}).get("content", "[]")
            return alignment_json 
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"Error communicating with Together AI: {e}")
        return []
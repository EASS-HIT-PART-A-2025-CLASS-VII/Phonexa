import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("Mistral API key not found. Please set it in the .env file.")

# Paths to our JSON files
ANIMALS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "animals.json")
AVAILABLE_ANIMALS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "available_animals.json")

def extract_animals_from_sentence(sentence, animal_list):
    """Extract animals mentioned in the sentence"""
    found = []
    for animal in animal_list:
        # Use word boundaries for exact match, case-insensitive
        if re.search(r'\b' + re.escape(animal) + r'\b', sentence, re.IGNORECASE):
            found.append(animal)
    return found

def reset_animals_if_needed():
    """Reset available animals if file doesn't exist or is empty"""
    if not os.path.exists(AVAILABLE_ANIMALS_JSON) or os.path.getsize(AVAILABLE_ANIMALS_JSON) == 0:
        # Copy from the master list
        with open(ANIMALS_JSON, 'r') as f:
            animals = json.load(f)
        
        with open(AVAILABLE_ANIMALS_JSON, 'w') as f:
            json.dump(animals, f)

def generate_advanced_sentence(previous_sentence, feedback):
    # Make sure we have available animals
    reset_animals_if_needed()
    
    # Load available animals
    with open(AVAILABLE_ANIMALS_JSON, 'r') as f:
        available_animals = json.load(f)
    
    # If we're running low on animals (less than 5), reset the list
    if len(available_animals) < 5:
        with open(ANIMALS_JSON, 'r') as f:
            available_animals = json.load(f)
            
        with open(AVAILABLE_ANIMALS_JSON, 'w') as f:
            json.dump(available_animals, f)
    
    animal_list_string = ", ".join(available_animals)

    user_prompt = f"""
You are an English sentence generating machine for a pronunciation game. 
Your task is to generate the next sentence for the user to pronounce, and the sentence must be themed around animals.
Instructions:
1. Only use animals from this list: [{animal_list_string}].
2. If the 'Feedback' is exactly "PERFECT!" or contains only "PERFECT!", generate a new animal-themed sentence that is generally slightly more difficult in terms of pronunciation than the 'Previous Sentence'.
3. If the 'Feedback' contains specific pronunciation advice (e.g., "Try saying X instead of Y"), generate a new animal-themed sentence that specifically includes sounds related to those difficulties to help the user practice.
4. Do NOT reuse the previous sentence's structure, vocabulary, or theme. The new sentence must be unique and introduce new words or patterns.
5. Your response MUST be a valid JSON object containing only two keys: 'sentence' (the new sentence string) and 'sentence_ipa' (the full IPA transcription of the new sentence with spaces between words). Do not include any other text, explanations, or formatting outside the JSON object.
Previous Sentence: "{previous_sentence}"
Feedback: "{feedback}"
"""

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are an English sentence generating machine that provides a JSON object containing a sentence and its IPA (International Phonetic Alphabet) representation with spaces. Ensure the response is a valid JSON object without any additional symbols or formatting."
            },
            {
                "role": "user",
                "content": user_prompt
            },
        ],
        "temperature": 0.9,
        "max_tokens": 120,
        "top_p": 1.0,
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    try:
        return_content = content.strip()
        if return_content.startswith("```json"):
            return_content = return_content.replace("```json", "").replace("```", "").strip()
        return_dict = eval(return_content) if return_content.startswith("{") else {"sentence": "Error generating sentence.", "sentence_ipa": "Error generating IPA."}
    except Exception:
        return_dict = {"sentence": "Error generating sentence.", "sentence_ipa": "Error generating IPA."}
    
    # Extract animals that were used in the generated sentence
    sentence = return_dict.get("sentence", "")
    used_animals = extract_animals_from_sentence(sentence, available_animals)
    
    # Update available animals by removing the ones just used
    updated_available_animals = [animal for animal in available_animals if animal not in used_animals]
    
    # Save the updated list
    with open(AVAILABLE_ANIMALS_JSON, 'w') as f:
        json.dump(updated_available_animals, f)
    
    # Add list of used animals to the response (optional)
    return_dict["used_animals"] = used_animals
    
    return return_dict
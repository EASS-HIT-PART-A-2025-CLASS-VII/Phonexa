import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("Mistral API key not found. Please set it in the .env file.")

# Path to animal JSON files
ANIMALS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "animals.json")
AVAILABLE_ANIMALS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "available_animals.json")

def generate_first_sentence():
    # Reset available_animals.json when starting a new game
    try:
        with open(ANIMALS_JSON, 'r') as f:
            animals = json.load(f)
        
        with open(AVAILABLE_ANIMALS_JSON, 'w') as f:
            json.dump(animals, f)
    except Exception as e:
        print(f"Error resetting animals: {e}")
    
    # Continue with existing functionality
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
                "content": (
                    "You are an English sentence generating machine that provides a JSON object containing a sentence and its IPA (International Phonetic Alphabet) representation with spaces. "
                    "Ensure the response is a valid JSON object without any additional symbols or formatting."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Generate a random basic sentence for pronunciation evaluation and its IPA representation. "
                    "Ensure the response is a valid JSON object without any irrelevant symbols or formatting, ensure the json field names are sentence and sentence_ipa"
                ),
            },
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 1.0,
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    # Extract the content from the LLM response
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        # Try to parse the JSON string returned by the LLM
        return_content = content.strip()
        if return_content.startswith("```json"):
            return_content = return_content.replace("```json", "").replace("```", "").strip()
        return_dict = eval(return_content) if return_content.startswith("{") else {"sentence": "Error generating sentence.", "sentence_ipa": "Error generating IPA."}
    except Exception:
        return_dict = {"sentence": "Error generating sentence.", "sentence_ipa": "Error generating IPA."}
    return return_dict
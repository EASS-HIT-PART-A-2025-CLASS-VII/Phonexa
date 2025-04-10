import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("Mistral API key not found. Please set it in the .env file.")


def analyze_pronunciation_with_llm(sentence, phoneme_text):
    """
    Sends the phoneme text and sentence to the Mistral LLM for pronunciation analysis.

    Parameters:
    sentence (str): The original sentence the user was asked to pronounce.
    phoneme_text (str): The phoneme transcription of the user's pronunciation.

    Returns:
    dict: A JSON response containing feedback, highlighted sentence, and score.
    """
    # Define the system and user messages for the LLM
    system_message = (
"You are an English pronunciation coach. Your task is to analyze a user's pronunciation and provide feedback based on the way the user's prompt'. "
"Always return a valid JSON response. Do not include any text, explanations, or formatting outside the JSON. "
"The JSON must be raw and directly processable by an API. "
"Do not wrap the JSON in backticks or add escape characters unnecessarily."
)

    user_message = (
f"Analyze the user's pronunciation based on the following:\n\n"
f"Target Sentence: {sentence}\n"
f"User's phoneme transcription (individual phonemes in order, not grouped): {phoneme_text}\n\n"

"Instructions:\n"
"1. FIRST, try to group the flat phoneme sequence into word attempts by comparing the number of words in the sentence and common English word phoneme patterns.\n"
"2. You MUST do this before evaluating accuracy.\n"
"3. Use flexible grouping. For example, 'k æ t' and 'kæt' should be treated as the same word.\n"
"4. DO NOT assume every space means a pause—assume it's just a separator between phonemes.\n"
"5. DO NOT penalize phoneme separation. 'k æ t' is equal to 'kæt'.\n"
"6. DO NOT penalize minor vowel variations (e.g., ɛ vs æ) unless they change the word meaning.\n"
"7. ONLY penalize clearly wrong, missing, or added phonemes.\n"
"8. Return feedback for up to 3 incorrect words in this format:\n"
"   'Try saying {correct phonemes} instead of {user phonemes}', using:\n"
"   - <span style='color:green'>...</span> for correct phonemes\n"
"   - <span style='color:red'>...</span> for incorrect ones\n"
"9. Also highlight incorrect words in the sentence using:\n"
"   - <span style='color:red'>...</span> around incorrect words\n"
"10. Return a JSON object with 3 keys:\n"
"   - \"highlighted_sentence\": The sentence with incorrect words wrapped\n"
"   - \"try_saying\": The feedback array (up to 3 items)\n"
"   - \"score\": A number from 0 to 100 (100 if all phonemes are correct, even if separated)\n\n"

"STRICT RULES:\n"
"- Do NOT wrap the JSON in backticks.\n"
"- Do NOT include any text outside the JSON.\n"
"- Do NOT penalize phoneme separation.\n"
"- DO group the phonemes into words first.\n"
)

    # API call to the Mistral LLM
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",  # Correct endpoint
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",  # Specify the model name
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 1.0,
                "stream": False
            }
        )
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.json()  # Return the JSON response from the LLM
    except requests.exceptions.RequestException as e:
        print(f"Error in LLM API call: {e}")
        raise ValueError("Failed to get a response from the LLM.")
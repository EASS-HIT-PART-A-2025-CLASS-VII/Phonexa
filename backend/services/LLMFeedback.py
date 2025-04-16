import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not MISTRAL_API_KEY or not TOGETHER_API_KEY:
    raise ValueError("Mistral API key not found. Please set it in the .env file.")


def analyze_pronunciation_with_llm(alignment_results):

    # Define the system and user messages for the LLM
    system_message = (
        "You are an English pronunciation coach. Your task is to analyze a user's pronunciation and provide feedback based on the user's prompt. "
        "Always return a valid JSON response. Do not include any text, explanations, or formatting outside the JSON. "
        "The JSON must be raw and directly processable by an API. "
        "Do not wrap the JSON in backticks or add escape characters unnecessarily."
    )

    user_message = (
        f"Provide feedback for the user's pronunciation based on the following:\n\n"
        f"Alignment Results: {alignment_results}\n"


        "Instructions:\n"
        " * Locate up to the three of the most incorrect words in the user's phoneme transcription.\n"
        " * If the phoneme transcription is perfectly matching (no difference to sentence phonemes), The feedback array will contain a single string saying 'PERFECT!' and the score will be 100.\n"

        "Return a JSON object with 3 keys:\n"
        "   - \"highlighted_sentence\": The original sentence with incorrect words wrapped in red HTML colour tag.\n"
        "   - \"try_saying\": The feedback array, each try_saying format:  'Try saying <font color = 'green'>{correct phonemes of the word}</font> instead of <font color = 'red'>{user incorrect phenomes representing word attempt}</font>' \n"
        "   - \"score\": A number from 0 to 100.\n\n"

        "STRICT RULES:\n"
        "- Do NOT wrap the JSON in backticks.\n"
        "- Do NOT include any text outside the JSON.\n"
        "- Review try_saying array strictly, if one of the sentences IPA's identical, scrape it off the array.\n"
    )

      # API call to Together's Llama-3-70B-Instruct-Turbo-Free
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
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
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in LLM API call: {e}")
        raise ValueError("Failed to get a response from the LLM.")
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
        f"Analyze the pronunciation alignment data below and generate feedback:\n\n"
        f"```json\n{alignment_results}\n```\n\n"
        "Instructions:\n"
        "1.  **Identify Errors:** Compare `IPA_word` and `user_phonemes` for each word. Find up to 3 words where they differ.\n"
        "2.  **Calculate Score:** Score is 100 if no errors found. Otherwise, score is `max(0, 100 - (number_of_error_words * 15))`.\n"
        "3.  **Generate JSON Output:** Create a JSON object with these exact keys:\n"
        "    *   `\"score\"`: The calculated score (number).\n"
        "    *   `\"highlighted_sentence\"`: The original `sentence` string, wrapping the English words corresponding to the identified errors in `<font color='red'>...</font>`.\n"
        "    *   `\"try_saying\"`: An array. If score is 100, it contains `[\"PERFECT!\"]`. Otherwise, it contains one string per error word (max 3), formatted exactly as: `'Try saying <font color='green'>{IPA_word}</font> instead of <font color='red'>{user_phonemes joined}</font>'`. **Only include entries for actual differences.**\n\n"
        "**Output Requirements:**\n"
        "- Return ONLY the raw JSON object.\n"
        "- Ensure `try_saying` only contains feedback for actual errors or \"PERFECT!\"."
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
                "temperature": 0.5,
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
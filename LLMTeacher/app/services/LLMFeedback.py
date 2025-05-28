import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment
MISTRAL_API_KEY = os.getenv("FASTAPI_APP_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY2")

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
    "Follow these steps in order:\n"
    "1. **Identify Mispronounced Words:**\n"
    "   - Examine each entry by comparing `IPA_word` (correct pronunciation) and `user_phonemes` (user's pronunciation).\n"
    "   - Using your linguistic expertise, identify up to 3 words that are most severely mispronounced. \n"
    "   - Use the `similarity` field to determine the severity of the mispronunciation.\n"
    "   - If the similarity is less than 85%, consider it a mispronunciation.\n"
    "   - Focus on major phonetic differences that would affect comprehensibility and accent quality.\n\n"
    "2. **Create Feedback Array:**\n"
    "   - For each mispronounced word identified from step 1, create a feedback object with the 2 fields: 'en_word: {word}, wrong_word: {user_phonemes}, right_word: {IPA_word}'\n"
    "   - If no mispronounced words found, set feedback to `[\"PERFECT!\"]`\n\n"
    "3. **Calculate Score:**\n"
    "   - If no mispronounced words: score = 100\n"
    "   - Otherwise: score = max(0, 100 - (number_of_mispronounced_words * 10))\n\n"
    "4. **Create Highlighted Sentence:**\n"
    "   - Start with the original `sentence` string.\n"
    "   - ONLY highlight words identified in step 1 and 2 as `<font color='red'>en_word</font>`\n"
    "   - All other words should remain unchanged (no tags).\n"
    "   - Maintain exact spacing and punctuation of the original sentence.\n\n"
    "5. **Return JSON Response:**\n"
    "   \n"
    "   {\n"
    "     \"score\": [calculated score],\n"
    "     \"highlighted_sentence\": [sentence with ONLY mispronounced words highlighted],\n"
    "     \"try_saying\": [array of feedback objects created in step 2]\n"
    "   }\n"
    "   \n\n"
    "**Important:**\n"
    "- There MUST be perfect correspondence between words in `try_saying` and highlighted words in `highlighted_sentence`\n"
    "- DO NOT highlight correctly pronounced words, only mark mispronounced words as red.\n"
    "- Use the `word` field from each entry to determine the English word to highlight in the sentence.\n"
    "- Return ONLY the raw JSON object with no additional commentary."
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
import os
from dotenv import load_dotenv

def test_env_keys_exist():
    """
    Test that required API keys are present in the environment.
    """
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

    fastapi_key = os.getenv("FASTAPI_APP_API_KEY")
    together_key = os.getenv("TOGETHER_API_KEY2")
    azure_key = os.getenv("AZURE_SPEECH_KEY")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")

    assert fastapi_key is not None and fastapi_key != "", "FASTAPI_APP_API_KEY is missing"
    assert together_key is not None and together_key != "", "TOGETHER_API_KEY2 is missing"
    assert azure_key is not None and azure_key != "", "AZURE_SPEECH_KEY is missing"
    assert azure_endpoint is not None and azure_endpoint != "", "AZURE_ENDPOINT is missing"

# Run the test when this file is executed directly
if __name__ == "__main__":
    test_env_keys_exist()
    print("All required API keys are present.")
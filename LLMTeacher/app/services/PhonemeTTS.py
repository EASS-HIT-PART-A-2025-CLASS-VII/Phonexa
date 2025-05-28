import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

class PhonemeTTS:
    def __init__(self):
        """Initialize Azure Speech SDK with credentials from environment variables."""
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = "westeurope"  # Extracted from your endpoint
        
        if not self.speech_key:
            raise ValueError("AZURE_SPEECH_KEY environment variable is not set")
        
        # Create speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, 
            region=self.speech_region
        )
        
        # Set the voice to match tts_service.py
        self.speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
        
        # Set output format for better quality
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

    async def generate_phoneme_audio_blob(self, phonetic_word: str) -> bytes:
        """
        Generate TTS audio from phonetic transcription and return as bytes.
        
        Args:
            phonetic_word (str): The word in phonetic notation (IPA or similar)
            
        Returns:
            bytes: Audio data as bytes
            
        Raises:
            RuntimeError: If TTS generation fails
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filepath = temp_file.name
            
            # Create audio config for file output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_filepath)
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Create SSML with phonetic pronunciation
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="en-US-AvaMultilingualNeural">
                    <phoneme alphabet="ipa" ph="{phonetic_word}">{phonetic_word}</phoneme>
                </voice>
            </speak>
            """
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()
            
            # Check if synthesis was successful
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Read the file content
                with open(temp_filepath, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Clean up the temporary file
                try:
                    os.remove(temp_filepath)
                except:
                    pass
                    
                if not audio_data or len(audio_data) == 0:
                    raise RuntimeError("TTS output is empty")
                return audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                raise RuntimeError(f"Speech synthesis canceled: {cancellation_details.reason}")
            else:
                raise RuntimeError(f"Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            raise RuntimeError(f"Failed to generate phoneme audio: {str(e)}")


# Convenience function for easy usage
async def generate_phoneme_audio_bytes(phonetic_word: str) -> bytes:
    """
    Convenience function to generate phoneme TTS audio as bytes.
    
    Args:
        phonetic_word (str): The word in phonetic notation
        
    Returns:
        bytes: Audio data as bytes
    """
    tts = PhonemeTTS()
    return await tts.generate_phoneme_audio_blob(phonetic_word)
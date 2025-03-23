from gtts import gTTS
from googletrans import Translator
import os
import tempfile
from typing import Tuple

class TextToSpeechService:
    def __init__(self):
        """Initialize the Text-to-Speech service"""
        self.translator = Translator()
    
    def translate_to_hindi(self, text: str) -> str:
        """
        Translate text from English to Hindi.
        
        Args:
            text: English text to translate
            
        Returns:
            Hindi translation of the text
        """
        try:
            # Strip the text to avoid issues with long inputs
            if len(text) > 5000:
                text = text[:5000] + "..."
                
            translation = self.translator.translate(text, dest='hi')
            return translation.text
        except Exception as e:
            print(f"Error translating text to Hindi: {e}")
            return text  # Return original text if translation fails
    
    def text_to_speech(self, text: str, lang: str = 'hi') -> Tuple[str, str]:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: Text to convert to speech
            lang: Language code (default is Hindi 'hi')
            
        Returns:
            Tuple of (file_path, temp_dir) where file_path is the path to the audio file
            and temp_dir is the temporary directory that should be cleaned up later
        """
        try:
            # Create a temporary directory to store the audio file
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, 'speech.mp3')
            
            # Generate the speech and save to file
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(file_path)
            
            return file_path, temp_dir
        
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None, None
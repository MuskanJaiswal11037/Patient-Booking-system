import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional

def text_to_speech(text: str, voice: str = "alloy") -> Optional[bytes]:
    if len(text) > 4096:
        text = text[:4096]
    try:
        load_dotenv()  # Load environment variables from .env file
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
        )
 
        # Stream the audio bytes back
        audio_bytes = response.content
        return audio_bytes
    except Exception as e:
        Exception(f"TTS error: {str(e)}")

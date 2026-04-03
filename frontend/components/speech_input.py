"""Speech input component for audio recording and playback."""
import streamlit as st
import base64
from io import BytesIO
import time


def play_audio(audio_bytes: bytes, autoplay: bool = False):
    """
    Play audio using Streamlit's audio player with autoplay support.
    
    Parameters
    ----------
    audio_bytes : bytes
        Raw audio bytes (MP3 or WAV)
    autoplay : bool
        Whether to autoplay the audio
    """
    print(f"DEBUG: play_audio called with autoplay={autoplay}, audio_bytes size={len(audio_bytes) if audio_bytes else 0}")
    
    if audio_bytes:
        print(f"DEBUG: Audio bytes exist, autoplay={autoplay}")
        if autoplay:
            print("DEBUG: Autoplay is True, rendering HTML audio")
            # Initialize audio playing state
            if "audio_playing" not in st.session_state:
                st.session_state.audio_playing = True
            
            # Use HTML5 audio with autoplay for automatic playback
            b64 = base64.b64encode(audio_bytes).decode()
            
            # Create unique ID using timestamp
            audio_id = f"audio_{int(time.time() * 1000000)}"
            
            html_audio = f'''
            <audio id="{audio_id}" autoplay preload="auto" controls style="width: 100%;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
            <script>
                var audio = document.getElementById("{audio_id}");
                audio.onended = function() {{
                    window.parent.postMessage({{"type": "streamlit:setComponentValue", "value": {{"audio_ended": true}}}}, "*");
                }};
            </script>
            '''
            st.markdown(html_audio, unsafe_allow_html=True)
            return True
        else:
            st.audio(audio_bytes, format="audio/mp3")
            return False


def render_text_to_speech_button(text: str, key_suffix: str = None) -> bool:
    """
    Render a button to convert text to speech.
    
    Parameters
    ----------
    text : str
        Text to convert to speech
    key_suffix : str, optional
        Unique suffix to append to the button key. If not provided, only text hash is used.
        It's recommended to pass a unique identifier (like message index) to avoid duplicate keys.
    
    Returns
    -------
    bool
        True if button clicked, False otherwise
    """
    if not text or not text.strip():
        return False
    
    # Generate unique key combining text hash and suffix
    if key_suffix is not None:
        unique_key = f"tts_btn_{hash(text)}_{key_suffix}"
    else:
        unique_key = f"tts_btn_{hash(text)}"
    
    return st.button(
        "🔊 Play response",
        use_container_width=True,
        key=unique_key
    )


def create_download_link(audio_bytes: bytes, filename: str = "audio.mp3"):
    """
    Create a download link for audio.
    
    Parameters
    ----------
    audio_bytes : bytes
        Audio data to download
    filename : str
        Download filename
    
    Returns
    -------
    str
        HTML download link
    """
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Download Audio</a>'
    return href

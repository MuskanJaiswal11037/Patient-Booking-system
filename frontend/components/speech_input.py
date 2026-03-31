"""Speech input component for audio recording and playback."""
import streamlit as st
import base64
from io import BytesIO


def render_audio_recorder():
    """
    Render an audio recording widget using Streamlit.
    
    Returns
    -------
    bytes or None
        Raw audio bytes if recording exists, None otherwise
    """
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
    
    col1, col2 = st.columns([5, 2])
    
    with col1:
        # Streamlit's built-in audio_input (requires Python 3.8+)
        audio_bytes = st.audio_input(
            label="🎤 Record your message",
            label_visibility="collapsed"
        )
        
        if audio_bytes:
            st.session_state.audio_data = audio_bytes
            return audio_bytes
    
    
    # with col2:
    #     # Clear button
    #     if st.session_state.audio_data is not None:
    #         if st.button("🗑️ Clear"):
    #             st.session_state.audio_data = None
    #             st.rerun()
    
    return st.session_state.audio_data


def play_audio(audio_bytes: bytes, autoplay: bool = False):
    """
    Play audio using Streamlit's audio player.
    
    Parameters
    ----------
    audio_bytes : bytes
        Raw audio bytes (MP3 or WAV)
    autoplay : bool
        Whether to autoplay the audio
    """
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")


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

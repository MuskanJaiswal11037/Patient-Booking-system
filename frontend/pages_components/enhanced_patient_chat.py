"""Enhanced patient chat component with speech and audio management."""
import streamlit as st
from components.api import send_chat_message, transcribe_audio, text_to_speech
from components.utils import get_chat_history, add_chat_message
from components.speech_input import render_audio_recorder
from components.audio_utils import (
    AudioCache,
    AudioMetrics,
    StreamlitAudioState,
    validate_audio_bytes,
    validate_text_for_tts,
    render_voice_selector,
    render_audio_debug_info,
)


def render_enhanced_patient_chat_page():
    """
    Render enhanced patient chat page with full speech functionality.
    
    Features:
    - Voice recording and transcription
    - Text-to-speech responses
    - Audio caching to reduce API calls
    - Voice selection
    - Usage metrics
    """
    # Initialize audio state
    StreamlitAudioState.init_audio_state()
    
    st.title("💬 Book an Appointment")
    st.caption("Talk naturally — describe your doctor and preferred time.")
    
    # Settings sidebar
    with st.sidebar:
        st.subheader("🎵 Audio Settings")
        st.session_state.selected_voice = render_voice_selector(
            st.session_state.get("selected_voice", "alloy")
        )
        
        # Show metrics if in debug mode
        if st.checkbox("📊 Show Usage Stats"):
            render_audio_debug_info()
    
    # Render conversation history
    render_chat_history()
    
    # Input section
    st.divider()
    render_input_section()


def render_chat_history():
    """Render conversation history with audio playback options."""
    chat_container = st.container()
    with chat_container:
        history = get_chat_history()
        
        if not history:
            st.info("💬 Start by typing or speaking your appointment request!")
            return
        
        for idx, msg in enumerate(history):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Add TTS button for assistant messages
                if msg["role"] == "assistant" and msg.get("content"):
                    render_audio_playback_button(msg["content"], idx)


def render_audio_playback_button(text: str, message_idx: int):
    """
    Render play/download buttons for assistant responses.
    
    Parameters
    ----------
    text : str
        Text to convert to speech
    message_idx : int
        Index of the message in history
    """
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔊 Play", key=f"play_{message_idx}", use_container_width=True):
            play_response_audio(text, message_idx)
    
    with col2:
        if st.button("🗑️ Clear", key=f"clear_{message_idx}", use_container_width=True):
            if message_idx in st.session_state.playing_audio:
                del st.session_state.playing_audio[message_idx]
                st.rerun()
    
    # Show audio player if audio is available
    if message_idx in st.session_state.playing_audio:
        with col3:
            st.audio(st.session_state.playing_audio[message_idx], format="audio/mp3")


def play_response_audio(text: str, message_idx: int):
    """
    Play or cache assistant response audio.
    
    Parameters
    ----------
    text : str
        Text to convert to speech
    message_idx : int
        Index for caching
    """
    with st.spinner("🔊 Generating speech..."):
        # Check cache first
        voice = st.session_state.get("selected_voice", "alloy")
        cached_audio = AudioCache.get_cached_audio(text, voice)
        
        if cached_audio:
            st.session_state.playing_audio[message_idx] = cached_audio
            AudioMetrics.log_tts(text)
        else:
            # Generate new audio
            audio_bytes = text_to_speech(text, voice)
            if audio_bytes:
                # Cache and store
                AudioCache.cache_audio(text, audio_bytes, voice)
                st.session_state.playing_audio[message_idx] = audio_bytes
                AudioMetrics.log_tts(text)
                del st.session_state.playing_audio[message_idx]
                st.rerun()
            else:
                st.error("Failed to generate speech. Please try again.")


def render_input_section():
    """Render input section with text and voice options."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        typed = st.chat_input("Type your message…")
    
    with col2:
        st.write("")  # Spacing for alignment

    # Audio recording section
    st.write("**Or use your voice:**")
    audio_bytes = render_audio_recorder()

    # Process input (prevent multiple submissions by clearing audio immediately)
    if typed:
        handle_chat_message(typed)
    elif audio_bytes and validate_audio_bytes(audio_bytes):
        # Store audio in temp variable and immediately clear session state
        # This prevents the same audio from being processed on next rerun
        temp_audio = audio_bytes
        st.session_state.audio_data = None
        handle_voice_message(temp_audio)


def handle_voice_message(audio_bytes: bytes):
    """
    Process voice message.
    
    Parameters
    ----------
    audio_bytes : bytes
        Raw audio data
    """
    with st.spinner("🎤 Converting speech to text..."):
        transcribed_text = transcribe_audio(audio_bytes)
        
        if transcribed_text and validate_text_for_tts(transcribed_text):
            AudioMetrics.log_transcription(len(audio_bytes), transcribed_text)
            st.success(f"✓ Heard: *{transcribed_text}*")

            # Clear cache after voice is converted to text
            AudioCache.clear_cache()
            
            handle_chat_message(transcribed_text)
        else:
            st.error("❌ Could not understand the audio. Please try again.")


def handle_chat_message(message_text: str):
    """
    Process and send chat message.
    
    Parameters
    ----------
    message_text : str
        The message to send
    """
    if not message_text or not message_text.strip():
        return
    
    # Add user message
    add_chat_message("user", message_text)
    with st.chat_message("user"):
        st.markdown(message_text)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("💭 MedBot is thinking…"):
            response = send_chat_message(message_text)
        
        if response and response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            
            if reply:
                st.markdown(reply)
                add_chat_message("assistant", reply)
                
                # Offer audio playback
                voice = st.session_state.get("selected_voice", "alloy")
                if validate_text_for_tts(reply):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button("🔊 Play Response", key=f"tts_new_{len(get_chat_history())}"):
                            play_response_audio(reply, len(get_chat_history()) - 1)
            else:
                st.error("Empty response from assistant")
        elif response:
            error_msg = response.json().get("detail", "Unknown error") if response else "Connection failed"
            st.error(f"❌ {error_msg}")
            add_chat_message("assistant", f"Error: {error_msg}")
    st.rerun()


# Export for use in main app
if __name__ == "__main__":
    render_enhanced_patient_chat_page()

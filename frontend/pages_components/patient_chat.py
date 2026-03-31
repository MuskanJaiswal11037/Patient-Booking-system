"""Patient chat page component."""
import streamlit as st
from datetime import datetime
from components.api import send_chat_message, transcribe_audio, text_to_speech
from components.utils import get_chat_history, add_chat_message
from components.speech_input import render_audio_recorder, render_text_to_speech_button, play_audio
from components.audio_utils import AudioCache, StreamlitAudioState

StreamlitAudioState.init_audio_state()


def render_patient_chat_page():
    """Render patient chat page for booking appointments."""
    st.title("💬 Book an Appointment")
    st.caption("Talk naturally — describe your doctor and preferred time.")

    # Initialize session state for audio playback
    if "playing_audio" not in st.session_state:
        st.session_state.playing_audio = {}
    
    # Initialize flag to track if audio was just processed
    if "audio_processed" not in st.session_state or st.session_state.audio_processed is None:
        st.session_state.audio_processed = False

    # Render conversation history
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(get_chat_history()):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Add play button for assistant messages
                if msg["role"] == "assistant":
                    if render_text_to_speech_button(msg["content"], key_suffix=str(idx)):
                        with st.spinner("🔊 Generating speech..."):
                            audio_bytes = text_to_speech(msg["content"])
                            if audio_bytes:
                                st.session_state.playing_audio[idx] = audio_bytes
                                st.rerun()
                
                # Play audio if available
                if msg["role"] == "assistant" and idx in st.session_state.playing_audio:
                    st.audio(st.session_state.playing_audio[idx], format="audio/mp3")

    # Input section with both text and speech options
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        typed = st.chat_input("Type your message…")
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing

    # Audio recording section
    st.write("**Or use your voice:**")
    audio_bytes = render_audio_recorder()
    # Add a submit button for voice input
    submitted = st.button("Submit Voice Input")
    print(submitted, audio_bytes)  # Debugging output

    # Handle input (prevent multiple submissions by using flags)
    if typed:
        # Handle text input
        handle_chat_message(typed)
    elif submitted and audio_bytes:
        # Mark audio as processed BEFORE processing it
        st.session_state.audio_processed = True

        # Handle speech input
        with st.spinner("🎤 Converting speech to text..."):
            transcribed_text = transcribe_audio(audio_bytes)
            if transcribed_text:
                st.success(f"✓ Heard: *{transcribed_text}*")
                # Clear cache after voice is converted to text
                AudioCache.clear_cache()
            else:
                st.error("❌ Could not transcribe audio. Please try again.")
                st.session_state.audio_processed = False  # Reset flag on error
                return

        # Send message and handle response WITHOUT calling st.rerun() inside
        if transcribed_text and transcribed_text.strip():
            # Add user message
            add_chat_message("user", transcribed_text)
            with st.chat_message("user"):
                st.markdown(transcribed_text)

            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("💭 MedBot is thinking…"):
                    response = send_chat_message(transcribed_text)

                if response and response.status_code == 200:
                    data = response.json()
                    reply = data["reply"]
                    st.markdown(reply)

                    # Add to chat history
                    add_chat_message("assistant", reply)

                    # Offer to play response as audio
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("🔊 Play", key=f"tts_new_{len(get_chat_history())}"):
                            with st.spinner("🔊 Generating speech..."):
                                audio_bytes_response = text_to_speech(reply)
                                if audio_bytes_response:
                                    play_audio(audio_bytes_response)
                elif response:
                    error_msg = response.json().get("detail", "Error") if response else "Unknown error"
                    st.error(f"❌ {error_msg}")
                    add_chat_message("assistant", f"Error: {error_msg}")

            # Reset flag and rerun AFTER all processing
            st.session_state.audio_data = None  # Clear audio data after processing
            StreamlitAudioState.reset_state()  # Reset audio state for next recording
            st.rerun()


def handle_chat_message(message_text: str):
    """
    Process and send chat message, handle response with optional TTS.
    
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
            reply = data["reply"]
            st.markdown(reply)

            # Add to chat history
            add_chat_message("assistant", reply)
            
            # Offer to play response as audio
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔊 Play", key=f"tts_new_{len(get_chat_history())}"):
                    with st.spinner("🔊 Generating speech..."):
                        audio_bytes = text_to_speech(reply)
                        if audio_bytes:
                            play_audio(audio_bytes)
        elif response:
            error_msg = response.json().get("detail", "Error") if response else "Unknown error"
            st.error(f"❌ {error_msg}")
            add_chat_message("assistant", f"Error: {error_msg}")

    st.rerun()
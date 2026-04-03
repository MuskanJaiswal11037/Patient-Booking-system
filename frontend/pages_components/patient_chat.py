"""Patient chat page component."""
import streamlit as st
from datetime import datetime

from streamlit_webrtc import webrtc_streamer
from components.api import send_chat_message
from components.utils import get_chat_history, add_chat_message
from components.speech_input import  render_text_to_speech_button
from components.audio_utils import text_to_speech
import numpy as np
import os
import streamlit.components.v1 as _stc

_VOICE_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "components", "voice_input")
_voice_input = _stc.declare_component("voice_input", path=_VOICE_COMPONENT_DIR)

if "_pending_tts_audio" not in st.session_state:
    st.session_state._pending_tts_audio = None

def render_patient_chat_page():
    """Render patient chat page for booking appointments."""
    st.title("💬 Book an Appointment")
    st.caption("Talk naturally — describe your doctor and preferred time.")

    
    # Render conversation history
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(get_chat_history()):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if "_pending_tts_audio" in st.session_state and st.session_state._pending_tts_audio:
        # _tts_bytes = st.session_state.pop("_pending_tts_audio")
        st.audio(st.session_state._pending_tts_audio, format="audio/mpeg", autoplay=True)
    

    # Input section with both text and speech options
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        typed = st.chat_input("Type your message…")
    
    with col2:
        if 'voice_mode' not in st.session_state: st.session_state.voice_mode = False
        voice_label = "🔊 Voice On" if st.session_state.voice_mode else "🔇 Voice Off"
        if st.button(voice_label, use_container_width=True, key="toggle_voice"):
            st.session_state.voice_mode = not st.session_state.voice_mode
            if not st.session_state.voice_mode:
                st.session_state.pop("_pending_tts_audio")
            st.rerun()

    # Handle input (prevent multiple submissions by using flags)
    if typed:
        # Handle text input
        handle_chat_message(typed)
    elif st.session_state.voice_mode:
        # ── Mic input (voice mode) ──
        # Hands-free mode: Web Speech API (Chrome/Edge) — no tap needed per message
        _voice_result = _voice_input(
            auto_start=True,
            resume=True,
            key="voice_input",
            default=None,
        )
        if _voice_result and isinstance(_voice_result, dict) and _voice_result.get("transcript"):
            _vts = _voice_result.get("ts", 0)
            # Check if this is new voice input
            if _vts != st.session_state.get("_last_voice_ts"):
                st.session_state._last_voice_ts = _vts
                _vtxt = _voice_result["transcript"].strip()
                if _vtxt:
                    st.caption(f'🗣️ *"{_vtxt}"*')
                    # Process message immediately to clear old audio
                    handle_chat_message(_vtxt)  
        else: 
            print("DEBUG: No valid voice result yet or waiting for user to speak...")
        #     st.info("⏳ Waiting for audio to finish playing... Click 'Pause' to stop it.")

def _autoplay_audio(audio_bytes: bytes):
    """Queue TTS audio for playback after next rerun (survives st.rerun cycle)."""
    st.session_state._pending_tts_audio = audio_bytes

def handle_chat_message(message_text: str):
    """
    Process and send chat message, handle response with optional TTS.
    
    Parameters
    ----------
    message_text : str
        The message to send
    audio_container : streamlit.container
        Container for rendering audio
    """
    if not message_text or not message_text.strip():
        return
    
    
    # Clear previous audio when processing new message
    st.session_state.playing_audio = {}
    st.session_state.audio_playing = False
    
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
                if st.session_state.voice_mode:
                    with st.spinner("🔊 Generating speech..."):
                        audio_bytes = text_to_speech(reply)
                    if audio_bytes:
                        msg_idx = len(get_chat_history()) - 1  # assistant message index
                        st.session_state.audio_playing = True  # Set flag when audio starts
                        # Render audio to container
                        # with audio_container:
                        _autoplay_audio(audio_bytes=audio_bytes)
                        
        elif response:
            error_msg = response.json().get("detail", "Error") if response else "Unknown error"
            st.error(f"❌ {error_msg}")
            add_chat_message("assistant", f"Error: {error_msg}")

        st.rerun()
    
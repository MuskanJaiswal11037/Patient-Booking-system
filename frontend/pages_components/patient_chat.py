"""Patient chat page component."""
import streamlit as st
from datetime import datetime
from components.api import send_chat_message
from components.utils import get_chat_history, add_chat_message


def render_patient_chat_page():
    """Render patient chat page for booking appointments."""
    st.title("💬 Book an Appointment")
    st.caption("Talk naturally — describe your doctor and preferred time.")

    # Render conversation history
    chat_container = st.container()
    with chat_container:
        for msg in get_chat_history():
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    typed = st.chat_input("Type your message…")
    if typed:
        # Add user message
        add_chat_message("user", typed)
        with st.chat_message("user"):
            st.markdown(typed)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("MedBot is thinking…"):
                response = send_chat_message(typed)
            
            if response and response.status_code == 200:
                data = response.json()
                reply = data["reply"]
                st.markdown(reply)

                # Add to chat history
                add_chat_message("assistant", reply)
            elif response:
                error_msg = response.json().get("detail", "Error")
                st.error(f"❌ {error_msg}")
                add_chat_message("assistant", f"Error: {error_msg}")

        st.rerun()



# Speech Functionality - Integration Guide

## Quick Start

### Option 1: Basic Chat with Speech (Simple)
Use the updated `patient_chat.py` for straightforward speech-to-text and text-to-speech.

#### In your main app file (e.g., `streamlit_app.py`):
```python
from pages_components.patient_chat import render_patient_chat_page

# In your page router
if selected_page == "Book Appointment":
    render_patient_chat_page()
```

### Option 2: Enhanced Chat with Caching & Analytics (Advanced)
Use the `enhanced_patient_chat.py` for production-ready features with metrics tracking.

#### In your main app file:
```python
from pages_components.enhanced_patient_chat import render_enhanced_patient_chat_page

# In your page router
if selected_page == "Book Appointment":
    render_enhanced_patient_chat_page()
```

## Feature Comparison

| Feature | Basic | Enhanced |
|---------|-------|----------|
| Speech-to-Text | ✅ | ✅ |
| Text-to-Speech | ✅ | ✅ |
| Voice Selection | ❌ | ✅ |
| Audio Caching | ❌ | ✅ |
| Usage Metrics | ❌ | ✅ |
| Debug Tools | ❌ | ✅ |
| Code Complexity | Low | Medium |

## Component Reference

### API Functions (`components/api.py`)

#### `transcribe_audio(audio_bytes, filename)`
Convert audio to text using OpenAI Whisper.

**Parameters:**
- `audio_bytes` (bytes): Raw audio data
- `filename` (str): Filename with extension (e.g., "audio.wav")

**Returns:** `str` or `None` - Transcribed text or None on error

**Example:**
```python
from components.api import transcribe_audio

audio_bytes = ...  # Your audio data
text = transcribe_audio(audio_bytes, "audio.wav")
if text:
    print(f"Transcribed: {text}")
```

---

#### `text_to_speech(text, voice)`
Convert text to speech using OpenAI TTS.

**Parameters:**
- `text` (str): Text to convert
- `voice` (str): Voice name - "alloy", "echo", "fable", "onyx", "nova", "shimmer"

**Returns:** `bytes` or `None` - Audio MP3 bytes or None on error

**Example:**
```python
from components.api import text_to_speech

reply = "Your appointment is booked for Monday"
audio_bytes = text_to_speech(reply, voice="alloy")
if audio_bytes:
    st.audio(audio_bytes, format="audio/mp3")
```

---

### UI Components (`components/speech_input.py`)

#### `render_audio_recorder()`
Render Streamlit audio recording widget.

**Returns:** `bytes` or `None` - Recorded audio or None if no recording

**Example:**
```python
from components.speech_input import render_audio_recorder

audio = render_audio_recorder()
if audio:
    print(f"Recorded {len(audio)} bytes")
```

---

#### `play_audio(audio_bytes, autoplay)`
Play audio using Streamlit player.

**Parameters:**
- `audio_bytes` (bytes): Audio data
- `autoplay` (bool): Whether to autoplay (default: False)

**Example:**
```python
from components.speech_input import play_audio

if audio_bytes:
    play_audio(audio_bytes, autoplay=True)
```

---

#### `render_text_to_speech_button(text)`
Render a button to trigger TTS for text.

**Parameters:**
- `text` (str): Text to convert

**Returns:** `bool` - True if button clicked

**Example:**
```python
from components.speech_input import render_text_to_speech_button

if render_text_to_speech_button("Click to hear this"):
    audio = text_to_speech("Click to hear this")
```

---

### Utilities (`components/audio_utils.py`)

#### `AudioCache` Class
Cache audio responses to minimize API calls.

**Methods:**
```python
# Check cache before API call
cached = AudioCache.get_cached_audio(text, voice="alloy")

# Store audio in cache
AudioCache.cache_audio(text, audio_bytes, voice="alloy")

# Clear all cached audio
AudioCache.clear_cache()
```

**Example:**
```python
from components.audio_utils import AudioCache

# Check if we have this cached
audio = AudioCache.get_cached_audio("Hello world")

if not audio:
    # Generate new if not cached
    audio = text_to_speech("Hello world")
    if audio:
        AudioCache.cache_audio("Hello world", audio)
```

---

#### `AudioMetrics` Class
Track audio usage for analytics.

**Methods:**
```python
# Log transcription
AudioMetrics.log_transcription(audio_bytes_count, text)

# Log TTS
AudioMetrics.log_tts(text)

# Get metrics
metrics = AudioMetrics.get_metrics()

# Reset
AudioMetrics.reset_metrics()
```

**Example:**
```python
from components.audio_utils import AudioMetrics

AudioMetrics.log_tts("Your appointment is confirmed")
metrics = AudioMetrics.get_metrics()
print(f"TTS calls: {metrics['tts_requests']}")
```

---

#### `StreamlitAudioState` Class
Manage session state for audio components.

**Methods:**
```python
# Initialize audio state
StreamlitAudioState.init_audio_state()

# Get all audio state
state = StreamlitAudioState.get_state()

# Reset to default
StreamlitAudioState.reset_state()
```

---

## Implementation Examples

### Example 1: Simple Voice Chat
```python
import streamlit as st
from components.api import transcribe_audio, text_to_speech, send_chat_message
from components.speech_input import render_audio_recorder
from components.utils import get_chat_history, add_chat_message

st.title("Simple Voice Chat")

# Display history
for msg in get_chat_history():
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Get voice input
audio = render_audio_recorder()

if audio:
    text = transcribe_audio(audio)
    if text:
        # Send to chat
        add_chat_message("user", text)
        response = send_chat_message(text)
        
        if response:
            reply = response.json()["reply"]
            add_chat_message("assistant", reply)
            
            # Play response
            audio_reply = text_to_speech(reply)
            if audio_reply:
                st.audio(audio_reply, format="audio/mp3")
```

### Example 2: Custom Voice Selection
```python
import streamlit as st
from components.api import text_to_speech
from components.audio_utils import render_voice_selector

st.title("Multi-Voice TTS")

voice = render_voice_selector(default_voice="alloy")
text = st.text_area("Enter text to convert:")

if st.button("Convert to Speech"):
    if text:
        audio = text_to_speech(text, voice=voice)
        if audio:
            st.audio(audio, format="audio/mp3")
            
            # Download option
            st.download_button(
                label="Download Audio",
                data=audio,
                file_name=f"speech_{voice}.mp3",
                mime="audio/mp3"
            )
```

### Example 3: With Error Handling
```python
import streamlit as st
from components.api import transcribe_audio, text_to_speech
from components.audio_utils import validate_audio_bytes, validate_text_for_tts

st.title("Robust Voice Chat")

audio = st.audio_input("Record message")

if audio:
    # Validate audio
    if not validate_audio_bytes(audio):
        st.error("Audio file too small or invalid")
    else:
        # Transcribe
        text = transcribe_audio(audio)
        if text:
            st.success(f"Transcribed: {text}")
            
            # Validate text
            if validate_text_for_tts(text):
                # Convert to speech
                audio_reply = text_to_speech(text)
                if audio_reply:
                    st.audio(audio_reply, format="audio/mp3")
            else:
                st.warning("Text too long or invalid for TTS")
```

## Configuration

### Environment Variables Required
```bash
# In your .env file
OPENAI_API_KEY=sk_...
```

### Backend Configuration
Ensure backend APIs are running:
- `POST /transcribe` - enabled
- `POST /tts` - enabled

Check `backend/main.py` lines 260+ for API implementations.

## Performance Optimization Tips

1. **Use Audio Caching**
   ```python
   from components.audio_utils import AudioCache
   
   # Always check cache first
   cached = AudioCache.get_cached_audio(text, voice)
   if not cached:
       audio = text_to_speech(text, voice)
   ```

2. **Validate Before API Call**
   ```python
   from components.audio_utils import validate_text_for_tts
   
   if validate_text_for_tts(text):
       audio = text_to_speech(text)
   ```

3. **Truncate Long Text**
   ```python
   # Max 4096 chars for TTS
   text_truncated = text[:4096]
   audio = text_to_speech(text_truncated)
   ```

4. **Batch Processing**
   For multiple API calls, implement request batching in your backend.

## Troubleshooting

### Issue: "No microphone detected"
- **Solution:** Check browser microphone permissions in site settings
- **Note:** HTTPS required in production

### Issue: "Transcription failed"
- **Solution:** Check OPENAI_API_KEY is set correctly
- **Solution:** Ensure audio file is not corrupted

### Issue: "TTS audio not playing"
- **Solution:** Update Streamlit to latest version
- **Solution:** Check browser audio output

### Issue: "API rate limit exceeded"
- **Solution:** Implement request throttling
- **Solution:** Use audio caching to reduce calls

## Monitoring & Debugging

### Enable Debug Mode
In the enhanced chat component, enable debug info via sidebar:
```python
if st.checkbox("📊 Show Usage Stats"):
    render_audio_debug_info()
```

### Check Metrics
```python
from components.audio_utils import AudioMetrics

metrics = AudioMetrics.get_metrics()
st.json(metrics)
```

### View Session State
```python
st.write("Audio State:", st.session_state.get("audio_cache", {}))
```

## Next Steps

1. **Test with real users** - Gather feedback on voice quality
2. **Implement analytics** - Track usage patterns
3. **Add voice activity detection** - Auto-stop recording on silence
4. **Support multiple languages** - Add language selection
5. **Optimize voice selection** - Learn user preferences

## Support

For issues or improvements:
1. Check [SPEECH_FUNCTIONALITY.md](SPEECH_FUNCTIONALITY.md) for detailed docs
2. Review error messages and logs
3. Test APIs directly with curl/Postman
4. Check OpenAI API status and limits

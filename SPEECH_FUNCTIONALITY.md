# Speech Functionality Documentation

## Overview
This document describes the speech-to-text (STT) and text-to-speech (TTS) functionality added to the Hospital Management System's patient appointment booking chat.

## Features

### 1. **Speech-to-Text (STT)**
User can speak their appointment request, and it gets converted to text.

**Backend API:** `POST /transcribe`
- **Input:** Audio file (WAV, WebM, MP3, M4A, OGG)
- **Output:** `{"text": "transcribed text"}`
- **Implementation:** OpenAI Whisper Model

**Frontend Implementation:**
- Component: `render_audio_recorder()` in `components/speech_input.py`
- Uses Streamlit's built-in `audio_input()` widget
- Automatically captures audio from browser microphone
- Returns raw audio bytes

### 2. **Text-to-Speech (TTS)**
Assistant's response can be played back as audio.

**Backend API:** `POST /tts`
- **Input:** `{"text": "...", "voice": "alloy"}`
- **Output:** Audio/MPEG stream
- **Implementation:** OpenAI TTS with multiple voice options
- **Voice Choices:** alloy, echo, fable, onyx, nova, shimmer

**Frontend Implementation:**
- Component: `text_to_speech()` in `components/api.py`
- Plays audio using Streamlit's `st.audio()` widget
- Button to trigger TTS for each assistant response

## File Structure

### Backend
- **Main API Routes:**
  - `POST /transcribe` - Speech-to-text conversion
  - `POST /tts` - Text-to-speech conversion

### Frontend Components

#### 1. **components/api.py** (Updated)
New functions added:
```python
def transcribe_audio(audio_bytes: bytes, filename: str) -> Optional[str]
def text_to_speech(text: str, voice: str) -> Optional[bytes]
```

#### 2. **components/speech_input.py** (New)
Handles audio UI components:
```python
def render_audio_recorder() -> Optional[bytes]
def play_audio(audio_bytes: bytes, autoplay: bool = False)
def render_text_to_speech_button(text: str) -> bool
def create_download_link(audio_bytes: bytes, filename: str) -> str
```

#### 3. **pages_components/patient_chat.py** (Updated)
Integrated speech functionality:
- Audio recording input widget
- Real-time transcription of recorded audio
- TTS button for assistant responses
- Audio playback for responses

## User Flow

### Scenario 1: User Speaks
1. User clicks "Record your message" button
2. Grants microphone permission (if first time)
3. Speaks their appointment request
4. Audio is automatically uploaded to backend
5. Backend transcribes using Whisper
6. Text appears in chat as user message
7. LLM processes and responds
8. User can click "🔊 Play" to hear the response

### Scenario 2: User Types
1. User types message in text input box
2. Normal chat flow continues
3. User can still click "🔊 Play" to hear the response

## Implementation Details

### Session State Management
```python
st.session_state.audio_data       # Stores recorded audio bytes
st.session_state.playing_audio    # Dictionary mapping message indices to audio
```

### Error Handling
- Microphone not available: Streamlit shows native error
- Transcription error: Clear error message displayed
- TTS error: Clear error message displayed
- Network errors: Try-catch with user-friendly messages

### Performance Considerations
- Audio files are compressed by Streamlit before upload
- TTS responses cached in session state
- No repeated API calls for same text

## Voice Options

For TTS, you can choose from 6 different voices:

| Voice | Character | Best For |
|-------|-----------|----------|
| **alloy** | Neutral, friendly | General use |
| **echo** | Deep, professional | Doctor/authority |
| **fable** | Warm, engaging | Patient communication |
| **onyx** | Deep, calm | Emergencies |
| **nova** | Clear, energetic | Instructions |
| **shimmer** | Bright, friendly | Support/assistance |

## API Response Examples

### Transcribe Audio
**Request:**
```
POST /transcribe
Content-Type: multipart/form-data
Authorization: Bearer {token}

[binary audio data]
```

**Response:**
```json
{
  "text": "I need to see a cardiologist next week"
}
```

### Text to Speech
**Request:**
```json
POST /tts
Content-Type: application/json
Authorization: Bearer {token}

{
  "text": "Your appointment has been booked for next Monday",
  "voice": "alloy"
}
```

**Response:**
```
audio/mpeg (binary audio stream)
```

## Dependencies

### Backend
- `openai>=1.3.0` - For Whisper and TTS
- `fastapi>=0.111.0` - API framework
- `python-multipart` - For file uploads

### Frontend
- `streamlit>=1.35.0` - UI framework (audio_input widget available in 1.18+)
- `httpx>=0.27.0` - HTTP client

## Configuration

### OpenAI API Key
Required environment variable in backend:
```bash
OPENAI_API_KEY=sk_...
```

### Audio Settings
- **Input Format:** Supports WAV, WebM, MP3, M4A, OGG
- **Output Format (TTS):** MP3
- **Language:** English (en)
- **Max TTS Length:** 4096 characters (automatically truncated)

## Troubleshooting

### No microphone detected
- Check browser microphone permissions
- Ensure HTTPS is used in production (browser requirement)
- Try a different browser

### Transcription failing
- Ensure audio quality is good
- Check OpenAI API key is valid
- Verify OPENAI_API_KEY environment variable
- Check API rate limits

### TTS audio not playing
- Check browser supports audio playback
- Verify OpenAI API key
- Check internet connection

### Audio file too large
- Streamlit automatically compresses audio
- If still failing, use shorter audio clips

## Future Enhancements

1. **Language Support**
   - Multi-language transcription
   - Language selection in UI

2. **Voice Selection UI**
   - Let users choose preferred voice
   - Save voice preference

3. **Audio Controls**
   - Playback speed adjustment
   - Volume control
   - Download audio button

4. **Advanced Features**
   - Audio file upload option (not just recording)
   - Voice activity detection
   - Ambient noise filtering

5. **Analytics**
   - Track STT/TTS usage
   - Monitor API costs
   - Analyze user preferences

## Security Considerations

1. **Authorization**
   - All endpoints require authentication
   - Bearer token validated before processing

2. **Data Privacy**
   - Audio files not stored on server
   - Deleted after transcription
   - OpenAI subject to their data policies

3. **Rate Limiting**
   - Implement in production
   - Prevent abuse of free trial APIs

4. **Input Validation**
   - Audio file size checks
   - Text length limits (4096 chars for TTS)
   - Filename validation

## Testing

### Manual Testing Checklist
- [ ] Record audio message and verify transcription
- [ ] Test with different audio qualities
- [ ] Verify TTS plays assistant response
- [ ] Test error handling (no API key, network error)
- [ ] Test with long text messages
- [ ] Verify session state clears properly
- [ ] Test on mobile browser

### Test Cases
1. Short audio clip (< 10 seconds)
2. Long audio clip (1+ minutes)
3. Audio with background noise
4. Very short text (1 word)
5. Maximum length text (4096 chars)
6. Network timeout scenarios

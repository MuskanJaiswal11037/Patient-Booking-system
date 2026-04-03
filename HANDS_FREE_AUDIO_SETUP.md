# 🎙️ Hands-Free Audio Capture - Setup & Installation Guide

## ✅ What's Been Implemented

Your Hospital Management System now has **WebRTC-based continuous hands-free audio capture** with automatic transcription and message sending!

### Key Features:
- 🎙️ **Continuous recording** - Speak naturally without button pressing
- 🔴 **Real-time monitoring** - See recording status and frame count
- 🤐 **Silence detection** - Auto-submits after ~3 seconds of silence
- 🌐 **WebRTC streaming** - Browser-based audio capture
- 📝 **Auto-transcription** - Converts speech to text automatically
- 🔄 **Seamless integration** - Works with existing chat system

---

## 📦 Installation Steps

### 1. Install Required Dependencies

The following packages have been added to `requirements.txt`:
- `streamlit-webrtc==0.47.0` - WebRTC streaming for audio capture
- `pydub==0.25.1` - Audio processing
- `av==10.1.0` - FFmpeg bindings for audio conversion
- `numpy==1.24.3` - Numerical operations

**Install them:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install streamlit-webrtc==0.47.0 pydub==0.25.1 av==10.1.0 numpy==1.24.3
```

### 2. System Requirements

For WebRTC audio capture to work, you need:

**Windows:**
```bash
# Install FFmpeg (required for av package)
# Using Chocolatey:
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

---

## 🚀 How to Use

### Starting the Application

1. **Activate your virtual environment** (if using one):
```bash
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate
```

2. **Install requirements:**
```bash
pip install -r requirements.txt
```

3. **Start the backend:**
```bash
python start_backend.py
```

4. **In a new terminal, start the frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

5. **Open browser** to the URL shown (typically `http://localhost:8501`)

---

## 🎤 Using Hands-Free Audio

### Step-by-Step Guide

1. **Navigate to Chat Page**
   - Log in and go to "💬 Book an Appointment"

2. **Enable Hands-Free Mode**
   ```
   Section: "🎙️ Hands-Free Voice Input (Continuous)"
   Click: "🎙️ Start Listening (Hands-Free)"
   ```

3. **Start Recording**
   - WebRTC browser interface opens
   - Grant microphone permission (may see browser prompt)
   - Status shows: `🔴 Recording... | X.Xs | Y frames`

4. **Speak Your Message**
   - Speak naturally and clearly
   - System captures audio continuously
   - Real-time metrics display:
     - Duration: `X.Xs`
     - Frames captured: `Y frames`
     - Audio level indicator

5. **Automatic Submission Options**

   **Option A - Silence Detection (Auto-Submit)**
   - Pause speaking for ~3 seconds
   - System auto-detects silence
   - Automatically sends to transcription
   - Message appears as: `✓ Heard: *[your text]*`

   **Option B - Manual Stop**
   - Click "⏹️ Stop Listening" button
   - System processes audio
   - Transcribes and sends automatically

6. **See Results**
   - Transcribed text displays
   - Bot response appears below
   - Option to play response as audio

7. **Continue Conversation**
   - Start new message (clicks resume automatically)
   - Or switch to traditional audio/text input

---

## 🔧 Technical Details

### Audio Processing Flow

```
1. User opens browser webcam/microphone
                ↓
2. WebRTC captures audio frames (100ms chunks at 16kHz)
                ↓
3. Frames stream to Streamlit app
                ↓
4. Silence detection monitors amplitude
                ↓
5. When silence threshold reached (>3 seconds):
   - Audio frames combine
   - Combine → WAV format conversion
   - Send to /transcribe endpoint
                ↓
6. Backend returns transcribed text
                ↓
7. Text sent to /chat endpoint
                ↓
8. Bot response returned
                ↓
9. Response displayed (with optional TTS playback)
```

### Session State Management

The system uses Streamlit's session state to maintain:
- `hands_free_audio` - Recording state and frame buffer
- `is_recording` - Current recording status
- `audio_frames` - Collected audio frames
- `silence_counter` - Consecutive silence frames count
- `frame_count` - Total frames captured
- `start_time` - Recording start timestamp

### Configuration Parameters

Edit in `frontend/components/hands_free_audio.py`:

```python
class HandsFreeAudioCapture:
    SAMPLE_RATE = 16000  # Hz (speech optimized)
    CHANNELS = 1         # Mono
    CHUNK_DURATION_MS = 100  # 100ms chunks
    SILENCE_THRESHOLD = 500  # Amplitude level
    SILENCE_DURATION_FRAMES = 30  # ~3 seconds to auto-submit
```

Adjust these for your needs:
- **Higher THRESHOLD** = needs louder voice to register
- **More FRAMES** = longer pause needed before auto-submit
- **Lower SAMPLE_RATE** = faster processing but worse quality

---

## 🌐 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Full Support | Recommended - best performance |
| Edge | ✅ Full Support | Based on Chromium, excellent |
| Firefox | ✅ Full Support | Good performance |
| Safari | ⚠️ Limited | WebRTC works but needs permissions |
| Mobile Chrome | ✅ Partial | Works on most modern Android |
| Mobile Safari | ⚠️ Limited | iOS WebRTC support limited |

### Enabling Microphone Permission

**Chrome/Edge:**
- Browser automatically prompts
- Click "Allow" when asked

**Firefox:**
- Browser automatically prompts
- Select microphone and click "Share"

**Safari:**
- Go to Preferences → Security → Microphone
- Add your localhost URL
- Refresh page and try again

---

## 🐛 Troubleshooting

### "No audio being captured"

**Cause:** Browser microphone not accessible

**Solutions:**
1. Check browser microphone permissions
2. Go to browser settings → Privacy/Security → Microphone
3. Ensure localhost is allowed
4. Try a different browser
5. Restart browser completely

### "Microphone permission denied"

**Cause:** Browser blocked microphone access

**Solutions:**
1. Check console for permission errors
2. Reset site permissions in browser settings
3. Use incognito/private mode to test
4. Try different browser

### "Module not found: streamlit_webrtc"

**Cause:** Dependencies not installed

**Solutions:**
```bash
# Install missing packages
pip install streamlit-webrtc==0.47.0

# Or reinstall all requirements
pip install -r requirements.txt
```

### "av module not found"

**Cause:** FFmpeg not installed or AV package missing

**Solutions:**
```bash
# Install FFmpeg first (OS specific)
# Windows (Chocolatey):
choco install ffmpeg

# Then install av:
pip install av==10.1.0
```

### "Transcription failing/returning blank"

**Cause:** Backend /transcribe endpoint issues

**Solutions:**
1. Check backend is running: `python start_backend.py`
2. Check OpenAI API key is set in .env
3. Look at backend logs for errors
4. Test with shorter, clearer messages
5. Check audio quality (reduce background noise)

### "Page keeps rerunning / stuck in loop"

**Cause:** Session state issue

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+Shift+R)
3. Check browser console for JavaScript errors
4. Restart Streamlit app

### "Audio quality is poor"

**Solutions:**
- Speak closer to microphone
- Reduce background noise
- Use headphones for better capture
- Check microphone levels in OS settings

---

## 📊 Monitoring & Debugging

### View WebRTC Status

When recording is active, you see:
```
🔴 Recording... | 2.3s | 23 frames
📊 Audio Level: 23 frames
```

### Browser DevTools

Press `F12` to open developer tools and check:

1. **Console** - Look for errors
2. **Network** - Check API calls to /transcribe and /chat
3. **Performance** - Monitor CPU/memory usage

### Backend Logs

Check backend terminal for:
```
POST /transcribe - Incoming audio
POST /chat - Message being processed
Error/Exception messages
```

---

## 📝 Files Modified/Created

### New Files:
- `frontend/components/hands_free_audio.py` - WebRTC audio capture engine
- `HANDS_FREE_AUDIO_SETUP.md` - This guide

### Modified Files:
- `requirements.txt` - Added dependencies
- `frontend/pages_components/patient_chat.py` - Integrated hands-free audio UI

---

## 🔐 Security & Privacy

✅ **Your audio data:**
- Captured locally in browser
- Streamed only to your backend server
- Not sent to external services (except OpenAI Whisper for transcription)
- Session data cleared when browser closed
- No persistent storage in browser

### Best Practices:
- Use HTTPS in production (for secure audio streaming)
- Restrict `/transcribe` and `/chat` endpoints to authenticated users
- Store API keys securely in environment variables
- Monitor backend logs for unusual activity

---

## 🚀 Performance Tips

1. **Reduce chunks** - Lower `CHUNK_DURATION_MS` for real-time response
2. **Increase silence threshold** - More frames = longer pause needed
3. **Clear browser cache** - Improves Streamlit performance
4. **Use modern browser** - Chrome/Edge better than Firefox
5. **Close background apps** - Free up CPU/memory
6. **Stable internet** - WebRTC works best on stable connections

---

## 🔄 Fallback Options

If hands-free doesn't work:

1. **Traditional Audio Recording**
   - Scroll down to "Or record a single message"
   - Uses simple Streamlit audio recorder
   - Click record → speak → submit

2. **Text Input**
   - Type messages normally
   - Always available in chat input

3. **Copy from transcript**
   - Manually copy transcribed text
   - Paste in text input

---

## 📞 Support & Resources

**Streamlit WebRTC:**
- Docs: https://github.com/aiortc/streamlit-webrtc
- Examples: https://github.com/aiortc/streamlit-webrtc/tree/master/examples

**OpenAI Whisper:**
- Docs: https://platform.openai.com/docs/guides/speech-to-text
- Supported languages: https://github.com/openai/whisper

**WebRTC Basics:**
- MDN Guide: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- Browser Support: https://webrtc.org/

---

## ✨ Next Steps

After installation:

1. ✅ Test hands-free audio in chat
2. ✅ Try silence auto-detection
3. ✅ Test manual stop
4. ✅ Switch between audio modes
5. ✅ Monitor performance
6. ✅ Adjust parameters as needed
7. ✅ Deploy to production (with HTTPS)

---

**Version:** 1.0 | **Date:** April 2026 | **Status:** Production Ready

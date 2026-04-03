# 🎙️ Hands-Free Audio - Quick Reference

## ⚡ Quick Start (30 seconds)

```
1. pip install streamlit-webrtc==0.47.0 pydub av numpy
2. Go to Patient Chat page
3. Enable "🎙️ Start Listening (Hands-Free)"
4. Grant browser microphone permission
5. Speak your message
6. Wait 3 seconds of silence OR click "⏹️ Stop"
7. Message transcribes and sends automatically
```

## 📱 Interface Buttons

| Button | Action | What Happens |
|--------|--------|--------------|
| 🎙️ Start Listening | Begin continuous recording | WebRTC opens, starts capturing audio frames |
| ⏹️ Stop Listening | End recording | Combines all frames, sends to transcription |
| ✓ Submit Voice Input | Submit single message | Traditional audio mode - for fallback |

## 📊 Status Indicators

| Icon | Meaning | Next Step |
|------|---------|-----------|
| 🔴 Recording... | Currently capturing audio | Keep speaking or click stop |
| 📊 Audio Level | Real-time frame counter | Normal - system is working |
| ✓ Heard: *[text]* | Transcription complete | Message sent to bot |

## 🔧 Troubleshooting Table

| Problem | Cause | Fix |
|---------|-------|-----|
| No microphone access | Browser blocked permission | Settings → Privacy → Microphone → Allow |
| "Import streamlit_webrtc error" | Dependencies not installed | `pip install streamlit-webrtc==0.47.0` |
| No audio captured | Microphone not enabled | Check OS microphone settings |
| Blank transcription | Audio quality poor | Speak louder, closer to mic |
| Backend error | No connection | Ensure `python start_backend.py` running |

## 🔊 Audio Settings (in `hands_free_audio.py`)

```python
SAMPLE_RATE = 16000      # Quality (lower = faster)
SILENCE_THRESHOLD = 500  # Voice detection level
SILENCE_DURATION_FRAMES = 30  # Pause time for auto-submit (~3 sec)
```

**Adjustments:**
- Loud environment? → Increase `SILENCE_THRESHOLD` to 1000
- Want faster response? → Decrease `SILENCE_DURATION_FRAMES` to 15
- Better quality? → Ignore sample rate (16kHz is optimal)

## 🌐 Browser Compatibility

✅ Chrome, Edge, Firefox  
⚠️ Safari (needs permission setup)  
❌ Very old browsers  

## 📝 File Locations

```
├── frontend/
│   ├── components/
│   │   ├── hands_free_audio.py  ← Core WebRTC handler
│   │   └── ...
│   └── pages_components/
│       └── patient_chat.py  ← UI integration
├── requirements.txt  ← Dependencies added
└── HANDS_FREE_AUDIO_SETUP.md  ← Full guide
```

## 🔄 Data Flow

```
Microphone 
  → Browser WebRTC 
    → Streamlit audio frames 
      → Session state buffer 
        → Silence detection 
          → Auto-submit (or manual stop)
            → Audio bytes 
              → /transcribe endpoint 
                → OpenAI Whisper 
                  → Text response 
                    → /chat endpoint 
                      → Bot reply 
                        → Display to user
```

## 🔐 Privacy Checklist

- ✅ Audio only streamed to local backend
- ✅ No cloud storage without consent
- ✅ Session cleared on browser close
- ✅ Use HTTPS in production
- ✅ API keys in .env file

## 🎯 Use Cases

| Scenario | How To Use |
|----------|-----------|
| Book appointment quickly | Use hands-free with auto-submit |
| Complex conversation | Manual stop for longer messages |
| Noisy environment | Use text input or adjust threshold |
| Multiple questions | Keep continuous mode enabled |
| Emergency | Switch to traditional audio if needed |

## 📈 Performance (Expected)

| Metric | Expected Value |
|--------|-----------------|
| Latency to transcription | 2-5 seconds |
| Silence detection | ~3 seconds |
| Frame rate | ~10 frames/second |
| Memory usage | 20-50MB |
| CPU usage | 5-15% |

## ⏰ Timing Guide

```
Total Time for Message:
  ├─ Speaking: Variable (your choice)
  ├─ Silence detection: ~3 seconds
  ├─ Transcription: 1-3 seconds
  ├─ Backend processing: 1-5 seconds
  └─ Total typical: 10-15 seconds

Fallback to Traditional Audio:
  ├─ Record: up to 5 minutes
  ├─ Click submit: instant
  ├─ Transcription: 1-3 seconds
  └─ Total typical: Same as above
```

## 🔊 Volume Guidelines

| Level | Sound | Recommendation |
|-------|-------|-----------------|
| Very Quiet | Whisper | 🟡 Might not detect |
| Quiet | Normal speak | ✅ OK |
| Normal | Conversational | ✅✅ Best |
| Loud | Shouting | ⚠️ May distort |
| Silence | No sound | 🔴 Triggers auto-submit |

## 📱 Mobile Support

| Platform | Support | Notes |
|----------|---------|-------|
| Android Chrome | ✅ Good | Best mobile option |
| iOS Safari | ⚠️ Limited | Permissions complex |
| Tablet Apps | ✅ Good | Same as phone |
| Desktop | ✅✅ Excellent | Recommended |

## 🚀 Performance Tuning

**For Real-Time Response:**
```python
CHUNK_DURATION_MS = 50  # Faster chunks
SILENCE_DURATION_FRAMES = 15  # Shorter pause
```

**For Better Accuracy:**
```python
SILENCE_THRESHOLD = 300  # More sensitive
SILENCE_DURATION_FRAMES = 45  # Longer pause
```

**For Noisy Environments:**
```python
SILENCE_THRESHOLD = 1000  # Less sensitive
SILENCE_DURATION_FRAMES = 50  # More pause needed
```

## 🔗 Commands Cheat Sheet

```bash
# Install everything
pip install -r requirements.txt

# Install only audio packages
pip install streamlit-webrtc==0.47.0 pydub av

# Start backend
python start_backend.py

# Start frontend
cd frontend && streamlit run streamlit_app.py

# Check FFmpeg installed
ffmpeg -version

# View requirements
cat requirements.txt | grep -E "streamlit|av|pydub"
```

## 🆘 Emergency Troubleshooting

```bash
# Nothing working? Do this:

# 1. Clear everything
pip uninstall streamlit-webrtc pydub av numpy -y

# 2. Reinstall
pip install -r requirements.txt

# 3. Check Python version (need 3.8+)
python --version

# 4. Verify FFmpeg
ffmpeg -version

# 5. Restart everything
# Kill all terminals, restart from scratch
```

## 📞 One-Liners

```python
# Check recording status
HandsFreeAudioCapture.is_recording()

# Get frame count
HandsFreeAudioCapture.get_frame_count()

# Get duration
HandsFreeAudioCapture.get_duration_seconds()

# Clear state
HandsFreeAudioCapture.clear_state()
```

## 🎨 UI Customization

Edit `patient_chat.py` to change:

```python
# Button text
st.button("🎙️ Start Listening (Hands-Free)")

# Status message
st.info(f"🔴 **Recording...** | {duration:.1f}s")

# Colors/icons emoji
# 🎙️ 🔴 ⏹️ ✓ 📊 🎤
```

---

**Last Updated:** April 2026 | **Version:** 1.0

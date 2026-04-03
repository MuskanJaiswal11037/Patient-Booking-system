# Web Speech API Voice Input Component

## Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best experience, continuous listening |
| Edge | ✅ Full | Excellent, continuous listening |
| Safari | ✅ Good | Works, requires user interaction |
| Firefox | ⚠️ Limited | Falls back to audio recorder |
| Opera | ✅ Good | Similar to Chrome |

## Troubleshooting

### Firefox Users
Firefox has limited Web Speech API support. When used in Firefox, the component:
1. Shows a fallback message
2. Uses the traditional audio recorder instead
3. Requires one-click recording rather than continuous listening

**Solution:** Try Chrome, Edge, or Safari for true hands-free experience.

### "Listening..." UI Stuck
If the "🔴 Listening..." indicator is stuck:
1. Check browser console (F12 > Console tab)
2. Look for "no-speech" or "network" errors
3. Reload the page (Ctrl+R)

### No Microphone Permission Prompt
If you don't see a permission prompt:
1. Check browser privacy settings
2. Ensure microphone is not blocked for the application
3. Check address bar for permission icons
4. Refresh the page (Ctrl+F5 for hard refresh)

### "No audio recorded" Error
1. Ensure microphone is working
2. Try recording a test message first
3. Check browser microphone access settings
4. Test microphone in another browser

## Technical Details

- **Sample Rate:** 16kHz (optimal for speech recognition)
- **Language:** English (en-US) by default
- **Mode:** Continuous recognition with interim results
- **Auto-start:** Enabled by default when component loads
- **Auto-resume:** Automatically resumes after silence if enabled

## Fallback Behavior

When Web Speech API is unavailable:
1. Component detects missing API
2. Switches to traditional audio recorder
3. Shows helpful message about browser limitations
4. User can record and submit voice message manually

## Testing

To test the voice input locally:
```bash
streamlit run frontend/streamlit_app.py
```

Then navigate to the Chat page and toggle "🔊 Voice On" button.

"""Advanced audio utilities for speech functionality."""
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib


class AudioCache:
    """Cache for audio responses to minimize API calls."""
    
    CACHE_DURATION_HOURS = 24
    
    @staticmethod
    def get_cache_key(text: str, voice: str = "alloy") -> str:
        """Generate cache key for text-to-speech result."""
        cache_input = f"{text}_{voice}".encode()
        return hashlib.md5(cache_input).hexdigest()
    
    @staticmethod
    def get_cached_audio(text: str, voice: str = "alloy") -> Optional[bytes]:
        """Retrieve cached audio if available and not expired."""
        if "audio_cache" not in st.session_state:
            return None
        
        cache_key = AudioCache.get_cache_key(text, voice)
        cached_data = st.session_state.audio_cache.get(cache_key)
        
        if cached_data:
            timestamp, audio_bytes = cached_data
            elapsed = datetime.now() - timestamp
            
            # Check if cache is still valid
            if elapsed < timedelta(hours=AudioCache.CACHE_DURATION_HOURS):
                return audio_bytes
            else:
                # Remove expired cache
                del st.session_state.audio_cache[cache_key]
        
        return None
    
    @staticmethod
    def cache_audio(text: str, audio_bytes: bytes, voice: str = "alloy"):
        """Store audio in cache."""
        if "audio_cache" not in st.session_state:
            st.session_state.audio_cache = {}
        
        cache_key = AudioCache.get_cache_key(text, voice)
        st.session_state.audio_cache[cache_key] = (datetime.now(), audio_bytes)
    
    @staticmethod
    def clear_cache():
        """Clear all cached audio."""
        if "audio_cache" in st.session_state:
            st.session_state.audio_cache.clear()


class AudioMetrics:
    """Track audio usage metrics."""
    
    @staticmethod
    def log_transcription(audio_bytes: int, text: str):
        """Log speech-to-text usage."""
        if "audio_metrics" not in st.session_state:
            st.session_state.audio_metrics = {
                "transcriptions": 0,
                "tts_requests": 0,
                "audio_bytes_processed": 0,
                "chars_synthesized": 0,
            }
        
        st.session_state.audio_metrics["transcriptions"] += 1
        st.session_state.audio_metrics["audio_bytes_processed"] += audio_bytes
    
    @staticmethod
    def log_tts(text: str):
        """Log text-to-speech usage."""
        if "audio_metrics" not in st.session_state:
            st.session_state.audio_metrics = {
                "transcriptions": 0,
                "tts_requests": 0,
                "audio_bytes_processed": 0,
                "chars_synthesized": 0,
            }
        
        st.session_state.audio_metrics["tts_requests"] += 1
        st.session_state.audio_metrics["chars_synthesized"] += len(text)
    
    @staticmethod
    def get_metrics() -> Optional[Dict[str, Any]]:
        """Get current metrics."""
        return st.session_state.get("audio_metrics")
    
    @staticmethod
    def reset_metrics():
        """Reset metrics counter."""
        st.session_state.audio_metrics = {
            "transcriptions": 0,
            "tts_requests": 0,
            "audio_bytes_processed": 0,
            "chars_synthesized": 0,
        }


def render_voice_selector(default_voice: str = "alloy") -> str:
    """
    Render voice selection dropdown.
    
    Parameters
    ----------
    default_voice : str
        Default voice option
    
    Returns
    -------
    str
        Selected voice name
    """
    voices = {
        "alloy": "👤 Alloy (Neutral, Friendly)",
        "echo": "🎙️ Echo (Deep, Professional)",
        "fable": "📖 Fable (Warm, Engaging)",
        "onyx": "🌙 Onyx (Deep, Calm)",
        "nova": "✨ Nova (Clear, Energetic)",
        "shimmer": "💫 Shimmer (Bright, Friendly)",
    }
    
    selected = st.selectbox(
        "Select voice for responses:",
        options=list(voices.keys()),
        format_func=lambda x: voices.get(x, x),
        index=list(voices.keys()).index(default_voice) if default_voice in voices else 0,
        key="voice_selector"
    )
    
    return selected


def render_audio_stats():
    """Render audio usage statistics."""
    metrics = AudioMetrics.get_metrics()
    
    if metrics and any(metrics.values()):
        st.divider()
        st.subheader("📊 Session Audio Usage")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Transcriptions", metrics.get("transcriptions", 0))
        
        with col2:
            st.metric("TTS Requests", metrics.get("tts_requests", 0))
        
        with col3:
            audio_mb = metrics.get("audio_bytes_processed", 0) / (1024 * 1024)
            st.metric("Audio Processed", f"{audio_mb:.2f} MB")
        
        with col4:
            st.metric("Text Synthesized", metrics.get("chars_synthesized", 0))


def render_audio_debug_info():
    """Render debug information for audio components."""
    with st.expander("🔧 Audio Debug Info"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Show Metrics"):
                metrics = AudioMetrics.get_metrics()
                st.json(metrics or {})
        
        with col2:
            if st.button("🗑️ Clear Cache"):
                AudioCache.clear_cache()
                st.success("Cache cleared!")
        
        # Show settings
        st.write("**Current Settings:**")
        st.write(f"- Cache Duration: {AudioCache.CACHE_DURATION_HOURS} hours")
        st.write(f"- Cache Size: {len(st.session_state.get('audio_cache', {}))}")


def validate_audio_bytes(audio_bytes: bytes, min_size: int = 100) -> bool:
    """
    Validate audio data.
    
    Parameters
    ----------
    audio_bytes : bytes
        Audio data to validate
    min_size : int
        Minimum acceptable file size in bytes
    
    Returns
    -------
    bool
        True if valid, False otherwise
    """
    if not audio_bytes:
        return False
    
    if len(audio_bytes) < min_size:
        return False
    
    return True


def validate_text_for_tts(text: str, max_length: int = 4096) -> bool:
    """
    Validate text for TTS conversion.
    
    Parameters
    ----------
    text : str
        Text to validate
    max_length : int
        Maximum allowed text length
    
    Returns
    -------
    bool
        True if valid, False otherwise
    """
    if not text or not text.strip():
        return False
    
    if len(text) > max_length:
        return False
    
    return True


def format_audio_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Parameters
    ----------
    seconds : float
        Duration in seconds
    
    Returns
    -------
    str
        Formatted duration (e.g., "1m 23s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def estimate_tts_duration(text: str) -> float:
    """
    Estimate TTS audio duration based on text length.
    
    Rough estimate: ~500 characters per minute
    
    Parameters
    ----------
    text : str
        Text to synthesize
    
    Returns
    -------
    float
        Estimated duration in seconds
    """
    # Average speaking rate: ~150 words per minute
    # Average word length: ~5 characters
    # So ~750 characters per minute
    
    chars_per_minute = 750
    estimated_minutes = max(1, len(text) / chars_per_minute)
    return estimated_minutes * 60


class StreamlitAudioState:
    """Streamlit session state manager for audio."""
    
    @staticmethod
    def init_audio_state():
        """Initialize audio-related session state."""
        if "audio_data" not in st.session_state:
            st.session_state.audio_data = None
        if "playing_audio" not in st.session_state:
            st.session_state.playing_audio = {}
        if "audio_cache" not in st.session_state:
            st.session_state.audio_cache = {}
        if "audio_metrics" not in st.session_state:
            st.session_state.audio_metrics = {
                "transcriptions": 0,
                "tts_requests": 0,
                "audio_bytes_processed": 0,
                "chars_synthesized": 0,
            }
        if "selected_voice" not in st.session_state:
            st.session_state.selected_voice = "alloy"
    
    @staticmethod
    def get_state() -> Dict[str, Any]:
        """Get all audio-related state."""
        StreamlitAudioState.init_audio_state()
        return {
            "audio_data": st.session_state.audio_data,
            "playing_audio": st.session_state.playing_audio,
            "audio_cache": st.session_state.audio_cache,
            "audio_metrics": st.session_state.audio_metrics,
            "selected_voice": st.session_state.selected_voice,
        }
    
    @staticmethod
    def reset_state():
        """Reset all audio state."""
        st.session_state.audio_data = None
        st.session_state.playing_audio = {}
        AudioCache.clear_cache()
        AudioMetrics.reset_metrics()

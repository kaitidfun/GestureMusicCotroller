"""
Configuration settings for Gesture Spotify Control
"""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill in your values."
        )
    return value


@dataclass
class Config:
    """การตั้งค่าของระบบ"""
    # ESP32-CAM
    ESP32_URL: str = field(default_factory=lambda: os.environ.get(
        "ESP32_URL", "http://192.168.1.101:81/stream"
    ))

    # Spotify API
    CLIENT_ID: str = field(default_factory=lambda: _require_env("SPOTIFY_CLIENT_ID"))
    CLIENT_SECRET: str = field(default_factory=lambda: _require_env("SPOTIFY_CLIENT_SECRET"))
    REDIRECT_URI: str = field(default_factory=lambda: os.environ.get(
        "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"
    ))
    SCOPE: str = "user-modify-playback-state,user-read-playback-state"
    
    # Gesture Detection
    COOLDOWN: float = 0.1
    MIN_DETECTION_CONFIDENCE: float = 0.7
    MIN_TRACKING_CONFIDENCE: float = 0.7
    
    # Display
    RESIZE_SCALE: int = 2
    WINDOW_NAME: str = "Gesture Spotify Control"

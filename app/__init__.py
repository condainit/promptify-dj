"""
Promptify DJ - Generate AI-powered Spotify playlists from your voice or text.

A Streamlit web application that generates personalized Spotify playlists from voice or text prompts.
Uses OpenAI Whisper for transcription, GPT-3.5 for intent parsing, and Spotify Web API for music curation.
"""

__version__ = "1.0.0"
__author__ = "condainit"
__description__ = "Generate AI-powered Spotify playlists from your voice or text"

from .config import Config
from .whisper_interface import WhisperInterface
from .gpt_parser import IntentParser
from .spotify_client import SpotifyClient
from .playlist_builder import PlaylistBuilder

__all__ = [
    "Config",
    "WhisperInterface", 
    "IntentParser",
    "SpotifyClient",
    "PlaylistBuilder"
] 
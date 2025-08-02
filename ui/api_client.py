"""
API Client for Promptify DJ

Handles communication with the FastAPI backend for playlist generation.
"""

import requests
import streamlit as st
import base64
from typing import Optional, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 60


def check_api_health() -> bool:
    """
    Check if the FastAPI server is running and healthy.
    
    Returns:
        bool: True if the API server is responding, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _handle_api_response(response: requests.Response) -> Optional[Dict[str, Any]]:
    """
    Process API response and extract result or display error.
    
    Args:
        response: HTTP response from the API
        
    Returns:
        Optional[Dict[str, Any]]: JSON response data if successful, None if error
    """
    if response.status_code == 200:
        return response.json()
    else:
        error_detail = response.json().get('detail', 'Unknown error')
        st.error(f"API Error: {error_detail}")
        return None


def _handle_api_exception(e: Exception, error_type: str) -> None:
    """
    Handle API exceptions with consistent error messaging.
    
    Args:
        e: The exception that occurred
        error_type: Description of the operation that failed
    """
    if isinstance(e, requests.exceptions.ConnectionError):
        st.error(f"API server connection failed. Make sure the FastAPI server is running.")
    elif isinstance(e, requests.exceptions.Timeout):
        st.error(f"API request timed out. The server may be overloaded.")
    elif isinstance(e, requests.exceptions.RequestException):
        st.error(f"API request failed: {e}")
    else:
        st.error(f"Unexpected error during {error_type}: {e}")


def process_audio_recording(audio_bytes: bytes, audio_format: str = 'webm', create_playlist: bool = True) -> Optional[Dict[str, Any]]:
    """
    Process uploaded audio file through the API for playlist generation.
    
    Args:
        audio_bytes: Raw audio data as bytes
        audio_format: Audio file format (e.g., 'wav', 'mp3', 'webm')
        create_playlist: Whether to create an actual Spotify playlist
        
    Returns:
        Optional[Dict[str, Any]]: Playlist generation result or None if failed
        
    Raises:
        Exception: If audio processing or API communication fails
    """
    try:
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        response = requests.post(
            f"{API_BASE_URL}/process_audio_recording",
            json={
                "audio_data": audio_base64,
                "audio_format": audio_format,
                "create_playlist": create_playlist
            },
            timeout=REQUEST_TIMEOUT
        )
        
        return _handle_api_response(response)
        
    except Exception as e:
        _handle_api_exception(e, "audio processing")
        return None


def generate_playlist_from_text(transcript: str, create_playlist: bool = True) -> Optional[Dict[str, Any]]:
    """
    Generate playlist from text input through the API.
    
    Args:
        transcript: Text input for playlist generation
        create_playlist: Whether to create an actual Spotify playlist
        
    Returns:
        Optional[Dict[str, Any]]: Playlist generation result or None if failed
        
    Raises:
        Exception: If playlist generation or API communication fails
    """
    try:
        with st.spinner("Generating your playlist..."):
            response = requests.post(
                f"{API_BASE_URL}/generate_playlist",
                data={"transcript": transcript, "create_playlist": create_playlist},
                timeout=REQUEST_TIMEOUT
            )
        
        return _handle_api_response(response)
        
    except Exception as e:
        _handle_api_exception(e, "playlist generation")
        return None

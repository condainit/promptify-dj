"""
Configuration for Promptify DJ UI

Centralized configuration for UI constants, styling, and settings.
"""

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================

# Supported audio file formats for upload
SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'm4a', 'ogg', 'webm']

# =============================================================================
# UI LAYOUT CONSTANTS
# =============================================================================

# Height of the text input area in pixels
TEXT_AREA_HEIGHT = 212

# Height of spacer div when no audio file is uploaded (matches audio player height)
AUDIO_PLAYER_SPACER_HEIGHT = 119

# Spotify embed iframe height
SPOTIFY_EMBED_HEIGHT = 400

# =============================================================================
# CONTENT CONFIGURATION
# =============================================================================

# Pre-defined example queries for quick playlist generation
EXAMPLE_QUERIES = [
    "I need energetic rock music for my workout",
    "Play some relaxing jazz for studying", 
    "I want romantic pop songs from the 80s",
    "Give me upbeat electronic music for productivity",
    "I need calming ambient music for sleeping"
]

# =============================================================================
# CSS CLASS NAMES
# =============================================================================

# CSS class names used throughout the application
CSS_CLASSES = {
    'main_title': 'main-title',      # Main application title styling
    'subtitle': 'subtitle',          # Subtitle text styling
    'section_title': 'section-title' # Section header styling
}

# =============================================================================
# USER INTERFACE TEXT
# =============================================================================

# Button labels for consistent UI text
BUTTON_LABELS = {
    'generate_audio': 'Generate Playlist from Audio',
    'generate_text': 'Generate Playlist from Text',
    'generate_another': 'Generate Another Playlist'
}

# Placeholder text for the text input area
PLACEHOLDER_TEXT = "e.g., 'I want upbeat pop music for a road trip.'"

# =============================================================================
# USER FEEDBACK MESSAGES
# =============================================================================

# Loading messages displayed during processing
LOADING_MESSAGES = {
    'audio_processing': 'Generating your playlist from audio...',
    'playlist_generation': 'Generating your playlist...'
}

# Error messages for various failure scenarios
ERROR_MESSAGES = {
    'api_server_down': 'API server is not running. Please start the FastAPI server first.',
    'api_server_instructions': 'To start the server, run: `uvicorn api.main:app --reload`',
    'audio_generation_failed': 'Failed to generate playlist from audio.',
    'playlist_generation_failed': 'Error generating playlist: {}',
    'empty_audio_file': 'Audio file is empty',
    'unsupported_format': 'Unsupported audio format: {}'
}

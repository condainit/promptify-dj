"""
UI Components for Promptify DJ

Reusable UI components for playlist display and user interface elements.
"""

import streamlit as st
from typing import Dict, Any, Optional
from api_client import process_audio_recording, generate_playlist_from_text
from config import (
    SUPPORTED_AUDIO_FORMATS,
    TEXT_AREA_HEIGHT,
    AUDIO_PLAYER_SPACER_HEIGHT,
    EXAMPLE_QUERIES,
    CSS_CLASSES,
    BUTTON_LABELS,
    PLACEHOLDER_TEXT,
    LOADING_MESSAGES,
    ERROR_MESSAGES,
    SPOTIFY_EMBED_HEIGHT
)


def render_audio_upload_section() -> None:
    """
    Render the audio file upload section with file uploader and generation button.
    
    Creates a file uploader for supported audio formats, displays an audio player
    when a file is uploaded, and provides a button to generate playlists from audio.
    The button is disabled until a file is uploaded.
    """
    st.markdown(f'<h2 class="{CSS_CLASSES["section_title"]}">Upload Audio File</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "",
        type=SUPPORTED_AUDIO_FORMATS,
        key="audio_uploader"
    )
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
    else:
        # Maintain consistent layout height when no file is uploaded
        st.markdown(f'<div style="height: {AUDIO_PLAYER_SPACER_HEIGHT}px;"></div>', unsafe_allow_html=True)
    
    button_disabled = uploaded_file is None
    if st.button(BUTTON_LABELS['generate_audio'], type="primary", use_container_width=True, disabled=button_disabled):
        _handle_audio_generation(uploaded_file)


def render_text_input_section() -> None:
    """
    Render the text input section with text area and generation button.
    
    Creates a text area for user input with placeholder text and a button to
    generate playlists from text. The button is disabled when the text area is empty.
    """
    st.markdown(f'<h2 class="{CSS_CLASSES["section_title"]}">Input Text</h2>', unsafe_allow_html=True)
    
    text_input = st.text_area(
        "",
        placeholder=PLACEHOLDER_TEXT,
        height=TEXT_AREA_HEIGHT,
        key="text_input"
    )
    
    button_disabled = not text_input.strip()
    if st.button(
        BUTTON_LABELS['generate_text'], 
        type="primary", 
        key="generate_from_text", 
        use_container_width=True,
        disabled=button_disabled
    ):
        _handle_text_generation(text_input)


def _handle_audio_generation(uploaded_file) -> None:
    """
    Process uploaded audio file and generate playlist.
    
    Args:
        uploaded_file: StreamlitUploadedFile object containing the audio data
    """
    with st.spinner(LOADING_MESSAGES['audio_processing']):
        try:
            # Validate file
            if not uploaded_file or uploaded_file.size == 0:
                st.error(ERROR_MESSAGES['empty_audio_file'])
                return
                
            # Validate file format
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in SUPPORTED_AUDIO_FORMATS:
                st.error(ERROR_MESSAGES['unsupported_format'].format(file_extension))
                return
            
            # Process audio
            audio_bytes = uploaded_file.read()
            result = process_audio_recording(
                audio_bytes,
                file_extension,
                st.session_state.create_playlist
            )
            
            if result:
                st.session_state.playlist_result = result
                st.rerun()
            else:
                st.error(ERROR_MESSAGES['audio_generation_failed'])
                
        except Exception as e:
            st.error(ERROR_MESSAGES['playlist_generation_failed'].format(str(e)))


def _handle_text_generation(text_input: str) -> None:
    """
    Process text input and generate playlist.
    
    Args:
        text_input: User-provided text for playlist generation
    """
    result = generate_playlist_from_text(text_input, st.session_state.create_playlist)
    if result:
        st.session_state.playlist_result = result
        st.rerun()


def render_example_queries() -> Optional[str]:
    """
    Render example query buttons for quick playlist generation.
    
    Returns:
        Optional[str]: The selected example query, or None if no query is selected
    """
    cols = st.columns(len(EXAMPLE_QUERIES))
    for i, (col, query) in enumerate(zip(cols, EXAMPLE_QUERIES)):
        with col:
            if st.button(query, key=f"example_{i}", help=f"Generate playlist for: {query}"):
                return query
    
    return None


def _extract_playlist_id(playlist_url: str) -> Optional[str]:
    """Extract playlist ID from Spotify URL."""
    if not playlist_url or 'playlist/' not in playlist_url:
        return None
    try:
        return playlist_url.split('playlist/')[-1].split('?')[0]
    except (IndexError, AttributeError):
        return None


def render_playlist_result(result: Dict[str, Any]) -> None:
    """
    Display playlist results with Spotify embed and reset functionality.
    
    Args:
        result: Dictionary containing playlist data including tracks and playlist_url
    """
    playlist_url = result.get("playlist_url")
    playlist_id = _extract_playlist_id(playlist_url) if playlist_url else None
    
    if playlist_id and result.get("tracks"):
        spotify_embed = f"""
        <iframe style="border-radius:8px; margin: 0;" 
                src="https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator" 
                width="100%" 
                height="{SPOTIFY_EMBED_HEIGHT}" 
                frameBorder="0" 
                allowfullscreen="" 
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                loading="lazy">
        </iframe>
        """
        st.markdown(spotify_embed, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(BUTTON_LABELS['generate_another'], type="primary", use_container_width=True):
        st.session_state.playlist_result = None
        st.rerun() 
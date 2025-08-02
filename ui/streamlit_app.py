"""
Promptify DJ - AI-Powered Playlist Generator

A Streamlit web application that generates personalized Spotify playlists from voice or text prompts.
Uses OpenAI Whisper for transcription, GPT-3.5 for intent parsing, and Spotify Web API for music curation.
"""

import streamlit as st
from loguru import logger
from components import (
    render_example_queries, 
    render_playlist_result,
    render_audio_upload_section,
    render_text_input_section
)
from api_client import check_api_health, generate_playlist_from_text
from config import CSS_CLASSES, ERROR_MESSAGES


def load_css() -> None:
    """
    Load and apply custom CSS styling to the Streamlit application.
    
    Reads the CSS file from 'ui/styles.css' and injects it into the Streamlit
    application for custom styling of UI elements. CSS is cached in session state
    to avoid repeated file reads.
    """
    if 'css_loaded' not in st.session_state:
        try:
            with open('ui/styles.css') as f:
                css_content = f.read()
            st.session_state.css_content = css_content
            st.session_state.css_loaded = True
        except FileNotFoundError:
            logger.error("CSS file not found: ui/styles.css")
        except Exception as e:
            logger.error(f"Failed to load CSS: {e}")
    
    if 'css_content' in st.session_state:
        st.markdown(f'<style>{st.session_state.css_content}</style>', unsafe_allow_html=True)


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables.
    
    Sets up default values for application state including user preferences
    and result storage. This ensures consistent state across application sessions.
    """
    # Initialize all session state variables in one pass
    defaults = {
        'create_playlist': True,
        'playlist_result': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_header() -> None:
    """
    Render the application header with title and subtitle.
    
    Displays the main application title "Promptify DJ" and descriptive subtitle
    using the configured CSS classes for consistent styling.
    """
    st.markdown(f'<h1 class="{CSS_CLASSES["main_title"]}">Promptify DJ</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="{CSS_CLASSES["subtitle"]}">Generate AI-powered Spotify playlists from your voice or text</p>', unsafe_allow_html=True)


def render_input_interface() -> None:
    """
    Render the main input interface with audio and text sections.
    
    Creates a two-column layout containing the audio upload section on the left
    and text input section on the right, providing users with multiple input methods.
    """
    col1, col2 = st.columns(2)
    
    with col1:
        render_audio_upload_section()
    
    with col2:
        render_text_input_section()


def handle_example_queries() -> None:
    """
    Handle example query selection and processing.
    
    Renders example query buttons and processes user selection to generate
    playlists from pre-defined examples. Updates session state with results.
    """
    example_query = render_example_queries()
    if example_query:
        result = generate_playlist_from_text(example_query, st.session_state.create_playlist)
        if result:
            st.session_state.playlist_result = result
            st.rerun()


def main() -> None:
    """
    Main application entry point and orchestration function.
    
    Configures the Streamlit page, initializes application state, checks API health,
    and renders the appropriate interface based on current application state.
    
    The function handles the complete application lifecycle from initialization
    to user interaction and result display.
    """
    st.set_page_config(
        page_title="Promptify DJ",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    load_css()
    initialize_session_state()
    
    if not check_api_health():
        st.error(ERROR_MESSAGES['api_server_down'])
        st.info(ERROR_MESSAGES['api_server_instructions'])
        return
    
    render_header()
    
    # Display results or input interface based on application state
    if st.session_state.playlist_result:
        render_playlist_result(st.session_state.playlist_result)
    else:
        render_input_interface()
        handle_example_queries()


if __name__ == "__main__":
    main() 
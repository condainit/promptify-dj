# Promptify DJ

AI-powered Spotify playlist generator that transforms voice or text prompts into personalized playlists using OpenAI Whisper, GPT-3.5, and the Spotify Web API.

## Demo

[![Promptify DJ Demo](https://img.youtube.com/vi/4dHHsrARAig/maxresdefault.jpg)](https://youtu.be/4dHHsrARAig)

## Tech Stack
- **Frontend**: Streamlit web application with audio file upload, text input, and playlist display
- **Backend**: FastAPI REST API with 6 endpoints handling audio processing, intent parsing, and playlist generation
- **AI/ML**: OpenAI Whisper for speech-to-text conversion and GPT-3.5 for intelligent search query generation
- **Music**: Spotify API for track search and playlist creation
- **Audio Processing**: librosa and soundfile for audio manipulation

## Data Flow

- **Input**: Audio file upload or text prompt
- **Transcription**: Audio -> Whisper -> Transcript
- **Analysis**: Text -> GPT-3.5 -> Search Queries
- **Curation**: Search Queries -> Spotify API ([`GET /search`](https://developer.spotify.com/documentation/web-api/reference/search)) -> Track Selection
- **Playlist**: Selected Tracks -> Spotify API ([`POST /users/{user_id}/playlists`](https://developer.spotify.com/documentation/web-api/reference/create-playlist), [`POST /playlists/{playlist_id}/tracks`](https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist)) -> Playlist URL

## FastAPI Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `POST /process_audio_recording` - Full audio-to-playlist pipeline
- `POST /generate_playlist` - Text-to-playlist pipeline
- `POST /transcribe` - Audio-to-text only
- `POST /parse_intent` - Text-to-intent only

## Prerequisites

- Python 3.11
- Spotify Developer Account
- OpenAI API Key
- Conda (recommended for environment management)

## Quick Start

1. **Clone and Setup**

   ```bash
   git clone https://github.com/condainit/promptify-dj.git
   cd promptify-dj
   conda env create -f environment.yml
   conda activate promptify-dj-env
   ```

2. **Configure Environment**

   **a.** Copy the environment file:
   ```bash
   cp env.example .env
   ```
   
   **b.** Edit `.env` with your API keys

3. **Start Application**

   **a.** Start the backend server:
   ```bash
   uvicorn api.main:app --reload
   ```
   
   **b.** In a new terminal, start the frontend:
   ```bash
   conda activate promptify-dj-env
   streamlit run ui/streamlit_app.py
   ```
   
   **c.** Open your browser and navigate to [http://localhost:8501](http://localhost:8501)

4. **Generate Playlist**

   Input an audio file or text prompt, then click the corresponding "Generate Playlist" button. 
   
   > **Note**: For examples, try the audio files in the `examples/` directory or click the text prompt buttons.
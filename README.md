# Promptify DJ

Generate Spotify playlists from voice or text prompts using OpenAI Whisper (speech-to-text), GPT-3.5, and the Spotify Web API. Built with a React frontend and FastAPI backend.

## Demo

[![Promptify DJ Demo](https://img.youtube.com/vi/jjFugV6u2do/maxresdefault.jpg)](https://youtu.be/jjFugV6u2do)

## FastAPI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check |
| `POST` | `/process_audio_recording` | Full audio-to-playlist pipeline |
| `POST` | `/generate_playlist` | Text-to-playlist pipeline |
| `POST` | `/transcribe` | Audio-to-text only |
| `POST` | `/parse_intent` | Text-to-intent only |
| `POST` | `/refine` | User feedback for playlist refinement (in development) |
| `PUT` | `/playlist/{playlist_id}/name` | Update playlist name |
| `DELETE` | `/playlist/{playlist_id}` | Delete playlist |

## Prerequisites

- Python 3.11
- Node.js 16+ and npm
- Spotify Developer Account
- OpenAI API Key
- Conda (recommended for environment management)

## Quick Start

1. **Clone and Setup**

   ```bash
   git clone https://github.com/condainit/promptify-dj.git
   cd promptify-dj
   
   # Setup Python environment
   conda env create -f environment.yml
   conda activate promptify-dj-env
   
   # Setup React frontend
   cd frontend
   npm install
   cd ..
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
   uvicorn backend.main:app --reload
   ```
   
   **b.** In a new terminal, start the React frontend:
   ```bash
   conda activate promptify-dj-env
   cd frontend
   npm start
   ```
   
   **c.** Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

4. **Generate Your First Playlist**

   - **Voice Input**: Click the microphone button to record your request
   - **Text Input**: Type your request in the search bar or click a recommended prompt
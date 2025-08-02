"""
FastAPI server for Promptify DJ.
Provides endpoints for audio recording processing and playlist generation.
"""

import os
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

# Add root path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.whisper_interface import WhisperInterface
from app.playlist_builder import PlaylistBuilder

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Promptify DJ API",
    description="Generate Spotify playlists from voice or text prompts",
    version="1.0.0"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Components ---
whisper_interface = WhisperInterface()
playlist_builder = PlaylistBuilder()

# --- Models ---
class PlaylistResponse(BaseModel):
    transcript: str
    parsed_intent: dict
    tracks: list
    playlist_url: Optional[str]
    generated_at: str
    total_tracks: int

class AudioRecordingRequest(BaseModel):
    audio_data: str
    audio_format: str = "webm"
    create_playlist: bool = True

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    try:
        if not Config.validate():
            raise RuntimeError("Invalid environment configuration")
        whisper_interface.load_model()
        logger.info("API startup complete.")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

# --- Routes ---
@app.get("/")
async def root():
    return {
        "message": "Promptify DJ API",
        "version": "1.0.0",
        "available_endpoints": [
            "/process_audio_recording",
            "/generate_playlist",
            "/transcribe",
            "/parse_intent",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "config_valid": Config.validate(),
        "whisper_loaded": whisper_interface.model is not None
    }

@app.post("/process_audio_recording", response_model=PlaylistResponse)
async def process_audio_recording(request: AudioRecordingRequest):
    """Process audio recording from microphone and generate playlist."""
    try:
        import base64
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Transcribe audio
        transcript, _ = whisper_interface.transcribe_from_bytes(audio_bytes, f".{request.audio_format}")
        
        if not transcript.strip():
            raise HTTPException(400, detail="Empty transcript from audio.")
        
        # Generate playlist
        result = playlist_builder.generate_playlist(transcript, request.create_playlist)
        if "error" in result:
            raise HTTPException(500, detail=result["error"])
        
        return PlaylistResponse(**result)
        
    except Exception as e:
        logger.error(f"Process audio recording failed: {e}")
        logger.error(f"Audio format: {request.audio_format}, create_playlist: {request.create_playlist}")
        raise HTTPException(500, detail=f"Audio processing failed: {str(e)}")

@app.post("/generate_playlist", response_model=PlaylistResponse)
async def generate_playlist_from_text(
    transcript: str = Form(...),
    create_playlist: bool = Form(True)
):
    """Generate playlist from text input."""
    if not transcript.strip():
        raise HTTPException(400, detail="Empty transcript.")
        
    try:
        result = playlist_builder.generate_playlist(transcript, create_playlist)
        if "error" in result:
            raise HTTPException(500, detail=result["error"])
        return PlaylistResponse(**result)
    except Exception as e:
        logger.error(f"Generate playlist failed: {e}")
        logger.error(f"Transcript: {transcript[:100]}..., create_playlist: {create_playlist}")
        raise HTTPException(500, detail=f"Playlist generation failed: {str(e)}")

@app.post("/transcribe")
async def transcribe_audio(audio_data: str = Form(...), audio_format: str = Form("webm")):
    """Transcribe audio data to text."""
    try:
        import base64
        audio_bytes = base64.b64decode(audio_data)
        transcript, metadata = whisper_interface.transcribe_from_bytes(audio_bytes, f".{audio_format}")
        return {"transcript": transcript, "metadata": metadata}
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        logger.error(f"Audio format: {audio_format}")
        raise HTTPException(500, detail=f"Audio transcription failed: {str(e)}")

@app.post("/parse_intent")
async def parse_intent_only(transcript: str = Form(...)):
    """Parse intent from text only."""
    try:
        raw = playlist_builder.intent_parser.parse_intent(transcript)
        enhanced = playlist_builder.intent_parser.enhance_intent(raw)
        return {"original_intent": raw, "enhanced_intent": enhanced, "transcript": transcript}
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        logger.error(f"Transcript: {transcript[:100]}...")
        raise HTTPException(500, detail=f"Intent parsing failed: {str(e)}")

# --- Global Error Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception in {request.method} {request.url}: {exc}")
    logger.error(f"Request headers: {dict(request.headers)}")
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(exc)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
Configuration module for Promptify DJ.
Loads environment variables and provides application settings.
"""

import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Spotify Configuration
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    MAX_AUDIO_DURATION: int = int(os.getenv("MAX_AUDIO_DURATION", "30"))
    PLAYLIST_LENGTH: int = int(os.getenv("PLAYLIST_LENGTH", "20"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            "OPENAI_API_KEY",
            "SPOTIFY_CLIENT_ID", 
            "SPOTIFY_CLIENT_SECRET"
        ]
        
        missing_vars = []
        for var in required_vars:
            value = getattr(cls, var)
            if not value or value.strip() == "":
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Only validate values that would cause runtime errors
        if cls.MAX_AUDIO_DURATION <= 0:
            logger.error("MAX_AUDIO_DURATION must be positive")
            return False
            
        if cls.PLAYLIST_LENGTH <= 0:
            logger.error("PLAYLIST_LENGTH must be positive")
            return False
        
        logger.info("Configuration validation successful")
        return True

os.makedirs("logs", exist_ok=True)

logger.remove()
logger.add(
    "logs/promptify_dj.log",
    rotation="10 MB",
    retention="7 days",
    level=Config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
logger.add(
    lambda msg: print(msg, end=""),
    level=Config.LOG_LEVEL,
    format="{time:HH:mm:ss} | {level} | {message}"
) 
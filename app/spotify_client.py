"""
Spotify client for handling authentication and API interactions.
Manages Spotify Web API authentication and provides methods for track search and playlist creation.
"""

from typing import Dict, List, Optional, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from loguru import logger
from app.config import Config

class SpotifyClient:
    """Client for interacting with Spotify Web API."""
    
    def __init__(self, use_user_auth: bool = False):
        """
        Initialize Spotify client.
        
        Args:
            use_user_auth: Whether to use user authentication (for playlist creation)
                          or client credentials (for search only)
        """
        self.use_user_auth = use_user_auth
        self.sp = None
        self.user_id = None
        logger.info(f"Initializing Spotify client (user_auth: {use_user_auth})")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Spotify API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if self.use_user_auth:
                # User authentication for playlist creation
                scope = "playlist-modify-public playlist-modify-private user-read-private"
                
                auth_manager = SpotifyOAuth(
                    client_id=Config.SPOTIFY_CLIENT_ID,
                    client_secret=Config.SPOTIFY_CLIENT_SECRET,
                    redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                    scope=scope
                )
                
                # Create Spotify client - spotipy handles token refresh automatically
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                
                # Get user ID
                user_info = self.sp.current_user()
                self.user_id = user_info['id']
                logger.info(f"Authenticated as user: {user_info['display_name']}")
                
            else:
                # Client credentials for search only
                self.sp = spotipy.Spotify(
                    auth_manager=SpotifyClientCredentials(
                        client_id=Config.SPOTIFY_CLIENT_ID,
                        client_secret=Config.SPOTIFY_CLIENT_SECRET
                    )
                )
                logger.info("Authenticated with client credentials")
            
            return True
            
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
            logger.error(f"Client ID configured: {bool(Config.SPOTIFY_CLIENT_ID)}")
            logger.error(f"Client Secret configured: {bool(Config.SPOTIFY_CLIENT_SECRET)}")
            logger.error(f"Use user auth: {self.use_user_auth}")
            return False
    
    def search_tracks(self, query: str, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            **kwargs: Additional search parameters
            
        Returns:
            List of track dictionaries
        """
        try:
            if self.sp is None:
                logger.info("Spotify client not initialized, attempting authentication...")
                if not self.authenticate():
                    logger.error("Failed to authenticate with Spotify")
                    return []
            
            # Verify we have a proper Spotify client
            if not hasattr(self.sp, 'search'):
                logger.error("Spotify client not properly initialized - missing search method")
                return []
            
            logger.info(f"Searching for tracks: {query}")
            
            # Build search query with filters
            search_params = {
                'q': query,
                'type': 'track',
                'limit': limit
            }
            search_params.update(kwargs)
            
            results = self.sp.search(**search_params)
            tracks = results['tracks']['items']
            
            # Extract relevant track information
            formatted_tracks = []
            for track in tracks:
                try:
                    formatted_track = {
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                        'album': track['album']['name'],
                        'uri': track['uri'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms'],
                        'external_url': track['external_urls']['spotify'],
                        'preview_url': track['preview_url']
                    }
                    formatted_tracks.append(formatted_track)
                except (KeyError, IndexError) as e:
                    logger.warning(f"Skipping malformed track: {e}")
                    continue
            
            logger.info(f"Found {len(formatted_tracks)} tracks")
            return formatted_tracks
            
        except Exception as e:
            logger.error(f"Spotify track search failed: {e}")
            logger.error(f"Search query: {query}")
            logger.error(f"Search limit: {limit}")
            logger.error(f"Spotify client initialized: {self.sp is not None}")
            return []
    
    def create_playlist(self, name: str, description: str, track_uris: List[str]) -> Optional[str]:
        """
        Create a new playlist and add tracks.
        
        Args:
            name: Playlist name
            description: Playlist description
            track_uris: List of Spotify track URIs
            
        Returns:
            Playlist URL if successful, None otherwise
        """
        try:
            if not self.use_user_auth:
                logger.error("User authentication required for playlist creation")
                return None
            
            if self.sp is None or self.user_id is None:
                if not self.authenticate():
                    return None
            
            logger.info(f"Creating playlist: {name}")
            
            # Create playlist
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                description=description,
                public=True
            )
            
            playlist_id = playlist['id']
            playlist_url = playlist['external_urls']['spotify']
            
            # Add tracks to playlist
            if track_uris:
                # Spotify API has a limit of 100 tracks per request
                chunk_size = 100
                for i in range(0, len(track_uris), chunk_size):
                    chunk = track_uris[i:i + chunk_size]
                    self.sp.playlist_add_items(playlist_id, chunk)
            
            logger.info(f"Created playlist: {playlist_url}")
            return playlist_url
            
        except Exception as e:
            logger.error(f"Playlist creation failed: {e}")
            return None

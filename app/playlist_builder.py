"""
Playlist builder that combines parsed intent and Spotify API to generate personalized playlists.
Orchestrates the entire playlist generation process from intent to final playlist.
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from app.config import Config
from app.spotify_client import SpotifyClient
from app.gpt_parser import IntentParser

class PlaylistBuilder:
    """Builder for creating personalized playlists based on user intent."""
    
    def __init__(self):
        """Initialize the playlist builder."""
        self.spotify_client = SpotifyClient(use_user_auth=True)
        self.intent_parser = IntentParser()
        logger.info("Initialized playlist builder")
    
    def generate_playlist(self, transcript: str, create_spotify_playlist: bool = True) -> Dict[str, Any]:
        """
        Generate a complete playlist from audio transcript.
        
        Args:
            transcript: Transcribed text from audio
            create_spotify_playlist: Whether to create a Spotify playlist
            
        Returns:
            Dictionary containing playlist information and tracks
        """
        if not transcript or not transcript.strip():
            logger.warning("Empty transcript provided")
            return {
                "error": "No transcript provided",
                "transcript": transcript,
                "tracks": [],
                "playlist_url": None
            }
            
        try:
            logger.info("Starting playlist generation process")
            
            logger.info("Step 1: Parsing user intent")
            intent = self.intent_parser.parse_intent(transcript)
            if not intent:
                logger.error("Failed to parse intent from transcript")
                return {
                    "error": "Failed to parse user intent",
                    "transcript": transcript,
                    "tracks": [],
                    "playlist_url": None
                }
                
            logger.info("Step 2: Searching for tracks")
            tracks = self._search_tracks_for_intent(intent)
            
            if not tracks:
                logger.error("No tracks found for the given criteria")
                return {
                    "error": "No tracks found for the given criteria",
                    "transcript": transcript,
                    "parsed_intent": intent,
                    "tracks": [],
                    "playlist_url": None
                }
            
            logger.info("Step 3: Curating playlist")
            curated_tracks = self._curate_playlist(tracks, intent)
            
            playlist_url = None
            if create_spotify_playlist and curated_tracks:
                logger.info("Step 4: Creating Spotify playlist")
                playlist_url = self._create_spotify_playlist(curated_tracks, intent)
            playlist_info = {
                "transcript": transcript,
                "parsed_intent": intent,
                "tracks": curated_tracks,
                "playlist_url": playlist_url,
                "generated_at": datetime.now().isoformat(),
                "total_tracks": len(curated_tracks)
            }
            
            logger.info(f"Playlist generation completed. {len(curated_tracks)} tracks selected")
            return playlist_info
            
        except Exception as e:
            logger.error(f"Playlist generation failed: {e}")
            return {
                "error": str(e),
                "transcript": transcript,
                "tracks": [],
                "playlist_url": None
            }
    
    def _search_tracks_for_intent(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for tracks based on parsed intent using Spotify Search API.
        
        Args:
            intent: Enhanced intent dictionary
            
        Returns:
            List of track dictionaries
        """
        try:
            tracks = []
            
            if not intent.get('search_queries'):
                error_msg = "GPT failed to generate search queries"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            for query in intent['search_queries']:
                query_tracks = self.spotify_client.search_tracks(query, limit=Config.PLAYLIST_LENGTH)
                tracks.extend(query_tracks)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Track search failed: {e}")
            return []

    def _curate_playlist(self, tracks: List[Dict[str, Any]], intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Curate and rank tracks for the final playlist.
        
        Args:
            tracks: List of candidate tracks
            intent: Enhanced intent dictionary
            
        Returns:
            Curated list of tracks
        """
        try:
            if not tracks:
                return []
            
            # Remove duplicates based on track ID
            seen_ids = set()
            unique_tracks = []
            for track in tracks:
                track_id = track.get('id')
                if track_id and track_id not in seen_ids:
                    seen_ids.add(track_id)
                    unique_tracks.append(track)
            
            logger.info(f"Removed {len(tracks) - len(unique_tracks)} duplicate tracks")
            
            # Score tracks based on intent
            scored_tracks = []
            for track in unique_tracks:
                score = self._calculate_track_score(track, intent)
                scored_tracks.append((track, score))
            
            # Sort by score (highest first)
            scored_tracks.sort(key=lambda x: x[1], reverse=True)
            
            # Select top tracks
            selected_tracks = [track for track, score in scored_tracks[:Config.PLAYLIST_LENGTH]]
            
            # Add variety by shuffling tracks after the first few
            if len(selected_tracks) > 5:
                first_tracks = selected_tracks[:2]
                remaining_tracks = selected_tracks[2:]
                random.shuffle(remaining_tracks)
                selected_tracks = first_tracks + remaining_tracks
            
            logger.info(f"Curated {len(selected_tracks)} tracks from {len(unique_tracks)} unique candidates")
            return selected_tracks
            
        except Exception as e:
            logger.error(f"Playlist curation failed: {e}")
            return tracks[:Config.PLAYLIST_LENGTH] if tracks else []
    
    def _calculate_track_score(self, track: Dict[str, Any], intent: Dict[str, Any]) -> float:
        """
        Calculate a score for a track based on popularity.
        
        Args:
            track: Track dictionary
            intent: Enhanced intent dictionary (unused but kept for interface consistency)
            
        Returns:
            Score between 0 and 1
        """
        try:
            popularity = track.get('popularity', 50)
            return popularity / 100
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return 0.5
    
    def _create_spotify_playlist(self, tracks: List[Dict[str, Any]], intent: Dict[str, Any]) -> Optional[str]:
        """
        Create a Spotify playlist with the selected tracks.
        
        Args:
            tracks: List of tracks to add to playlist
            intent: Enhanced intent dictionary
            
        Returns:
            Playlist URL if successful, None otherwise
        """
        try:
            if not tracks:
                return None
            
            playlist_name = self._generate_playlist_name(intent)
            playlist_description = self._generate_playlist_description(intent, tracks)
            
            track_uris = [track['uri'] for track in tracks if track.get('uri')]
            playlist_url = self.spotify_client.create_playlist(
                name=playlist_name,
                description=playlist_description,
                track_uris=track_uris
            )
            
            return playlist_url
            
        except Exception as e:
            logger.error(f"Spotify playlist creation failed: {e}")
            return None
    
    def _generate_playlist_name(self, intent: Dict[str, Any]) -> str:
        """
        Generate a playlist name based on intent.
        
        Args:
            intent: Enhanced intent dictionary
            
        Returns:
            Generated playlist name
        """
        try:
            search_queries = intent.get('search_queries', [])
            if search_queries:
                first_query = search_queries[0]
                clean_name = first_query.replace('artist:', '').replace('track:', '').replace('genre:', '').replace('year:', '')
                clean_name = clean_name.replace('"', '').strip()
                playlist_name = f"{clean_name.title()} Vibes"
            else:
                playlist_name = "Promptify DJ Playlist"
            
            return playlist_name
            
        except Exception as e:
            logger.error(f"Playlist name generation failed: {e}")
            return "Promptify DJ Playlist"
    
    def _generate_playlist_description(self, intent: Dict[str, Any], tracks: List[Dict[str, Any]]) -> str:
        """
        Generate a playlist description based on intent and tracks.
        
        Args:
            intent: Enhanced intent dictionary
            tracks: List of tracks in playlist
            
        Returns:
            Generated playlist description
        """
        try:
            description_parts = []
            
            search_queries = intent.get('search_queries', [])
            if search_queries:
                description_parts.append(f"Queries: {', '.join(search_queries[:2])}")
            
            description_parts.append(f"{len(tracks)} tracks")
            description_parts.append("Generated by Promptify DJ")
            
            return " | ".join(description_parts)
            
        except Exception as e:
            logger.error(f"Playlist description generation failed: {e}")
            return f"Generated by Promptify DJ - {len(tracks)} tracks" 
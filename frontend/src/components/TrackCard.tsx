import { useState } from 'react';
import { Track } from '../types';
import { apiClient } from '../api';
import { FaPlay, FaPause, FaThumbsUp, FaThumbsDown, FaSpotify } from 'react-icons/fa';

interface TrackCardProps {
  track: Track;
  playlistId?: string;
}

const TrackCard: React.FC<TrackCardProps> = ({ track, playlistId }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [thumbsUpClicked, setThumbsUpClicked] = useState(false);
  const [thumbsDownClicked, setThumbsDownClicked] = useState(false);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleRefinement = async (action: 'more_like_this' | 'less_like_this') => {
    try {
      setIsRefining(true);
      
      // Update visual state
      if (action === 'more_like_this') {
        setThumbsUpClicked(true);
        setThumbsDownClicked(false);
      } else {
        setThumbsDownClicked(true);
        setThumbsUpClicked(false);
      }
      
      await apiClient.refinePlaylist({
        track_id: track.id,
        action,
        playlist_id: playlistId
      });
    } catch (error) {
      console.error('Refinement failed:', error);
    } finally {
      setIsRefining(false);
    }
  };

  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="track-card">
      <div className="track-image">
        <img 
          src={track.album_art_url} 
          alt={`${track.album} album art`}
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik04MCAxMDBMMTYwIDEwMEw4MCAxMDBaIiBmaWxsPSIjNjc3NDhCIi8+Cjwvc3ZnPgo=';
          }}
        />
      </div>

      <div className="track-info">
        <h3 className="track-title">{track.name}</h3>
        <p className="track-artist">{track.artist}</p>
        <p className="track-album">{track.album}</p>
        <p className="track-duration">{formatDuration(track.duration_ms)}</p>
      </div>

      <div className="track-controls">
        {track.preview_url && (
          <button 
            className={`play-button ${isPlaying ? 'playing' : ''}`}
            onClick={handlePlayPause}
            title={isPlaying ? 'Pause' : 'Play Preview'}
          >
            {isPlaying ? <FaPause /> : <FaPlay />}
          </button>
        )}

        <div className="refinement-buttons">
          <button
            className={`refine-button more-like ${thumbsUpClicked ? 'clicked' : ''}`}
            onClick={() => handleRefinement('more_like_this')}
            disabled={isRefining}
            title="More like this"
          >
            <FaThumbsUp />
          </button>
          
          <button
            className={`refine-button less-like ${thumbsDownClicked ? 'clicked' : ''}`}
            onClick={() => handleRefinement('less_like_this')}
            disabled={isRefining}
            title="Less like this"
          >
            <FaThumbsDown />
          </button>
        </div>

        <a 
          href={track.spotify_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="spotify-link"
          title="Open in Spotify"
        >
          <FaSpotify />
        </a>
      </div>

      {track.preview_url && (
        <audio
          src={track.preview_url}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onEnded={() => setIsPlaying(false)}
          style={{ display: 'none' }}
        />
      )}
    </div>
  );
};

export default TrackCard; 
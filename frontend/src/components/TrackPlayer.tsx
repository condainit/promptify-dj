import { useState, useRef, useEffect } from 'react';
import { Track } from '../types';
import { apiClient } from '../api';
import { FaPlay, FaPause, FaThumbsUp, FaThumbsDown, FaSpotify, FaVolumeUp, FaVolumeMute } from 'react-icons/fa';

interface TrackPlayerProps {
  track: Track;
  playlistId?: string;
  onNext?: () => void;
  onPrevious?: () => void;
  isActive?: boolean;
}

const TrackPlayer: React.FC<TrackPlayerProps> = ({ 
  track, 
  playlistId, 
  onNext, 
  onPrevious, 
  isActive = false 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [thumbsUpClicked, setThumbsUpClicked] = useState(false);
  const [thumbsDownClicked, setThumbsDownClicked] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const [isAudioLoading, setIsAudioLoading] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  useEffect(() => {
    if (isActive && audioRef.current) {
      audioRef.current.play().catch(console.error);
    }
  }, [isActive]);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        setIsAudioLoading(true);
        setAudioError(null);
        audioRef.current.play().catch((error) => {
          console.error('Audio playback failed:', error);
          setAudioError('Failed to play audio preview');
          setIsAudioLoading(false);
        });
      }
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      setIsAudioLoading(false);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    setIsAudioLoading(false);
    if (onNext) {
      onNext();
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (progressRef.current && audioRef.current) {
      const rect = progressRef.current.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const width = rect.width;
      const clickTime = (clickX / width) * duration;
      audioRef.current.currentTime = clickTime;
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
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

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={`track-player ${isActive ? 'active' : ''}`}>
      <div className="track-player-header">
        <div className="track-info">
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
          <div className="track-details">
            <h3 className="track-title">{track.name}</h3>
            <p className="track-artist">{track.artist}</p>
            <p className="track-album">{track.album}</p>
          </div>
        </div>
        
        <div className="track-actions">
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
      </div>

      {track.preview_url && (
        <>
          <div className="player-controls">
            <div className="control-buttons">
              {onPrevious && (
                <button className="control-button" onClick={onPrevious} title="Previous">
                  <span>⏮</span>
                </button>
              )}
              
              <button 
                className={`play-button ${isPlaying ? 'playing' : ''}`}
                onClick={handlePlayPause}
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <FaPause /> : <FaPlay />}
              </button>
              
              {onNext && (
                <button className="control-button" onClick={onNext} title="Next">
                  <span>⏭</span>
                </button>
              )}
            </div>

            <div className="progress-container">
              <span className="time-display">{formatTime(currentTime)}</span>
              <div 
                className="progress-bar" 
                ref={progressRef}
                onClick={handleProgressClick}
              >
                <div className="progress-fill" style={{ width: `${progressPercentage}%` }} />
              </div>
              <span className="time-display">{formatDuration(track.duration_ms)}</span>
            </div>

            <div className="volume-controls">
              <button 
                className="volume-button" 
                onClick={toggleMute}
                title={isMuted ? 'Unmute' : 'Mute'}
              >
                {isMuted ? <FaVolumeMute /> : <FaVolumeUp />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="volume-slider"
                title="Volume"
              />
            </div>
          </div>

                     <audio
             ref={audioRef}
             src={track.preview_url}
             onPlay={() => setIsPlaying(true)}
             onPause={() => setIsPlaying(false)}
             onTimeUpdate={handleTimeUpdate}
             onLoadedMetadata={handleLoadedMetadata}
             onEnded={handleEnded}
             onError={() => {
               setAudioError('Audio preview not available');
               setIsAudioLoading(false);
             }}
             preload="metadata"
           />
        </>
      )}

             {(!track.preview_url || audioError) && (
         <div className="no-preview">
           <p>{audioError || 'No preview available for this track'}</p>
           
           <a 
             href={track.spotify_url} 
             target="_blank" 
             rel="noopener noreferrer"
             className="spotify-link"
           >
             Listen on Spotify
           </a>
         </div>
       )}

       {isAudioLoading && (
         <div className="audio-loading">
           <div className="loading-spinner"></div>
           <p>Loading audio preview...</p>
         </div>
       )}
    </div>
  );
};

export default TrackPlayer; 
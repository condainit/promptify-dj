import { useState, useRef } from 'react';
import { Track } from '../types';
import { apiClient } from '../api';
import { FaThumbsUp, FaThumbsDown } from 'react-icons/fa';

interface TrackItemProps {
  track: Track;
  index: number;
  isActive: boolean;
  onSelect: () => void;
  playlistId?: string;
}

const TrackItem: React.FC<TrackItemProps> = ({ 
  track, 
  index, 
  isActive, 
  onSelect, 
  playlistId 
}) => {
  const [isRefining, setIsRefining] = useState(false);
  const [thumbsUpClicked, setThumbsUpClicked] = useState(false);
  const [thumbsDownClicked, setThumbsDownClicked] = useState(false);
  
  const handleRefinement = async (action: 'more_like_this' | 'less_like_this', e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent track selection
    
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
    <div 
      className={`track-item ${isActive ? 'active' : ''}`}
      onClick={onSelect}
    >
      <div className="track-number">{index + 1}</div>
      
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
        <h4 className="track-title">{track.name}</h4>
        <p className="track-artist">{track.artist}</p>
        <p className="track-album">{track.album}</p>
      </div>
      
      <div className="track-actions">
         <button
           className={`refine-button more-like ${thumbsUpClicked ? 'clicked' : ''}`}
           onClick={(e) => handleRefinement('more_like_this', e)}
           disabled={isRefining}
           title="More like this"
         >
           <FaThumbsUp />
         </button>
         
         <button
           className={`refine-button less-like ${thumbsDownClicked ? 'clicked' : ''}`}
           onClick={(e) => handleRefinement('less_like_this', e)}
           disabled={isRefining}
           title="Less like this"
         >
           <FaThumbsDown />
         </button>
       </div>
      
      <div className="track-duration">
        {formatDuration(track.duration_ms)}
      </div>
    </div>
  );
};

export default TrackItem; 
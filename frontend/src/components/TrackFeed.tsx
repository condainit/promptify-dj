import React from 'react';
import { PlaylistResponse } from '../types';
import TrackCard from './TrackCard';

interface TrackFeedProps {
  playlist: PlaylistResponse;
}

const TrackFeed: React.FC<TrackFeedProps> = ({ playlist }) => {
  const extractPlaylistId = (playlistUrl?: string): string | undefined => {
    if (!playlistUrl || !playlistUrl.includes('playlist/')) {
      return undefined;
    }
    try {
      return playlistUrl.split('playlist/')[-1]?.split('?')[0];
    } catch {
      return undefined;
    }
  };

  const playlistId = extractPlaylistId(playlist.playlist_url);

  return (
    <div className="track-feed">
      <div className="playlist-header">
        <div className="playlist-info">
          <h2>Your Generated Playlist</h2>
          <p className="transcript">
            <strong>Original request:</strong> "{playlist.transcript}"
          </p>
          
          {playlist.parsed_intent && (
            <div className="intent-info">
              <h3>Detected Intent:</h3>
              <ul>
                {Object.entries(playlist.parsed_intent).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {value}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <p className="track-count">
            {playlist.total_tracks} tracks generated
          </p>
        </div>

        {playlist.playlist_url && (
          <div className="playlist-actions">
            <a 
              href={playlist.playlist_url}
              target="_blank"
              rel="noopener noreferrer"
              className="spotify-playlist-link"
            >
              Open in Spotify
            </a>
          </div>
        )}
      </div>

      <div className="tracks-container">
        {playlist.tracks.length > 0 ? (
          playlist.tracks.map((track, index) => (
            <TrackCard 
              key={`${track.id}-${index}`}
              track={track}
              playlistId={playlistId}
            />
          ))
        ) : (
          <div className="no-tracks">
            <p>No tracks were generated. Please try a different prompt.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrackFeed; 
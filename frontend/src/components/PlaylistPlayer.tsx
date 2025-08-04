import { PlaylistResponse } from '../types';
import TrackItem from './TrackItem';

interface PlaylistPlayerProps {
  playlist: PlaylistResponse;
}

const PlaylistPlayer: React.FC<PlaylistPlayerProps> = ({ playlist }) => {
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
    <div className="playlist-player">
      {/* Header */}
      <div className="playlist-header">
        <div className="playlist-info">
          <h2>{playlist.name || playlist.playlist_name || 'Your Generated Playlist'}</h2>
          <p className="playlist-description">{playlist.transcript}</p>
        </div>

        {playlist.playlist_url && (
          <a 
            href={playlist.playlist_url}
            target="_blank"
            rel="noopener noreferrer"
            className="spotify-playlist-link"
          >
            Open in Spotify
          </a>
        )}
      </div>

      {/* Tracks List */}
      <div className="tracks-list">
        {playlist.tracks.map((track, index) => (
          <TrackItem
            key={`${track.id}-${index}`}
            track={track}
            index={index}
            isActive={false}
            onSelect={() => {}}
            playlistId={playlistId}
          />
        ))}
      </div>
    </div>
  );
};

export default PlaylistPlayer; 
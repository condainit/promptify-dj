export interface Track {
  id: string;
  name: string;
  artist: string;
  album: string;
  preview_url?: string;
  album_art_url?: string;
  spotify_url: string;
  duration_ms: number;
  popularity: number;
}

export interface PlaylistResponse {
  transcript: string;
  parsed_intent: {
    mood?: string;
    genre?: string;
    era?: string;
    tempo?: string;
    energy?: string;
    [key: string]: any;
  };
  tracks: Track[];
  playlist_url?: string;
  playlist_id?: string;
  playlist_name?: string;
  generated_at: string;
  total_tracks: number;
  name?: string;
}

export interface AudioRecordingRequest {
  audio_data: string;
  audio_format: string;
  create_playlist: boolean;
}

export interface RefinementRequest {
  track_id: string;
  action: 'more_like_this' | 'less_like_this';
  playlist_id?: string;
} 
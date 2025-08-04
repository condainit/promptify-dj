import React, { useState, useCallback } from 'react';
import { PlaylistResponse } from '../types';
import { apiClient } from '../api';

interface PromptFormProps {
  onPlaylistGenerated: (result: PlaylistResponse) => void;
  onError: (error: string) => void;
  onLoading: (loading: boolean) => void;
}

const PromptForm: React.FC<PromptFormProps> = ({ 
  onPlaylistGenerated, 
  onError, 
  onLoading 
}) => {
  const [prompt, setPrompt] = useState('');
  const [createPlaylist, setCreatePlaylist] = useState(true);

  const exampleQueries = [
    'Upbeat workout music',
    'Chill study vibes',
    'Road trip country songs',
    'Party dance hits',
    'Relaxing bedtime tunes'
  ];

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      onError('Please enter a prompt');
      return;
    }

    try {
      onLoading(true);
      const result = await apiClient.generatePlaylistFromText(prompt.trim(), createPlaylist);
      onPlaylistGenerated(result);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Playlist generation failed');
    } finally {
      onLoading(false);
    }
  }, [prompt, createPlaylist, onPlaylistGenerated, onError, onLoading]);

  const handleExampleClick = useCallback(async (example: string) => {
    setPrompt(example);
    
    try {
      onLoading(true);
      const result = await apiClient.generatePlaylistFromText(example, createPlaylist);
      onPlaylistGenerated(result);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Playlist generation failed');
    } finally {
      onLoading(false);
    }
  }, [createPlaylist, onPlaylistGenerated, onError, onLoading]);

  return (
    <div className="prompt-form">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <textarea
            className="prompt-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the playlist you want... (e.g., 'Upbeat workout music with high energy')"
            rows={4}
            disabled={false}
          />
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={createPlaylist}
              onChange={(e) => setCreatePlaylist(e.target.checked)}
            />
            Create actual Spotify playlist
          </label>
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={!prompt.trim()}
        >
          Generate Playlist
        </button>
      </form>

      <div className="examples-section">
        <h3>Try these examples:</h3>
        <div className="example-buttons">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              className="example-button"
              onClick={() => handleExampleClick(example)}
              type="button"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PromptForm; 
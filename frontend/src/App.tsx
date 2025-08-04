import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import PlaylistPlayer from './components/PlaylistPlayer';
import { PlaylistResponse } from './types';
import { FaMicrophone, FaSearch, FaHome, FaEdit, FaTrash } from 'react-icons/fa';
import { apiClient } from './api';

function App() {
  const [playlistResult, setPlaylistResult] = useState<PlaylistResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [savedPlaylists, setSavedPlaylists] = useState<PlaylistResponse[]>([]);
  const [editingPlaylistIndex, setEditingPlaylistIndex] = useState<number | null>(null);
  const [editingPlaylistName, setEditingPlaylistName] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const recommendedPrompts = [
    "High-energy workout playlist",
    "Focus music for studying and productivity",
    "90s alternative rock classics",
    "Birthday party celebration hits",
    "Songs by artists like The Weeknd and Dua Lipa",
    "Classic 80s pop and rock anthems"
  ];

  const handlePlaylistGenerated = (result: PlaylistResponse) => {
    console.log('Generated playlist result:', result);
    setPlaylistResult(result);
    setError(null);
    // Save to local storage
    const updatedPlaylists = [result, ...savedPlaylists.slice(0, 4)]; // Keep only 5 most recent
    setSavedPlaylists(updatedPlaylists);
    localStorage.setItem('savedPlaylists', JSON.stringify(updatedPlaylists));
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setIsLoading(false);
  };

  const handleLoading = (loading: boolean) => {
    setIsLoading(loading);
    if (loading) {
      setError(null);
    }
  };

  const handleReset = () => {
    setPlaylistResult(null);
    setError(null);
    setIsLoading(false);
    setSearchQuery('');
  };

  // Load saved playlists on component mount
  useEffect(() => {
    const saved = localStorage.getItem('savedPlaylists');
    if (saved) {
      try {
        const playlists = JSON.parse(saved);
        const updatedPlaylists = playlists.map((playlist: any, index: number) => ({
          ...playlist,
          playlist_name: playlist.playlist_name || playlist.name || `Playlist ${index + 1}`,
          playlist_id: playlist.playlist_id || null
        }));
        setSavedPlaylists(updatedPlaylists);
        localStorage.setItem('savedPlaylists', JSON.stringify(updatedPlaylists));
      } catch (error) {
        console.error('Failed to load saved playlists:', error);
      }
    }
  }, []);

  const handleEditPlaylist = (index: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent playlist selection
    const playlist = savedPlaylists[index];
    const currentName = playlist.name || playlist.playlist_name || `Playlist ${index + 1}`;
    setEditingPlaylistIndex(index);
    setEditingPlaylistName(currentName);
  };

  const handleSavePlaylistName = async (index: number) => {
    const playlist = savedPlaylists[index];
    const newName = editingPlaylistName.trim() || `Playlist ${index + 1}`;
    
    try {
      // Update in Spotify if playlist has a Spotify ID
      if (playlist.playlist_id) {
        console.log('Updating Spotify playlist:', playlist.playlist_id, 'to name:', newName);
        await apiClient.updatePlaylistName(playlist.playlist_id, newName);
        console.log('Successfully updated Spotify playlist name');
      } else {
        console.log('No playlist_id found, skipping Spotify update');
      }
      
      // Update local state
      const updatedPlaylists = [...savedPlaylists];
      updatedPlaylists[index] = {
        ...updatedPlaylists[index],
        name: newName,
        playlist_name: newName // Also update the Spotify playlist name
      };
      setSavedPlaylists(updatedPlaylists);
      localStorage.setItem('savedPlaylists', JSON.stringify(updatedPlaylists));
      
      setEditingPlaylistIndex(null);
      setEditingPlaylistName('');
    } catch (error) {
      console.error('Failed to update playlist name:', error);
      alert(`Failed to update playlist name: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleCancelEdit = () => {
    setEditingPlaylistIndex(null);
    setEditingPlaylistName('');
  };

  const handleDeletePlaylist = async (index: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent playlist selection
    if (window.confirm('Are you sure you want to delete this playlist? This will also delete it from Spotify.')) {
      const playlist = savedPlaylists[index];
      
      try {
        // Delete from Spotify if playlist has a Spotify ID
        if (playlist.playlist_id) {
          await apiClient.deletePlaylist(playlist.playlist_id);
        }
        
        // Remove from local state
        const updatedPlaylists = savedPlaylists.filter((_, i) => i !== index);
        setSavedPlaylists(updatedPlaylists);
        localStorage.setItem('savedPlaylists', JSON.stringify(updatedPlaylists));
      } catch (error) {
        console.error('Failed to delete playlist:', error);
        alert('Failed to delete playlist. Please try again.');
      }
    }
  };

  const handleSearchSubmit = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const result = await apiClient.generatePlaylistFromText(searchQuery.trim(), true);
      handlePlaylistGenerated(result);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate playlist');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="main-title" onClick={handleReset} style={{ cursor: 'pointer' }}>
              Promptify DJ
            </h1>
          </div>
          
          <div className="search-section">
            <button 
              className="home-fab"
              onClick={handleReset}
              title="Home"
            >
              <FaHome />
            </button>
            <button 
              className={`record-fab ${isRecording ? 'recording' : ''}`}
                      onClick={async () => {
                        if (isRecording) {
                          // Stop recording
                          setIsRecording(false);
                          if (mediaRecorderRef.current) {
                            mediaRecorderRef.current.stop();
                          }
                        } else {
                          // Start recording
                          try {
                            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                            const mediaRecorder = new MediaRecorder(stream, {
                              mimeType: 'audio/webm;codecs=opus'
                            });
                            
                            const audioChunks: Blob[] = [];
                            
                            mediaRecorder.ondataavailable = (event) => {
                              if (event.data.size > 0) {
                                audioChunks.push(event.data);
                              }
                            };

                            mediaRecorder.onstop = async () => {
                              const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                              
                              // Convert to base64
                              const arrayBuffer = await audioBlob.arrayBuffer();
                              const uint8Array = new Uint8Array(arrayBuffer);
                              const base64Audio = btoa(Array.from(uint8Array, byte => String.fromCharCode(byte)).join(''));
                              
                              // Generate playlist directly
                              try {
                                setIsLoading(true);
                                setError(null);
                                const result = await apiClient.processAudioRecording(base64Audio, 'webm', true);
                                handlePlaylistGenerated(result);
                              } catch (error) {
                                setError(error instanceof Error ? error.message : 'Failed to generate playlist');
                              } finally {
                                setIsLoading(false);
                              }
                              
                              // Stop all tracks
                              stream.getTracks().forEach(track => track.stop());
                            };

                            mediaRecorder.start();
                            mediaRecorderRef.current = mediaRecorder;
                            setIsRecording(true);
                            
                          } catch (error) {
                            setError('Failed to access microphone. Please check permissions.');
                          }
                        }
                      }}
                      title={isRecording ? "Stop Recording" : "Record"}
                    >
                      {isRecording ? '⏹' : <FaMicrophone />}
                    </button>
            <div className="search-container">
              <div className="search-input-wrapper">
                <FaSearch className="search-icon" />
                <input
                  type="text"
                  className="main-search-input"
                  placeholder="What kind of playlist do you want to create?"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchQuery.trim()) {
                      handleSearchSubmit();
                    }
                  }}
                />
              </div>
              <button 
                className="search-submit-btn"
                onClick={handleSearchSubmit}
                disabled={!searchQuery.trim()}
              >
                Generate
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-modal">
              <div className="spinner"></div>
              <p>Generating your playlist...</p>
            </div>
          </div>
        )}

                {playlistResult ? (
                  <div className="results-container">
                    <PlaylistPlayer playlist={playlistResult} />
                  </div>
                ) : (
                  <div className="main-container">

            {/* Recommended Prompts */}
            <div className="recommended-section">
              <h2 className="section-title">Recommended for you</h2>
              <div className="recommended-grid">
                {recommendedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    className="recommended-card"
                    onClick={async () => {
                      setSearchQuery(prompt);
                      try {
                        setIsLoading(true);
                        setError(null);
                        const result = await apiClient.generatePlaylistFromText(prompt, true);
                        handlePlaylistGenerated(result);
                      } catch (error) {
                        setError(error instanceof Error ? error.message : 'Failed to generate playlist');
                      } finally {
                        setIsLoading(false);
                      }
                    }}
                  >
                    <div className="card-content">
                      <h3>{prompt}</h3>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Your Playlists */}
            {savedPlaylists.length > 0 && (
              <div className="playlists-section">
                <h2 className="section-title">Your playlists</h2>
                <div className="playlists-grid">
                  {savedPlaylists.map((playlist, index) => (
                    <div
                      key={index}
                      className="playlist-card"
                    >
                      <div className="card-content" onClick={() => setPlaylistResult(playlist)}>
                        {editingPlaylistIndex === index ? (
                          <div className="edit-playlist-form">
                            <input
                              type="text"
                              value={editingPlaylistName}
                              onChange={(e) => setEditingPlaylistName(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  handleSavePlaylistName(index);
                                } else if (e.key === 'Escape') {
                                  handleCancelEdit();
                                }
                              }}
                              autoFocus
                              className="playlist-name-input"
                            />
                            <div className="edit-actions">
                              <button
                                className="save-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSavePlaylistName(index);
                                }}
                              >
                                Save
                              </button>
                              <button
                                className="cancel-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCancelEdit();
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <h3>{playlist.name || playlist.playlist_name || `Playlist ${index + 1}`}</h3>
                            <p className="playlist-description">{playlist.transcript || 'No description'}</p>
                          </>
                        )}
                      </div>
                      {editingPlaylistIndex !== index && (
                        <div className="playlist-actions">
                          <button
                            className="edit-playlist-btn"
                            onClick={(e) => handleEditPlaylist(index, e)}
                            title="Edit playlist name"
                          >
                            <FaEdit />
                          </button>
                          <button
                            className="delete-playlist-btn"
                            onClick={(e) => handleDeletePlaylist(index, e)}
                            title="Delete playlist"
                          >
                            <FaTrash />
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App; 
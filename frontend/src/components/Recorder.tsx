import React, { useState, useRef, useCallback } from 'react';
import { PlaylistResponse } from '../types';
import { apiClient } from '../api';

interface RecorderProps {
  onPlaylistGenerated: (result: PlaylistResponse) => void;
  onError: (error: string) => void;
  onLoading: (loading: boolean) => void;
}

const Recorder: React.FC<RecorderProps> = ({ 
  onPlaylistGenerated, 
  onError, 
  onLoading 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [showTranscript, setShowTranscript] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        setAudioUrl(URL.createObjectURL(audioBlob));
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      onError('Failed to access microphone. Please check permissions.');
    }
  }, [onError]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const handleTranscribe = useCallback(async () => {
    if (!audioBlob) return;

    try {
      onLoading(true);
      
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const base64Audio = btoa(Array.from(uint8Array, byte => String.fromCharCode(byte)).join(''));
      
      const result = await apiClient.transcribeAudio(base64Audio, 'webm');
      setTranscript(result.transcript);
      setShowTranscript(true);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Transcription failed');
    } finally {
      onLoading(false);
    }
  }, [audioBlob, onLoading, onError]);

  const handleGeneratePlaylist = useCallback(async () => {
    if (!audioBlob) return;

    try {
      onLoading(true);
      
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const base64Audio = btoa(Array.from(uint8Array, byte => String.fromCharCode(byte)).join(''));
      
      const result = await apiClient.processAudioRecording(base64Audio, 'webm', true);
      onPlaylistGenerated(result);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Playlist generation failed');
    } finally {
      onLoading(false);
    }
  }, [audioBlob, onPlaylistGenerated, onError, onLoading]);

  const handleReset = useCallback(() => {
    setAudioBlob(null);
    setAudioUrl(null);
    setTranscript('');
    setShowTranscript(false);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
  }, [audioUrl]);

  return (
    <div className="recorder">
      <div className="recorder-controls">
        {!isRecording && !audioBlob && (
          <button 
            className="record-button"
            onClick={startRecording}
          >
            Start Recording
          </button>
        )}
        
        {isRecording && (
          <button 
            className="stop-button"
            onClick={stopRecording}
          >
            Stop Recording
          </button>
        )}
      </div>

      {audioUrl && (
        <div className="audio-preview">
          <h3>Audio Preview</h3>
          <audio controls src={audioUrl} className="audio-player" />
          
          <div className="audio-actions">
            <button 
              className="transcribe-button"
              onClick={handleTranscribe}
            >
              Transcribe Audio
            </button>
            
            <button 
              className="generate-button"
              onClick={handleGeneratePlaylist}
            >
              Generate Playlist
            </button>
            
            <button 
              className="reset-button"
              onClick={handleReset}
            >
              Record Again
            </button>
          </div>
        </div>
      )}

      {showTranscript && transcript && (
        <div className="transcript-section">
          <h3>Transcription</h3>
          <div className="transcript-text">
            {transcript}
          </div>
          <button 
            className="generate-from-transcript-button"
            onClick={handleGeneratePlaylist}
          >
            Generate Playlist from Transcript
          </button>
        </div>
      )}
    </div>
  );
};

export default Recorder; 
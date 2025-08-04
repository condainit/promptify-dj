import { PlaylistResponse, AudioRecordingRequest, RefinementRequest } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClient {
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('API server connection failed. Make sure the FastAPI server is running.');
      }
      throw error;
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.makeRequest<{ status: string }>('/health');
      return response.status === 'healthy';
    } catch {
      return false;
    }
  }

  async processAudioRecording(
    audioData: string,
    audioFormat: string = 'webm',
    createPlaylist: boolean = true
  ): Promise<PlaylistResponse> {
    const request: AudioRecordingRequest = {
      audio_data: audioData,
      audio_format: audioFormat,
      create_playlist: createPlaylist,
    };

    return this.makeRequest<PlaylistResponse>('/process_audio_recording', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generatePlaylistFromText(
    transcript: string,
    createPlaylist: boolean = true
  ): Promise<PlaylistResponse> {
    const formData = new FormData();
    formData.append('transcript', transcript);
    formData.append('create_playlist', createPlaylist.toString());

    return this.makeRequest<PlaylistResponse>('/generate_playlist', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async transcribeAudio(
    audioData: string,
    audioFormat: string = 'webm'
  ): Promise<{ transcript: string; metadata: any }> {
    const formData = new FormData();
    formData.append('audio_data', audioData);
    formData.append('audio_format', audioFormat);

    return this.makeRequest<{ transcript: string; metadata: any }>('/transcribe', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async refinePlaylist(request: RefinementRequest): Promise<void> {
    return this.makeRequest<void>('/refine', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

    async updatePlaylistName(playlistId: string, newName: string): Promise<void> {
    return this.makeRequest<void>('/playlist/update', {
      method: 'PUT',
      body: JSON.stringify({ playlist_id: playlistId, new_name: newName }),
    });
  }

  async deletePlaylist(playlistId: string): Promise<void> {
    return this.makeRequest<void>('/playlist/delete', {
      method: 'DELETE',
      body: JSON.stringify({ playlist_id: playlistId }),
    });
  }
}

export const apiClient = new ApiClient();
export default apiClient; 
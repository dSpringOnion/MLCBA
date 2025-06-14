import axios from 'axios';
import { ProcessingResult, VideoAnalysisResult, UploadProgress } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for video processing
});

export const uploadVideo = async (
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<VideoAnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress: UploadProgress = {
          loaded: progressEvent.loaded,
          total: progressEvent.total,
          percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total),
        };
        onProgress(progress);
      }
    },
  });

  return response.data;
};

export const processFrame = async (imageData: string): Promise<ProcessingResult> => {
  const response = await api.post('/process_frame', {
    image: imageData,
  });

  return response.data;
};

export const getSampleVideos = async () => {
  const response = await api.get('/sample_videos');
  return response.data;
};

export const processSampleVideo = async (videoId: string): Promise<VideoAnalysisResult> => {
  const response = await api.post(`/process_sample/${videoId}`);
  return response.data;
};

export const getHealthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};
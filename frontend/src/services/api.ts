import axios from 'axios';
import type { QueueState, Song } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const musicApi = {
    // Health & Songs
    getHealth: () => api.get('/health'),
    getSongs: () => api.get<{ success: boolean, songs: Song[] }>('/songs'),

    // Queue Management
    getQueue: () => api.get<QueueState>('/queue'),
    addToQueue: (songId: number) => api.post('/queue/add', { song_id: songId }),
    removeFromQueue: (songId: number) => api.post('/queue/remove', { song_id: songId }),
    skipNext: () => api.post('/queue/skip/next'),
    skipPrev: () => api.post('/queue/skip/prev'),
    moveUp: (songId: number) => api.post('/queue/move-up', { song_id: songId }),
    moveDown: (songId: number) => api.post('/queue/move-down', { song_id: songId }),
    updatePriority: (songId: number, priority: number) =>
        api.post('/queue/update-priority', { song_id: songId, priority }),

    // Undo/Redo
    undo: () => api.post('/undo'),
    redo: () => api.post('/redo'),

    // Recommendations
    getRecommendations: () => api.get<{ success: boolean, recommendations: Song[] }>('/recommendations'),
};

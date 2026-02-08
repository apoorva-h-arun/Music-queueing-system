export interface Song {
    id: number;
    title: string;
    artist: string;
    duration: number;
    popularity: number;
    audio_url?: string;
    cover_url?: string;
    position?: number;
    is_current?: boolean;
}

export interface QueueState {
    success: boolean;
    queue: Song[];
    current_song_id: number;
    size: number;
    mode: string;
}

export interface ApiResponse<T> {
    success: boolean;
    message?: string;
    error?: string;
    data?: T;
}

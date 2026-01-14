import React, { useState, useEffect } from 'react';
import { musicApi } from '../services/api';
import type { Song } from '../types';
import { Plus, Music } from 'lucide-react';

interface AddSongFormProps {
    onAdd: (songId: number) => void;
    loading: boolean;
}

const AddSongForm: React.FC<AddSongFormProps> = ({ onAdd, loading }) => {
    const [availableSongs, setAvailableSongs] = useState<Song[]>([]);
    const [selectedSongId, setSelectedSongId] = useState<string>('');
    const [fetching, setFetching] = useState(false);

    useEffect(() => {
        const fetchAllSongs = async () => {
            try {
                setFetching(true);
                const response = await musicApi.getSongs();
                if (response.data.success) {
                    setAvailableSongs(response.data.songs);
                }
            } catch (err) {
                console.error('Failed to fetch songs', err);
            } finally {
                setFetching(false);
            }
        };
        fetchAllSongs();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedSongId) {
            onAdd(parseInt(selectedSongId));
            setSelectedSongId('');
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                <Plus className="w-4 h-4" />
                Add to Queue
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
                <div className="relative">
                    <select
                        value={selectedSongId}
                        onChange={(e) => setSelectedSongId(e.target.value)}
                        disabled={loading || fetching}
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none disabled:opacity-50"
                    >
                        <option value="">Select a song to add...</option>
                        {availableSongs.map(song => (
                            <option key={song.id} value={song.id}>
                                {song.title} — {song.artist}
                            </option>
                        ))}
                    </select>
                    <Music className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                </div>

                <button
                    type="submit"
                    disabled={!selectedSongId || loading}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold shadow-md transition-all active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
                >
                    {loading ? 'Adding...' : 'Add Song'}
                </button>
            </form>
        </div>
    );
};

export default AddSongForm;

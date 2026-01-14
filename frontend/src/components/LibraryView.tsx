import React from 'react';
import type { Song } from '../types';
import { Play, Plus, Trash2, Music } from 'lucide-react';

interface LibraryViewProps {
    songs: Song[];
    onPlayNow: (song: Song) => void;
    onAddToQueue: (songId: number) => void;
    onRemoveFromLibrary: (songId: number) => void;
}

const LibraryView: React.FC<LibraryViewProps> = ({ songs, onPlayNow, onAddToQueue, onRemoveFromLibrary }) => {
    if (songs.length === 0) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-[var(--text-muted)]">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                    <Music size={40} />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Your library is empty</h2>
                <p>Songs you save will appear here.</p>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-8">
            <div className="flex items-center justify-between mb-8">
                <h2 className="text-3xl font-black text-white">Your Library</h2>
                <span className="text-sm text-[var(--text-muted)]">{songs.length} songs</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {songs.map((song) => (
                    <div key={song.id} className="song-card group">
                        <div className="relative aspect-square rounded-xl overflow-hidden mb-4 shadow-2xl border border-white/5">
                            <img
                                src={song.cover_url}
                                alt={song.title}
                                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                            />
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                <button
                                    onClick={() => onPlayNow(song)}
                                    className="w-12 h-12 bg-[var(--accent)] rounded-full flex items-center justify-center text-[var(--bg-main)] transform hover:scale-110 transition-all active:scale-95 shadow-xl"
                                    title="Play Now"
                                >
                                    <Play size={24} fill="currentColor" />
                                </button>
                                <button
                                    onClick={() => onAddToQueue(song.id)}
                                    className="w-10 h-10 bg-white/10 backdrop-blur-md rounded-full flex items-center justify-center text-white hover:bg-white/20 transition-all active:scale-95"
                                    title="Add to Queue"
                                >
                                    <Plus size={20} />
                                </button>
                            </div>
                        </div>
                        <div className="flex justify-between items-start gap-2">
                            <div className="min-w-0">
                                <h3 className="font-bold truncate text-white">{song.title}</h3>
                                <p className="text-sm text-[var(--text-muted)] truncate">{song.artist}</p>
                            </div>
                            <button
                                onClick={() => onRemoveFromLibrary(song.id)}
                                className="text-[var(--text-muted)] hover:text-red-500 transition-colors p-1"
                                title="Remove from Library"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LibraryView;

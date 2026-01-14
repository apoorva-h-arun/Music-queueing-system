import React from 'react';
import type { Song } from '../types';
import { Play } from 'lucide-react';

interface MainViewProps {
    featuredSong: Song | null;
    allSongs: Song[];
    onPlay: (song: Song) => void;
}

import LibraryView from './LibraryView';
import QueueList from './QueueList';
import type { QueueState } from '../types';
import { Heart, Plus } from 'lucide-react';

interface MainViewProps {
    view: 'home' | 'library';
    allSongs: Song[];
    queueState: QueueState | null;
    library: Song[];
    onPlay: (song: Song) => void;
    onPlayNow: (song: Song) => void;
    onAddToQueue: (songId: number) => void;
    onRemoveFromQueue: (songId: number) => void;
    onMoveUp: (songId: number) => void;
    onMoveDown: (songId: number) => void;
    addToLibrary: (song: Song) => void;
    removeFromLibrary: (id: number) => void;
    loading: boolean;
}

const MainView: React.FC<MainViewProps> = ({
    view,
    allSongs,
    queueState,
    library,
    onPlay,
    onPlayNow,
    onAddToQueue,
    onRemoveFromQueue,
    onMoveUp,
    onMoveDown,
    addToLibrary,
    removeFromLibrary,
    loading
}) => {
    if (view === 'library') {
        return (
            <LibraryView
                songs={library}
                onPlayNow={onPlayNow}
                onAddToQueue={onAddToQueue}
                onRemoveFromLibrary={removeFromLibrary}
            />
        );
    }

    return (
        <div className="flex-1 h-full overflow-y-auto p-8 scroll-smooth">
            {/* Queue Section */}
            <section className="mb-12">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-black text-white">Current Queue</h2>
                    <span className="text-sm text-[var(--text-muted)]">{queueState?.queue.length || 0} songs</span>
                </div>
                <div className="bg-white/5 rounded-2xl overflow-hidden border border-white/10 backdrop-blur-sm">
                    <QueueList
                        queue={queueState?.queue || []}
                        currentSongId={queueState?.current_song_id || -1}
                        onRemove={onRemoveFromQueue}
                        onMoveUp={onMoveUp}
                        onMoveDown={onMoveDown}
                        loading={loading}
                    />
                </div>
            </section>

            {/* Popular Songs Section */}
            <section className="mb-12">
                <h2 className="text-2xl font-bold mb-6 text-white">Popular Songs</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {allSongs.slice(0, 4).map((song) => {
                        const isSaved = library.some(s => s.id === song.id);
                        return (
                            <div key={song.id} className="song-card group relative">
                                <div className="aspect-square rounded-xl overflow-hidden mb-4 shadow-lg border border-white/5">
                                    <img src={song.cover_url} alt={song.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                        <button
                                            onClick={() => onPlay(song)}
                                            className="w-12 h-12 bg-[var(--accent)] text-[var(--bg-main)] rounded-full flex items-center justify-center shadow-xl transform hover:scale-110 active:scale-95 transition-all"
                                        >
                                            <Play size={20} fill="currentColor" />
                                        </button>
                                        <button
                                            onClick={() => onAddToQueue(song.id)}
                                            className="w-10 h-10 bg-white/10 backdrop-blur-md text-white rounded-full flex items-center justify-center hover:bg-white/20 active:scale-95 transition-all"
                                            title="Add to queue"
                                        >
                                            <Plus size={20} />
                                        </button>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between gap-2">
                                    <div className="min-w-0">
                                        <h3 className="font-bold truncate text-white">{song.title}</h3>
                                        <p className="text-sm text-[var(--text-muted)] truncate">{song.artist}</p>
                                    </div>
                                    <button
                                        onClick={() => isSaved ? removeFromLibrary(song.id) : addToLibrary(song)}
                                        className={`${isSaved ? 'text-[var(--accent)]' : 'text-[var(--text-muted)] hover:text-white'} transition-colors p-1`}
                                    >
                                        <Heart size={18} fill={isSaved ? "currentColor" : "none"} />
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </section>
        </div>
    );
};

export default MainView;

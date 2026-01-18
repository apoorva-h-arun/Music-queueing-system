import React from 'react';
import type { Song, QueueState } from '../types';
import { Heart, Plus, Search as SearchIcon, Play } from 'lucide-react';
import QueueList from './QueueList';

interface MainViewProps {
    allSongs: Song[];
    queueState: QueueState | null;
    searchResults: Song[];
    searchQuery: string;
    onPlay: (song: Song) => void;
    onAddToQueue: (songId: number) => void;
    onRemoveFromQueue: (songId: number) => void;
    onMoveUp: (songId: number) => void;
    onMoveDown: (songId: number) => void;
    onLike: (songId: number) => void;
    loading: boolean;
}

const MainView: React.FC<MainViewProps> = ({
    allSongs,
    queueState,
    searchResults,
    searchQuery,
    onPlay,
    onAddToQueue,
    onRemoveFromQueue,
    onMoveUp,
    onMoveDown,
    onLike,
    loading
}) => {
    return (
        <div className="flex-1 h-full overflow-y-auto p-8 scroll-smooth bg-gradient-to-b from-[var(--bg-main)] to-black">
            {/* Search Results Section */}
            {searchQuery && (
                <section className="mb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center gap-2 mb-6">
                        <SearchIcon size={24} className="text-[var(--accent)]" />
                        <h2 className="text-3xl font-black text-white">Search Results</h2>
                    </div>
                    {searchResults.length > 0 ? (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                            {searchResults.map((song) => (
                                <SongCard
                                    key={song.id}
                                    song={song}
                                    onPlay={onPlay}
                                    onAdd={onAddToQueue}
                                    onLike={onLike}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-10 text-[var(--text-muted)] italic">
                            No songs found for "{searchQuery}"
                        </div>
                    )}
                    <div className="h-px bg-white/10 my-12" />
                </section>
            )}

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

            {/* Popular Songs Section (Max Heap Order) */}
            <section className="mb-12">
                <h2 className="text-3xl font-black mb-6 text-white italic tracking-tight">POPULAR SONGS</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {allSongs
                        .filter((song, index, self) => 
                            index === self.findIndex((s) => s.id === song.id)
                        )
                        .slice(0, 10)
                        .map((song) => (
                            <SongCard
                                key={song.id}
                                song={song}
                                onPlay={onPlay}
                                onAdd={onAddToQueue}
                                onLike={onLike}
                            />
                        ))}
                </div>
            </section>
        </div>
    );
};

interface SongCardProps {
    song: Song;
    onPlay: (song: Song) => void;
    onAdd: (songId: number) => void;
    onLike: (songId: number) => void;
}

const SongCard: React.FC<SongCardProps> = ({ song, onPlay, onAdd, onLike }) => {
    return (
        <div className="song-card group relative bg-white/5 p-4 rounded-2xl hover:bg-white/10 transition-all border border-transparent hover:border-white/10">
            <div className="aspect-square rounded-xl overflow-hidden mb-4 shadow-2xl relative">
                <img src={song.cover_url} alt={song.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                    <button
                        onClick={() => onPlay(song)}
                        className="w-12 h-12 bg-[var(--accent)] text-[var(--bg-main)] rounded-full flex items-center justify-center shadow-xl transform hover:scale-110 active:scale-95 transition-all"
                    >
                        <Play size={24} fill="currentColor" />
                    </button>
                    <button
                        onClick={() => onAdd(song.id)}
                        className="w-10 h-10 bg-white/10 backdrop-blur-md text-white rounded-full flex items-center justify-center hover:bg-white/20 active:scale-95 transition-all"
                        title="Add to queue"
                    >
                        <Plus size={24} />
                    </button>
                </div>
            </div>
            <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                    <h3 className="font-bold truncate text-white text-lg">{song.title}</h3>
                    <p className="text-sm text-[var(--text-muted)] truncate">{song.artist}</p>
                    <div className="mt-2 text-xs flex items-center gap-1 text-[var(--accent)] font-mono">
                        <span>LIKES:</span>
                        <span>{song.popularity}</span>
                    </div>
                </div>
                <button
                    onClick={() => onLike(song.id)}
                    className="text-[var(--text-muted)] hover:text-red-500 transition-colors p-1"
                >
                    <Heart size={20} />
                </button>
            </div>
        </div>
    );
};

export default MainView;

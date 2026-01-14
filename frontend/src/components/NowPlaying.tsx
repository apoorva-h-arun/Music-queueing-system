import React from 'react';
import type { Song } from '../types';
import { Play, SkipBack, SkipForward, Music } from 'lucide-react';

interface NowPlayingProps {
    song: Song | null;
    onSkipNext: () => void;
    onSkipPrev: () => void;
    loading: boolean;
}

const NowPlaying: React.FC<NowPlayingProps> = ({ song, onSkipNext, onSkipPrev, loading }) => {
    return (
        <div className="glass-panel p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-widest">Now Playing</h2>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/20">
                    Live State
                </span>
            </div>

            <div className="flex flex-col items-center text-center">
                <div className="w-48 h-48 bg-[var(--bg-main)] rounded-2xl flex items-center justify-center mb-6 shadow-2xl border border-white/5 relative overflow-hidden group">
                    {song && song.cover_url ? (
                        <>
                            <img
                                src={song.cover_url}
                                alt={song.title}
                                className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        </>
                    ) : (
                        <div className="w-full h-full flex items-center justify-center">
                            <Music className={`w-20 h-20 ${song ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'} relative z-10 opacity-20`} />
                        </div>
                    )}
                </div>

                {song ? (
                    <div className="space-y-1 mb-8">
                        <h3 className="text-2xl font-bold text-[var(--text-primary)] leading-tight">{song.title}</h3>
                        <p className="text-[var(--text-secondary)] font-medium">{song.artist}</p>
                        <div className="mt-4 inline-block bg-white/5 border border-white/10 text-[var(--text-muted)] text-[10px] font-bold px-3 py-1 rounded-full tracking-wider">
                            PRIORITY: {song.popularity.toFixed(1)}
                        </div>
                    </div>
                ) : (
                    <div className="space-y-1 mb-8">
                        <h3 className="text-2xl font-bold text-[var(--text-muted)] italic">No Title</h3>
                        <p className="text-[var(--text-muted)]/60 italic">Queue is empty</p>
                    </div>
                )}

                <div className="flex items-center gap-6">
                    <button
                        onClick={onSkipPrev}
                        disabled={loading}
                        className="p-3 rounded-full hover:bg-white/5 text-[var(--text-secondary)] active:scale-95 transition-all disabled:opacity-30"
                        title="Previous Track"
                    >
                        <SkipBack className="w-6 h-6" />
                    </button>

                    <button className="btn-play shadow-[0_0_20px_rgba(214,174,123,0.3)]">
                        <Play className="w-6 h-6 fill-current translate-x-0.5" />
                    </button>

                    <button
                        onClick={onSkipNext}
                        disabled={loading}
                        className="p-3 rounded-full hover:bg-white/5 text-[var(--text-secondary)] active:scale-95 transition-all disabled:opacity-30"
                        title="Next Track"
                    >
                        <SkipForward className="w-6 h-6" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NowPlaying;

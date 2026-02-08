import React from 'react';
import type { Song } from '../types';
import { ChevronRight } from 'lucide-react';

interface TrendingNowProps {
    songs: Song[];
    onPlay: (song: Song) => void;
}

const TrendingNow: React.FC<TrendingNowProps> = ({ songs, onPlay }) => {
    return (
        <div className="w-80 bg-[var(--bg-sidebar)] h-full p-6 border-l border-white/5 overflow-y-auto">
            <h2 className="text-xl font-bold mb-6">Trending Now</h2>

            <div className="flex flex-col gap-4">
                {songs.map((song) => (
                    <div
                        key={song.id}
                        className="flex items-center gap-3 group cursor-pointer hover:bg-white/5 p-2 rounded-xl transition-all"
                        onClick={() => onPlay(song)}
                    >
                        <div className="w-10 h-10 rounded-full overflow-hidden bg-[var(--bg-card)]">
                            {song.cover_url ? (
                                <img src={song.cover_url} alt={song.title} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-[var(--accent)] text-[var(--bg-main)] font-bold">
                                    {song.title[0]}
                                </div>
                            )}
                        </div>

                        <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold truncate group-hover:text-[var(--accent)] transition-colors">{song.title}</h3>
                            <p className="text-xs text-[var(--text-muted)] truncate">{song.artist}</p>
                        </div>

                        <ChevronRight size={16} className="text-[var(--text-muted)] group-hover:text-white" />
                    </div>
                ))}

                {songs.length === 0 && (
                    <div className="text-center py-10 text-[var(--text-muted)] italic">
                        No trending songs
                    </div>
                )}
            </div>
        </div>
    );
};

export default TrendingNow;

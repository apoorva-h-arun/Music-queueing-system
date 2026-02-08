import React from 'react';
import type { Song } from '../types';
import { ChevronUp, ChevronDown, Trash2, GripVertical } from 'lucide-react';

interface QueueItemProps {
    song: Song;
    isCurrent: boolean;
    position: number;
    onRemove: () => void;
    onMoveUp: () => void;
    onMoveDown: () => void;
    isFirst: boolean;
    isLast: boolean;
    loading: boolean;
}

const QueueItem: React.FC<QueueItemProps> = ({
    song,
    isCurrent,
    position,
    onRemove,
    onMoveUp,
    onMoveDown,
    isFirst,
    isLast,
    loading
}) => {
    // Priority based background intensity
    const priorityLevel = Math.min(Math.floor(song.popularity / 20), 4); // 0-4
    const priorityColors = [
        'bg-transparent',
        'bg-white/[0.02]',
        'bg-white/[0.04]',
        'bg-white/[0.06]',
        'bg-white/[0.08]'
    ];

    return (
        <div className={`group flex items-center gap-4 px-6 py-4 transition-all border-b border-white/[0.03] ${isCurrent ? 'bg-[var(--accent)] text-[var(--bg-main)]' : 'hover:bg-white/[0.05]'} ${!isCurrent ? priorityColors[priorityLevel] : ''}`}>
            {/* Position & Handle */}
            <div className="flex items-center gap-3 w-12 shrink-0">
                <GripVertical className={`w-4 h-4 ${isCurrent ? 'text-[var(--bg-main)]/30' : 'text-[var(--text-muted)] opacity-0 group-hover:opacity-100'}`} />
                <span className={`text-sm font-black ${isCurrent ? 'text-[var(--bg-main)]/60' : 'text-[var(--text-muted)]'}`}>
                    {position.toString().padStart(2, '0')}
                </span>
            </div>

            {/* Song Info */}
            <div className="flex-1 min-w-0">
                <h4 className="font-bold truncate text-sm md:text-base leading-tight">
                    {song.title}
                </h4>
                <p className={`text-xs md:text-sm truncate ${isCurrent ? 'text-[var(--bg-main)]/70' : 'text-[var(--text-muted)]'}`}>
                    {song.artist}
                </p>
            </div>


            {/* Actions */}
            <div className="flex items-center gap-1 shrink-0">
                <button
                    onClick={onMoveUp}
                    disabled={isFirst || loading}
                    className={`p-2 rounded-full transition-all ${isCurrent ? 'hover:bg-black/10 text-[var(--bg-main)]' : 'hover:bg-white/10 text-[var(--text-secondary)]'} disabled:opacity-20`}
                    title="Move Up"
                >
                    <ChevronUp className="w-5 h-5 font-bold" />
                </button>
                <button
                    onClick={onMoveDown}
                    disabled={isLast || loading}
                    className={`p-2 rounded-full transition-all ${isCurrent ? 'hover:bg-black/10 text-[var(--bg-main)]' : 'hover:bg-white/10 text-[var(--text-secondary)]'} disabled:opacity-20`}
                    title="Move Down"
                >
                    <ChevronDown className="w-5 h-5 font-bold" />
                </button>
                <button
                    onClick={onRemove}
                    disabled={loading}
                    className={`p-2 rounded-full transition-all ${isCurrent ? 'hover:bg-red-900/40 text-[var(--bg-main)]' : 'hover:bg-red-500/10 text-red-500'} disabled:opacity-20`}
                    title="Remove"
                >
                    <Trash2 className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
};

export default QueueItem;

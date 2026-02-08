import React from 'react';
import type { Song } from '../types';
import QueueItem from './QueueItem';

interface QueueListProps {
    queue: Song[];
    currentSongId: number;
    onRemove: (id: number) => void;
    onMoveUp: (id: number) => void;
    onMoveDown: (id: number) => void;
    loading: boolean;
}

const QueueList: React.FC<QueueListProps> = ({
    queue,
    currentSongId,
    onRemove,
    onMoveUp,
    onMoveDown,
    loading
}) => {
    if (queue.length === 0) {
        return (
            <div className="py-20 text-center">
                <p className="text-slate-400 italic">Queue is empty. Add a song to begin.</p>
            </div>
        );
    }

    return (
        <div className="divide-y divide-slate-100">
            {queue.map((song, index) => (
                <QueueItem
                    key={`${song.id}-${index}`}
                    song={song}
                    isCurrent={song.id === currentSongId}
                    position={index + 1}
                    onRemove={() => onRemove(song.id)}
                    onMoveUp={() => onMoveUp(song.id)}
                    onMoveDown={() => onMoveDown(song.id)}
                    isFirst={index === 0}
                    isLast={index === queue.length - 1}
                    loading={loading}
                />
            ))}
        </div>
    );
};

export default QueueList;

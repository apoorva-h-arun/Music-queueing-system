import React, { useState, useEffect, useRef } from 'react';
import type { Song } from '../types';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react';

interface PlaybackControlsProps {
    currentSong: Song | null;
    onSkipNext: () => void;
    onSkipPrev: () => void;
    onSongPlay?: (songId: number) => void;
}

const PlaybackControls: React.FC<PlaybackControlsProps> = ({ currentSong, onSkipNext, onSkipPrev, onSongPlay }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(Number(localStorage.getItem('player-volume')) || 0.7);
    const [isMuted, setIsMuted] = useState(false);
    const [isSeeking, setIsSeeking] = useState(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Sync audio source and handle auto-play
    useEffect(() => {
        if (currentSong && audioRef.current) {
            const newSrc = currentSong.audio_url || '';
            // Only update src if it's actually a different song
            if (audioRef.current.src !== newSrc) {
                audioRef.current.src = newSrc;
                if (isPlaying) {
                    audioRef.current.play().catch(e => console.error("Playback failed", e));
                }
            }
        } else if (!currentSong && audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
        }
    }, [currentSong?.id]);

    // Track when audio actually starts playing
    const lastPlayedSongRef = React.useRef<number | null>(null);
    const playTrackedRef = React.useRef<boolean>(false);
    
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio || !currentSong) return;

        // Reset tracking when song changes
        if (lastPlayedSongRef.current !== currentSong.id) {
            lastPlayedSongRef.current = currentSong.id;
            playTrackedRef.current = false;
        }

        const handlePlay = () => {
            // Track play when audio starts (only once per song)
            if (currentSong && onSongPlay && !playTrackedRef.current) {
                // Only track if starting from near beginning (within first 2 seconds)
                // This prevents counting resume after pause as a new play
                if (audio.currentTime < 2) {
                    playTrackedRef.current = true;
                    console.log(`Tracking play for song ${currentSong.id}`);
                    onSongPlay(currentSong.id);
                }
            }
        };

        audio.addEventListener('play', handlePlay);
        
        return () => {
            audio.removeEventListener('play', handlePlay);
        };
    }, [currentSong?.id, onSongPlay]);

    // Handle initial volume
    useEffect(() => {
        if (audioRef.current) {
            audioRef.current.volume = isMuted ? 0 : volume;
        }
    }, [volume, isMuted]);

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.code === 'Space' && e.target === document.body) {
                e.preventDefault();
                togglePlay();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isPlaying]);

    const togglePlay = () => {
        if (!audioRef.current) return;
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play().catch(e => console.error("Playback failed", e));
        }
        setIsPlaying(!isPlaying);
    };

    const handleTimeUpdate = () => {
        if (audioRef.current && !isSeeking) {
            setCurrentTime(audioRef.current.currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setDuration(audioRef.current.duration);
        }
    };

    const handleEnded = () => {
        // Track that song finished playing (ensure it's counted)
        if (currentSong && onSongPlay) {
            // Reset tracking so if song restarts, it can be tracked again
            playTrackedRef.current = false;
            onSongPlay(currentSong.id);
        }
        onSkipNext();
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseFloat(e.target.value);
        setCurrentTime(val);
        if (audioRef.current) {
            audioRef.current.currentTime = val;
        }
    };

    const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseFloat(e.target.value);
        setVolume(val);
        localStorage.setItem('player-volume', val.toString());
        if (val > 0) setIsMuted(false);
    };

    const formatTime = (time: number) => {
        if (isNaN(time)) return "0:00";
        const mins = Math.floor(time / 60);
        const secs = Math.floor(time % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="h-24 bg-[var(--bg-main)] border-t border-white/5 px-8 flex items-center justify-between gap-8 select-none">
            <audio
                ref={audioRef}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={handleEnded}
            />

            {/* Song Info */}
            <div className="flex items-center gap-4 w-1/4">
                <div className="w-14 h-14 rounded-lg overflow-hidden bg-[var(--bg-card)] shadow-[0_8px_20px_rgba(0,0,0,0.4)] border border-white/10 group relative">
                    {currentSong?.cover_url ? (
                        <img
                            src={currentSong.cover_url}
                            alt={currentSong.title}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center bg-white/5">
                            <SkipBack className="w-6 h-6 text-white/20" />
                        </div>
                    )}
                </div>
                <div className="min-w-0">
                    <h4 className="font-bold text-sm truncate text-white">{currentSong?.title || "Not Playing"}</h4>
                    <p className="text-xs text-[var(--text-muted)] truncate">{currentSong?.artist || "Select a song"}</p>
                </div>
            </div>

            {/* Controls & Progress */}
            <div className="flex-1 flex flex-col items-center max-w-2xl gap-2 mt-1">
                <div className="flex items-center gap-6">
                    <button onClick={onSkipPrev} className="text-[var(--text-muted)] hover:text-white transition-all active:scale-90">
                        <SkipBack size={22} fill="currentColor" />
                    </button>

                    <button
                        onClick={togglePlay}
                        className="w-10 h-10 bg-white text-black rounded-full flex items-center justify-center hover:scale-105 active:scale-95 transition-all shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                    >
                        {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" className="translate-x-0.5" />}
                    </button>

                    <button onClick={onSkipNext} className="text-[var(--text-muted)] hover:text-white transition-all active:scale-90">
                        <SkipForward size={22} fill="currentColor" />
                    </button>
                </div>

                <div className="w-full flex items-center gap-3 group px-4">
                    <span className="text-[10px] text-[var(--text-muted)] w-8 text-right font-medium tabular-nums">
                        {formatTime(currentTime)}
                    </span>
                    <div className="flex-1 relative h-6 flex items-center">
                        <input
                            type="range"
                            min="0"
                            max={duration || 0}
                            step="0.1"
                            value={currentTime}
                            onChange={handleSeek}
                            onMouseDown={() => setIsSeeking(true)}
                            onMouseUp={() => setIsSeeking(false)}
                            className="absolute w-full h-1 bg-white/10 rounded-full appearance-none cursor-pointer outline-none hover:bg-white/20 transition-colors [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:opacity-0 group-hover:[&::-webkit-slider-thumb]:opacity-100 [&::-webkit-slider-thumb]:transition-opacity"
                            style={{
                                background: `linear-gradient(to right, #d6ae7b ${(currentTime / (duration || 1)) * 100}%, rgba(255,255,255,0.1) 0%)`
                            }}
                        />
                    </div>
                    <span className="text-[10px] text-[var(--text-muted)] w-8 font-medium tabular-nums">
                        {formatTime(duration)}
                    </span>
                </div>
            </div>

            {/* Volume Controls */}
            <div className="flex items-center gap-3 w-1/4 justify-end group/volume">
                <button
                    onClick={() => setIsMuted(!isMuted)}
                    className="text-[var(--text-muted)] hover:text-white transition-colors"
                >
                    {isMuted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
                </button>
                <div className="w-24 relative h-6 flex items-center">
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={isMuted ? 0 : volume}
                        onChange={handleVolumeChange}
                        className="w-full h-1 bg-white/10 rounded-full appearance-none cursor-pointer outline-none hover:bg-white/20 transition-colors [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:opacity-0 group-hover/volume:[&::-webkit-slider-thumb]:opacity-100 [&::-webkit-slider-thumb]:transition-opacity"
                        style={{
                            background: `linear-gradient(to right, #d6ae7b ${(isMuted ? 0 : volume) * 100}%, rgba(255,255,255,0.1) 0%)`
                        }}
                    />
                </div>
            </div>
        </div>
    );
};

export default PlaybackControls;

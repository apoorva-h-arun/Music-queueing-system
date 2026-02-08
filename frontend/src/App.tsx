import React, { useState, useEffect, useCallback, useRef } from 'react';
import { musicApi } from './services/api';
import type { Song, QueueState } from './types';
import Sidebar from './components/Sidebar';
import TrendingNow from './components/TrendingNow';
import MainView from './components/MainView';
import Header from './components/Header';
import PlaybackControls from './components/PlaybackControls';

const App: React.FC = () => {
  const [queueState, setQueueState] = useState<QueueState | null>(null);
  const [allSongs, setAllSongs] = useState<Song[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Song[]>([]);
  const [loading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [queueRes, songsRes] = await Promise.all([
        musicApi.getQueue(),
        musicApi.getSongs()
      ]);

      if (queueRes.data.success) setQueueState(queueRes.data);
      if (songsRes.data.success) {
        // Deduplicate songs by ID to prevent duplicates
        const songs = songsRes.data.songs || [];
        const uniqueSongs = songs.filter((song: Song, index: number, self: Song[]) => 
          index === self.findIndex((s: Song) => s.id === song.id)
        );
        setAllSongs(uniqueSongs);
      }

      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error connecting to backend');
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Handle real-time search with debounce
  useEffect(() => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);

    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const res = await musicApi.search(searchQuery);
        if (res.data.success) {
          // Deduplicate search results by ID
          const results = res.data.results || [];
          const uniqueResults = results.filter((song: Song, index: number, self: Song[]) => 
            index === self.findIndex((s: Song) => s.id === song.id)
          );
          setSearchResults(uniqueResults);
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 300); // 300ms debounce

    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
  }, [searchQuery]);

  const handleAction = async (action: () => Promise<any>, successMsg: string) => {
    try {
      const response = await action();
      if (response.data.success) {
        setLastAction(successMsg);
        await fetchData();
        setTimeout(() => setLastAction(null), 3000);
      } else {
        setError(response.data.error || 'Operation failed');
      }
    } catch (err: any) {
      setError(err.message || 'Error performing operation');
    }
  };

  const onPlaySong = async (song: Song) => {
    await handleAction(() => musicApi.addToQueue(song.id), `Added ${song.title} to queue`);
    // Trigger play update to backend
    musicApi.playSong(song.id).catch(console.error);
  };

  const onLikeSong = async (songId: number) => {
    try {
      const res = await musicApi.likeSong(songId);
      if (res.data.success) {
        setLastAction('Song liked!');
        fetchData(); // Refresh to see updated popular songs
        setTimeout(() => setLastAction(null), 2000);
      }
    } catch (err) {
      setError('Failed to like song');
    }
  };

  const currentSong = queueState?.queue.find(s => s.id === queueState.current_song_id) || null;

  return (
    <div className="h-screen flex flex-col bg-[var(--bg-main)] text-[var(--text-primary)]">
      {(error || lastAction) && (
        <div className={`fixed top-24 right-4 z-50 p-4 rounded-xl shadow-2xl ${error ? 'bg-red-900 border border-red-500 text-white' : 'bg-[var(--accent)] text-[var(--bg-main)] font-bold'} animate-in fade-in slide-in-from-top-4 duration-300`}>
          {error || lastAction}
        </div>
      )}

      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />

        <MainView
          allSongs={allSongs}
          queueState={queueState}
          searchResults={searchResults}
          searchQuery={searchQuery}
          onPlay={onPlaySong}
          onAddToQueue={(id) => handleAction(() => musicApi.addToQueue(id), 'Added to queue')}
          onRemoveFromQueue={(id) => handleAction(() => musicApi.removeFromQueue(id), 'Removed from queue')}
          onMoveUp={(id) => handleAction(() => musicApi.moveUp(id), 'Moved up')}
          onMoveDown={(id) => handleAction(() => musicApi.moveDown(id), 'Moved down')}
          onLike={onLikeSong}
          loading={loading}
        />

        <TrendingNow
          songs={allSongs
            .filter((song, index, self) => 
              index === self.findIndex((s) => s.id === song.id)
            )
            .slice(0, 10)}
          onPlay={onPlaySong}
        />
      </div>

      <PlaybackControls
        currentSong={currentSong}
        onSkipNext={() => handleAction(musicApi.skipNext, 'Skipped next')}
        onSkipPrev={() => handleAction(musicApi.skipPrev, 'Skipped previous')}
        onSongPlay={(songId) => {
          // Track actual playback
          musicApi.playSong(songId).catch(console.error);
        }}
      />
    </div>
  );
};

export default App;

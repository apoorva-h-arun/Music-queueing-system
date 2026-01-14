import React, { useState, useEffect, useCallback } from 'react';
import { musicApi } from './services/api';
import type { Song, QueueState } from './types';
import Sidebar from './components/Sidebar';
import TrendingNow from './components/TrendingNow';
import MainView from './components/MainView';
import PlaybackControls from './components/PlaybackControls';
import { AlertCircle } from 'lucide-react';

const App: React.FC = () => {
  const [view, setView] = useState<'home' | 'library'>('home');
  const [queueState, setQueueState] = useState<QueueState | null>(null);
  const [allSongs, setAllSongs] = useState<Song[]>([]);
  const [library, setLibrary] = useState<Song[]>(() => {
    const saved = localStorage.getItem('music-library');
    return saved ? JSON.parse(saved) : [];
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);

  // Persist library
  useEffect(() => {
    localStorage.setItem('music-library', JSON.stringify(library));
  }, [library]);

  const fetchData = useCallback(async () => {
    try {
      const [queueRes, songsRes] = await Promise.all([
        musicApi.getQueue(),
        musicApi.getSongs()
      ]);

      if (queueRes.data.success) setQueueState(queueRes.data);
      if (songsRes.data.success) setAllSongs(songsRes.data.songs);

      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error connecting to backend');
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleAction = async (action: () => Promise<any>, successMsg: string, optimisticUpdate?: () => void) => {
    try {
      if (optimisticUpdate) optimisticUpdate();
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

  const currentSong = queueState?.queue.find(s => s.id === queueState.current_song_id) || null;

  const onPlaySong = async (song: Song) => {
    // Simple add to queue for trending/featured
    await handleAction(() => musicApi.addToQueue(song.id), `Added ${song.title} to queue`);
  };

  const onPlayNow = async (song: Song) => {
    // Clear all (if supported by API, otherwise just skip) and add this one
    // For simplicity with current API, we just add it and it might be at the end, 
    // but a real "play now" would prioritize it.
    await handleAction(() => musicApi.addToQueue(song.id), `Playing ${song.title}`);
  };

  const addToLibrary = (song: Song) => {
    if (!library.find(s => s.id === song.id)) {
      setLibrary([...library, song]);
      setLastAction(`Added ${song.title} to library`);
      setTimeout(() => setLastAction(null), 3000);
    }
  };

  const removeFromLibrary = (id: number) => {
    setLibrary(library.filter(s => s.id !== id));
  };

  return (
    <div className="h-screen flex flex-col bg-[var(--bg-main)] text-[var(--text-primary)]">
      {(error || lastAction) && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-xl shadow-2xl ${error ? 'bg-red-900 border border-red-500' : 'bg-green-900 border border-green-500'} animate-bounce`}>
          {error || lastAction}
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentView={view} onViewChange={setView} />

        <MainView
          view={view}
          allSongs={allSongs}
          queueState={queueState}
          library={library}
          onPlay={onPlaySong}
          onPlayNow={onPlayNow}
          onAddToQueue={(id) => handleAction(() => musicApi.addToQueue(id), 'Added to queue')}
          onRemoveFromQueue={(id) => handleAction(() => musicApi.removeFromQueue(id), 'Removed from queue')}
          onMoveUp={(id) => handleAction(() => musicApi.moveUp(id), 'Moved up')}
          onMoveDown={(id) => handleAction(() => musicApi.moveDown(id), 'Moved down')}
          addToLibrary={addToLibrary}
          removeFromLibrary={removeFromLibrary}
          loading={loading}
        />

        <TrendingNow
          songs={allSongs.slice(0, 6)}
          onPlay={onPlaySong}
        />
      </div>

      <PlaybackControls
        currentSong={currentSong}
        onSkipNext={() => handleAction(musicApi.skipNext, 'Skipped next')}
        onSkipPrev={() => handleAction(musicApi.skipPrev, 'Skipped previous')}
      />
    </div>
  );
};

export default App;

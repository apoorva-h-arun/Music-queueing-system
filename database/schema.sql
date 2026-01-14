-- Music Queue Manager - Database Schema
-- PostgreSQL Schema Definition

-- Drop existing tables if they exist
DROP TABLE IF EXISTS play_history CASCADE;
DROP TABLE IF EXISTS queue_snapshot CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS songs CASCADE;

-- Songs table
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    album VARCHAR(255),
    duration INTEGER NOT NULL,  -- Duration in seconds
    popularity DECIMAL(5,2) DEFAULT 0.0,  -- Popularity score 0-100
    genre VARCHAR(100),
    release_year INTEGER,
    audio_url TEXT,
    cover_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Queue snapshot table
CREATE TABLE queue_snapshot (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    priority DECIMAL(5,2) DEFAULT 0.0,
    is_current BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Play history table
CREATE TABLE play_history (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_played INTEGER,  -- How long the song was played (seconds)
    completed BOOLEAN DEFAULT FALSE  -- Did the user listen to the whole song?
);

-- Indexes for performance
CREATE INDEX idx_queue_position ON queue_snapshot(position);
CREATE INDEX idx_queue_priority ON queue_snapshot(priority DESC);
CREATE INDEX idx_queue_current ON queue_snapshot(is_current);
CREATE INDEX idx_history_user ON play_history(user_id);
CREATE INDEX idx_history_song ON play_history(song_id);
CREATE INDEX idx_history_played_at ON play_history(played_at DESC);
CREATE INDEX idx_songs_popularity ON songs(popularity DESC);
CREATE INDEX idx_songs_artist ON songs(artist);
CREATE INDEX idx_songs_genre ON songs(genre);

-- Comments
COMMENT ON TABLE songs IS 'Music tracks available in the system';
COMMENT ON TABLE users IS 'System users who can create and manage queues';
COMMENT ON TABLE queue_snapshot IS 'Current state of the music queue';
COMMENT ON TABLE play_history IS 'History of songs played by users';

COMMENT ON COLUMN songs.duration IS 'Song duration in seconds';
COMMENT ON COLUMN songs.popularity IS 'Popularity score from 0 to 100';
COMMENT ON COLUMN queue_snapshot.priority IS 'Calculated priority for recommendations';
COMMENT ON COLUMN queue_snapshot.is_current IS 'Whether this is the currently playing song';
COMMENT ON COLUMN play_history.completed IS 'Whether the user listened to the entire song';

-- Success message
SELECT 'Database schema created successfully!' AS status;

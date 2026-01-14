"""
Database Connection and Operations

Handles PostgreSQL connection, session management, and queue persistence
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from models import Base, Song, User, QueueSnapshot, PlayHistory
from typing import List, Optional, Dict
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./music_queue.db'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for simplicity
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

def init_database():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

def get_session():
    """Get a new database session"""
    return Session()

def close_session():
    """Close the current session"""
    Session.remove()

# ============================================================================
# SONG OPERATIONS
# ============================================================================

def get_song_by_id(song_id: int) -> Optional[Song]:
    """Get a song by ID"""
    session = get_session()
    try:
        return session.query(Song).filter(Song.id == song_id).first()
    finally:
        session.close()

def get_all_songs() -> List[Song]:
    """Get all songs"""
    session = get_session()
    try:
        return session.query(Song).all()
    finally:
        session.close()

def get_song_by_title(title: str) -> Optional[Song]:
    """Get a song by title"""
    session = get_session()
    try:
        return session.query(Song).filter(Song.title == title).first()
    finally:
        session.close()

def create_song(title: str, artist: str, duration: int, **kwargs) -> Song:
    """Create a new song"""
    session = get_session()
    try:
        song = Song(
            title=title,
            artist=artist,
            duration=duration,
            album=kwargs.get('album'),
            popularity=kwargs.get('popularity', 0.0),
            genre=kwargs.get('genre'),
            release_year=kwargs.get('release_year'),
            audio_url=kwargs.get('audio_url'),
            cover_url=kwargs.get('cover_url')
        )
        session.add(song)
        session.commit()
        session.refresh(song)
        return song
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_song(song_id: int) -> bool:
    """Delete a song"""
    session = get_session()
    try:
        song = session.query(Song).filter(Song.id == song_id).first()
        if song:
            session.delete(song)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ============================================================================
# QUEUE SNAPSHOT OPERATIONS
# ============================================================================

def save_queue_snapshot(queue_data: List[Dict]) -> bool:
    """
    Save the current queue state to database
    queue_data: List of dicts with {song_id, position, priority, is_current}
    """
    session = get_session()
    try:
        # Clear existing snapshot
        session.query(QueueSnapshot).delete()
        
        # Insert new snapshot
        for item in queue_data:
            snapshot = QueueSnapshot(
                song_id=item['song_id'],
                position=item['position'],
                priority=item.get('priority', 0.0),
                is_current=item.get('is_current', False)
            )
            session.add(snapshot)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving queue snapshot: {e}")
        return False
    finally:
        session.close()

def load_queue_snapshot() -> List[Dict]:
    """Load the queue state from database"""
    session = get_session()
    try:
        snapshots = session.query(QueueSnapshot).order_by(QueueSnapshot.position).all()
        return [s.to_dict() for s in snapshots]
    finally:
        session.close()

def clear_queue_snapshot() -> bool:
    """Clear the queue snapshot"""
    session = get_session()
    try:
        session.query(QueueSnapshot).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

# ============================================================================
# USER OPERATIONS
# ============================================================================

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by ID"""
    session = get_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()

def create_user(name: str, email: str, premium: bool = False) -> User:
    """Create a new user"""
    session = get_session()
    try:
        user = User(name=name, email=email, premium=premium)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# ============================================================================
# PLAY HISTORY OPERATIONS
# ============================================================================

def add_play_history(song_id: int, user_id: int, duration_played: int = None, completed: bool = False) -> PlayHistory:
    """Add a play history entry"""
    session = get_session()
    try:
        history = PlayHistory(
            song_id=song_id,
            user_id=user_id,
            duration_played=duration_played,
            completed=completed
        )
        session.add(history)
        session.commit()
        session.refresh(history)
        return history
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_history(user_id: int, limit: int = 50) -> List[PlayHistory]:
    """Get play history for a user"""
    session = get_session()
    try:
        return session.query(PlayHistory)\
            .filter(PlayHistory.user_id == user_id)\
            .order_by(PlayHistory.played_at.desc())\
            .limit(limit)\
            .all()
    finally:
        session.close()

def get_popular_songs(limit: int = 10) -> List[Song]:
    """Get most popular songs based on play count"""
    session = get_session()
    try:
        from sqlalchemy import func
        
        popular = session.query(
            Song,
            func.count(PlayHistory.id).label('play_count')
        )\
        .join(PlayHistory)\
        .group_by(Song.id)\
        .order_by(func.count(PlayHistory.id).desc())\
        .limit(limit)\
        .all()
        
        return [song for song, count in popular]
    finally:
        session.close()

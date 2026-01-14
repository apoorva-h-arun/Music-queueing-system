"""
Database Models

SQLAlchemy ORM models for the music queue system
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Song(Base):
    """Song model - represents a music track"""
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    album = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in seconds
    popularity = Column(Float, default=0.0)  # Popularity score 0-100
    genre = Column(String(100), nullable=True)
    release_year = Column(Integer, nullable=True)
    audio_url = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    queue_snapshots = relationship("QueueSnapshot", back_populates="song", cascade="all, delete-orphan")
    play_history = relationship("PlayHistory", back_populates="song", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'popularity': self.popularity,
            'genre': self.genre,
            'release_year': self.release_year,
            'audio_url': self.audio_url,
            'cover_url': self.cover_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Song(id={self.id}, title='{self.title}', artist='{self.artist}')>"


class User(Base):
    """User model - represents a system user"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    play_history = relationship("PlayHistory", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'premium': self.premium,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', premium={self.premium})>"


class QueueSnapshot(Base):
    """Queue Snapshot - represents the current state of the queue"""
    __tablename__ = 'queue_snapshot'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), nullable=False)
    position = Column(Integer, nullable=False)
    priority = Column(Float, default=0.0)
    is_current = Column(Boolean, default=False)  # Is this the currently playing song?
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    song = relationship("Song", back_populates="queue_snapshots")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'song_id': self.song_id,
            'position': self.position,
            'priority': self.priority,
            'is_current': self.is_current,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'song': self.song.to_dict() if self.song else None
        }
    
    def __repr__(self):
        return f"<QueueSnapshot(song_id={self.song_id}, position={self.position})>"


class PlayHistory(Base):
    """Play History - tracks what songs users have played"""
    __tablename__ = 'play_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
    duration_played = Column(Integer, nullable=True)  # How long the song was played (seconds)
    completed = Column(Boolean, default=False)  # Did the user listen to the whole song?
    
    # Relationships
    song = relationship("Song", back_populates="play_history")
    user = relationship("User", back_populates="play_history")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'song_id': self.song_id,
            'user_id': self.user_id,
            'played_at': self.played_at.isoformat() if self.played_at else None,
            'duration_played': self.duration_played,
            'completed': self.completed,
            'song': self.song.to_dict() if self.song else None,
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f"<PlayHistory(song_id={self.song_id}, user_id={self.user_id})>"

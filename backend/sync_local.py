import os
import database as db

# Hardcoded metadata for the local files found in media/songs
LOCAL_SONGS = [
    {
        "title": "Changes",
        "artist": "Black Sabbath",
        "filename": "Black Sabbath - Changes.mp3",
        "cover": "cover_changes.png",
        "album": "Vol. 4",
        "duration": 284
    },
    {
        "title": "End Of Beginning",
        "artist": "Djo",
        "filename": "Djo - End Of Beginning.mp3",
        "cover": "cover_end_of_beginning.png",
        "album": "Decide",
        "duration": 159
    },
    {
        "title": "Illahi",
        "artist": "Arijit Singh",
        "filename": "Illahi - Arijit Singh.mp3",
        "cover": "cover_illahi.png",
        "album": "Yeh Jawaani Hai Deewani",
        "duration": 229
    },
    {
        "title": "If It Only Gets Better",
        "artist": "Joji",
        "filename": "Joji - If It Only Gets Better.mp3",
        "cover": "cover_if_it_only_gets_better.png",
        "album": "SMITHEREENS",
        "duration": 146
    },
    {
        "title": "Blinding Lights",
        "artist": "The Weeknd",
        "filename": "The Weeknd - Blinding Lights.mp3",
        "cover": "cover_blinding_lights.png",
        "album": "After Hours",
        "duration": 200
    },
]

def sync_local_songs():
    print("🚀 Starting local song sync...")
    db.init_database()
    
    # We'll use filenames as unique identifiers in audio_url
    for song_data in LOCAL_SONGS:
        song = db.get_song_by_title(song_data["title"])
        
        if not song:
            print(f"➕ Adding {song_data['title']}...")
            song = db.create_song(
                title=song_data["title"],
                artist=song_data["artist"],
                duration=song_data["duration"],
                album=song_data["album"],
                audio_url=song_data["filename"], # Store just the filename
                cover_url=f"/media/covers/{song_data['cover']}",
                popularity=95.0,
                genre="Modern"
            )
        else:
            print(f"🔄 Updating {song_data['title']}...")
            session = db.get_session()
            song_in_db = session.query(db.Song).filter(db.Song.id == song.id).first()
            song_in_db.audio_url = song_data["filename"]
            song_in_db.cover_url = f"/media/covers/{song_data['cover']}"
            song_in_db.duration = song_data["duration"]
            song_in_db.album = song_data["album"]
            session.commit()
            session.close()

    print("✅ Sync complete!")

if __name__ == "__main__":
    sync_local_songs()

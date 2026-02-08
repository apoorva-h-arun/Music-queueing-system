import os
import database as db
from gdrive_utils import get_direct_link

# List of songs found in the provided GDrive folder
SONGS_TO_SYNC = [
    {"title": "Changes", "artist": "Black Sabbath", "gdrive_id": "1qjHzPS4aNRaVLAaf2Bj_pc2btPnOere3", "cover": "cover_changes.png"},
    {"title": "End Of Beginning", "artist": "Djo", "gdrive_id": "1haLSChHDxiMB-f-Ja4RBmzCeSJ7mkh9U", "cover": "cover_end_of_beginning.png"},
    {"title": "Illahi", "artist": "Arijit Singh", "gdrive_id": "1CjsLPLTrhQmamgBmP7AW8afY89NrjRm8", "cover": "cover_illahi.png"},
    {"title": "If It Only Gets Better", "artist": "Joji", "gdrive_id": "1UDb-UyrJlq8gBzDaUveUV23Vb7WXwowB", "cover": "cover_if_it_only_gets_better.png"},
    {"title": "Blinding Lights", "artist": "The Weeknd", "gdrive_id": "1QHn_Tdawam5XBgUdAKrh3G06S-8EveOJ", "cover": "cover_blinding_lights.png"},
]

def sync_songs():
    print("Starting sync...")
    db.init_database()
    
    # Simple check: clear existing songs (or we could update them)
    # For this demo, let's just add them if they don't exist by title
    existing_songs = db.get_all_songs()
    existing_titles = [s.title for s in existing_songs]
    
    for song_data in SONGS_TO_SYNC:
        song = db.get_song_by_title(song_data["title"])
        if not song:
            print(f"Adding {song_data['title']}...")
            song = db.create_song(
                title=song_data["title"],
                artist=song_data["artist"],
                duration=200,
                audio_url=song_data["gdrive_id"], 
                cover_url=f"http://localhost:5000/media/covers/{song_data['cover']}",
                popularity=90.0,
                genre="Modern"
            )
        
        if song:
            session = db.get_session()
            song_in_db = session.query(db.Song).filter(db.Song.id == song.id).first()
            song_in_db.audio_url = song_data["gdrive_id"]  # Store RAW ID
            song_in_db.cover_url = f"http://localhost:5000/media/covers/{song_data['cover']}"
            session.commit()
            session.close()

if __name__ == "__main__":
    sync_songs()

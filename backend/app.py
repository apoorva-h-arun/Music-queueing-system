"""
Music Queue Manager - Flask REST API

Production-grade backend with all queue management endpoints
Integrates C library via ctypes wrapper and PostgreSQL for persistence
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from c_wrapper import MusicQueueWrapper
import database as db
from models import Song, User
from typing import Dict, List
import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='media', static_url_path='/media')
CORS(app)  # Enable CORS for frontend

# Initialize database
db.init_database()

# Optional: Sync local songs on startup
try:
    from sync_local import sync_local_songs
    sync_local_songs()
except Exception as e:
    print(f"⚠ Could not auto-sync local songs: {e}")

# Initialize Queue Manager (with Python fallback)
queue_manager = None
try:
    print("Initializing Music Queue Manager...")
    # This will use the Python fallback internally if C lib is missing
    queue_manager = MusicQueueWrapper()
    print("✓ Music Queue Manager initialized")
    
    # Load ALL songs into the heap for recommendations
    try:
        all_songs = db.get_all_songs()
        for song in all_songs:
            play_count = db.get_play_count(song.id)
            queue_manager.update_priority(song.id, int(song.popularity or 0), play_count)
        print(f"✓ Loaded {len(all_songs)} songs into recommendation heap")
        
        # Load queue state from database for CDLL
        snapshot = db.load_queue_snapshot()
        if snapshot:
            for item in snapshot:
                song = db.get_song_by_id(item['song_id'])
                if song:
                    queue_manager.add_song(item['song_id'], song.title, song.artist, int(song.popularity or 0), db.get_play_count(song.id))
            print(f"✓ Loaded {len(snapshot)} songs into active queue")
    except Exception as db_e:
        print(f"⚠ Warning during queue manager initialization: {db_e}")
except Exception as e:
    print(f"❌ Error initializing queue manager: {e}")
    # Force a fallback if initialization failed
    if queue_manager is None:
        try:
            queue_manager = MusicQueueWrapper()
        except:
            print("❌ Absolute failure to create queue manager")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sync_queue_to_db():
    """Sync the current queue state to database"""
    if not queue_manager:
        return False
    
    try:
        queue_songs = queue_manager.get_queue()
        current_song_id = queue_manager.get_current_song()
        
        queue_data = []
        for position, song_id in enumerate(queue_songs):
            queue_data.append({
                'song_id': song_id,
                'position': position,
                'priority': 0.0,  # TODO: Get from heap
                'is_current': (song_id == current_song_id)
            })
        
        return db.save_queue_snapshot(queue_data)
    except Exception as e:
        print(f"Error syncing queue: {e}")
        return False

def calculate_priority(song: Song, user_votes: int = 0, is_premium: bool = False) -> float:
    """Calculate song priority based on formula"""
    popularity_score = song.popularity * 0.5
    votes_score = user_votes * 0.3
    premium_score = 20.0 if is_premium else 0.0
    premium_weight = premium_score * 0.2
    
    return popularity_score + votes_score + premium_weight

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'queue_manager': queue_manager is not None,
        'database': True
    })

# ============================================================================
# HELPER FUNCTIONS (API SPECIFIC)
# ============================================================================

def format_song(song):
    """Ensure song metadata has absolute proxy URLs and includes priority"""
    port = os.getenv('PORT', 8000)
    d = song.to_dict()
    
    # Calculate priority: (likes * 2 + play_count)
    # This matches the C core logic
    play_count = db.get_play_count(song.id)
    d['play_count'] = play_count
    d['priority'] = int(song.popularity or 0) * 2 + play_count
    
    # Transform audio_url to proxy path
    d['audio_url'] = f"http://localhost:{port}/api/proxy-audio/{song.id}"
    # Ensure cover is absolute
    if d['cover_url'] and not d['cover_url'].startswith('http'):
        d['cover_url'] = f"http://localhost:{port}{d['cover_url']}"
    return d

# ============================================================================
# SONG ENDPOINTS
# ============================================================================

@app.route('/api/songs', methods=['GET'])
def get_songs():
    """Get all songs, sorted by popularity using the C Max Heap if possible"""
    try:
        # Get songs from database sorted by popularity
        all_db_songs = db.get_all_songs()
        
        # Deduplicate by ID first (in case database has duplicates)
        seen_ids = set()
        unique_songs = []
        for song in all_db_songs:
            if song.id not in seen_ids:
                seen_ids.add(song.id)
                unique_songs.append(song)
        
        # Try to use C heap for recommendations if available
        if queue_manager:
            try:
                # Get heap-recommended songs (if available) - FIXED: now using recommendations
                heap_song_ids = queue_manager.get_recommendations(limit=100)
                
                if heap_song_ids:
                    # Deduplicate heap IDs
                    unique_heap_ids = []
                    seen_heap_ids = set()
                    for sid in heap_song_ids:
                        if sid not in seen_heap_ids:
                            unique_heap_ids.append(sid)
                            seen_heap_ids.add(sid)
                    
                    # Sort by heap order
                    song_dict = {song.id: song for song in unique_songs}
                    songs = []
                    seen_in_results = set()
                    
                    for sid in unique_heap_ids:
                        if sid in song_dict and sid not in seen_in_results:
                            songs.append(format_song(song_dict[sid]))
                            seen_in_results.add(sid)
                    
                    # Add remaining songs
                    for song in unique_songs:
                        if song.id not in seen_in_results:
                            songs.append(format_song(song))
                else:
                    # Sort by popularity from database
                    songs = [format_song(song) for song in sorted(unique_songs, key=lambda s: s.popularity or 0, reverse=True)]
            except Exception as e:
                print(f"Error using queue_manager, falling back: {e}")
                # Fallback to database order
                songs = [format_song(song) for song in sorted(unique_songs, key=lambda s: s.popularity or 0, reverse=True)]
        else:
            # Sort by popularity from database
            songs = [format_song(song) for song in sorted(unique_songs, key=lambda s: s.popularity or 0, reverse=True)]
        
        # Final deduplication by ID to be absolutely sure
        seen_final = set()
        final_songs = []
        for song in songs:
            if song['id'] not in seen_final:
                seen_final.add(song['id'])
                final_songs.append(song)
            
        return jsonify({
            'success': True,
            'songs': final_songs
        })
    except Exception as e:
        print(f"Error in get_songs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_songs():
    """Real-time search using C Trie or database fallback"""
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({'success': True, 'results': []})
    
    try:
        # Try C Trie search first if available
        if queue_manager:
            try:
                song_ids = queue_manager.search_songs(query)
                artist_song_ids = queue_manager.search_artists(query)
                all_ids = list(set(song_ids + artist_song_ids))
                
                # Fetch song details
                results = []
                for sid in all_ids:
                    song = db.get_song_by_id(sid)
                    if song:
                        results.append(format_song(song))
                
                if results:
                    return jsonify({
                        'success': True,
                        'results': results
                    })
            except Exception as e:
                print(f"Trie search failed, using database fallback: {e}")
        
        # Fallback to database search
        all_songs = db.get_all_songs()
        results = []
        for song in all_songs:
            if (query in song.title.lower() or 
                query in song.artist.lower() or 
                (song.album and query in song.album.lower())):
                results.append(format_song(song))
                
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        print(f"Error in search_songs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """Get a specific song"""
    try:
        song = db.get_song_by_id(song_id)
        if song:
            return jsonify({'success': True, 'song': format_song(song)})
        return jsonify({'success': False, 'error': 'Song not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/proxy-audio/<int:song_id>', methods=['GET'])
def proxy_audio(song_id):
    """Serve local audio file"""
    try:
        song = db.get_song_by_id(song_id)
        if not song:
            return "Song not found", 404
            
        # The filename is stored in audio_url
        filename = song.audio_url
        song_path = os.path.join(app.root_path, 'media', 'songs', filename)
        
        if not os.path.exists(song_path):
            print(f"❌ File not found: {song_path}")
            return "Audio file not found on server", 404

        from flask import send_file
        return send_file(
            song_path,
            mimetype="audio/mpeg",
            as_attachment=False,
            conditional=True # Support for range requests (scrubbing)
        )
    except Exception as e:
        print(f"Server error serving audio: {e}")
        return str(e), 500

@app.route('/api/songs', methods=['POST'])
def create_song():
    """Create a new song"""
    try:
        data = request.json
        song = db.create_song(
            title=data['title'],
            artist=data['artist'],
            duration=data['duration'],
            album=data.get('album'),
            popularity=data.get('popularity', 0.0),
            genre=data.get('genre'),
            release_year=data.get('release_year')
        )
        return jsonify({'success': True, 'song': song.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# QUEUE MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/queue', methods=['GET'])
def get_queue():
    """Get current queue state"""
    try:
        # Fallback to database snapshot if queue_manager not available
        if not queue_manager:
            snapshot = db.load_queue_snapshot()
            if snapshot:
                queue_with_details = []
                for item in snapshot:
                    song = db.get_song_by_id(item['song_id'])
                    if song:
                        song_dict = format_song(song)
                        song_dict['position'] = item['position']
                        song_dict['is_current'] = item.get('is_current', False)
                        queue_with_details.append(song_dict)
                
                current_song = next((s for s in queue_with_details if s['is_current']), None)
                return jsonify({
                    'success': True,
                    'queue': queue_with_details,
                    'current_song_id': current_song['id'] if current_song else -1,
                    'size': len(queue_with_details)
                })
            else:
                return jsonify({
                    'success': True,
                    'queue': [],
                    'current_song_id': -1,
                    'size': 0
                })
        
        queue_song_ids = queue_manager.get_queue()
        current_song_id = queue_manager.get_current_song()
        
        # Fetch song details from database
        queue_with_details = []
        for position, song_id in enumerate(queue_song_ids):
            song = db.get_song_by_id(song_id)
            if song:
                song_dict = format_song(song)
                song_dict['position'] = position
                song_dict['is_current'] = (song_id == current_song_id)
                queue_with_details.append(song_dict)
        
        return jsonify({
            'success': True,
            'queue': queue_with_details,
            'current_song_id': current_song_id,
            'size': queue_manager.get_queue_size()
        })
    except Exception as e:
        print(f"Error in get_queue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """Add a song to the queue"""
    try:
        data = request.json
        if not data or 'song_id' not in data:
            return jsonify({'success': False, 'error': 'song_id is required'}), 400
            
        song_id = data['song_id']
        
        # Get song from database
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({'success': False, 'error': 'Song not found'}), 404
        
        if not queue_manager:
            # Fallback: save to database queue snapshot
            snapshot = db.load_queue_snapshot() or []
            max_position = max([item['position'] for item in snapshot], default=-1) if snapshot else -1
            new_item = {
                'song_id': song_id,
                'position': max_position + 1,
                'priority': song.popularity or 0,
                'is_current': len(snapshot) == 0  # First song is current
            }
            # Update existing current song if adding first item
            if snapshot and new_item['is_current']:
                for item in snapshot:
                    item['is_current'] = False
            snapshot.append(new_item)
            db.save_queue_snapshot(snapshot)
            return jsonify({'success': True, 'message': 'Song added to queue'})
        
        # Get actual play count for the song
        play_count = db.get_play_count(song_id)
        
        # Add to queue (duplicates allowed)
        success = queue_manager.add_song(
            song_id, 
            song.title, 
            song.artist, 
            int(song.popularity or 0), # Use popularity as base for likes
            play_count # Use actual play_count
        )
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song added to queue'})
        else:
            return jsonify({'success': False, 'error': 'Failed to add song'}), 400
    except Exception as e:
        print(f"Error in add_to_queue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/remove', methods=['POST'])
def remove_from_queue():
    """Remove a song from the queue"""
    try:
        data = request.json
        if not data or 'song_id' not in data:
            return jsonify({'success': False, 'error': 'song_id is required'}), 400
            
        song_id = data['song_id']
        
        if not queue_manager:
            # Fallback: remove from database queue snapshot
            snapshot = db.load_queue_snapshot()
            updated = [item for item in snapshot if item['song_id'] != song_id]
            # Re-index positions
            for i, item in enumerate(updated):
                item['position'] = i
            db.save_queue_snapshot(updated)
            return jsonify({'success': True, 'message': 'Song removed from queue'})
        
        success = queue_manager.remove_song(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song removed from queue'})
        else:
            return jsonify({'success': False, 'error': 'Song not in queue'}), 404
    except Exception as e:
        print(f"Error in remove_from_queue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/skip/next', methods=['POST'])
def skip_next():
    """Skip to next song"""
    try:
        if not queue_manager:
            # Fallback: update database queue snapshot
            snapshot = db.load_queue_snapshot()
            if not snapshot:
                return jsonify({'success': False, 'error': 'Queue is empty'}), 400
            
            current_idx = next((i for i, item in enumerate(snapshot) if item.get('is_current')), 0)
            next_idx = (current_idx + 1) % len(snapshot)
            
            snapshot[current_idx]['is_current'] = False
            snapshot[next_idx]['is_current'] = True
            db.save_queue_snapshot(snapshot)
            
            return jsonify({
                'success': True,
                'current_song_id': snapshot[next_idx]['song_id'],
                'message': 'Skipped to next song'
            })
        
        success = queue_manager.skip_next()
        
        if success:
            current_song_id = queue_manager.get_current_song()
            sync_queue_to_db()
            return jsonify({
                'success': True,
                'current_song_id': current_song_id,
                'message': 'Skipped to next song'
            })
        else:
            return jsonify({'success': False, 'error': 'No next song'}), 400
    except Exception as e:
        print(f"Error in skip_next: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/skip/prev', methods=['POST'])
def skip_prev():
    """Skip to previous song"""
    try:
        if not queue_manager:
            # Fallback: update database queue snapshot
            snapshot = db.load_queue_snapshot()
            if not snapshot:
                return jsonify({'success': False, 'error': 'Queue is empty'}), 400
            
            current_idx = next((i for i, item in enumerate(snapshot) if item.get('is_current')), 0)
            prev_idx = (current_idx - 1) % len(snapshot)
            
            snapshot[current_idx]['is_current'] = False
            snapshot[prev_idx]['is_current'] = True
            db.save_queue_snapshot(snapshot)
            
            return jsonify({
                'success': True,
                'current_song_id': snapshot[prev_idx]['song_id'],
                'message': 'Skipped to previous song'
            })
        
        success = queue_manager.skip_prev()
        
        if success:
            current_song_id = queue_manager.get_current_song()
            sync_queue_to_db()
            return jsonify({
                'success': True,
                'current_song_id': current_song_id,
                'message': 'Skipped to previous song'
            })
        else:
            return jsonify({'success': False, 'error': 'No previous song'}), 400
    except Exception as e:
        print(f"Error in skip_prev: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/move-up', methods=['POST'])
def move_up():
    """Move a song up in the queue"""
    try:
        data = request.json
        if not data or 'song_id' not in data:
            return jsonify({'success': False, 'error': 'song_id is required'}), 400
            
        song_id = data['song_id']
        
        if not queue_manager:
            # Fallback: update database queue snapshot
            snapshot = db.load_queue_snapshot()
            idx = next((i for i, item in enumerate(snapshot) if item['song_id'] == song_id), None)
            if idx is None or idx == 0:
                return jsonify({'success': False, 'error': 'Cannot move song up'}), 400
            
            snapshot[idx], snapshot[idx - 1] = snapshot[idx - 1], snapshot[idx]
            snapshot[idx]['position'] = idx
            snapshot[idx - 1]['position'] = idx - 1
            db.save_queue_snapshot(snapshot)
            return jsonify({'success': True, 'message': 'Song moved up'})
        
        success = queue_manager.move_up(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song moved up'})
        else:
            return jsonify({'success': False, 'error': 'Cannot move song up'}), 400
    except Exception as e:
        print(f"Error in move_up: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/move-down', methods=['POST'])
def move_down():
    """Move a song down in the queue"""
    try:
        data = request.json
        if not data or 'song_id' not in data:
            return jsonify({'success': False, 'error': 'song_id is required'}), 400
            
        song_id = data['song_id']
        
        if not queue_manager:
            # Fallback: update database queue snapshot
            snapshot = db.load_queue_snapshot()
            idx = next((i for i, item in enumerate(snapshot) if item['song_id'] == song_id), None)
            if idx is None or idx == len(snapshot) - 1:
                return jsonify({'success': False, 'error': 'Cannot move song down'}), 400
            
            snapshot[idx], snapshot[idx + 1] = snapshot[idx + 1], snapshot[idx]
            snapshot[idx]['position'] = idx
            snapshot[idx + 1]['position'] = idx + 1
            db.save_queue_snapshot(snapshot)
            return jsonify({'success': True, 'message': 'Song moved down'})
        
        success = queue_manager.move_down(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song moved down'})
        else:
            return jsonify({'success': False, 'error': 'Cannot move song down'}), 400
    except Exception as e:
        print(f"Error in move_down: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/update-priority', methods=['POST'])
def update_priority():
    """Update song priority"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        data = request.json
        song_id = data['song_id']
        priority = data['priority']
        
        success = queue_manager.update_priority(song_id, priority)
        
        if success:
            return jsonify({'success': True, 'message': 'Priority updated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update priority'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# UNDO/REDO ENDPOINTS
# ============================================================================

@app.route('/api/undo', methods=['POST'])
def undo():
    """Undo last operation"""
    try:
        if not queue_manager:
            return jsonify({'success': False, 'error': 'Undo not available without queue manager'}), 400
        
        success = queue_manager.undo()
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Operation undone'})
        else:
            return jsonify({'success': False, 'error': 'Nothing to undo'}), 400
    except Exception as e:
        print(f"Error in undo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/redo', methods=['POST'])
def redo():
    """Redo last undone operation"""
    try:
        if not queue_manager:
            return jsonify({'success': False, 'error': 'Redo not available without queue manager'}), 400
        
        success = queue_manager.redo()
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Operation redone'})
        else:
            return jsonify({'success': False, 'error': 'Nothing to redo'}), 400
    except Exception as e:
        print(f"Error in redo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================================

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get priority-based recommendations"""
    try:
        # Get popular songs from database
        popular_songs = db.get_popular_songs(limit=10)
        
        # If no play history, use songs sorted by popularity
        if not popular_songs:
            all_songs = db.get_all_songs()
            popular_songs = sorted(all_songs, key=lambda s: s.popularity or 0, reverse=True)[:10]
        
        return jsonify({
            'success': True,
            'recommendations': [format_song(song) for song in popular_songs]
        })
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        # Fallback: return all songs sorted by popularity
        try:
            all_songs = db.get_all_songs()
            popular_songs = sorted(all_songs, key=lambda s: s.popularity or 0, reverse=True)[:10]
            return jsonify({
                'success': True,
                'recommendations': [format_song(song) for song in popular_songs]
            })
        except:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/songs/like', methods=['POST'])
def like_song():
    """Implement like system using C priority heap"""
    try:
        data = request.json
        song_id = data['song_id']
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({'success': False, 'error': 'Song not found'}), 404
        
        # Increment likes in DB (using popularity field for parity with existing schema)
        song.popularity = (song.popularity or 0) + 1
        db.update_song_likes(song_id, song.popularity) 
        
        # Get actual play count for the song
        play_count = db.get_play_count(song_id)
        
        # Update C heap priority if available
        if queue_manager:
            try:
                # Use actual play_count, not hardcoded 0
                queue_manager.update_priority(song_id, int(song.popularity), play_count)
                print(f"Updated priority for song {song_id}: likes={song.popularity}, play_count={play_count}, priority={2*song.popularity + play_count}")
            except Exception as e:
                print(f"Warning: Could not update priority in C heap: {e}")
        
        return jsonify({
            'success': True, 
            'new_popularity': song.popularity,
            'play_count': play_count,
            'priority': 2 * song.popularity + play_count
        })
    except Exception as e:
        print(f"Error in like_song: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/songs/play', methods=['POST'])
def play_song():
    """Triggered when song plays: update play count and heap"""
    try:
        data = request.json
        song_id = data['song_id']
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({'success': False, 'error': 'Song not found'}), 404
        
        # Get or create default user (user_id=1) for play tracking
        default_user_id = 1
        user = db.get_user_by_id(default_user_id)
        if not user:
            user = db.create_user("Default User", "default@music.com", False)
            default_user_id = user.id
        
        # Record play in history
        try:
            db.add_play_history(song_id, default_user_id, duration_played=None, completed=True)
        except Exception as e:
            print(f"Warning: Could not add play history: {e}")
        
        # Get actual play count from history
        play_count = db.get_play_count(song_id)
        
        # Update C heap priority if available
        if queue_manager:
            try:
                likes = int(song.popularity or 0)
                # Use actual play_count, not hardcoded 1
                queue_manager.update_priority(song_id, likes, play_count)
                print(f"Updated priority for song {song_id}: likes={likes}, play_count={play_count}, priority={2*likes + play_count}")
            except Exception as e:
                print(f"Warning: Could not update priority in C heap: {e}")
        
        priority = 2 * (song.popularity or 0) + play_count
        return jsonify({
            'success': True, 
            'message': 'Play count updated',
            'play_count': play_count,
            'priority': priority
        })
    except Exception as e:
        print(f"Error in play_song: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"Music Queue Manager API")
    print(f"{'='*50}")
    print(f"Server running on: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

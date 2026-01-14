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
    
    # Load queue state from database
    try:
        snapshot = db.load_queue_snapshot()
        if snapshot:
            for item in snapshot:
                song = db.get_song_by_id(item['song_id'])
                if song:
                    priority = song.popularity * 0.5
                    queue_manager.add_song(item['song_id'], priority)
            print(f"✓ Loaded {len(snapshot)} songs from database")
    except Exception as db_e:
        print(f"⚠ Warning: Could not load queue snapshot: {db_e}")
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
    """Ensure song metadata has absolute proxy URLs"""
    d = song.to_dict()
    # Transform audio_url to proxy path
    d['audio_url'] = f"http://localhost:5000/api/proxy-audio/{song.id}"
    # Ensure cover is absolute
    if d['cover_url'] and not d['cover_url'].startswith('http'):
        d['cover_url'] = f"http://localhost:5000{d['cover_url']}"
    return d

# ============================================================================
# SONG ENDPOINTS
# ============================================================================

@app.route('/api/songs', methods=['GET'])
def get_songs():
    """Get all songs"""
    try:
        songs = db.get_all_songs()
        song_dicts = [format_song(song) for song in songs]
            
        return jsonify({
            'success': True,
            'songs': song_dicts
        })
    except Exception as e:
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
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """Add a song to the queue"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        data = request.json
        song_id = data['song_id']
        
        # Get song from database
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({'success': False, 'error': 'Song not found'}), 404
        
        # Calculate priority
        priority = calculate_priority(song, data.get('user_votes', 0), data.get('is_premium', False))
        
        # Add to queue
        success = queue_manager.add_song(song_id, priority)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song added to queue'})
        else:
            return jsonify({'success': False, 'error': 'Failed to add song'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/remove', methods=['POST'])
def remove_from_queue():
    """Remove a song from the queue"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        data = request.json
        song_id = data['song_id']
        
        success = queue_manager.remove_song(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song removed from queue'})
        else:
            return jsonify({'success': False, 'error': 'Song not in queue'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/skip/next', methods=['POST'])
def skip_next():
    """Skip to next song"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/skip/prev', methods=['POST'])
def skip_prev():
    """Skip to previous song"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queue/move-up', methods=['POST'])
def move_up():
    """Move a song up in the queue"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        data = request.json
        song_id = data['song_id']
        
        success = queue_manager.move_up(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song moved up'})
        else:
            return jsonify({'success': False, 'error': 'Cannot move song up'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/queue/move-down', methods=['POST'])
def move_down():
    """Move a song down in the queue"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        data = request.json
        song_id = data['song_id']
        
        success = queue_manager.move_down(song_id)
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Song moved down'})
        else:
            return jsonify({'success': False, 'error': 'Cannot move song down'}), 400
    except Exception as e:
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
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        success = queue_manager.undo()
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Operation undone'})
        else:
            return jsonify({'success': False, 'error': 'Nothing to undo'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/redo', methods=['POST'])
def redo():
    """Redo last undone operation"""
    if not queue_manager:
        return jsonify({'success': False, 'error': 'Queue manager not initialized'}), 503
    
    try:
        success = queue_manager.redo()
        
        if success:
            sync_queue_to_db()
            return jsonify({'success': True, 'message': 'Operation redone'})
        else:
            return jsonify({'success': False, 'error': 'Nothing to redo'}), 400
    except Exception as e:
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
        
        return jsonify({
            'success': True,
            'recommendations': [format_song(song) for song in popular_songs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"Music Queue Manager API")
    print(f"{'='*50}")
    print(f"Server running on: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

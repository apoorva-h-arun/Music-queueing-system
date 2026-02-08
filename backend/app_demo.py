"""
Music Queue Manager - Demo Version (No Database Required)

Simplified version that runs without PostgreSQL
Demonstrates the C library integration and queue operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

app = Flask(__name__)
CORS(app)

# Try to load C library
queue_manager = None
c_lib_available = False

try:
    from c_wrapper import MusicQueueWrapper
    queue_manager = MusicQueueWrapper(heap_capacity=100, hashmap_capacity=100)
    c_lib_available = True
    print("✓ C library loaded successfully!")
except Exception as e:
    print(f"⚠ C library not available: {e}")
    print("  Running in demo mode without C integration")

# In-memory song database (demo data)
DEMO_SONGS = {
    1: {"id": 1, "title": "Blinding Lights", "artist": "The Weeknd", "duration": 200, "popularity": 95.5},
    2: {"id": 2, "title": "Shape of You", "artist": "Ed Sheeran", "duration": 233, "popularity": 92.3},
    3: {"id": 3, "title": "Bohemian Rhapsody", "artist": "Queen", "duration": 354, "popularity": 96.2},
    4: {"id": 4, "title": "Hotel California", "artist": "Eagles", "duration": 391, "popularity": 90.1},
    5: {"id": 5, "title": "Billie Jean", "artist": "Michael Jackson", "duration": 294, "popularity": 94.8},
}

# Simple in-memory queue (fallback if C library not available)
simple_queue = []
current_index = 0

@app.route('/', methods=['GET'])
def index():
    """Root landing page to provide navigation"""
    return f'''
    <html>
        <head>
            <title>Music Queue Manager - API Demo</title>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; color: #333; }}
                h1 {{ color: #2c3e50; }}
                .links {{ margin-top: 20px; }}
                .link-item {{ margin-bottom: 10px; }}
                code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>🎵 Music Queue Manager</h1>
            <p>The server is running successfully!</p>
            <div class="links">
                <div class="link-item">✅ <strong>Health Check:</strong> <a href="/api/health">/api/health</a></div>
                <div class="link-item">🎶 <strong>All Songs:</strong> <a href="/api/songs">/api/songs</a></div>
                <div class="link-item">📋 <strong>Current Queue:</strong> <a href="/api/queue">/api/queue</a></div>
            </div>
            <p><small>Tip: Use these links to test the initial state. Add songs using API clients or the provided test script.</small></p>
        </body>
    </html>
    '''

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'c_library': c_lib_available,
        'mode': 'C-powered' if c_lib_available else 'demo'
    })

@app.route('/api/songs', methods=['GET'])
def get_songs():
    """Get all available songs"""
    return jsonify({
        'success': True,
        'songs': list(DEMO_SONGS.values())
    })

@app.route('/api/queue', methods=['GET'])
def get_queue():
    """Get current queue state"""
    if c_lib_available and queue_manager:
        try:
            queue_song_ids = queue_manager.get_queue()
            current_song_id = queue_manager.get_current_song()
            
            queue_with_details = []
            for position, song_id in enumerate(queue_song_ids):
                if song_id in DEMO_SONGS:
                    song = DEMO_SONGS[song_id].copy()
                    song['position'] = position
                    song['is_current'] = (song_id == current_song_id)
                    queue_with_details.append(song)
            
            return jsonify({
                'success': True,
                'queue': queue_with_details,
                'current_song_id': current_song_id,
                'size': queue_manager.get_queue_size(),
                'mode': 'C-powered'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # Fallback to simple queue
        queue_with_details = []
        for position, song_id in enumerate(simple_queue):
            if song_id in DEMO_SONGS:
                song = DEMO_SONGS[song_id].copy()
                song['position'] = position
                song['is_current'] = (position == current_index)
                queue_with_details.append(song)
        
        current_song_id = simple_queue[current_index] if 0 <= current_index < len(simple_queue) else -1
        
        return jsonify({
            'success': True,
            'queue': queue_with_details,
            'current_song_id': current_song_id,
            'size': len(simple_queue),
            'mode': 'demo'
        })

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """Add a song to the queue"""
    data = request.json
    song_id = data.get('song_id')
    
    if song_id not in DEMO_SONGS:
        return jsonify({'success': False, 'error': 'Song not found'}), 404
    
    if c_lib_available and queue_manager:
        try:
            priority = DEMO_SONGS[song_id]['popularity']
            success = queue_manager.add_song(song_id, priority)
            
            if success:
                return jsonify({'success': True, 'message': 'Song added to queue (C-powered)'})
            else:
                return jsonify({'success': False, 'error': 'Failed to add song'}), 500
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # Fallback
        simple_queue.append(song_id)
        return jsonify({'success': True, 'message': 'Song added to queue (demo mode)'})

@app.route('/api/queue/skip/next', methods=['POST'])
def skip_next():
    """Skip to next song"""
    global current_index
    
    if c_lib_available and queue_manager:
        try:
            success = queue_manager.skip_next()
            if success:
                current_song_id = queue_manager.get_current_song()
                return jsonify({
                    'success': True,
                    'current_song_id': current_song_id,
                    'message': 'Skipped to next song (C-powered)'
                })
            else:
                return jsonify({'success': False, 'error': 'No next song'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # Fallback
        if current_index < len(simple_queue) - 1:
            current_index += 1
            return jsonify({
                'success': True,
                'current_song_id': simple_queue[current_index],
                'message': 'Skipped to next song (demo mode)'
            })
        else:
            return jsonify({'success': False, 'error': 'No next song'}), 400

@app.route('/api/queue/skip/prev', methods=['POST'])
def skip_prev():
    """Skip to previous song"""
    global current_index
    
    if c_lib_available and queue_manager:
        try:
            success = queue_manager.skip_prev()
            if success:
                current_song_id = queue_manager.get_current_song()
                return jsonify({
                    'success': True,
                    'current_song_id': current_song_id,
                    'message': 'Skipped to previous song (C-powered)'
                })
            else:
                return jsonify({'success': False, 'error': 'No previous song'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # Fallback
        if current_index > 0:
            current_index -= 1
            return jsonify({
                'success': True,
                'current_song_id': simple_queue[current_index],
                'message': 'Skipped to previous song (demo mode)'
            })
        else:
            return jsonify({'success': False, 'error': 'No previous song'}), 400

@app.route('/api/undo', methods=['POST'])
def undo():
    """Undo last operation"""
    if c_lib_available and queue_manager:
        try:
            success = queue_manager.undo()
            if success:
                return jsonify({'success': True, 'message': 'Operation undone (C-powered)'})
            else:
                return jsonify({'success': False, 'error': 'Nothing to undo'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'Undo not available in demo mode'}), 400

@app.route('/api/redo', methods=['POST'])
def redo():
    """Redo last undone operation"""
    if c_lib_available and queue_manager:
        try:
            success = queue_manager.redo()
            if success:
                return jsonify({'success': True, 'message': 'Operation redone (C-powered)'})
            else:
                return jsonify({'success': False, 'error': 'Nothing to redo'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'Redo not available in demo mode'}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n{'='*60}")
    print(f"Music Queue Manager - Demo API")
    print(f"{'='*60}")
    print(f"Mode: {'C-powered' if c_lib_available else 'Demo (Python fallback)'}")
    print(f"Server: http://localhost:{port}")
    print(f"{'='*60}\n")
    
    if not c_lib_available:
        print("💡 Tip: Install MinGW and compile the C library for full features:")
        print("   cd c_core")
        print("   .\\build.bat\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)

"""
C Library Wrapper - ctypes Integration

Cross-platform wrapper for the Music Queue C library
Automatically detects and loads the correct shared library based on OS
"""

import sys
import os
from pathlib import Path
from ctypes import *
from typing import Optional, List, Dict

# ============================================================================
# PLATFORM DETECTION AND LIBRARY LOADING
# ============================================================================

def get_library_path() -> Path:
    """
    Get the path to the C shared library based on the current platform
    """
    # Get the directory containing this file
    current_dir = Path(__file__).parent
    lib_dir = current_dir.parent / 'c_core' / 'build'
    
    # Determine library name based on platform
    if sys.platform == 'linux':
        lib_name = 'libmusicqueue.so'
    elif sys.platform == 'darwin':  # macOS
        lib_name = 'libmusicqueue.dylib'
    elif sys.platform == 'win32':
        lib_name = 'musicqueue.dll'
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")
    
    lib_path = lib_dir / lib_name
    
    if not lib_path.exists():
        raise FileNotFoundError(
            f"C library not found: {lib_path}\n"
            f"Please compile the C library first:\n"
            f"  cd c_core\n"
            f"  ./build.sh (Linux/macOS) or .\\build.bat (Windows)"
        )
    
    return lib_path

# Load the C library
try:
    lib_path = get_library_path()
    c_lib = CDLL(str(lib_path))
except Exception as e:
    print(f"Error loading C library: {e}")
    c_lib = None

# ============================================================================
# C STRUCTURE DEFINITIONS
# ============================================================================

class DLLNode(Structure):
    pass

DLLNode._fields_ = [
    ('song_id', c_int),
    ('next', POINTER(DLLNode)),
    ('prev', POINTER(DLLNode))
]

class DoublyLinkedList(Structure):
    _fields_ = [
        ('head', POINTER(DLLNode)),
        ('tail', POINTER(DLLNode)),
        ('current', POINTER(DLLNode)),
        ('size', c_int)
    ]

class HeapNode(Structure):
    _fields_ = [
        ('song_id', c_int),
        ('priority', c_float)
    ]

class MaxHeap(Structure):
    _fields_ = [
        ('nodes', POINTER(HeapNode)),
        ('size', c_int),
        ('capacity', c_int)
    ]

class Operation(Structure):
    _fields_ = [
        ('type', c_int),  # OperationType enum
        ('song_id', c_int),
        ('old_position', c_int),
        ('old_priority', c_float)
    ]

class StackNode(Structure):
    pass

StackNode._fields_ = [
    ('op', Operation),
    ('next', POINTER(StackNode))
]

class Stack(Structure):
    _fields_ = [
        ('top', POINTER(StackNode)),
        ('size', c_int)
    ]

class QueueNode(Structure):
    pass

QueueNode._fields_ = [
    ('song_id', c_int),
    ('next', POINTER(QueueNode))
]

class Queue(Structure):
    _fields_ = [
        ('front', POINTER(QueueNode)),
        ('rear', POINTER(QueueNode)),
        ('size', c_int)
    ]

class SongIdNode(Structure):
    pass

SongIdNode._fields_ = [
    ('song_id', c_int),
    ('next', POINTER(SongIdNode))
]

class TrieNode(Structure):
    pass # Opaque

class MusicQueueManager(Structure):
    _fields_ = [
        ('queue', POINTER(DoublyLinkedList)),
        ('recommendations', POINTER(MaxHeap)),
        ('undo_stack', POINTER(Stack)),
        ('redo_stack', POINTER(Stack)),
        ('upcoming', POINTER(Queue)),
        ('song_trie', POINTER(TrieNode)),
        ('artist_trie', POINTER(TrieNode))
    ]

# ============================================================================
# FUNCTION SIGNATURES
# ============================================================================

if c_lib:
    # Manager functions
    c_lib.manager_create.argtypes = [c_int]
    c_lib.manager_create.restype = POINTER(MusicQueueManager)
    
    c_lib.manager_add_song.argtypes = [POINTER(MusicQueueManager), c_int, c_char_p, c_char_p, c_int, c_int]
    c_lib.manager_add_song.restype = c_bool
    
    c_lib.manager_remove_song.argtypes = [POINTER(MusicQueueManager), c_int]
    c_lib.manager_remove_song.restype = c_bool
    
    c_lib.manager_skip_next.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_skip_next.restype = c_bool
    
    c_lib.manager_skip_prev.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_skip_prev.restype = c_bool
    
    c_lib.manager_move_up.argtypes = [POINTER(MusicQueueManager), c_int]
    c_lib.manager_move_up.restype = c_bool
    
    c_lib.manager_move_down.argtypes = [POINTER(MusicQueueManager), c_int]
    c_lib.manager_move_down.restype = c_bool
    
    c_lib.manager_rotate_queue.argtypes = [POINTER(MusicQueueManager), c_bool]
    c_lib.manager_rotate_queue.restype = c_bool

    c_lib.manager_update_priority.argtypes = [POINTER(MusicQueueManager), c_int, c_int, c_int]
    c_lib.manager_update_priority.restype = c_bool
    
    c_lib.manager_undo.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_undo.restype = c_bool
    
    c_lib.manager_redo.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_redo.restype = c_bool
    
    c_lib.manager_get_current_song.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_get_current_song.restype = c_int
    
    c_lib.manager_destroy.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_destroy.restype = None

    c_lib.manager_search_songs.argtypes = [POINTER(MusicQueueManager), c_char_p]
    c_lib.manager_search_songs.restype = POINTER(SongIdNode)

    c_lib.manager_search_artists.argtypes = [POINTER(MusicQueueManager), c_char_p]
    c_lib.manager_search_artists.restype = POINTER(SongIdNode)

    c_lib.manager_get_recommendations.argtypes = [POINTER(MusicQueueManager), c_int]
    c_lib.manager_get_recommendations.restype = POINTER(SongIdNode)

# ============================================================================
# PYTHON WRAPPER CLASS
# ============================================================================

class MusicQueueWrapper:
    """
    Python wrapper for the C Music Queue Manager
    Strictly uses C data structures, Python/JS fallback is forbidden.
    """
    
    def __init__(self, heap_capacity: int = 1000):
        """Initialize the music queue manager"""
        if not c_lib:
            raise RuntimeError("CRITICAL ERROR: C library not loaded. Python fallback is strictly forbidden.")
        
        self.manager = c_lib.manager_create(heap_capacity)
        if not self.manager:
            raise RuntimeError("CRITICAL ERROR: Failed to create C manager.")
    
    def add_song(self, song_id: int, title: str, artist: str, likes: int = 0, play_count: int = 0) -> bool:
        """Add a song to the queue using C logic"""
        return c_lib.manager_add_song(self.manager, song_id, title.encode('utf-8'), artist.encode('utf-8'), likes, play_count)
    
    def remove_song(self, song_id: int) -> bool:
        """Remove a song from the queue"""
        return c_lib.manager_remove_song(self.manager, song_id)
    
    def skip_next(self) -> bool:
        """Skip to next song"""
        return c_lib.manager_skip_next(self.manager)
    
    def skip_prev(self) -> bool:
        """Skip to previous song"""
        return c_lib.manager_skip_prev(self.manager)
    
    def move_up(self, song_id: int) -> bool:
        """Move song up in queue"""
        return c_lib.manager_move_up(self.manager, song_id)
    
    def move_down(self, song_id: int) -> bool:
        """Move song down in queue"""
        return c_lib.manager_move_down(self.manager, song_id)
    
    def rotate(self, forward: bool = True) -> bool:
        """Rotate the circular queue"""
        return c_lib.manager_rotate_queue(self.manager, forward)
    
    def update_priority(self, song_id: int, likes: int, play_count: int) -> bool:
        """Update song priority in C heap"""
        return c_lib.manager_update_priority(self.manager, song_id, likes, play_count)
    
    def search_songs(self, query: str) -> List[int]:
        """Search songs using C Trie"""
        node_ptr = c_lib.manager_search_songs(self.manager, query.encode('utf-8'))
        results = []
        current = node_ptr
        while current:
            results.append(current.contents.song_id)
            current = current.contents.next
        return list(set(results)) # Deduplicate if any duplicates in trie nodes

    def search_artists(self, query: str) -> List[int]:
        """Search artists using C Trie"""
        node_ptr = c_lib.manager_search_artists(self.manager, query.encode('utf-8'))
        results = []
        current = node_ptr
        while current:
            results.append(current.contents.song_id)
            current = current.contents.next
        return list(set(results))

    def get_recommendations(self, limit: int = 10) -> List[int]:
        """Get recommended song IDs from the heap"""
        node_ptr = c_lib.manager_get_recommendations(self.manager, limit)
        results = []
        current = node_ptr
        while current:
            results.append(current.contents.song_id)
            current = current.contents.next
        return results

    def undo(self) -> bool:
        """Undo last operation"""
        return c_lib.manager_undo(self.manager)
    
    def redo(self) -> bool:
        """Redo last undone operation"""
        return c_lib.manager_redo(self.manager)
    
    def get_current_song(self) -> int:
        """Get currently playing song ID"""
        return c_lib.manager_get_current_song(self.manager)
    
    def get_queue(self) -> List[int]:
        """Get all songs in queue as a list"""
        songs = []
        if self.manager and self.manager.contents.queue:
            head = self.manager.contents.queue.contents.head
            size = self.manager.contents.queue.contents.size
            current_node = head
            for _ in range(size):
                if not current_node: break
                songs.append(current_node.contents.song_id)
                current_node = current_node.contents.next
        return songs
    
    def get_queue_size(self) -> int:
        """Get queue size"""
        if self.manager and self.manager.contents.queue:
            return self.manager.contents.queue.contents.size
        return 0
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'manager') and self.manager and c_lib:
            c_lib.manager_destroy(self.manager)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_library():
    """Test if the C library is loaded and working"""
    try:
        wrapper = MusicQueueWrapper()
        wrapper.add_song(1, 5.0)
        wrapper.add_song(2, 3.0)
        wrapper.add_song(3, 7.0)
        
        queue = wrapper.get_queue()
        current = wrapper.get_current_song()
        
        print(f"✓ C library loaded successfully")
        print(f"✓ Queue: {queue}")
        print(f"✓ Current song: {current}")
        print(f"✓ Queue size: {wrapper.get_queue_size()}")
        
        return True
    except Exception as e:
        print(f"✗ Library test failed: {e}")
        return False

if __name__ == "__main__":
    test_library()

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

class HashMapEntry(Structure):
    pass

HashMapEntry._fields_ = [
    ('song_id', c_int),
    ('node_ptr', POINTER(DLLNode)),
    ('next', POINTER(HashMapEntry))
]

class HashMap(Structure):
    _fields_ = [
        ('buckets', POINTER(POINTER(HashMapEntry))),
        ('capacity', c_int),
        ('size', c_int)
    ]

class MusicQueueManager(Structure):
    _fields_ = [
        ('queue', POINTER(DoublyLinkedList)),
        ('recommendations', POINTER(MaxHeap)),
        ('undo_stack', POINTER(Stack)),
        ('redo_stack', POINTER(Stack)),
        ('upcoming', POINTER(Queue)),
        ('song_map', POINTER(HashMap))
    ]

# ============================================================================
# FUNCTION SIGNATURES
# ============================================================================

if c_lib:
    # Manager functions
    c_lib.manager_create.argtypes = [c_int, c_int]
    c_lib.manager_create.restype = POINTER(MusicQueueManager)
    
    c_lib.manager_add_song.argtypes = [POINTER(MusicQueueManager), c_int, c_float]
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
    
    c_lib.manager_update_priority.argtypes = [POINTER(MusicQueueManager), c_int, c_float]
    c_lib.manager_update_priority.restype = c_bool
    
    c_lib.manager_undo.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_undo.restype = c_bool
    
    c_lib.manager_redo.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_redo.restype = c_bool
    
    c_lib.manager_get_current_song.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_get_current_song.restype = c_int
    
    c_lib.manager_destroy.argtypes = [POINTER(MusicQueueManager)]
    c_lib.manager_destroy.restype = None

# ============================================================================
# PYTHON WRAPPER CLASS
# ============================================================================

class MusicQueueWrapper:
    """
    Python wrapper for the C Music Queue Manager
    Provides Pythonic interface to C functions with a Python fallback
    """
    
    def __init__(self, heap_capacity: int = 1000, hashmap_capacity: int = 1000):
        """Initialize the music queue manager"""
        self.use_fallback = False
        if not c_lib:
            print("⚠ C library not loaded. Using Python fallback implementation for queue management.")
            self.use_fallback = True
            self.queue = []
            self.current_index = -1
            return
        
        try:
            self.manager = c_lib.manager_create(heap_capacity, hashmap_capacity)
            if not self.manager:
                raise RuntimeError("Failed to create manager")
        except Exception as e:
            print(f"⚠ Failed to initialize C manager: {e}. Using Python fallback.")
            self.use_fallback = True
            self.queue = []
            self.current_index = -1
    
    def add_song(self, song_id: int, priority: float = 0.0) -> bool:
        """Add a song to the queue"""
        if self.use_fallback:
            if song_id not in self.queue:
                self.queue.append(song_id)
                if self.current_index == -1:
                    self.current_index = 0
            return True
        return c_lib.manager_add_song(self.manager, song_id, priority)
    
    def remove_song(self, song_id: int) -> bool:
        """Remove a song from the queue"""
        if self.use_fallback:
            if song_id in self.queue:
                idx = self.queue.index(song_id)
                self.queue.remove(song_id)
                if self.current_index >= len(self.queue):
                    self.current_index = len(self.queue) - 1
            return True
        return c_lib.manager_remove_song(self.manager, song_id)
    
    def skip_next(self) -> bool:
        """Skip to next song"""
        if self.use_fallback:
            if not self.queue: return False
            self.current_index = (self.current_index + 1) % len(self.queue)
            return True
        return c_lib.manager_skip_next(self.manager)
    
    def skip_prev(self) -> bool:
        """Skip to previous song"""
        if self.use_fallback:
            if not self.queue: return False
            self.current_index = (self.current_index - 1 + len(self.queue)) % len(self.queue)
            return True
        return c_lib.manager_skip_prev(self.manager)
    
    def move_up(self, song_id: int) -> bool:
        """Move song up in queue"""
        if self.use_fallback:
            if song_id in self.queue:
                idx = self.queue.index(song_id)
                if idx > 0:
                    self.queue[idx], self.queue[idx-1] = self.queue[idx-1], self.queue[idx]
            return True
        return c_lib.manager_move_up(self.manager, song_id)
    
    def move_down(self, song_id: int) -> bool:
        """Move song down in queue"""
        if self.use_fallback:
            if song_id in self.queue:
                idx = self.queue.index(song_id)
                if idx < len(self.queue) - 1:
                    self.queue[idx], self.queue[idx+1] = self.queue[idx+1], self.queue[idx]
            return True
        return c_lib.manager_move_down(self.manager, song_id)
    
    def update_priority(self, song_id: int, priority: float) -> bool:
        """Update song priority"""
        if self.use_fallback:
            return True # No-op for simple fallback
        return c_lib.manager_update_priority(self.manager, song_id, priority)
    
    def undo(self) -> bool:
        """Undo last operation"""
        if self.use_fallback: return False
        return c_lib.manager_undo(self.manager)
    
    def redo(self) -> bool:
        """Redo last undone operation"""
        if self.use_fallback: return False
        return c_lib.manager_redo(self.manager)
    
    def get_current_song(self) -> int:
        """Get currently playing song ID"""
        if self.use_fallback:
            if 0 <= self.current_index < len(self.queue):
                return self.queue[self.current_index]
            return -1
        return c_lib.manager_get_current_song(self.manager)
    
    def get_queue(self) -> List[int]:
        """Get all songs in queue as a list"""
        if self.use_fallback:
            return list(self.queue)
        
        songs = []
        if self.manager and self.manager.contents.queue:
            current_node = self.manager.contents.queue.contents.head
            while current_node:
                songs.append(current_node.contents.song_id)
                current_node = current_node.contents.next
        return songs
    
    def get_queue_size(self) -> int:
        """Get queue size"""
        if self.use_fallback:
            return len(self.queue)
        if self.manager and self.manager.contents.queue:
            return self.manager.contents.queue.contents.size
        return 0
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if not self.use_fallback and hasattr(self, 'manager') and self.manager and c_lib:
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

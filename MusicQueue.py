import ctypes as ct
import os

class song(ct.Structure):
    pass

song._fields_ = [
    ("song_id", ct.c_int),
    ("next_song", ct.POINTER(song)),
    ("prev_song", ct.POINTER(song))
]

path = os.getcwd()
cll = ct.CDLL(os.path.join(path, 'linkedlist.so'))

cll.create_new_song.argtypes = [ct.c_int]
cll.create_new_song.restype = ct.POINTER(song)

cll.insert_begin.argtypes = [ct.POINTER(song), ct.c_int]
cll.insert_begin.restype = ct.POINTER(song)

cll.insert_end.argtypes = [ct.POINTER(song), ct.c_int]
cll.insert_end.restype = ct.POINTER(song)

cll.play_next.argtypes = [ct.POINTER(song)]
cll.play_next.restype = ct.POINTER(song)

cll.play_prev.argtypes = [ct.POINTER(song)]
cll.play_prev.restype = ct.POINTER(song)

cll.delete_song.argtypes = [ct.POINTER(song)]
cll.delete_song.restype = ct.POINTER(song)

cll.display.argtypes = [ct.POINTER(song)]
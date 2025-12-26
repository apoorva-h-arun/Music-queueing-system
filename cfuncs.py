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

set_as_current = cll.set_as_current
set_as_current.argtypes = [ct.POINTER(song), ct.c_int]
set_as_current.restype = ct.POINTER(song)

insert_begin = cll.insert_begin
insert_begin.argtypes = [ct.POINTER(song), ct.c_int]
insert_begin.restype = ct.POINTER(song)

insert_end = cll.insert_end
insert_end.argtypes = [ct.POINTER(song), ct.c_int]
insert_end.restype = ct.POINTER(song)

play_next = cll.play_next
play_next.argtypes = [ct.POINTER(song)]
play_next.restype = ct.POINTER(song)

play_prev = cll.play_prev
play_prev.argtypes = [ct.POINTER(song)]
play_prev.restype = ct.POINTER(song)

delete_song = cll.delete_song
delete_song.argtypes = [ct.POINTER(song)]
delete_song.restype = ct.POINTER(song)

display = cll.display
display.argtypes = [ct.POINTER(song)]

get_curr_id = cll.get_curr_id
get_curr_id.argtypes = [ct.POINTER(song)]
get_curr_id.restype = ct.c_int

song_pointer = ct.POINTER(song)()
curr_song = ct.POINTER(song)()
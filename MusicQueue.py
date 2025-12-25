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

create_new_song = cll.create_new_song
create_new_song.argtypes = [ct.c_int]
create_new_song.restype = ct.POINTER(song)

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

song_pointer = ct.POINTER(song)()
while True:
    choice = int(input("Enter your choice: "))
    if choice == 1:
        id = int(input("Enter song id: "))
        song_pointer = insert_begin(song_pointer, id)
        display(song_pointer)
    elif choice == 2:
        id = int(input("Enter song id: "))
        song_pointer = insert_end(song_pointer, id)
        display(song_pointer)
    elif choice == 3:
        pass
    elif choice == 4:
        pass
    elif choice == 5:
        pass
    elif choice == 6:
        display(song_pointer)
    else:
        break
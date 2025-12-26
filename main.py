from cfuncs import song, song_pointer, curr_song, set_as_current, insert_begin, insert_end, play_next, play_prev, delete_song, display, get_curr_id
from database import insert_song_db, delete_song_db, delete_all

while True:
    choice = int(input("Enter your choice: "))
    if choice == 1:
        song_name = input("Enter song name: ")
        id = int(insert_song_db(song_name))
        song_pointer = insert_begin(song_pointer, id)
        curr_song = set_as_current(song_pointer, id)
        display(song_pointer)
    elif choice == 2:
        song_name = input("Enter song name: ")
        id = int(insert_song_db(song_name))
        song_pointer = insert_end(song_pointer, id)
        curr_song = set_as_current(song_pointer, id)
        display(song_pointer)
    elif choice == 3:
        id = int(input("Enter the song you want to switch to: "))
        curr_song = set_as_current(song_pointer, id)
    elif choice == 4:
        curr_song = play_next(curr_song)
    elif choice == 5:
        curr_song = play_next(curr_song)
    elif choice == 6:
        delete_song_db(get_curr_id(curr_song))
        curr_song = delete_song(curr_song)
    elif choice == 7:
        display(song_pointer)
    else:
        delete_all()
        exit(0)
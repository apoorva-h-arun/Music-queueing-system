#include <stdio.h>
#include <stdlib.h>

struct song {
    int song_id;
    struct song *next_song;
    struct song *prev_song;
};
typedef struct song* SONG;

SONG create_new_song (int id) {
    SONG new_song = (SONG)malloc(sizeof(struct song));
    new_song->song_id = id;
    new_song->next_song = new_song;
    new_song->prev_song = new_song;
    return new_song;
}

SONG insert_begin (SONG song_queue, int id) {
    SONG new_song = (SONG)malloc(sizeof(struct song));
    new_song->song_id = id;
    new_song->next_song = song_queue;
    new_song->prev_song = song_queue->prev_song;
    song_queue->prev_song->next_song = new_song;
    song_queue->prev_song = new_song;
    return new_song;
}

SONG insert_end (SONG song_queue, int id) {
    SONG new_song = (SONG)malloc(sizeof(struct song));
    new_song->song_id = id;
    new_song->next_song = song_queue;
    new_song->prev_song = song_queue->prev_song;
    song_queue->prev_song->next_song = new_song;
    song_queue->prev_song = new_song;
    return song_queue;
}

SONG play_next (SONG curr_song) {
    return curr_song->next_song;
}

SONG play_prev (SONG curr_song) {
    return curr_song->prev_song;
}

SONG delete_song (SONG curr_song) {
    SONG temp = curr_song;
    curr_song->prev_song->next_song = curr_song->next_song;
    curr_song->next_song->prev_song = curr_song->prev_song;
    free(temp);
    return curr_song;
}

void display(SONG song_queue) {
    SONG temp = song_queue;
    printf("----MY PLAYLIST----\n");
    do {
        printf("%d\t", temp->song_id);
        temp = temp->next_song;
    } while (temp->next_song != song_queue);
}

void callFunc (int choice) {
    SONG root = (SONG)malloc(sizeof(struct song));
    root->next_song = root;
    root->prev_song = root;
    switch (choice) {
        case 0:
            root = insertBegin(root, 5);
            display(root);
    }
}
#include <stdio.h>
#include <stdlib.h>

struct song {
    int song_id;
    struct song *next_song;
    struct song *prev_song;
};
typedef struct song* SONG;

SONG set_as_current (SONG song_queue, int id) {
    if (song_queue == NULL) {
        printf("Playlist is empty.\n");
        return NULL;
    }
    else if (song_queue->next_song == song_queue) {
        printf("Currently playing song %d", song_queue->song_id);
        return song_queue;
    }
    else {
        SONG temp = song_queue;
        while (temp->song_id != id && temp->next_song != song_queue) {
            temp = temp->next_song;
        }
        if (temp->song_id == id) {
            printf("Currently playing song %d\n", id);
            return temp;
        }
        else {
            printf("Song %d not found.\n", id);
            return NULL;
        }
    }
}

SONG insert_begin (SONG song_queue, int id) {
    SONG new_song = (SONG)malloc(sizeof(struct song));
    new_song->song_id = id;
    if (song_queue == NULL) {
        new_song->next_song = new_song;
        new_song->prev_song = new_song;
        return new_song;
    }
    new_song->next_song = song_queue;
    new_song->prev_song = song_queue->prev_song;
    song_queue->prev_song->next_song = new_song;
    song_queue->prev_song = new_song;
    return new_song;
}

SONG insert_end (SONG song_queue, int id) {
    SONG new_song = (SONG)malloc(sizeof(struct song));
    new_song->song_id = id;
    if (song_queue == NULL) {
        new_song->next_song = new_song;
        new_song->prev_song = new_song;
        return new_song;
    }
    new_song->next_song = song_queue;
    new_song->prev_song = song_queue->prev_song;
    song_queue->prev_song->next_song = new_song;
    song_queue->prev_song = new_song;
    return song_queue;
}

SONG play_next (SONG curr_song) {
    if (curr_song == NULL) {
        return NULL;
    }
    printf("Currently playing song %d\n", curr_song->next_song->song_id);
    return curr_song->next_song;
}

SONG play_prev (SONG curr_song) {
    if (curr_song == NULL) {
        return NULL;
    }
    printf("Currently playing song %d\n", curr_song->prev_song->song_id);
    return curr_song->prev_song;
}

SONG delete_song (SONG curr_song) {
    if (curr_song == NULL) {
        return NULL;
    }
    SONG temp = curr_song;
    curr_song->prev_song->next_song = curr_song->next_song;
    curr_song->next_song->prev_song = curr_song->prev_song;
    free(temp);
    return curr_song->prev_song;
}

void display(SONG song_queue) {
    if (song_queue == NULL) {
        printf("\nPlaylist is empty.\n\n");
        return;
    }
    SONG temp = song_queue;
    printf("\n----MY PLAYLIST----\n");
    do {
        printf("%d\t", temp->song_id);
        //temp = temp->next_song;
    } while ((temp = temp->next_song) != song_queue);
    printf("\n\n");
}

int get_curr_id (SONG curr_song) {
    return curr_song->song_id;
}
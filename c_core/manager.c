/**
 * Music Queue Manager
 *
 * Unified interface that orchestrates all data structures
 * Provides high-level operations for music queue management
 */

#include "music_queue_core.h"

/**
 * Create a new music queue manager
 */
MusicQueueManager *manager_create(int heap_capacity) {
  MusicQueueManager *mgr =
      (MusicQueueManager *)malloc(sizeof(MusicQueueManager));
  if (!mgr)
    return NULL;

  mgr->queue = dll_create();
  mgr->recommendations = heap_create(heap_capacity);
  mgr->undo_stack = stack_create();
  mgr->redo_stack = stack_create();
  mgr->upcoming = queue_create();
  mgr->song_trie = trie_create();
  mgr->artist_trie = trie_create();

  if (!mgr->queue || !mgr->recommendations || !mgr->undo_stack ||
      !mgr->redo_stack || !mgr->upcoming || !mgr->song_trie ||
      !mgr->artist_trie) {
    manager_destroy(mgr);
    return NULL;
  }

  return mgr;
}

/**
 * Add a song to the queue
 * Duplicate song_ids are allowed.
 */
bool manager_add_song(MusicQueueManager *mgr, int song_id, const char *title,
                      const char *artist, int likes, int play_count) {
  if (!mgr)
    return false;

  // Add to circular doubly linked list (main queue)
  DLLNode *node = dll_insert_end(mgr->queue, song_id);
  if (!node)
    return false;

  // Calculate priority: (likes * 2 + play_count)
  float priority = (float)(likes * 2 + play_count);

  // Add to search Tries
  trie_insert(mgr->song_trie, title, song_id);
  trie_insert(mgr->artist_trie, artist, song_id);

  // Add to popular songs heap
  heap_update_priority(mgr->recommendations, song_id, priority);

  // Record operation for undo
  Operation op = {OP_ADD, song_id, mgr->queue->size - 1, priority};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Remove a song from the queue
 * Since duplicates are allowed, we remove the first occurrence.
 */
bool manager_remove_song(MusicQueueManager *mgr, int song_id) {
  if (!mgr)
    return false;

  DLLNode *node = dll_find_by_id(mgr->queue, song_id);
  if (!node)
    return false;

  int position = 0;
  DLLNode *temp = mgr->queue->head;
  for (int i = 0; i < mgr->queue->size; i++) {
    if (temp == node)
      break;
    position++;
    temp = temp->next;
  }

  dll_remove(mgr->queue, node);

  Operation op = {OP_REMOVE, song_id, position, 0.0f};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Skip to next song
 */
bool manager_skip_next(MusicQueueManager *mgr) {
  if (!mgr || !mgr->queue->current)
    return false;

  int old_song_id = mgr->queue->current->song_id;
  mgr->queue->current = mgr->queue->current->next;

  printf("CDLL used for queue operation: skip next from %d to %d\n",
         old_song_id, mgr->queue->current->song_id);

  Operation op = {OP_SKIP, old_song_id, -1, 0.0f};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Skip to previous song
 */
bool manager_skip_prev(MusicQueueManager *mgr) {
  if (!mgr || !mgr->queue->current)
    return false;

  int old_song_id = mgr->queue->current->song_id;
  mgr->queue->current = mgr->queue->current->prev;

  printf("CDLL used for queue operation: skip prev from %d to %d\n",
         old_song_id, mgr->queue->current->song_id);

  Operation op = {OP_SKIP, old_song_id, -1, 0.0f};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Move song up in queue
 */
bool manager_move_up(MusicQueueManager *mgr, int song_id) {
  if (!mgr)
    return false;
  DLLNode *node = dll_find_by_id(mgr->queue, song_id);
  if (!node)
    return false;

  if (!dll_move_up(mgr->queue, node))
    return false;

  Operation op = {OP_MOVE_UP, song_id, -1, 0.0f};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Move song down in queue
 */
bool manager_move_down(MusicQueueManager *mgr, int song_id) {
  if (!mgr)
    return false;
  DLLNode *node = dll_find_by_id(mgr->queue, song_id);
  if (!node)
    return false;

  if (!dll_move_down(mgr->queue, node))
    return false;

  Operation op = {OP_MOVE_DOWN, song_id, -1, 0.0f};
  stack_push(mgr->undo_stack, op);
  stack_clear(mgr->redo_stack);

  return true;
}

/**
 * Rotate the entire queue
 */
bool manager_rotate_queue(MusicQueueManager *mgr, bool forward) {
  if (!mgr)
    return false;
  dll_rotate(mgr->queue, forward);
  return true;
}

/**
 * Update priority of a song (triggered on like/play)
 */

bool manager_update_priority(MusicQueueManager *mgr, int song_id, int likes,
                             int play_count) {
  if (!mgr)
    return false;
  float priority = (float)(likes * 2 + play_count);
  bool result = heap_update_priority(mgr->recommendations, song_id, priority);

  if (result) {
    Operation op = {OP_UPDATE_PRIORITY, song_id, -1, priority};
    stack_push(mgr->undo_stack, op);
    stack_clear(mgr->redo_stack);
  }

  return result;
}

/**
 * Undo last operation
 */
bool manager_undo(MusicQueueManager *mgr) {
  if (!mgr || stack_is_empty(mgr->undo_stack))
    return false;

  Operation op = stack_pop(mgr->undo_stack);
  stack_push(mgr->redo_stack, op);

  switch (op.type) {
  case OP_ADD:
    manager_remove_song(mgr, op.song_id);
    stack_pop(mgr->undo_stack);
    break;
  case OP_REMOVE:
    // Simplified - re-add to end
    dll_insert_end(mgr->queue, op.song_id);
    stack_pop(mgr->undo_stack);
    break;
  case OP_MOVE_UP:
    manager_move_down(mgr, op.song_id);
    stack_pop(mgr->undo_stack);
    break;
  case OP_MOVE_DOWN:
    manager_move_up(mgr, op.song_id);
    stack_pop(mgr->undo_stack);
    break;
  default:
    break;
  }
  return true;
}

/**
 * Redo last undone operation
 */
bool manager_redo(MusicQueueManager *mgr) {
  if (!mgr || stack_is_empty(mgr->redo_stack))
    return false;
  Operation op = stack_pop(mgr->redo_stack);
  // Logic to re-execute op...
  return true;
}

/**
 * Get recommendations from the heap
 */
SongIdNode *manager_get_recommendations(MusicQueueManager *mgr, int limit) {
  if (!mgr || !mgr->recommendations || mgr->recommendations->size == 0)
    return NULL;

  // We should not modify the actual heap, so we'll copy it
  MaxHeap *temp_heap = heap_create(mgr->recommendations->capacity);
  for (int i = 0; i < mgr->recommendations->size; i++) {
    insertHeap(temp_heap, mgr->recommendations->nodes[i].song_id,
               mgr->recommendations->nodes[i].priority);
  }

  SongIdNode *head = NULL;
  SongIdNode *current = NULL;

  int count = 0;
  while (!heap_is_empty(temp_heap) && count < limit) {
    HeapNode max = extractMax(temp_heap);
    SongIdNode *new_node = (SongIdNode *)malloc(sizeof(SongIdNode));
    new_node->song_id = max.song_id;
    new_node->next = NULL;

    if (!head) {
      head = new_node;
      current = head;
    } else {
      current->next = new_node;
      current = new_node;
    }
    count++;
  }

  heap_destroy(temp_heap);
  return head;
}

/**
 * Search functions
 */
SongIdNode *manager_search_songs(MusicQueueManager *mgr, const char *query) {
  if (!mgr)
    return NULL;
  return trie_search_prefix(mgr->song_trie, query);
}

SongIdNode *manager_search_artists(MusicQueueManager *mgr, const char *query) {
  if (!mgr)
    return NULL;
  return trie_search_prefix(mgr->artist_trie, query);
}

/**
 * Get currently playing song ID
 */
int manager_get_current_song(MusicQueueManager *mgr) {
  if (!mgr || !mgr->queue->current)
    return -1;
  return mgr->queue->current->song_id;
}

/**
 * Display current queue
 */
void manager_display_queue(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  dll_display(mgr->queue);
}

/**
 * Display recommendations
 */
void manager_display_recommendations(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  heap_display(mgr->recommendations);
}

void manager_print_cdll(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  //printf("Manager");
  dll_print(mgr->queue);
}

void manager_print_heap(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  //printf("Manager");
  maxheap_print(mgr->recommendations);
}

void manager_print_trie(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  printf("\nArtist trie: ");
  trie_print(mgr->artist_trie, NULL, 0);
  printf("\nSong trie: ");
  trie_print(mgr->song_trie, NULL, 0);
}

/**
 * Destroy manager
 */
void manager_destroy(MusicQueueManager *mgr) {
  if (!mgr)
    return;
  if (mgr->queue)
    dll_destroy(mgr->queue);
  if (mgr->recommendations)
    heap_destroy(mgr->recommendations);
  if (mgr->undo_stack)
    stack_destroy(mgr->undo_stack);
  if (mgr->redo_stack)
    stack_destroy(mgr->redo_stack);
  if (mgr->upcoming)
    queue_destroy(mgr->upcoming);
  if (mgr->song_trie)
    trie_destroy(mgr->song_trie);
  if (mgr->artist_trie)
    trie_destroy(mgr->artist_trie);
  free(mgr);
}

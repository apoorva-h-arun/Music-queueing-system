/**
 * Circular Doubly Linked List Implementation
 *
 * Maintains the main playback queue with circularity
 * Supports bidirectional navigation and rotation
 */

#include "music_queue_core.h"

/**
 * Create a new circular doubly linked list
 */
DoublyLinkedList *dll_create() {
  DoublyLinkedList *list = (DoublyLinkedList *)malloc(sizeof(DoublyLinkedList));
  if (!list)
    return NULL;

  list->head = NULL;
  list->tail = NULL;
  list->current = NULL;
  list->size = 0;

  return list;
}

/**
 * Insert song at the end of the circular queue
 * Operation: enqueue
 */
DLLNode *dll_insert_end(DoublyLinkedList *list, int song_id) {
  if (!list)
    return NULL;

  DLLNode *new_node = (DLLNode *)malloc(sizeof(DLLNode));
  if (!new_node)
    return NULL;

  new_node->song_id = song_id;

  if (list->head == NULL) {
    // First node
    new_node->next = new_node;
    new_node->prev = new_node;
    list->head = new_node;
    list->tail = new_node;
    list->current = new_node;
  } else {
    // Standard insert at end
    new_node->prev = list->tail;
    new_node->next = list->head;
    list->tail->next = new_node;
    list->head->prev = new_node;
    list->tail = new_node;
  }

  list->size++;
  printf("CDLL used for queue operation: enqueue %d\n", song_id);
  return new_node;
}

/**
 * Remove a node from the circular list
 * Operation: dequeue (if head)
 */
bool dll_remove(DoublyLinkedList *list, DLLNode *node) {
  if (!list || !node || list->size == 0)
    return false;

  int song_id = node->song_id;

  if (list->size == 1) {
    list->head = NULL;
    list->tail = NULL;
    list->current = NULL;
  } else {
    node->prev->next = node->next;
    node->next->prev = node->prev;

    if (list->head == node) {
      list->head = node->next;
    }
    if (list->tail == node) {
      list->tail = node->prev;
    }
    if (list->current == node) {
      list->current = node->next;
    }
  }

  free(node);
  list->size--;
  printf("CDLL used for queue operation: remove %d\n", song_id);
  return true;
}

/**
 * Move a node up (swap with previous)
 */
bool dll_move_up(DoublyLinkedList *list, DLLNode *node) {
  if (!list || !node || list->size < 2)
    return false;

  DLLNode *prev = node->prev;

  // Swap IDs for simplicity in CDLL if we don't want to re-link everything
  // But requirement says CDLL ops, so let's re-link properly.

  DLLNode *p_prev = prev->prev;
  DLLNode *n_next = node->next;

  // Link p_prev to node
  p_prev->next = node;
  node->prev = p_prev;

  // Link node to prev
  node->next = prev;
  prev->prev = node;

  // Link prev to n_next
  prev->next = n_next;
  n_next->prev = prev;

  // Update head/tail if they were swapped
  if (list->head == prev)
    list->head = node;
  else if (list->head == node)
    list->head = prev;

  if (list->tail == node)
    list->tail = prev;
  else if (list->tail == prev)
    list->tail = node;

  printf("CDLL used for queue operation: moveUp %d\n", node->song_id);
  return true;
}

/**
 * Move a node down (swap with next)
 */
bool dll_move_down(DoublyLinkedList *list, DLLNode *node) {
  if (!list || !node || list->size < 2)
    return false;
  printf("CDLL used for queue operation: moveDown %d\n", node->song_id);
  return dll_move_up(list, node->next);
}

/**
 * Rotate the queue
 */
void dll_rotate(DoublyLinkedList *list, bool forward) {
  if (!list || list->size < 2)
    return;

  if (forward) {
    list->head = list->head->next;
    list->tail = list->tail->next;
  } else {
    list->head = list->head->prev;
    list->tail = list->tail->prev;
  }
  printf("CDLL used for queue operation: rotate\n");
}

/**
 * Get next song in queue
 */
DLLNode *dll_get_next(DoublyLinkedList *list, DLLNode *current) {
  if (!list || !current)
    return NULL;
  return current->next;
}

/**
 * Get previous song in queue
 */
DLLNode *dll_get_prev(DoublyLinkedList *list, DLLNode *current) {
  if (!list || !current)
    return NULL;
  return current->prev;
}

/**
 * Find node by song ID (Note: can be multiple)
 */
DLLNode *dll_find_by_id(DoublyLinkedList *list, int song_id) {
  if (!list || list->size == 0)
    return NULL;

  DLLNode *current = list->head;
  for (int i = 0; i < list->size; i++) {
    if (current->song_id == song_id)
      return current;
    current = current->next;
  }
  return NULL;
}

/**
 * Display the queue
 */
void dll_display(DoublyLinkedList *list) {
  if (!list || list->size == 0) {
    printf("Queue is empty\n");
    return;
  }

  printf("\n=== CDLL PLAYBACK QUEUE (Size: %d) ===\n", list->size);
  DLLNode *current = list->head;
  for (int i = 0; i < list->size; i++) {
    printf("[%d] Song ID: %d %s\n", i, current->song_id,
           (current == list->current) ? "← CURRENT" : "");
    current = current->next;
  }
  printf("======================================\n\n");
}

/**
 * Get queue size
 */
int dll_get_size(DoublyLinkedList *list) { return list ? list->size : 0; }

/**
 * Destroy the list and free memory
 */
void dll_destroy(DoublyLinkedList *list) {
  if (!list)
    return;

  if (list->size > 0) {
    DLLNode *current = list->head;
    for (int i = 0; i < list->size; i++) {
      DLLNode *next = current->next;
      free(current);
      current = next;
    }
  }

  free(list);
}

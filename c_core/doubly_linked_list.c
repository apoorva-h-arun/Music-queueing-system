/**
 * Doubly Linked List Implementation
 * 
 * Maintains the main playback queue with O(1) operations when node reference is available
 * Supports bidirectional navigation for music player functionality
 */

#include "music_queue_core.h"

/**
 * Create a new doubly linked list
 * Time Complexity: O(1)
 */
DoublyLinkedList* dll_create() {
    DoublyLinkedList* list = (DoublyLinkedList*)malloc(sizeof(DoublyLinkedList));
    if (!list) return NULL;
    
    list->head = NULL;
    list->tail = NULL;
    list->current = NULL;
    list->size = 0;
    
    return list;
}

/**
 * Insert song at the end of the queue
 * Time Complexity: O(1)
 */
DLLNode* dll_insert_end(DoublyLinkedList* list, int song_id) {
    if (!list) return NULL;
    
    DLLNode* new_node = (DLLNode*)malloc(sizeof(DLLNode));
    if (!new_node) return NULL;
    
    new_node->song_id = song_id;
    new_node->next = NULL;
    new_node->prev = list->tail;
    
    if (list->tail) {
        list->tail->next = new_node;
    } else {
        // First node
        list->head = new_node;
        list->current = new_node;  // Set as current if first song
    }
    
    list->tail = new_node;
    list->size++;
    
    return new_node;
}

/**
 * Insert song at a specific position
 * Time Complexity: O(n) - needs to traverse to position
 */
DLLNode* dll_insert_at(DoublyLinkedList* list, int song_id, int position) {
    if (!list || position < 0 || position > list->size) return NULL;
    
    // Special case: insert at end
    if (position == list->size) {
        return dll_insert_end(list, song_id);
    }
    
    DLLNode* new_node = (DLLNode*)malloc(sizeof(DLLNode));
    if (!new_node) return NULL;
    
    new_node->song_id = song_id;
    
    // Special case: insert at beginning
    if (position == 0) {
        new_node->next = list->head;
        new_node->prev = NULL;
        
        if (list->head) {
            list->head->prev = new_node;
        }
        
        list->head = new_node;
        
        if (!list->tail) {
            list->tail = new_node;
        }
        
        if (!list->current) {
            list->current = new_node;
        }
        
        list->size++;
        return new_node;
    }
    
    // Traverse to position
    DLLNode* current = list->head;
    for (int i = 0; i < position; i++) {
        current = current->next;
    }
    
    // Insert before current
    new_node->next = current;
    new_node->prev = current->prev;
    
    if (current->prev) {
        current->prev->next = new_node;
    }
    current->prev = new_node;
    
    list->size++;
    return new_node;
}

/**
 * Remove a node from the list
 * Time Complexity: O(1) with node reference
 */
bool dll_remove(DoublyLinkedList* list, DLLNode* node) {
    if (!list || !node) return false;
    
    // Update current pointer if removing current song
    if (list->current == node) {
        list->current = node->next ? node->next : node->prev;
    }
    
    // Update head if removing first node
    if (list->head == node) {
        list->head = node->next;
    }
    
    // Update tail if removing last node
    if (list->tail == node) {
        list->tail = node->prev;
    }
    
    // Update links
    if (node->prev) {
        node->prev->next = node->next;
    }
    
    if (node->next) {
        node->next->prev = node->prev;
    }
    
    free(node);
    list->size--;
    
    return true;
}

/**
 * Move a node up (swap with previous)
 * Time Complexity: O(1)
 */
bool dll_move_up(DoublyLinkedList* list, DLLNode* node) {
    if (!list || !node || !node->prev) return false;
    
    DLLNode* prev_node = node->prev;
    
    // Update head if necessary
    if (list->head == prev_node) {
        list->head = node;
    }
    
    // Update tail if necessary
    if (list->tail == node) {
        list->tail = prev_node;
    }
    
    // Perform swap
    node->prev = prev_node->prev;
    prev_node->next = node->next;
    
    if (node->prev) {
        node->prev->next = node;
    }
    
    if (prev_node->next) {
        prev_node->next->prev = prev_node;
    }
    
    node->next = prev_node;
    prev_node->prev = node;
    
    return true;
}

/**
 * Move a node down (swap with next)
 * Time Complexity: O(1)
 */
bool dll_move_down(DoublyLinkedList* list, DLLNode* node) {
    if (!list || !node || !node->next) return false;
    
    DLLNode* next_node = node->next;
    
    // Update head if necessary
    if (list->head == node) {
        list->head = next_node;
    }
    
    // Update tail if necessary
    if (list->tail == next_node) {
        list->tail = node;
    }
    
    // Perform swap
    node->next = next_node->next;
    next_node->prev = node->prev;
    
    if (node->next) {
        node->next->prev = node;
    }
    
    if (next_node->prev) {
        next_node->prev->next = next_node;
    }
    
    node->prev = next_node;
    next_node->next = node;
    
    return true;
}

/**
 * Get next song in queue
 * Time Complexity: O(1)
 */
DLLNode* dll_get_next(DoublyLinkedList* list, DLLNode* current) {
    if (!list || !current) return NULL;
    return current->next;
}

/**
 * Get previous song in queue
 * Time Complexity: O(1)
 */
DLLNode* dll_get_prev(DoublyLinkedList* list, DLLNode* current) {
    if (!list || !current) return NULL;
    return current->prev;
}

/**
 * Find node by song ID
 * Time Complexity: O(n) - linear search
 * Note: Use HashMap for O(1) lookup in production
 */
DLLNode* dll_find_by_id(DoublyLinkedList* list, int song_id) {
    if (!list) return NULL;
    
    DLLNode* current = list->head;
    while (current) {
        if (current->song_id == song_id) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

/**
 * Display the queue
 * Time Complexity: O(n)
 */
void dll_display(DoublyLinkedList* list) {
    if (!list) {
        printf("List is NULL\n");
        return;
    }
    
    if (!list->head) {
        printf("Queue is empty\n");
        return;
    }
    
    printf("\n=== PLAYBACK QUEUE (Size: %d) ===\n", list->size);
    
    DLLNode* current = list->head;
    int position = 0;
    
    while (current) {
        if (current == list->current) {
            printf("[%d] Song ID: %d ← CURRENTLY PLAYING\n", position, current->song_id);
        } else {
            printf("[%d] Song ID: %d\n", position, current->song_id);
        }
        current = current->next;
        position++;
    }
    
    printf("================================\n\n");
}

/**
 * Get queue size
 * Time Complexity: O(1)
 */
int dll_get_size(DoublyLinkedList* list) {
    return list ? list->size : 0;
}

/**
 * Destroy the list and free memory
 * Time Complexity: O(n)
 */
void dll_destroy(DoublyLinkedList* list) {
    if (!list) return;
    
    DLLNode* current = list->head;
    while (current) {
        DLLNode* next = current->next;
        free(current);
        current = next;
    }
    
    free(list);
}

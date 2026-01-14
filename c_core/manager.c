/**
 * Music Queue Manager
 * 
 * Unified interface that orchestrates all data structures
 * Provides high-level operations for music queue management
 * Implements undo/redo functionality
 */

#include "music_queue_core.h"

/**
 * Create a new music queue manager
 * Time Complexity: O(n) where n is max(heap_capacity, hashmap_capacity)
 */
MusicQueueManager* manager_create(int heap_capacity, int hashmap_capacity) {
    MusicQueueManager* mgr = (MusicQueueManager*)malloc(sizeof(MusicQueueManager));
    if (!mgr) return NULL;
    
    mgr->queue = dll_create();
    mgr->recommendations = heap_create(heap_capacity);
    mgr->undo_stack = stack_create();
    mgr->redo_stack = stack_create();
    mgr->upcoming = queue_create();
    mgr->song_map = hashmap_create(hashmap_capacity);
    
    // Check if all components were created successfully
    if (!mgr->queue || !mgr->recommendations || !mgr->undo_stack || 
        !mgr->redo_stack || !mgr->upcoming || !mgr->song_map) {
        manager_destroy(mgr);
        return NULL;
    }
    
    return mgr;
}

/**
 * Add a song to the queue
 * Time Complexity: O(log n) due to heap insertion
 */
bool manager_add_song(MusicQueueManager* mgr, int song_id, float priority) {
    if (!mgr) return false;
    
    // Add to doubly linked list (main queue)
    DLLNode* node = dll_insert_end(mgr->queue, song_id);
    if (!node) return false;
    
    // Add to hash map for O(1) lookup
    if (!hashmap_insert(mgr->song_map, song_id, node)) {
        dll_remove(mgr->queue, node);
        return false;
    }
    
    // Add to recommendations heap
    heap_insert(mgr->recommendations, song_id, priority);
    
    // Record operation for undo
    Operation op = {OP_ADD, song_id, mgr->queue->size - 1, priority};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack when new operation is performed
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Remove a song from the queue
 * Time Complexity: O(1) for queue removal, O(n) for heap (if we remove from heap)
 */
bool manager_remove_song(MusicQueueManager* mgr, int song_id) {
    if (!mgr) return false;
    
    // Get node from hash map
    DLLNode* node = hashmap_get(mgr->song_map, song_id);
    if (!node) return false;
    
    // Find position for undo
    int position = 0;
    DLLNode* temp = mgr->queue->head;
    while (temp && temp != node) {
        position++;
        temp = temp->next;
    }
    
    // Remove from hash map
    hashmap_remove(mgr->song_map, song_id);
    
    // Remove from doubly linked list
    dll_remove(mgr->queue, node);
    
    // Record operation for undo
    Operation op = {OP_REMOVE, song_id, position, 0.0f};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Skip to next song
 * Time Complexity: O(1)
 */
bool manager_skip_next(MusicQueueManager* mgr) {
    if (!mgr || !mgr->queue->current) return false;
    
    int old_song_id = mgr->queue->current->song_id;
    
    DLLNode* next = dll_get_next(mgr->queue, mgr->queue->current);
    if (!next) return false;
    
    mgr->queue->current = next;
    
    // Record operation for undo
    Operation op = {OP_SKIP, old_song_id, -1, 0.0f};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Skip to previous song
 * Time Complexity: O(1)
 */
bool manager_skip_prev(MusicQueueManager* mgr) {
    if (!mgr || !mgr->queue->current) return false;
    
    int old_song_id = mgr->queue->current->song_id;
    
    DLLNode* prev = dll_get_prev(mgr->queue, mgr->queue->current);
    if (!prev) return false;
    
    mgr->queue->current = prev;
    
    // Record operation for undo
    Operation op = {OP_SKIP, old_song_id, -1, 0.0f};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Move song up in queue
 * Time Complexity: O(1)
 */
bool manager_move_up(MusicQueueManager* mgr, int song_id) {
    if (!mgr) return false;
    
    DLLNode* node = hashmap_get(mgr->song_map, song_id);
    if (!node) return false;
    
    if (!dll_move_up(mgr->queue, node)) return false;
    
    // Record operation for undo
    Operation op = {OP_MOVE_UP, song_id, -1, 0.0f};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Move song down in queue
 * Time Complexity: O(1)
 */
bool manager_move_down(MusicQueueManager* mgr, int song_id) {
    if (!mgr) return false;
    
    DLLNode* node = hashmap_get(mgr->song_map, song_id);
    if (!node) return false;
    
    if (!dll_move_down(mgr->queue, node)) return false;
    
    // Record operation for undo
    Operation op = {OP_MOVE_DOWN, song_id, -1, 0.0f};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Update priority of a song
 * Time Complexity: O(log n) due to heap update
 */
bool manager_update_priority(MusicQueueManager* mgr, int song_id, float new_priority) {
    if (!mgr) return false;
    
    // Check if song exists
    if (!hashmap_contains(mgr->song_map, song_id)) return false;
    
    // Update in heap (this is simplified - in production you'd need to track old priority)
    heap_increase_priority(mgr->recommendations, song_id, new_priority);
    
    // Record operation for undo
    Operation op = {OP_UPDATE_PRIORITY, song_id, -1, new_priority};
    stack_push(mgr->undo_stack, op);
    
    // Clear redo stack
    stack_clear(mgr->redo_stack);
    
    return true;
}

/**
 * Undo last operation
 * Time Complexity: Varies by operation type
 */
bool manager_undo(MusicQueueManager* mgr) {
    if (!mgr || stack_is_empty(mgr->undo_stack)) return false;
    
    Operation op = stack_pop(mgr->undo_stack);
    
    // Push to redo stack
    stack_push(mgr->redo_stack, op);
    
    // Reverse the operation
    switch (op.type) {
        case OP_ADD:
            // Undo add = remove
            manager_remove_song(mgr, op.song_id);
            // Remove the extra undo entry we just created
            stack_pop(mgr->undo_stack);
            break;
            
        case OP_REMOVE:
            // Undo remove = add back (simplified - doesn't restore exact position)
            manager_add_song(mgr, op.song_id, op.old_priority);
            stack_pop(mgr->undo_stack);
            break;
            
        case OP_MOVE_UP:
            // Undo move up = move down
            manager_move_down(mgr, op.song_id);
            stack_pop(mgr->undo_stack);
            break;
            
        case OP_MOVE_DOWN:
            // Undo move down = move up
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
 * Time Complexity: Varies by operation type
 */
bool manager_redo(MusicQueueManager* mgr) {
    if (!mgr || stack_is_empty(mgr->redo_stack)) return false;
    
    Operation op = stack_pop(mgr->redo_stack);
    
    // Re-execute the operation
    switch (op.type) {
        case OP_ADD:
            manager_add_song(mgr, op.song_id, op.old_priority);
            break;
            
        case OP_REMOVE:
            manager_remove_song(mgr, op.song_id);
            break;
            
        case OP_MOVE_UP:
            manager_move_up(mgr, op.song_id);
            break;
            
        case OP_MOVE_DOWN:
            manager_move_down(mgr, op.song_id);
            break;
            
        default:
            break;
    }
    
    return true;
}

/**
 * Get currently playing song ID
 * Time Complexity: O(1)
 */
int manager_get_current_song(MusicQueueManager* mgr) {
    if (!mgr || !mgr->queue->current) return -1;
    
    return mgr->queue->current->song_id;
}

/**
 * Display current queue
 * Time Complexity: O(n)
 */
void manager_display_queue(MusicQueueManager* mgr) {
    if (!mgr) {
        printf("Manager is NULL\n");
        return;
    }
    
    dll_display(mgr->queue);
}

/**
 * Display recommendations
 * Time Complexity: O(n)
 */
void manager_display_recommendations(MusicQueueManager* mgr) {
    if (!mgr) {
        printf("Manager is NULL\n");
        return;
    }
    
    heap_display(mgr->recommendations);
}

/**
 * Destroy manager and free all memory
 * Time Complexity: O(n)
 */
void manager_destroy(MusicQueueManager* mgr) {
    if (!mgr) return;
    
    if (mgr->queue) dll_destroy(mgr->queue);
    if (mgr->recommendations) heap_destroy(mgr->recommendations);
    if (mgr->undo_stack) stack_destroy(mgr->undo_stack);
    if (mgr->redo_stack) stack_destroy(mgr->redo_stack);
    if (mgr->upcoming) queue_destroy(mgr->upcoming);
    if (mgr->song_map) hashmap_destroy(mgr->song_map);
    
    free(mgr);
}

/**
 * Music Queue Core - Header File
 * 
 * Production-grade data structures for music streaming queue management
 * All core DSA implemented in pure C for optimal performance
 * 
 * Complexity guarantees:
 * - Doubly Linked List: O(1) insert/delete with reference
 * - Max Heap: O(log n) insert/extract, O(1) peek
 * - Stack: O(1) push/pop
 * - Queue: O(1) enqueue/dequeue
 * - HashMap: O(1) average case lookup/insert/delete
 */

#ifndef MUSIC_QUEUE_CORE_H
#define MUSIC_QUEUE_CORE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// ============================================================================
// COMMON STRUCTURES
// ============================================================================

/**
 * Song structure - represents a single song
 */
typedef struct {
    int id;
    float priority;  // Calculated: popularity * 0.5 + votes * 0.3 + premium * 0.2
} Song;

/**
 * Operation types for undo/redo system
 */
typedef enum {
    OP_ADD,
    OP_REMOVE,
    OP_SKIP,
    OP_MOVE_UP,
    OP_MOVE_DOWN,
    OP_UPDATE_PRIORITY
} OperationType;

// ============================================================================
// DOUBLY LINKED LIST (Main Queue)
// ============================================================================

typedef struct DLLNode {
    int song_id;
    struct DLLNode* next;
    struct DLLNode* prev;
} DLLNode;

typedef struct {
    DLLNode* head;
    DLLNode* tail;
    DLLNode* current;  // Currently playing song
    int size;
} DoublyLinkedList;

// DLL Functions
DoublyLinkedList* dll_create();
DLLNode* dll_insert_end(DoublyLinkedList* list, int song_id);
DLLNode* dll_insert_at(DoublyLinkedList* list, int song_id, int position);
bool dll_remove(DoublyLinkedList* list, DLLNode* node);
bool dll_move_up(DoublyLinkedList* list, DLLNode* node);
bool dll_move_down(DoublyLinkedList* list, DLLNode* node);
DLLNode* dll_get_next(DoublyLinkedList* list, DLLNode* current);
DLLNode* dll_get_prev(DoublyLinkedList* list, DLLNode* current);
DLLNode* dll_find_by_id(DoublyLinkedList* list, int song_id);
void dll_display(DoublyLinkedList* list);
void dll_destroy(DoublyLinkedList* list);
int dll_get_size(DoublyLinkedList* list);

// ============================================================================
// MAX HEAP (Priority Queue for Recommendations)
// ============================================================================

typedef struct {
    int song_id;
    float priority;
} HeapNode;

typedef struct {
    HeapNode* nodes;
    int size;
    int capacity;
} MaxHeap;

// Heap Functions
MaxHeap* heap_create(int capacity);
bool heap_insert(MaxHeap* heap, int song_id, float priority);
HeapNode heap_extract_max(MaxHeap* heap);
HeapNode heap_peek(MaxHeap* heap);
bool heap_increase_priority(MaxHeap* heap, int song_id, float new_priority);
bool heap_decrease_priority(MaxHeap* heap, int song_id, float new_priority);
void heap_display(MaxHeap* heap);
void heap_destroy(MaxHeap* heap);
int heap_get_size(MaxHeap* heap);
bool heap_is_empty(MaxHeap* heap);

// ============================================================================
// STACK (Undo/Redo System)
// ============================================================================

typedef struct {
    OperationType type;
    int song_id;
    int old_position;
    float old_priority;
} Operation;

typedef struct StackNode {
    Operation op;
    struct StackNode* next;
} StackNode;

typedef struct {
    StackNode* top;
    int size;
} Stack;

// Stack Functions
Stack* stack_create();
bool stack_push(Stack* stack, Operation op);
Operation stack_pop(Stack* stack);
Operation stack_peek(Stack* stack);
bool stack_is_empty(Stack* stack);
int stack_get_size(Stack* stack);
void stack_clear(Stack* stack);
void stack_destroy(Stack* stack);

// ============================================================================
// QUEUE (Upcoming Songs Buffer)
// ============================================================================

typedef struct QueueNode {
    int song_id;
    struct QueueNode* next;
} QueueNode;

typedef struct {
    QueueNode* front;
    QueueNode* rear;
    int size;
} Queue;

// Queue Functions
Queue* queue_create();
bool queue_enqueue(Queue* queue, int song_id);
int queue_dequeue(Queue* queue);
int queue_peek(Queue* queue);
bool queue_is_empty(Queue* queue);
int queue_get_size(Queue* queue);
void queue_clear(Queue* queue);
void queue_destroy(Queue* queue);

// ============================================================================
// HASH MAP (Fast Song Lookup)
// ============================================================================

typedef struct HashMapEntry {
    int song_id;
    DLLNode* node_ptr;  // Pointer to node in doubly linked list
    struct HashMapEntry* next;  // For chaining
} HashMapEntry;

typedef struct {
    HashMapEntry** buckets;
    int capacity;
    int size;
} HashMap;

// HashMap Functions
HashMap* hashmap_create(int capacity);
bool hashmap_insert(HashMap* map, int song_id, DLLNode* node_ptr);
DLLNode* hashmap_get(HashMap* map, int song_id);
bool hashmap_remove(HashMap* map, int song_id);
bool hashmap_contains(HashMap* map, int song_id);
void hashmap_display(HashMap* map);
void hashmap_destroy(HashMap* map);
int hashmap_get_size(HashMap* map);

// ============================================================================
// UNIFIED MUSIC QUEUE MANAGER
// ============================================================================

typedef struct {
    DoublyLinkedList* queue;
    MaxHeap* recommendations;
    Stack* undo_stack;
    Stack* redo_stack;
    Queue* upcoming;
    HashMap* song_map;
} MusicQueueManager;

// Manager Functions
MusicQueueManager* manager_create(int heap_capacity, int hashmap_capacity);
bool manager_add_song(MusicQueueManager* mgr, int song_id, float priority);
bool manager_remove_song(MusicQueueManager* mgr, int song_id);
bool manager_skip_next(MusicQueueManager* mgr);
bool manager_skip_prev(MusicQueueManager* mgr);
bool manager_move_up(MusicQueueManager* mgr, int song_id);
bool manager_move_down(MusicQueueManager* mgr, int song_id);
bool manager_update_priority(MusicQueueManager* mgr, int song_id, float new_priority);
bool manager_undo(MusicQueueManager* mgr);
bool manager_redo(MusicQueueManager* mgr);
int manager_get_current_song(MusicQueueManager* mgr);
void manager_display_queue(MusicQueueManager* mgr);
void manager_display_recommendations(MusicQueueManager* mgr);
void manager_destroy(MusicQueueManager* mgr);

#endif // MUSIC_QUEUE_CORE_H

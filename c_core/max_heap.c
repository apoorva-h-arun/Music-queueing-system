/**
 * Max Heap Implementation (Priority Queue)
 * 
 * Used for priority-based song recommendations
 * Maintains songs ordered by priority score
 * 
 * Priority = popularity * 0.5 + user_votes * 0.3 + premium_weight * 0.2
 */

#include "music_queue_core.h"

// Helper function prototypes
static void heapify_up(MaxHeap* heap, int index);
static void heapify_down(MaxHeap* heap, int index);
static void swap_nodes(HeapNode* a, HeapNode* b);
static int find_song_index(MaxHeap* heap, int song_id);

/**
 * Create a new max heap
 * Time Complexity: O(1)
 */
MaxHeap* heap_create(int capacity) {
    if (capacity <= 0) return NULL;
    
    MaxHeap* heap = (MaxHeap*)malloc(sizeof(MaxHeap));
    if (!heap) return NULL;
    
    heap->nodes = (HeapNode*)malloc(sizeof(HeapNode) * capacity);
    if (!heap->nodes) {
        free(heap);
        return NULL;
    }
    
    heap->size = 0;
    heap->capacity = capacity;
    
    return heap;
}

/**
 * Insert a song into the heap
 * Time Complexity: O(log n)
 */
bool heap_insert(MaxHeap* heap, int song_id, float priority) {
    if (!heap || heap->size >= heap->capacity) return false;
    
    // Add at the end
    heap->nodes[heap->size].song_id = song_id;
    heap->nodes[heap->size].priority = priority;
    
    // Heapify up to maintain max heap property
    heapify_up(heap, heap->size);
    heap->size++;
    
    return true;
}

/**
 * Extract the maximum priority song
 * Time Complexity: O(log n)
 */
HeapNode heap_extract_max(MaxHeap* heap) {
    HeapNode invalid = {-1, -1.0f};
    
    if (!heap || heap->size == 0) return invalid;
    
    HeapNode max = heap->nodes[0];
    
    // Move last element to root
    heap->nodes[0] = heap->nodes[heap->size - 1];
    heap->size--;
    
    // Heapify down to maintain max heap property
    if (heap->size > 0) {
        heapify_down(heap, 0);
    }
    
    return max;
}

/**
 * Peek at the maximum priority song without removing
 * Time Complexity: O(1)
 */
HeapNode heap_peek(MaxHeap* heap) {
    HeapNode invalid = {-1, -1.0f};
    
    if (!heap || heap->size == 0) return invalid;
    
    return heap->nodes[0];
}

/**
 * Increase priority of a song
 * Time Complexity: O(log n)
 */
bool heap_increase_priority(MaxHeap* heap, int song_id, float new_priority) {
    if (!heap) return false;
    
    int index = find_song_index(heap, song_id);
    if (index == -1) return false;
    
    if (new_priority <= heap->nodes[index].priority) return false;
    
    heap->nodes[index].priority = new_priority;
    heapify_up(heap, index);
    
    return true;
}

/**
 * Decrease priority of a song
 * Time Complexity: O(log n)
 */
bool heap_decrease_priority(MaxHeap* heap, int song_id, float new_priority) {
    if (!heap) return false;
    
    int index = find_song_index(heap, song_id);
    if (index == -1) return false;
    
    if (new_priority >= heap->nodes[index].priority) return false;
    
    heap->nodes[index].priority = new_priority;
    heapify_down(heap, index);
    
    return true;
}

/**
 * Display heap contents
 * Time Complexity: O(n)
 */
void heap_display(MaxHeap* heap) {
    if (!heap) {
        printf("Heap is NULL\n");
        return;
    }
    
    if (heap->size == 0) {
        printf("Heap is empty\n");
        return;
    }
    
    printf("\n=== PRIORITY RECOMMENDATIONS (Size: %d) ===\n", heap->size);
    
    for (int i = 0; i < heap->size && i < 10; i++) {  // Show top 10
        printf("[%d] Song ID: %d, Priority: %.2f\n", 
               i + 1, heap->nodes[i].song_id, heap->nodes[i].priority);
    }
    
    if (heap->size > 10) {
        printf("... and %d more\n", heap->size - 10);
    }
    
    printf("==========================================\n\n");
}

/**
 * Get heap size
 * Time Complexity: O(1)
 */
int heap_get_size(MaxHeap* heap) {
    return heap ? heap->size : 0;
}

/**
 * Check if heap is empty
 * Time Complexity: O(1)
 */
bool heap_is_empty(MaxHeap* heap) {
    return !heap || heap->size == 0;
}

/**
 * Destroy heap and free memory
 * Time Complexity: O(1)
 */
void heap_destroy(MaxHeap* heap) {
    if (!heap) return;
    
    if (heap->nodes) {
        free(heap->nodes);
    }
    
    free(heap);
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Heapify up - restore max heap property by moving element up
 * Time Complexity: O(log n)
 */
static void heapify_up(MaxHeap* heap, int index) {
    if (index == 0) return;
    
    int parent = (index - 1) / 2;
    
    if (heap->nodes[index].priority > heap->nodes[parent].priority) {
        swap_nodes(&heap->nodes[index], &heap->nodes[parent]);
        heapify_up(heap, parent);
    }
}

/**
 * Heapify down - restore max heap property by moving element down
 * Time Complexity: O(log n)
 */
static void heapify_down(MaxHeap* heap, int index) {
    int largest = index;
    int left = 2 * index + 1;
    int right = 2 * index + 2;
    
    if (left < heap->size && heap->nodes[left].priority > heap->nodes[largest].priority) {
        largest = left;
    }
    
    if (right < heap->size && heap->nodes[right].priority > heap->nodes[largest].priority) {
        largest = right;
    }
    
    if (largest != index) {
        swap_nodes(&heap->nodes[index], &heap->nodes[largest]);
        heapify_down(heap, largest);
    }
}

/**
 * Swap two heap nodes
 * Time Complexity: O(1)
 */
static void swap_nodes(HeapNode* a, HeapNode* b) {
    HeapNode temp = *a;
    *a = *b;
    *b = temp;
}

/**
 * Find index of song in heap
 * Time Complexity: O(n) - linear search
 * Note: Could be optimized with additional HashMap
 */
static int find_song_index(MaxHeap* heap, int song_id) {
    for (int i = 0; i < heap->size; i++) {
        if (heap->nodes[i].song_id == song_id) {
            return i;
        }
    }
    return -1;
}

/**
 * Queue Implementation
 * 
 * Used for upcoming songs buffer
 * FIFO structure for prefetching and auto-play pipeline
 */

#include "music_queue_core.h"

/**
 * Create a new queue
 * Time Complexity: O(1)
 */
Queue* queue_create() {
    Queue* queue = (Queue*)malloc(sizeof(Queue));
    if (!queue) return NULL;
    
    queue->front = NULL;
    queue->rear = NULL;
    queue->size = 0;
    
    return queue;
}

/**
 * Add song to the end of queue
 * Time Complexity: O(1)
 */
bool queue_enqueue(Queue* queue, int song_id) {
    if (!queue) return false;
    
    QueueNode* new_node = (QueueNode*)malloc(sizeof(QueueNode));
    if (!new_node) return false;
    
    new_node->song_id = song_id;
    new_node->next = NULL;
    
    if (queue->rear) {
        queue->rear->next = new_node;
    } else {
        // First element
        queue->front = new_node;
    }
    
    queue->rear = new_node;
    queue->size++;
    
    return true;
}

/**
 * Remove and return song from front of queue
 * Time Complexity: O(1)
 */
int queue_dequeue(Queue* queue) {
    if (!queue || !queue->front) return -1;
    
    QueueNode* temp = queue->front;
    int song_id = temp->song_id;
    
    queue->front = queue->front->next;
    
    if (!queue->front) {
        // Queue is now empty
        queue->rear = NULL;
    }
    
    free(temp);
    queue->size--;
    
    return song_id;
}

/**
 * Peek at front song without removing
 * Time Complexity: O(1)
 */
int queue_peek(Queue* queue) {
    if (!queue || !queue->front) return -1;
    
    return queue->front->song_id;
}

/**
 * Check if queue is empty
 * Time Complexity: O(1)
 */
bool queue_is_empty(Queue* queue) {
    return !queue || queue->front == NULL;
}

/**
 * Get queue size
 * Time Complexity: O(1)
 */
int queue_get_size(Queue* queue) {
    return queue ? queue->size : 0;
}

/**
 * Clear all songs from queue
 * Time Complexity: O(n)
 */
void queue_clear(Queue* queue) {
    if (!queue) return;
    
    while (queue->front) {
        QueueNode* temp = queue->front;
        queue->front = queue->front->next;
        free(temp);
    }
    
    queue->rear = NULL;
    queue->size = 0;
}

/**
 * Destroy queue and free memory
 * Time Complexity: O(n)
 */
void queue_destroy(Queue* queue) {
    if (!queue) return;
    
    queue_clear(queue);
    free(queue);
}

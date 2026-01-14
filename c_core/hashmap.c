/**
 * HashMap Implementation
 * 
 * Provides O(1) average case lookup for songs by ID
 * Uses chaining for collision resolution
 * Maps song_id -> DLLNode pointer for fast queue operations
 */

#include "music_queue_core.h"

// Helper function prototypes
static unsigned int hash_function(int song_id, int capacity);

/**
 * Create a new hash map
 * Time Complexity: O(n) where n is capacity
 */
HashMap* hashmap_create(int capacity) {
    if (capacity <= 0) return NULL;
    
    HashMap* map = (HashMap*)malloc(sizeof(HashMap));
    if (!map) return NULL;
    
    map->buckets = (HashMapEntry**)calloc(capacity, sizeof(HashMapEntry*));
    if (!map->buckets) {
        free(map);
        return NULL;
    }
    
    map->capacity = capacity;
    map->size = 0;
    
    return map;
}

/**
 * Insert song into hash map
 * Time Complexity: O(1) average case
 */
bool hashmap_insert(HashMap* map, int song_id, DLLNode* node_ptr) {
    if (!map || !node_ptr) return false;
    
    unsigned int index = hash_function(song_id, map->capacity);
    
    // Check if song already exists
    HashMapEntry* current = map->buckets[index];
    while (current) {
        if (current->song_id == song_id) {
            // Update existing entry
            current->node_ptr = node_ptr;
            return true;
        }
        current = current->next;
    }
    
    // Create new entry
    HashMapEntry* new_entry = (HashMapEntry*)malloc(sizeof(HashMapEntry));
    if (!new_entry) return false;
    
    new_entry->song_id = song_id;
    new_entry->node_ptr = node_ptr;
    new_entry->next = map->buckets[index];
    
    map->buckets[index] = new_entry;
    map->size++;
    
    return true;
}

/**
 * Get DLL node pointer for a song
 * Time Complexity: O(1) average case
 */
DLLNode* hashmap_get(HashMap* map, int song_id) {
    if (!map) return NULL;
    
    unsigned int index = hash_function(song_id, map->capacity);
    
    HashMapEntry* current = map->buckets[index];
    while (current) {
        if (current->song_id == song_id) {
            return current->node_ptr;
        }
        current = current->next;
    }
    
    return NULL;
}

/**
 * Remove song from hash map
 * Time Complexity: O(1) average case
 */
bool hashmap_remove(HashMap* map, int song_id) {
    if (!map) return false;
    
    unsigned int index = hash_function(song_id, map->capacity);
    
    HashMapEntry* current = map->buckets[index];
    HashMapEntry* prev = NULL;
    
    while (current) {
        if (current->song_id == song_id) {
            if (prev) {
                prev->next = current->next;
            } else {
                map->buckets[index] = current->next;
            }
            
            free(current);
            map->size--;
            return true;
        }
        
        prev = current;
        current = current->next;
    }
    
    return false;
}

/**
 * Check if song exists in hash map
 * Time Complexity: O(1) average case
 */
bool hashmap_contains(HashMap* map, int song_id) {
    return hashmap_get(map, song_id) != NULL;
}

/**
 * Display hash map contents
 * Time Complexity: O(n + m) where n is capacity, m is number of entries
 */
void hashmap_display(HashMap* map) {
    if (!map) {
        printf("HashMap is NULL\n");
        return;
    }
    
    printf("\n=== HASH MAP (Size: %d, Capacity: %d) ===\n", map->size, map->capacity);
    
    int displayed = 0;
    for (int i = 0; i < map->capacity && displayed < 20; i++) {
        HashMapEntry* current = map->buckets[i];
        
        while (current && displayed < 20) {
            printf("Song ID: %d -> Node Ptr: %p\n", current->song_id, (void*)current->node_ptr);
            current = current->next;
            displayed++;
        }
    }
    
    if (map->size > 20) {
        printf("... and %d more entries\n", map->size - 20);
    }
    
    printf("=====================================\n\n");
}

/**
 * Get hash map size
 * Time Complexity: O(1)
 */
int hashmap_get_size(HashMap* map) {
    return map ? map->size : 0;
}

/**
 * Destroy hash map and free memory
 * Time Complexity: O(n + m)
 */
void hashmap_destroy(HashMap* map) {
    if (!map) return;
    
    for (int i = 0; i < map->capacity; i++) {
        HashMapEntry* current = map->buckets[i];
        
        while (current) {
            HashMapEntry* next = current->next;
            free(current);
            current = next;
        }
    }
    
    free(map->buckets);
    free(map);
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Hash function - simple modulo hash
 * Time Complexity: O(1)
 */
static unsigned int hash_function(int song_id, int capacity) {
    // Use absolute value to handle negative IDs
    unsigned int hash = (unsigned int)(song_id < 0 ? -song_id : song_id);
    
    // Simple modulo hash
    return hash % capacity;
}

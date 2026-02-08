#include "music_queue_core.h"

static void swap_nodes(HeapNode *a, HeapNode *b);
static int find_song_index(MaxHeap *heap, int song_id);

MaxHeap *heap_create(int capacity) {
  if (capacity <= 0)
    return NULL;

  MaxHeap *heap = (MaxHeap *)malloc(sizeof(MaxHeap));
  if (!heap)
    return NULL;

  heap->nodes = (HeapNode *)malloc(sizeof(HeapNode) * capacity);
  if (!heap->nodes) {
    free(heap);
    return NULL;
  }

  heap->size = 0;
  heap->capacity = capacity;

  return heap;
}

void maxheap_print(MaxHeap *heap) {
  HeapNode *array = heap->nodes;
  int i;
  printf("\nMaxheap (Priority Queue): ");
  for (i = 0; i < heap->size; ++i) {
    printf(" %d", array[i].song_id);
  }
}

bool insertHeap(MaxHeap *heap, int song_id, float priority) {
  if (!heap || heap->size >= heap->capacity)
    return false;

  heap->nodes[heap->size].song_id = song_id;
  heap->nodes[heap->size].priority = priority;

  heapifyUp(heap, heap->size);
  heap->size++;

  return true;
}


HeapNode extractMax(MaxHeap *heap) {
  HeapNode invalid = {-1, -1.0f};

  if (!heap || heap->size == 0)
    return invalid;

  HeapNode max = heap->nodes[0];

  heap->nodes[0] = heap->nodes[heap->size - 1];
  heap->size--;

  if (heap->size > 0) {
    heapifyDown(heap, 0);
  }

  return max;
}

HeapNode heap_peek(MaxHeap *heap) {
  HeapNode invalid = {-1, -1.0f};
  if (!heap || heap->size == 0)
    return invalid;
  return heap->nodes[0];
}


void heapifyUp(MaxHeap *heap, int index) {
  if (index <= 0)
    return;

  int parent = (index - 1) / 2;

  if (heap->nodes[index].priority > heap->nodes[parent].priority) {
    swap_nodes(&heap->nodes[index], &heap->nodes[parent]);
    heapifyUp(heap, parent);
  }
}


void heapifyDown(MaxHeap *heap, int index) {
  int largest = index;
  int left = 2 * index + 1;
  int right = 2 * index + 2;

  if (left < heap->size &&
      heap->nodes[left].priority > heap->nodes[largest].priority) {
    largest = left;
  }

  if (right < heap->size &&
      heap->nodes[right].priority > heap->nodes[largest].priority) {
    largest = right;
  }

  if (largest != index) {
    swap_nodes(&heap->nodes[index], &heap->nodes[largest]);
    heapifyDown(heap, largest);
  }
}

bool heap_update_priority(MaxHeap *heap, int song_id, float new_priority) {
  if (!heap)
    return false;

  int index = find_song_index(heap, song_id);
  if (index == -1) {
    return insertHeap(heap, song_id, new_priority);
  }

  float old_priority = heap->nodes[index].priority;
  heap->nodes[index].priority = new_priority;

  if (new_priority > old_priority) {
    heapifyUp(heap, index);
  } else {
    heapifyDown(heap, index);
  }

  return true;
}

void heap_display(MaxHeap *heap) {
  if (!heap || heap->size == 0) {
    printf("Heap is empty\n");
    return;
  }

  printf("\n=== POPULAR SONGS (Size: %d) ===\n", heap->size);
  for (int i = 0; i < heap->size && i < 10; i++) {
    printf("[%d] Song ID: %d, Priority: %.2f\n", i + 1, heap->nodes[i].song_id,
           heap->nodes[i].priority);
  }
  printf("================================\n\n");
}

int heap_get_size(MaxHeap *heap) { return heap ? heap->size : 0; }


bool heap_is_empty(MaxHeap *heap) { return !heap || heap->size == 0; }


void heap_destroy(MaxHeap *heap) {
  if (!heap)
    return;
  if (heap->nodes)
    free(heap->nodes);
  free(heap);
}

// HELPER FUNCTIONS
static void swap_nodes(HeapNode *a, HeapNode *b) {
  HeapNode temp = *a;
  *a = *b;
  *b = temp;
}

static int find_song_index(MaxHeap *heap, int song_id) {
  for (int i = 0; i < heap->size; i++) {
    if (heap->nodes[i].song_id == song_id) {
      return i;
    }
  }
  return -1;
}

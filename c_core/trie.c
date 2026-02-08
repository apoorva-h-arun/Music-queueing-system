/**
 * Trie Implementation
 *
 * Provides prefix-based search for songs and artists
 * Case-insensitive support
 */

#include "music_queue_core.h"
#include <ctype.h>

/**
 * Create a new Trie node
 */
TrieNode *trie_create_node() {
  TrieNode *node = (TrieNode *)malloc(sizeof(TrieNode));
  if (!node)
    return NULL;

  node->isEnd = false;
  node->song_ids = NULL;
  for (int i = 0; i < 26; i++) {
    node->children[i] = NULL;
  }

  return node;
}

/**
 * Initialize a new Trie
 */
TrieNode *trie_create() { return trie_create_node(); }

/**
 * Insert a key into the Trie
 * Maps to lowercase and only allows a-z
 */
void trie_insert(TrieNode *root, const char *key, int song_id) {
  if (!root || !key)
    return;

  TrieNode *current = root;
  for (int i = 0; key[i] != '\0'; i++) {
    char c = tolower(key[i]);
    if (c < 'a' || c > 'z')
      continue; // Skip non-alphabetic characters

    int index = c - 'a';
    if (!current->children[index]) {
      current->children[index] = trie_create_node();
    }
    current = current->children[index];
  }

  current->isEnd = true;

  // Add song_id to the list in this node
  SongIdNode *new_id = (SongIdNode *)malloc(sizeof(SongIdNode));
  if (new_id) {
    new_id->song_id = song_id;
    new_id->next = current->song_ids;
    current->song_ids = new_id;
  }
}

/**
 * Search for a prefix in the Trie
 * Returns the SongIdNode list of the prefix node
 */
SongIdNode *trie_search_prefix(TrieNode *root, const char *prefix) {
  if (!root || !prefix)
    return NULL;

  TrieNode *current = root;
  for (int i = 0; prefix[i] != '\0'; i++) {
    char c = tolower(prefix[i]);
    if (c < 'a' || c > 'z')
      continue;

    int index = c - 'a';
    if (!current->children[index]) {
      return NULL;
    }
    current = current->children[index];
  }

  return current->song_ids;
}

/**
 * Collect all song IDs from a node and its children (Helper)
 */
static void collect_ids(TrieNode *node, SongIdNode **results) {
  if (!node)
    return;

  // Add IDs from this node
  SongIdNode *current_id = node->song_ids;
  while (current_id) {
    // Create a copy to avoid pointer issues with Trie destruction
    SongIdNode *copy = (SongIdNode *)malloc(sizeof(SongIdNode));
    if (copy) {
      copy->song_id = current_id->song_id;
      copy->next = *results;
      *results = copy;
    }
    current_id = current_id->next;
  }

  // Recurse for children
  for (int i = 0; i < 26; i++) {
    if (node->children[i]) {
      collect_ids(node->children[i], results);
    }
  }
}

/**
 * Display results (simplified for current requirements - returns all matching
 * IDs under prefix)
 */
void trie_display_results(TrieNode *root, const char *prefix) {
  // In a real implementation, this might print to stdout.
  // For our API, search_prefix is more useful.
  printf("Trie search results for: %s\n", prefix);
}

/**
 * Destroy the Trie and free memory
 */
void trie_destroy(TrieNode *root) {
  if (!root)
    return;

  for (int i = 0; i < 26; i++) {
    if (root->children[i]) {
      trie_destroy(root->children[i]);
    }
  }

  // Free song ID list
  SongIdNode *current = root->song_ids;
  while (current) {
    SongIdNode *next = current->next;
    free(current);
    current = next;
  }

  free(root);
}

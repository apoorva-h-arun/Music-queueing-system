#include "music_queue_core.h"
#include <ctype.h>

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


void trie_print(TrieNode *trie, char *word, int k) {
  if (word == NULL) {
    word = (char*)malloc(50);
  }
  if (!trie)
    return;
  for (int i = 0; i < 26; ++i) {
    if (trie->children[i]) {
      word[k] = i + 'a';
      trie_print(trie->children[i], word, k + 1);
    }
    else if (trie->isEnd) {
      word[k] = '\0';
      printf(" %s", word);
      return;
    }
  }
}


TrieNode *trie_create() { return trie_create_node(); }


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

static void collect_ids(TrieNode *node, SongIdNode **results) {
  if (!node)
    return;

  SongIdNode *current_id = node->song_ids;
  while (current_id) {
    SongIdNode *copy = (SongIdNode *)malloc(sizeof(SongIdNode));
    if (copy) {
      copy->song_id = current_id->song_id;
      copy->next = *results;
      *results = copy;
    }
    current_id = current_id->next;
  }

  for (int i = 0; i < 26; i++) {
    if (node->children[i]) {
      collect_ids(node->children[i], results);
    }
  }
}


void trie_display_results(TrieNode *root, const char *prefix) {
  printf("Trie search results for: %s\n", prefix);
}

void trie_destroy(TrieNode *root) {
  if (!root)
    return;

  for (int i = 0; i < 26; i++) {
    if (root->children[i]) {
      trie_destroy(root->children[i]);
    }
  }

  SongIdNode *current = root->song_ids;
  while (current) {
    SongIdNode *next = current->next;
    free(current);
    current = next;
  }

  free(root);
}

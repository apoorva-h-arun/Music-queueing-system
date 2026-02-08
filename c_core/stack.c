/**
 * Stack Implementation
 * 
 * Used for undo/redo functionality
 * Stores operation history for reversible actions
 */

#include "music_queue_core.h"

/**
 * Create a new stack
 * Time Complexity: O(1)
 */
Stack* stack_create() {
    Stack* stack = (Stack*)malloc(sizeof(Stack));
    if (!stack) return NULL;
    
    stack->top = NULL;
    stack->size = 0;
    
    return stack;
}

/**
 * Push an operation onto the stack
 * Time Complexity: O(1)
 */
bool stack_push(Stack* stack, Operation op) {
    if (!stack) return false;
    
    StackNode* new_node = (StackNode*)malloc(sizeof(StackNode));
    if (!new_node) return false;
    
    new_node->op = op;
    new_node->next = stack->top;
    stack->top = new_node;
    stack->size++;
    
    return true;
}

/**
 * Pop an operation from the stack
 * Time Complexity: O(1)
 */
Operation stack_pop(Stack* stack) {
    Operation invalid = {OP_ADD, -1, -1, -1.0f};
    
    if (!stack || !stack->top) return invalid;
    
    StackNode* temp = stack->top;
    Operation op = temp->op;
    
    stack->top = stack->top->next;
    free(temp);
    stack->size--;
    
    return op;
}

/**
 * Peek at top operation without removing
 * Time Complexity: O(1)
 */
Operation stack_peek(Stack* stack) {
    Operation invalid = {OP_ADD, -1, -1, -1.0f};
    
    if (!stack || !stack->top) return invalid;
    
    return stack->top->op;
}

/**
 * Check if stack is empty
 * Time Complexity: O(1)
 */
bool stack_is_empty(Stack* stack) {
    return !stack || stack->top == NULL;
}

/**
 * Get stack size
 * Time Complexity: O(1)
 */
int stack_get_size(Stack* stack) {
    return stack ? stack->size : 0;
}

/**
 * Clear all operations from stack
 * Time Complexity: O(n)
 */
void stack_clear(Stack* stack) {
    if (!stack) return;
    
    while (stack->top) {
        StackNode* temp = stack->top;
        stack->top = stack->top->next;
        free(temp);
    }
    
    stack->size = 0;
}

/**
 * Destroy stack and free memory
 * Time Complexity: O(n)
 */
void stack_destroy(Stack* stack) {
    if (!stack) return;
    
    stack_clear(stack);
    free(stack);
}

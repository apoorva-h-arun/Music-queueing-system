# Music Queue Core - Makefile
# Cross-platform build configuration

# Detect OS
UNAME_S := $(shell uname -s)

# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -Wextra -O2 -fPIC

# Source files
SOURCES = doubly_linked_list.c max_heap.c stack.c queue.c hashmap.c manager.c

# Output directory
BUILD_DIR = build

# Platform-specific settings
ifeq ($(UNAME_S),Linux)
    TARGET = $(BUILD_DIR)/libmusicqueue.so
    LDFLAGS = -shared
endif

ifeq ($(UNAME_S),Darwin)
    TARGET = $(BUILD_DIR)/libmusicqueue.dylib
    LDFLAGS = -dynamiclib
endif

# Windows (MinGW)
ifeq ($(OS),Windows_NT)
    TARGET = $(BUILD_DIR)/musicqueue.dll
    LDFLAGS = -shared -Wl,--out-implib,$(BUILD_DIR)/libmusicqueue.a
    CC = gcc
endif

# Default target
all: $(TARGET)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Build shared library
$(TARGET): $(SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(SOURCES)
	@echo "Build successful: $@"

# Debug build
debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	@echo "Clean complete"

# Rebuild
rebuild: clean all

# Help
help:
	@echo "Music Queue Core - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Build shared library (default)"
	@echo "  debug   - Build with debug symbols"
	@echo "  clean   - Remove build artifacts"
	@echo "  rebuild - Clean and build"
	@echo "  help    - Show this help message"
	@echo ""
	@echo "Platform: $(UNAME_S)"
	@echo "Target:   $(TARGET)"

.PHONY: all debug clean rebuild help

#!/bin/bash

# Music Queue Core - Build Script for Linux/macOS
# Automatically detects OS and compiles with appropriate flags

set -e  # Exit on error

echo "==================================="
echo "Music Queue Core - Build Script"
echo "==================================="
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"

# Create build directory
mkdir -p build

# Set compiler and flags
CC=gcc
CFLAGS="-Wall -Wextra -O2 -fPIC"
SOURCES="doubly_linked_list.c max_heap.c stack.c queue.c hashmap.c manager.c"

# Platform-specific compilation
if [ "$OS_TYPE" = "Linux" ]; then
    echo "Building for Linux..."
    TARGET="build/libmusicqueue.so"
    LDFLAGS="-shared"
    
elif [ "$OS_TYPE" = "Darwin" ]; then
    echo "Building for macOS..."
    TARGET="build/libmusicqueue.dylib"
    LDFLAGS="-dynamiclib"
    
else
    echo "Unsupported OS: $OS_TYPE"
    echo "Please use Windows build.bat for Windows"
    exit 1
fi

# Compile
echo ""
echo "Compiling..."
echo "Command: $CC $CFLAGS $LDFLAGS -o $TARGET $SOURCES"
echo ""

$CC $CFLAGS $LDFLAGS -o $TARGET $SOURCES

# Check if compilation was successful
if [ -f "$TARGET" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "Output: $TARGET"
    echo ""
    ls -lh $TARGET
    echo ""
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi

echo "==================================="
echo "Build complete"
echo "==================================="

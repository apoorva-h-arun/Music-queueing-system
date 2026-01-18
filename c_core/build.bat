@echo off
REM Music Queue Core - Build Script for Windows
REM Supports both MinGW and MSVC compilers

echo ===================================
echo Music Queue Core - Build Script
echo ===================================
echo.

REM Create build directory
if not exist build mkdir build

REM Check for MinGW
where gcc >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Detected: MinGW GCC
    goto :build_mingw
)

REM Check for MSVC
where cl >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Detected: Microsoft Visual C++
    goto :build_msvc
)

REM No compiler found
echo ERROR: No compiler found!
echo.
echo Please install one of the following:
echo   - MinGW: choco install mingw
echo   - Visual Studio with C++ tools
echo.
exit /b 1

:build_mingw
echo.
echo Building with MinGW...
echo.

gcc -Wall -Wextra -O2 -shared -o build\musicqueue.dll ^
    doubly_linked_list.c max_heap.c stack.c queue.c trie.c manager.c ^
    -Wl,--out-implib,build\libmusicqueue.a

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed!
    exit /b 1
)

echo.
echo Build successful!
echo Output: build\musicqueue.dll
dir build\musicqueue.dll
goto :end

:build_msvc
echo.
echo Building with MSVC...
echo.

cl /LD /O2 /Fe:build\musicqueue.dll ^
    doubly_linked_list.c max_heap.c stack.c queue.c trie.c manager.c

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed!
    exit /b 1
)

echo.
echo Build successful!
echo Output: build\musicqueue.dll
dir build\musicqueue.dll
goto :end

:end
echo.
echo Build complete
echo ===================================
echo.
exit /b 0

#!/bin/bash

# Windows Executable Builder for Talki App (One Directory Version)
# This script creates Windows executables from Linux using PyInstaller

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="talki-app"
BUILD_MODE="onedir"  # Options: onefile, onedir
TARGET_ARCH="64bit"
OUTPUT_DIR="dist"
WORK_DIR="build"

# Check if we're in the right directory
if [ ! -f "talki_app/__main__.py" ]; then
    echo -e "${RED}Error: This script must be run from the project root directory${NC}"
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
fi

# Check if MinGW-w64 is installed (for Windows cross-compilation)
if ! command -v x86_64-w64-mingw32-g++ &> /dev/null; then
    echo -e "${YELLOW}MinGW-w64 not found. Installing...${NC}"
    sudo apt-get update
sudo apt-get install -y mingw-w64
fi

# Set PATH for MinGW
export PATH=/usr/x86_64-w64-mingw32/bin:$PATH

echo -e "${GREEN}Building Windows executable (One Directory) for Talki App...${NC}"
echo -e "${YELLOW}Mode: $BUILD_MODE | Architecture: $TARGET_ARCH${NC}"

# Clean previous builds
if [ -d "$OUTPUT_DIR" ]; then
    echo -e "${YELLOW}Cleaning previous build...${NC}"
    rm -rf "$OUTPUT_DIR"
fi

if [ -d "$WORK_DIR" ]; then
    echo -e "${YELLOW}Cleaning previous work directory...${NC}"
    rm -rf "$WORK_DIR"
fi

# Build command
PYINSTALLER_CMD="pyinstaller --target-arch=$TARGET_ARCH"

case $BUILD_MODE in
    "onefile")
        PYINSTALLER_CMD="$PYINSTALLER_CMD --onefile --windowed"
        ;;
    "onedir")
        PYINSTALLER_CMD="$PYINSTALLER_CMD --onedir --windowed"
        ;;
    *)
        echo -e "${RED}Invalid build mode: $BUILD_MODE${NC}"
        echo -e "${YELLOW}Valid options: onefile, onedir${NC}"
        exit 1
        ;;
esac

# Add common options
PYINSTALLER_CMD="$PYINSTALLER_CMD --name=$APP_NAME"
PYINSTALLER_CMD="$PYINSTALLER_CMD --distpath=$OUTPUT_DIR"
PYINSTALLER_CMD="$PYINSTALLER_CMD --workpath=$WORK_DIR"

# Add hidden imports for PyQt6 and other dependencies
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=PyQt6"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=pynput"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=mouse"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=numpy"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=sounddevice"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=librosa"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=faster-whisper"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=torch"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=transformers"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=tokenizers"
PYINSTALLER_CMD="$PYINSTALLER_CMD --hidden-import=ctranslate2"

# Add the main script
PYINSTALLER_CMD="$PYINSTALLER_CMD talki_app/__main__.py"

echo -e "${GREEN}Executing PyInstaller command:${NC}"
echo "$PYINSTALLER_CMD"

# Execute the build
$PYINSTALLER_CMD

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${YELLOW}Output location: $OUTPUT_DIR/$APP_NAME/$APP_NAME.exe${NC}"

# Check if the executable was created
if [ -f "$OUTPUT_DIR/$APP_NAME/$APP_NAME.exe" ]; then
    echo -e "${GREEN}Executable created: $OUTPUT_DIR/$APP_NAME/$APP_NAME.exe${NC}"
    echo -e "${YELLOW}Size: $(du -h "$OUTPUT_DIR/$APP_NAME/$APP_NAME.exe" | cut -f1)${NC}"
    
    # Create a simple test script
    cat > "$OUTPUT_DIR/$APP_NAME/test_run.sh" << 'EOF'
#!/bin/bash
echo "Testing Windows executable (One Directory)..."
echo "This is a test script to verify the executable works."
echo "The executable $APP_NAME.exe should be in this directory."
echo "To run it on Windows, use: $APP_NAME.exe"
echo "To transfer to Windows, use: scp -r $APP_NAME user@windows-machine:/path/to/destination"
EOF
    chmod +x "$OUTPUT_DIR/$APP_NAME/test_run.sh"
    
    echo -e "${GREEN}Test script created: $OUTPUT_DIR/$APP_NAME/test_run.sh${NC}"
else
    echo -e "${RED}Error: Executable not found at $OUTPUT_DIR/$APP_NAME/$APP_NAME.exe${NC}"
    exit 1
fi

echo -e "${GREEN}Windows executable (One Directory) build process completed!${NC}"
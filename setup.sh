#!/bin/bash
# 2webm Setup Script for Linux/Mac
echo "2webm - Setup Utility"
echo "==========================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_DIR="$SCRIPT_DIR/python"
FFMPEG_DIR="$SCRIPT_DIR/ffmpeg"
FFMPEG_BIN_DIR="$SCRIPT_DIR/ffmpeg/bin"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Check if running on macOS or Linux
if [[ "$(uname)" == "Darwin" ]]; then
    PLATFORM="macos"
    ARCH="$(uname -m)"
    if [[ "$ARCH" == "arm64" ]]; then
        PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.9.18+20240224-aarch64-apple-darwin-install_only.tar.gz"
        FFMPEG_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    else
        PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.9.18+20240224-x86_64-apple-darwin-install_only.tar.gz"
        FFMPEG_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    fi
else
    PLATFORM="linux"
    ARCH="$(uname -m)"
    if [[ "$ARCH" == "x86_64" ]]; then
        PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.9.18+20240224-x86_64-unknown-linux-gnu-install_only.tar.gz"
        FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.9.18+20240224-aarch64-unknown-linux-gnu-install_only.tar.gz"
        FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
    else
        echo "Unsupported architecture: $ARCH"
        exit 1
    fi
fi

# Create directories if they don't exist
mkdir -p "$PYTHON_DIR" "$FFMPEG_BIN_DIR" "$OUTPUT_DIR"

# Download and extract Python
echo "Downloading Python standalone package..."
PYTHON_ARCHIVE="$SCRIPT_DIR/python_standalone.tar.gz"
if command -v curl &> /dev/null; then
    curl -L "$PYTHON_URL" -o "$PYTHON_ARCHIVE"
elif command -v wget &> /dev/null; then
    wget "$PYTHON_URL" -O "$PYTHON_ARCHIVE"
else
    echo "Error: Neither curl nor wget is installed. Please install one of them and try again."
    exit 1
fi

echo "Extracting Python..."
tar -xzf "$PYTHON_ARCHIVE" -C "$PYTHON_DIR" --strip-components=1
rm "$PYTHON_ARCHIVE"

# Make scripts executable
chmod +x "$PYTHON_DIR/bin/python3"
echo "Python extracted successfully."

# Set up symlink for python3 -> python (if on Linux)
if [[ "$PLATFORM" == "linux" ]]; then
    ln -sf "$PYTHON_DIR/bin/python3" "$PYTHON_DIR/bin/python"
fi

# Download and extract FFmpeg
echo "Downloading FFmpeg..."
FFMPEG_ARCHIVE="$SCRIPT_DIR/ffmpeg_archive"

if command -v curl &> /dev/null; then
    curl -L "$FFMPEG_URL" -o "$FFMPEG_ARCHIVE"
elif command -v wget &> /dev/null; then
    wget "$FFMPEG_URL" -O "$FFMPEG_ARCHIVE"
else
    echo "Error: Neither curl nor wget is installed. Please install one of them and try again."
    exit 1
fi

echo "Extracting FFmpeg..."
if [[ "$PLATFORM" == "macos" ]]; then
    # macOS typically provides zip files
    unzip -q "$FFMPEG_ARCHIVE" -d "$SCRIPT_DIR/ffmpeg_temp"
    # Find and move the ffmpeg binary
    find "$SCRIPT_DIR/ffmpeg_temp" -name "ffmpeg" -exec cp {} "$FFMPEG_BIN_DIR/" \;
    chmod +x "$FFMPEG_BIN_DIR/ffmpeg"
else
    # Linux typically provides tar.xz files
    mkdir -p "$SCRIPT_DIR/ffmpeg_temp"
    tar -xf "$FFMPEG_ARCHIVE" -C "$SCRIPT_DIR/ffmpeg_temp"
    # Find and move the ffmpeg binary
    find "$SCRIPT_DIR/ffmpeg_temp" -name "ffmpeg" -exec cp {} "$FFMPEG_BIN_DIR/" \;
    chmod +x "$FFMPEG_BIN_DIR/ffmpeg"
fi

# Clean up temporary files
rm -rf "$FFMPEG_ARCHIVE" "$SCRIPT_DIR/ffmpeg_temp"

echo "FFmpeg extracted successfully."

# Make the launcher script executable
chmod +x "$SCRIPT_DIR/2webm.sh"

echo ""
echo "Setup complete!"
echo "Run ./2webm.sh to start the application"
read -p "Press Enter to continue..." 
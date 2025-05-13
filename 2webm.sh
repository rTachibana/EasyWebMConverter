#!/bin/bash
# 2webm - MP4 to WebM Encoder (Linux/Mac version)
echo "2webm - MP4 to WebM Encoder"
echo "==========================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# ディレクトリの存在確認とセットアップの自動実行
NEEDS_SETUP=0

# Check for Python
if [ ! -f "$SCRIPT_DIR/python/bin/python3" ]; then
    echo "Python not found. Setup required."
    NEEDS_SETUP=1
fi

# Check for FFmpeg
if [ ! -f "$SCRIPT_DIR/ffmpeg/bin/ffmpeg" ]; then
    echo "FFmpeg not found. Setup required."
    NEEDS_SETUP=1
fi

# セットアップの自動実行
if [ $NEEDS_SETUP -eq 1 ]; then
    echo "Running automatic setup..."
    echo "This may take a few minutes. Please wait..."
    echo ""
    
    # セットアップスクリプトに実行権限を付与
    chmod +x "$SCRIPT_DIR/setup.sh"
    
    # セットアップを実行
    "$SCRIPT_DIR/setup.sh"
    
    # セットアップ後に再度存在確認
    SETUP_FAILED=0
    if [ ! -f "$SCRIPT_DIR/python/bin/python3" ]; then
        SETUP_FAILED=1
    fi
    if [ ! -f "$SCRIPT_DIR/ffmpeg/bin/ffmpeg" ]; then
        SETUP_FAILED=1
    fi
    
    if [ $SETUP_FAILED -eq 1 ]; then
        echo ""
        echo "Setup failed to install required components."
        echo "Please try running setup.sh manually."
        read -p "Press Enter to continue..."
        exit 1
    fi
    
    echo ""
    echo "Setup completed successfully."
    echo ""
fi

# Launch the application
echo "Launching application..."
"$SCRIPT_DIR/python/bin/python3" "$SCRIPT_DIR/src/main.py"

# If there was an error
if [ $? -ne 0 ]; then
    echo "Failed to start the application."
    echo "Run setup.sh to reinstall."
    read -p "Press Enter to continue..."
fi 
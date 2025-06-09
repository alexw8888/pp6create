#!/bin/bash
# Build script for ProPresenter 6 Generator CLI macOS app

set -e  # Exit on error

echo "🔨 Building ProPresenter 6 Generator CLI App..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to script directory
cd "$SCRIPT_DIR"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.log *.spec

# Use system Python (which works reliably)
PYTHON="/usr/bin/python3"
PYINSTALLER="/Users/alex/Library/Python/3.9/bin/pyinstaller"

# Check if PyInstaller is available
if [ ! -f "$PYINSTALLER" ]; then
    echo "📦 Installing PyInstaller for system Python..."
    $PYTHON -m pip install --user pyinstaller
    PYINSTALLER="/Users/alex/Library/Python/3.9/bin/pyinstaller"
fi

# Check dependencies
echo "🔍 Checking dependencies..."
$PYTHON -c "
try:
    import PIL, lxml, pptx
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    print('Installing missing dependencies...')
    import subprocess
    subprocess.run(['$PYTHON', '-m', 'pip', 'install', '--user', 'Pillow', 'python-pptx', 'python-dotenv', 'lxml'])
"

# CLI apps don't need icons - removed icon creation

# Build the CLI app
echo "🏗️  Building CLI application..."

# No icon needed for CLI app

# Build with PyInstaller
$PYINSTALLER \
    --name "pp6generator" \
    --onefile \
    --console \
    --clean \
    --noconfirm \
    --add-data "$PROJECT_ROOT/generate_presentation.py:." \
    --add-data "$PROJECT_ROOT/generate_pp6_doc.py:." \
    --add-data "$PROJECT_ROOT/generate_pp6_playlist.py:." \
    --add-data "$PROJECT_ROOT/pptx_generator.py:." \
    --add-data "$PROJECT_ROOT/pp6_xml_elements.py:." \
    --add-data "$PROJECT_ROOT/pp6_color_utils.py:." \
    --add-data "$PROJECT_ROOT/pp6_song_parser.py:." \
    --hidden-import PIL \
    --hidden-import PIL.Image \
    --hidden-import pptx \
    --hidden-import lxml \
    --hidden-import lxml.etree \
    --hidden-import dotenv \
    --hidden-import json \
    --hidden-import pathlib \
    --hidden-import argparse \
    --hidden-import uuid \
    --hidden-import base64 \
    --hidden-import xml.etree.ElementTree \
    --hidden-import re \
    --hidden-import datetime \
    pp6_cli_app.py

# Check if build was successful
if [ -f "dist/pp6generator" ]; then
    echo "✅ Build successful!"
    echo "📍 CLI app location: $SCRIPT_DIR/dist/pp6generator"
    
    # Get app size
    APP_SIZE=$(du -sh "dist/pp6generator" | cut -f1)
    echo "📊 CLI app size: $APP_SIZE"
    
    # Make executable
    chmod +x "dist/pp6generator"
    
    # Test basic functionality
    echo "🧪 Testing CLI app..."
    if ./dist/pp6generator --help > /dev/null 2>&1; then
        echo "✅ CLI app responds to --help"
    else
        echo "⚠️ CLI app may have issues"
    fi
    
else
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi

echo ""
echo "🎉 CLI Build completed successfully!"
echo ""
echo "To test the CLI app:"
echo "  ./dist/pp6generator --help"
echo ""
echo "To install globally (optional):"
echo "  sudo cp dist/pp6generator /usr/local/bin/"
echo ""
echo "To create distribution package:"
echo "  cp -r dist/pp6generator ../source_materials ."
echo "  zip -r pp6generator-cli.zip pp6generator source_materials/"
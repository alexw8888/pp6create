#!/usr/bin/env python3
"""
ProPresenter 6 Playlist Generator - macOS CLI Application
A command-line interface for generating PP6 playlists and PowerPoint presentations
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the main generation function
from generate_presentation import main as generate_presentation_main


def get_executable_dir():
    """Get directory where the executable is located"""
    if getattr(sys, 'frozen', False):
        # PyInstaller executable
        return os.path.dirname(sys.executable)
    else:
        # Development mode
        return os.path.dirname(os.path.abspath(__file__))


def show_help():
    """Show enhanced help message"""
    print("""
ProPresenter 6 Playlist Generator v1.0.0

USAGE:
    pp6generator [options]

OPTIONS:
    --source PATH        Source directory containing materials (default: source_materials next to executable)
    --format FORMAT      Output format: 'pro6', 'pptx', or 'both' (default: both)
    --output NAME        Output file name (without extension)
    --width WIDTH        Slide width in pixels (default: 1024)
    --height HEIGHT      Slide height in pixels (default: 768)
    --font-size SIZE     Font size for text
    --lines-per-slide N  Lines per slide for songs
    --title TITLE        Presentation title
    --help, -h           Show this help message

EXAMPLES:
    # Generate both formats from default folder
    pp6generator
    
    # Generate from specific folder
    pp6generator --source /path/to/materials
    
    # Generate only PowerPoint
    pp6generator --format pptx
    
    # Generate with custom output name
    pp6generator --output "Sunday Service"
    
    # Generate with custom dimensions
    pp6generator --width 1920 --height 1080

INPUT FOLDER STRUCTURE:
    Place source_materials folder next to pp6generator executable:
    
    source_materials/
    ├── 1-worship/
    │   ├── 1.jpg
    │   └── 1.json
    ├── 2-song1/
    │   ├── song1.txt
    │   └── bg2.png
    └── 3-sermon/
        ├── slide1.jpg
        └── slide2.jpg

OUTPUT:
    - GeneratedPlaylist.pro6plx (ProPresenter 6 playlist)
    - GeneratedPresentation.pptx (PowerPoint presentation)
    
    Files are created next to the pp6generator executable.

For more information, visit: https://github.com/yourcompany/pp6generator
""")


def main():
    """Main CLI entry point"""
    # Always change to executable directory for consistent output location
    exe_dir = get_executable_dir()
    original_cwd = os.getcwd()
    os.chdir(exe_dir)
    
    try:
        # Handle special cases first
        if len(sys.argv) == 1:
            # No arguments - use default source_materials next to executable
            default_source = os.path.join(exe_dir, 'source_materials')
            
            if os.path.exists(default_source):
                sys.argv.extend(['--source', default_source])
            else:
                print(f"❌ No source_materials folder found at: {default_source}")
                print(f"💡 Place source_materials folder next to pp6generator executable")
                print(f"💡 Or run: pp6generator --source /path/to/your/materials")
                return 1
        
        # Check for help flag
        for arg in sys.argv[1:]:
            if arg in ['--help', '-h']:
                show_help()
                return 0
        
        # Enhance error messages
        try:
            result = generate_presentation_main()
            print(f"\n📍 Output files created in: {exe_dir}")
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"💡 Run 'pp6generator --help' for usage information")
            return 1
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


if __name__ == '__main__':
    sys.exit(main())
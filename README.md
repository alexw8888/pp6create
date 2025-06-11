# Unified Presentation Generator

A Python-based tool that generates presentations in multiple formats from source materials. Supports both ProPresenter 6 (.pro6) and PowerPoint (.pptx) formats.

## Features

- **Multi-format Support**: Generate ProPresenter 6 and/or PowerPoint presentations from the same source
- **Song Support**: Automatically detect and process songs with arrangements
- **JSON Configuration**: Precise text positioning using JSON files
- **Media Support**: Images (PNG, JPG, JPEG) and videos (MP4)
- **Flexible Input**: Process directories of images, text files, or JSON configurations
- **Playlist Generation**: Create ProPresenter 6 playlists with media management

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Process All Subdirectories (Complete Presentation)
```bash
# Process all subdirectories under source_materials (default)
python generate_presentation.py

# Creates:
# - GeneratedPlaylist.pro6plx (ProPresenter 6 playlist with all content)
# - GeneratedPresentation.pptx (PowerPoint with all slides)

# Or explicitly specify source:
python generate_presentation.py --source source_materials
```

### Process Single Directory
```bash
# Generate both formats (default)
python generate_presentation.py --source source_materials/1

# Generate ProPresenter 6 only
python generate_presentation.py --source source_materials/1 --format pro6

# Generate PowerPoint only
python generate_presentation.py --source source_materials/1 --format pptx
```

## Source Materials Directory Structure

The generator supports three different processing modes based on your directory structure:

### Mode 1: Process All Subdirectories (Default)
When you run the generator without specifying a source or point it to the main `source_materials` directory, it processes all subdirectories in numbered order:

```bash
python generate_presentation.py
# OR
python generate_presentation.py --source source_materials
```

Directory structure:
```
source_materials/
├── 1-worship-countdown/
│   ├── 1.jpg
│   └── 2.jpg
├── 2-song1/
│   ├── song1.txt
│   └── background.png
├── 3-sermon/
│   ├── slides.json
│   └── logo.png
└── 4-announcement/
    └── announcement.jpg
```

This creates:
- `GeneratedPlaylist.pro6plx` - Complete ProPresenter 6 playlist with all content
- `GeneratedPresentation.pptx` - PowerPoint with all slides from all directories

### Mode 2: Process Single Directory
Specify a single subdirectory to process only that content:

```bash
python generate_presentation.py --source source_materials/2-song1
```

This creates individual presentation files:
- `GeneratedPresentation.pro6` (single document, not playlist)
- `GeneratedPresentation.pptx`

### Mode 3: Process Direct Files
Point directly to a file for single-file processing:

```bash
python generate_presentation.py --source source_materials/2-song1/song1.txt --type song
```

## Source Material Types & Processing Rules

### 1. Image-Only Directories
When a directory contains only image files (PNG, JPG, JPEG):

```
source_materials/1-worship-countdown/
├── 1.jpg
├── 2.jpg
└── 3.png
```

**Processing Rules:**
- Images are sorted naturally (1.jpg, 2.jpg, 10.jpg, not 1.jpg, 10.jpg, 2.jpg)
- Each image becomes a full-screen slide
- No text overlay is added
- Images maintain aspect ratio

### 2. Song Text Files
Text files with section markers and arrangements:

```
source_materials/2-song1/
├── song1.txt
└── background.png  # Optional background
```

Song file format:
```
V1
Amazing grace, how sweet the sound
That saved a wretch like me
V2
I once was lost but now am found
Was blind, but now I see
C1
How great is our God
Sing with me, how great is our God
Arrangement
V1 C1 V2 C1 C1
```

**Processing Rules:**
- Detects songs by presence of "Arrangement" line
- Sections: V=Verse (Blue), C=Chorus (Red), B=Bridge (White)
- Text breaks into slides based on `PAGE_BREAK_EVERY` (default: 2 lines)
- Background image used if present in same directory
- Creates grouped slides with arrangement metadata

### 3. JSON + Media Combinations
For precise text positioning and formatting:

```
source_materials/3-announcement/
├── slide1.json
├── slide1.png    # Matched by base name
├── slide2.json
└── slide2.jpg    # Matched by base name
```

JSON format:
```json
{
    "text": "日期: 7/6, 18/7",
    "x": 231,
    "y": 653,
    "fontSize": 59,
    "fontFamily": "Arial",
    "pptxFontScale": 0.4,     // PowerPoint font = 59 * 0.4 = 23.6
    "pptxXoffset": -50,       // Adjust PowerPoint X position
    "pptxYoffset": -100,      // Adjust PowerPoint Y position
    "media": "custom_bg.png"  // Optional: override base name matching
}
```

**Processing Rules:**
- JSON files must have corresponding media files (matched by base name)
- If `"media"` field specified in JSON, that file is used instead
- Text positioned at exact coordinates
- PowerPoint uses adjusted positioning and scaling
- Multiple text entries supported in single JSON

### 4. Content Directory Processing

Each source directory should contain a single type of content. The generator uses a priority-based system to determine how to process files:


**Processing Priority:**
1. **JSON Priority** - If any `.json` files exist, ONLY JSON configurations and their associated media are processed
2. **Song Priority** - If no JSON files but text files with "Arrangement" lines exist, ONLY the first song is processed
3. **Media Only** - If no JSON or song files, only image/video files are processed

**Important**: Mixed content types in the same directory will result in some files being ignored. For complex presentations, use separate directories for each content type and let the playlist generator combine them.


## Processing Examples

### Example 1: Complete Worship Service
```
source_materials/
├── 1-countdown/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── 3.jpg
├── 2-welcome/
│   ├── welcome.json
│   └── welcome_bg.png
├── 3-song1/
│   ├── amazing_grace.txt
│   └── hymn_bg.png
├── 4-sermon/
│   ├── sermon_title.json
│   ├── sermon_title.png
│   ├── point1.json
│   ├── point1.png
│   ├── point2.json
│   └── point2.png
├── 5-song2/
│   └── how_great.txt
└── 6-closing/
    └── closing.jpg
```

Run: `python generate_presentation.py`
Output: Complete service playlist with all elements

### Example 2: Single Song
```bash
python generate_presentation.py --source source_materials/3-song1 --output "AmazingGrace"
```
Output: `AmazingGrace.pro6` and `AmazingGrace.pptx`

### Example 3: Announcement Slides
```bash
python generate_presentation.py --source announcements/ --format pptx --output "WeeklyAnnouncements"
```
Output: `WeeklyAnnouncements.pptx` only

## Advanced Usage

### Custom Output Names
```bash
# For all subdirectories
python generate_presentation.py --source source_materials --output "SundayService"
# Creates: SundayService.pro6plx and SundayService.pptx

# For single directory
python generate_presentation.py --source source_materials/3 --output "MySong"
# Creates: MySong.pro6 and MySong.pptx
```

### Custom Dimensions (both formats)
```bash
# Applies to both ProPresenter 6 and PowerPoint
python generate_presentation.py --source source_materials/1 --format both --width 1920 --height 1080
```

### Custom Font Size (PowerPoint only)
```bash
# Note: --font-size only applies to PowerPoint. ProPresenter 6 uses font sizes from JSON configs
python generate_presentation.py --source source_materials/1 --format pptx --font-size 48
```

### Lines Per Slide (for songs - both formats)
```bash
# Applies to both ProPresenter 6 and PowerPoint song generation
python generate_presentation.py --source source_materials/3 --format both --lines-per-slide 6
```

### Custom Title (for ProPresenter 6 songs)
```bash
# Set a custom title for song documents
python generate_presentation.py --source songs/amazing_grace.txt --format pro6 --title "Amazing Grace"

# The title appears in ProPresenter's interface and document metadata
# If not specified, uses the output filename or directory name
```

## Environment Variables

Create a `.env` file to set defaults:

```env
PAGE_BREAK_EVERY=2

# below are powerpoint only
WIDTH=1024
HEIGHT=768
FONT_SIZE=40
FONT_FAMILY=Arial
FONT_COLOR=0xFFFFFF
TOP_MARGIN=100
ADD_TEXT_SHADOW=true
```

## Output Files

- **ProPresenter 6**: Creates `.pro6` XML files
- **PowerPoint**: Creates `.pptx` files
- **Playlists**: Creates `.pro6pl` and `.pro6plx` (zipped) files

## License

This project is licensed under the MIT License.
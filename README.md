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

## Source Material Types

### 1. Image Directories
Place images in a directory. They'll be added as slides in order:
```
source_materials/1-worship-countdown/
├── 1.jpg
└── 2.jpg
```

### 2. Song Files
Create text files with sections and arrangements:
```
V1
First verse lyrics
More verse content

C1
Chorus lyrics here

Arrangement
V1 C1 V1 C1
```

### 3. JSON Configuration
For precise text positioning:
```json
{
    "text": "Welcome",
    "x": 100,
    "y": 100,
    "fontSize": 48,
    "pptxFontScale": 0.5,     // Optional: scale factor for PowerPoint (0.5 = half size)
    "pptxXoffset": -20,       // Optional: X position adjustment for PowerPoint
    "pptxYoffset": -30,       // Optional: Y position adjustment for PowerPoint
    "fontFamily": "Arial",
    "media": "background.png"
}
```

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

### Custom Dimensions
```bash
python generate_presentation.py --source source_materials/1 --format both --width 1920 --height 1080
```

### Custom Font Size
```bash
python generate_presentation.py --source source_materials/1 --format pptx --font-size 48
```

### Lines Per Slide (for songs)
```bash
python generate_presentation.py --source source_materials/3 --format pro6 --lines-per-slide 6
```

## Environment Variables

Create a `.env` file to set defaults:

```env
WIDTH=1024
HEIGHT=768
FONT_SIZE=40
FONT_FAMILY=Arial
FONT_COLOR=0xFFFFFF
TOP_MARGIN=100
PAGE_BREAK_EVERY=2
ADD_TEXT_SHADOW=true
```

## Output Files

- **ProPresenter 6**: Creates `.pro6` XML files
- **PowerPoint**: Creates `.pptx` files
- **Playlists**: Creates `.pro6pl` and `.pro6plx` (zipped) files

## License

This project is licensed under the MIT License.
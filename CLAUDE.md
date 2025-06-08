# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a unified presentation generator that creates presentations in multiple formats:
- **ProPresenter 6** (.pro6) - XML-based presentation format for worship services and events
- **PowerPoint** (.pptx) - Standard Microsoft PowerPoint presentations

The generator supports various source materials including images, text files, songs with arrangements, and JSON-based configurations for precise control.

## Recent Updates (2025-06-08)

- **Unified Presentation Generator** - Merged PowerPoint generation capability from separate project
- **Multi-format support** - Single command can generate both PP6 and PowerPoint formats
- **Unified JSON/Media Processing Rules** - Implemented consistent rules for both formats:
  - JSON files must match media files by base name (e.g., slide1.json + slide1.png)
  - JSON files can specify media via "media" field (overrides base name matching)
  - Media files without JSON create image-only slides
  - JSON files without media use backgroundColor for colored backgrounds
  - Supports hex color conversion to PP6 RGBA format
- Added JSON-based document generation for precise text positioning and formatting
- Support for custom text placement, font size, and font family via JSON configuration
- Fixed text visibility issues (transparent fill color, proper shadow settings)
- Updated playlist generator to automatically detect and use JSON configurations
- Added support for background media behavior settings
- **Known Issue**: When playlists contain media files with identical names from different directories (e.g., "2.jpg" in multiple folders), ProPresenter may experience media cache conflicts during playlist loading, potentially displaying the wrong image file

## Recent Updates (2025-06-07)

- Added song document generation with section arrangements
- Implemented automatic song detection based on "Arrangement" line in text files
- Fixed playlist XML structure to match ProPresenter 6 format exactly
- Added .pro6plx (zipped playlist) generation
- Environment variable support for PAGE_BREAK_EVERY (lines per slide)
- Added --pro6plx-only flag to create only .pro6plx file with temp directories

## Key Components

1. **pp6_creation_guide.md** - Comprehensive technical specification for the ProPresenter 6 XML format
2. **pp6playlist/** - Sample ProPresenter 6 playlist directory containing:
   - Various .pro6 document files (songs, announcements, sermons)
   - data.pro6pl playlist file
   - Media resources (images, videos) in ProgramData/ and Users/ subdirectories
3. **generate_pp6_doc.py** - Python module for generating individual ProPresenter 6 documents
4. **generate_pp6_playlist.py** - Python module for generating complete PP6 playlist directories with proper structure

## ProPresenter 6 Document Structure

.pro6 files are XML documents with specific structure:
- Root element: `<RVPresentationDocument>`
- Contains slides organized in groups (verses, chorus, etc.)
- Text content is Base64 encoded in multiple formats (PlainText, RTFData, WinFlowData)
- Supports media elements (images, videos) with URL-encoded paths
- Uses UUIDs for all elements and references

## Development Tasks

### Creating the Python Generator
1. Parse the XML structure of existing .pro6 files
2. Implement Base64 encoding for text content (UTF-8, RTF, XAML)
3. Generate valid UUID4 identifiers
4. Handle media file path encoding
5. Create proper slide groups and arrangements
6. Validate generated XML structure

### Key Technical Requirements
- All text must be Base64 encoded in three formats: PlainText (UTF-8), RTFData (RTF), and WinFlowData (XAML)
- UUIDs must be unique and in uppercase format
- Media paths need URL encoding
- Colors use RGBA format with 0-1 range values
- Standard resolution: 1024×768 or 1920×1080

### Common Commands

#### Unified Presentation Generator (NEW)
```bash
# Generate complete presentation from all subdirectories (default behavior)
python generate_presentation.py
# Creates: GeneratedPlaylist.pro6plx and GeneratedPresentation.pptx

# Generate ProPresenter 6 document from specific directory
python generate_presentation.py --source source_materials/1 --format pro6

# Generate PowerPoint presentation from specific directory
python generate_presentation.py --source source_materials/1 --format pptx

# Generate both formats at once (default format)
python generate_presentation.py --source source_materials/1

# Generate with custom output name
python generate_presentation.py --output "SundayService"
# Creates: SundayService.pro6plx and SundayService.pptx

# Generate with custom dimensions and font size
python generate_presentation.py --source source_materials/3 --width 1920 --height 1080 --font-size 48
```

#### ProPresenter 6 Specific Commands
```bash
# Generate a single PP6 document (regular presentation)
python generate_pp6_doc.py --source source_materials/1 --output presentation.pro6

# Generate a song document with arrangements
python generate_pp6_doc.py --type song --source source_materials/3/song2.txt --output song.pro6

# Generate a document with JSON-based text positioning (automatic when JSON files present)
python generate_pp6_doc.py --source source_materials/8-gathering --output gathering.pro6

# Generate a PP6 playlist with automatic document generation
python generate_pp6_playlist.py

# Generate only .pro6plx file (uses temp directories for all other files)
python generate_pp6_playlist.py --pro6plx-only

# Generate a playlist with specific name
python generate_pp6_playlist.py --name "Sunday Service"

# Generate a playlist from existing documents
python generate_pp6_playlist.py doc1.pro6 doc2.pro6 doc3.pro6

# Generate playlist directory structure (old behavior)
python generate_pp6_playlist.py --output my_playlist_dir

# Validate XML output
xmllint --noout generated.pro6
```

## Architecture Considerations

The implemented Python modules include:

1. **generate_presentation.py** - Unified presentation generator (NEW):
   - Single entry point for all presentation formats
   - Supports ProPresenter 6 (.pro6) and PowerPoint (.pptx) outputs
   - Can generate both formats in a single command
   - Automatically detects content type (songs, JSON configs, regular slides)
   - Consistent command-line interface across formats

2. **generate_pp6_doc.py** - ProPresenter 6 document generator:
   - XML structure creation for individual .pro6 files
   - Base64 encoding for all text formats (PlainText, RTFData, WinFlowData)
   - UUID generation for all elements
   - Media file path encoding
   - JSON-based positioning support
   - CLI interface for creating documents

3. **generate_pp6_playlist.py** - ProPresenter 6 playlist generator:
   - Complete playlist directory creation
   - data.pro6pl playlist file generation with proper XML structure
   - Automatic song detection (looks for "Arrangement" line)
   - Media file discovery and copying
   - Cross-platform path handling (Windows/macOS)
   - Document scanning for media references
   - .pro6plx (zipped playlist) creation
   - CLI interface for playlist creation
   - --pro6plx-only mode for creating only the .pro6plx file with automatic temp directory cleanup

4. **pptx_generator.py** - PowerPoint generator (NEW):
   - Creates .pptx files using python-pptx library
   - Supports text shadows and custom fonts
   - Preserves image aspect ratios
   - JSON-based positioning support
   - Compatible with song arrangements
   - Environment variable configuration support

## Song Document Features

Songs are detected by the presence of an "Arrangement" line in the text file. Song files should have:
- Section markers (e.g., V1, C1, V2, C2, B1)
- Lyrics under each section
- An "Arrangement" line followed by the section order (e.g., V1 C1 V1 C1 C1)

The generator will:
- Create colored slide groups for each section type (Verse=Blue, Chorus=Red, Bridge=White)
- Split sections into multiple slides based on PAGE_BREAK_EVERY environment variable
- Generate an RVSongArrangement element with the specified section order
- Set proper UUIDs for arrangement playback

## JSON-Based Document Features

For precise text positioning and custom formatting, create JSON configuration files alongside media files:

```json
{
    "text": "日期: 7/6, 18/7",
    "x": 231,
    "y": 653,
    "fontSize": 59,           // ProPresenter 6 font size
    "pptxFontScale": 0.4,     // Scale factor for PowerPoint font (0.4 = 40% of PP6 size)
    "pptxXoffset": -50,       // X position offset for PowerPoint
    "pptxYoffset": -100,      // Y position offset for PowerPoint
    "fontFamily": "Arial",
    "media": "slide1.png"
}
```

The generator automatically detects JSON files and:
- Positions text at exact coordinates
- Uses specified font family and size
- PowerPoint font size scales relative to PP6 size using pptxFontScale
- PowerPoint position can be fine-tuned with pptxXoffset and pptxYoffset
- Creates slides with transparent text overlays
- Matches each format's text rendering requirements
- PowerPoint: Uses left alignment for JSON-based slides, center for songs

## Important Notes

- The pp6_creation_guide.md contains the complete XML specification
- Sample .pro6 files in Sample playlist/ can be used as reference templates
- Chinese text support is important (note the Chinese filenames in samples)
- Media files should maintain relative paths when possible
- Songs support arrangements that define playback order

## Development Environment

- Python 3.x with virtual environment (venv)
- Required packages: python-dotenv
- Environment variables:
  - PAGE_BREAK_EVERY: Number of lines per slide for songs (default: 4)
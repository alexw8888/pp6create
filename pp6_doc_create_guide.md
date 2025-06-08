# ProPresenter 6 Document Creation Guide

This guide explains how to create ProPresenter 6 (.pro6) documents programmatically based on the methods implemented in `generate_pp6_doc.py`.

## Overview

ProPresenter 6 documents are XML files with a specific structure that includes slides, text elements, media elements, and metadata. The generator supports creating both regular presentation documents and song documents with arrangements.

## Document Types

### 1. Regular Presentation Documents
- Created from directories containing text files and media files
- Automatically pairs text with media or creates separate slides
- Supports images (PNG, JPG, JPEG) and videos (MP4)

### 2. Song Documents
- Created from specially formatted text files with section markers
- Supports arrangements that define playback order
- Includes colored slide groups for different song sections
- Can include media files from the same directory

## Core Components

### 1. PP6Generator Class

The main class that handles document generation:

```python
generator = PP6Generator(width=1024, height=768)
```

- Default resolution: 1024×768 (can be customized)
- Build number: 100991749
- Version number: 600
- Platform: macOS (os="2")

### 2. Text Encoding

ProPresenter 6 requires text to be encoded in RTF format and then Base64 encoded:

```python
def encode_text(self, text: str) -> str:
    # Converts text to RTF with proper encoding for Chinese characters
    # Handles special characters using GB2312 or Unicode encoding
    # Wraps in RTF template with formatting
    # Returns Base64 encoded RTF string
```

Key features:
- Supports Chinese characters using GB2312 encoding
- Falls back to Unicode for characters not in GB2312
- Uses PingFangSC-Semibold font for Chinese support
- Text formatting: Bold, 114pt size, centered, with outline

### 3. Creating Text Elements

Text elements are created with specific attributes:

```python
text_element = self.create_text_element(text, slide_uuid)
```

Attributes include:
- UUID: Unique identifier
- Position: Default centered at `{0 69 0 1024 434}`
- Font settings via RTF encoding
- Shadow and stroke properties
- Only RTFData is included (not PlainText or WinFlowData)

### 4. Creating Media Elements

Background media (images/videos) are created as RVMediaCue elements:

```python
media_cue = self.create_background_media_cue(media_path)
```

Features:
- Converts paths to absolute file:// URLs
- Detects media type by extension
- Images: PNG, JPG, JPEG
- Videos: MP4 with loop behavior
- Default video properties: 30fps, 1920×1080

### 5. Creating Slides

Slides are RVDisplaySlide elements containing:

```python
slide, slide_uuid = self.create_slide(text, background_image, label)
```

Components:
- Empty cues array
- Optional background media cue
- Display elements array with text
- Label for identification
- Background color (default: black)

## Document Structure

### Basic XML Structure

```xml
<RVPresentationDocument>
    <RVTimeline>
        <array rvXMLIvarName="timeCues"/>
        <array rvXMLIvarName="mediaTracks"/>
    </RVTimeline>
    <array rvXMLIvarName="groups">
        <RVSlideGrouping>
            <array rvXMLIvarName="slides">
                <RVDisplaySlide>
                    <array rvXMLIvarName="cues"/>
                    <RVMediaCue/> <!-- Optional background -->
                    <array rvXMLIvarName="displayElements">
                        <RVTextElement/>
                    </array>
                </RVDisplaySlide>
            </array>
        </RVSlideGrouping>
    </array>
    <array rvXMLIvarName="arrangements"/>
</RVPresentationDocument>
```

### Document Attributes

Root element attributes:
- CCLISongTitle: Document title
- category: "Presentation"
- docType: "0"
- os: "2" (macOS)
- width/height: Resolution
- uuid: Document UUID
- buildNumber/versionNumber: PP6 version info

## Song Document Features

### Song File Format

Song files should contain:
1. Section markers (e.g., V1, C1, V2, C2, B1)
2. Lyrics under each section
3. An "Arrangement" line followed by section order

Example:
```
V1
First verse lyrics
More verse content

C1
Chorus lyrics here
More chorus content

Arrangement
V1 C1 V1 C1 B1
```

### Section Colors

Automatic color coding based on section type:
- Verse (V): Blue `0 0 0.998 1`
- Chorus (C): Red `0.986 0 0.027 1`
- Bridge (B): White `1 1 1 1`
- Pre-Chorus (PC): Green `0.135 1 0.025 1`
- Tag: Yellow `0.999 1 0 1`
- Default: Dark gray `0.264 0.264 0.264 1`

### Arrangements

Song arrangements define playback order:
- Created as RVSongArrangement elements
- Contains array of group UUIDs in playback order
- Set as selectedArrangementID on document

### Lines Per Slide

Songs are split into multiple slides:
- Default: 4 lines per slide
- Configurable via PAGE_BREAK_EVERY environment variable
- Or --lines-per-slide command line argument

## Generation Process

### 1. For Regular Documents

```python
# From a directory with mixed content
generator.generate_from_directory(source_dir, output_file)
```

Process:
1. Scan directory for text files (*.txt)
2. Scan for media files (images and videos)
3. Sort files by name
4. Pair text with media if counts match
5. Otherwise create separate slides
6. Generate XML structure
7. Write to .pro6 file

### 2. For Song Documents

```python
# From a song text file
doc = generator.create_song_document(title, song_file_path)
```

Process:
1. Parse song file for sections and arrangement
2. Extract valid section names from arrangement
3. Create colored slide groups for each section
4. Split sections into slides based on lines_per_slide
5. Add media files from same directory if present
6. Create arrangement element
7. Generate complete XML structure

## JSON-Based Document Generation

For precise control over text positioning and formatting, you can use JSON configuration files. When JSON files are present in a directory, the generator will automatically use them to create slides with custom formatting.

### JSON Configuration Format

Create a `.json` file for each slide with the following structure:

```json
{
    "text": "日期: 7/6, 18/7",
    "x": 100,
    "y": 100,
    "width": 374,           // optional, defaults to 374
    "height": 55,           // optional, defaults to 55
    "fontSize": 24,         // font size for ProPresenter 6
    "pptxFontScale": 0.5,   // optional, scales PP6 fontSize for PowerPoint (0.5 = half size)
    "pptxXoffset": -20,     // optional, adjusts X position for PowerPoint
    "pptxYoffset": -30,     // optional, adjusts Y position for PowerPoint
    "fontFamily": "Arial",
    "fontBold": false,      // optional, defaults to false
    "color": "#000000",     // used for PowerPoint text color
    "media": "slide1.png"   // optional, looks for matching media file
}
```

The generator will:
1. Look for JSON files in the source directory
2. For each JSON file, look for a matching media file (same base name)
3. Create slides with custom text positioning and formatting
4. Use simpler RTF formatting (like gathering.pro6)

### Position Calculation

- `x`, `y`: Top-left position of the text box
- `width`, `height`: Size of the text box
- Position format in PP6: `{x y z width height}` where z is always 0

## Command Line Usage

### Basic Document Generation

```bash
# Generate from default source directory
python generate_pp6_doc.py

# Generate from specific directory
python generate_pp6_doc.py --source source_materials/1 --output presentation.pro6

# Generate with custom title
python generate_pp6_doc.py --source media_dir --output output.pro6 --title "My Presentation"

# Generate from JSON configurations (automatic when JSON files present)
python generate_pp6_doc.py --source source_materials/8-gathering --output gathering.pro6
```

### Song Document Generation

```bash
# Generate song with default settings
python generate_pp6_doc.py --type song --source song.txt --output song.pro6

# Generate with custom lines per slide
python generate_pp6_doc.py --type song --source song.txt --output song.pro6 --lines-per-slide 6

# Title defaults to filename if not specified
python generate_pp6_doc.py --type song --source worship_song.txt --output worship.pro6
```

## Technical Details

### UUID Generation
- All elements require unique UUID4 identifiers
- Generated in uppercase format
- Used for elements, slides, groups, and arrangements

### Path Handling
- Media paths converted to absolute file:// URLs
- Cross-platform support (Windows/macOS)
- Proper URL encoding for special characters

### XML Formatting
- No XML declaration
- Single-line format (not pretty-printed)
- UTF-8 encoding

### Media Support
- Images: PNG, JPG, JPEG
- Videos: MP4
- Automatic format detection
- Proper MIME type settings

## Best Practices

1. **File Organization**
   - Keep related text and media in same directory
   - Use consistent naming for pairing
   - Song files should have clear section markers
   - Place JSON files alongside media for custom positioning

2. **Text Content**
   - Keep slide text concise
   - For songs, use standard section abbreviations
   - Include arrangement line for songs
   - Use JSON for precise text placement needs

3. **Media Files**
   - Use supported formats only
   - Keep media in relative paths when possible
   - Name files descriptively for labels
   - Match JSON filenames to media filenames

4. **Error Handling**
   - Validate source directories exist
   - Check for required song sections
   - Ensure media files are accessible
   - Verify JSON syntax is valid

## Key Implementation Details

### Text Visibility Settings
- `fillColor`: Must be `"0 0 0 0"` (transparent) for text to be visible
- `fromTemplate`: Set to `"false"` for custom text elements
- `behavior`: Use `"2"` for background media cues
- `enabled`: Must be `"true"` for media to display

### Shadow and Stroke Settings
- Shadow: `0.000000|0 0 0 0.3294117748737335|{4, -4}`
- Stroke width: `hint="double"` with value `"0.000000"` when not drawing stroke
- Stroke color: `0 0 0 1` (black)

## Environment Variables

- `PAGE_BREAK_EVERY`: Default lines per slide for songs (default: 4)

## Output

The generator creates valid ProPresenter 6 XML files that can be:
- Opened directly in ProPresenter 6
- Added to playlists
- Used as templates for further customization

The generated files include all necessary metadata, proper encoding, and structure to work seamlessly with ProPresenter 6.
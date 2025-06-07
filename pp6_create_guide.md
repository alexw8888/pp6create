# ProPresenter 6 Document Creation Guide

## Overview
This guide explains how to create ProPresenter 6 (.pro6) documents with text slides and media backgrounds (images and videos). These documents work correctly on Mac versions of ProPresenter 6.

## Key Differences: Mac vs Windows Format
ProPresenter 6 on Mac uses a different format than Windows:
- **No XML declaration** at the beginning of the file
- **Mac-specific RTF encoding** with Cocoa RTF format
- **Only RTFData is required** - no PlainText, WinFlowData, or WinFontData
- **Different attribute values** and ordering

## Basic Document Structure

### 1. Root Element
```xml
<RVPresentationDocument CCLIArtistCredits="" CCLIAuthor="" CCLICopyrightYear="" CCLIDisplay="false" CCLIPublisher="" CCLISongNumber="" CCLISongTitle="Your Title" backgroundColor="" buildNumber="100991749" category="Presentation" chordChartPath="" docType="0" drawingBackgroundColor="false" height="768" lastDateUsed="" notes="" os="2" resourcesDirectory="" selectedArrangementID="" usedCount="0" uuid="[UUID]" versionNumber="600" width="1024">
```

Key attributes:
- `os="2"` - Mac OS (not "1" for Windows)
- `buildNumber="100991749"` - Mac build number
- `uuid` - Document UUID (uppercase)
- No XML declaration before this element

### 2. Timeline (Required)
```xml
<RVTimeline duration="0.000000" loop="false" playBackRate="0.000000" rvXMLIvarName="timeline" selectedMediaTrackIndex="0" timeOffset="0.000000">
    <array rvXMLIvarName="timeCues"></array>
    <array rvXMLIvarName="mediaTracks"></array>
</RVTimeline>
```

### 3. Groups Array
```xml
<array rvXMLIvarName="groups">
    <RVSlideGrouping color="0.2637968361377716 0.2637968361377716 0.2637968361377716 1" name="Group" uuid="[UUID]">
        <array rvXMLIvarName="slides">
            <!-- Slides go here -->
        </array>
    </RVSlideGrouping>
</array>
```

### 4. Arrangements Array (Empty)
```xml
<array rvXMLIvarName="arrangements"></array>
```

## Slide Structure

Each slide in the slides array:
```xml
<RVDisplaySlide UUID="[UUID]" backgroundColor="0 0 0 1" chordChartPath="" drawingBackgroundColor="false" enabled="true" highlightColor="0 0 0 0" hotKey="" label="" notes="" socialItemCount="1">
    <array rvXMLIvarName="cues"></array>
    <!-- Optional: Background media cue goes here -->
    <array rvXMLIvarName="displayElements">
        <!-- Text elements go here -->
    </array>
</RVDisplaySlide>
```

Note: `socialItemCount` should be:
- `"0"` for slides with only background media (no text)
- `"1"` for slides with text elements

## Text Element Structure

```xml
<RVTextElement UUID="[UUID]" additionalLineFillHeight="0.000000" adjustsHeightToFit="false" bezelRadius="0.000000" displayDelay="0.000000" displayName="TextElement" drawLineBackground="false" drawingFill="false" drawingShadow="false" drawingStroke="false" fillColor="0 0 0 1" fromTemplate="true" lineBackgroundType="0" lineFillVerticalOffset="0.000000" locked="false" opacity="1.000000" persistent="false" revealType="0" rotation="0.000000" source="" textSourceRemoveLineReturnsOption="false" typeID="0" useAllCaps="false" verticalAlignment="1">
    <RVRect3D rvXMLIvarName="position">{0 69 0 1024 434}</RVRect3D>
    <shadow rvXMLIvarName="shadow">0.000000|0 0 0 0.3333333432674408|{3.9999997911970171, -3.999999397539229}</shadow>
    <dictionary rvXMLIvarName="stroke">
        <NSColor rvXMLDictionaryKey="RVShapeElementStrokeColorKey">0 0 0 1</NSColor>
        <NSNumber hint="float" rvXMLDictionaryKey="RVShapeElementStrokeWidthKey">1.000000</NSNumber>
    </dictionary>
    <NSString rvXMLIvarName="RTFData">[Base64 Encoded RTF]</NSString>
</RVTextElement>
```

Important attributes:
- `fromTemplate="true"` - Required for text to display
- `position`: `{0 69 0 1024 434}` for centered text
- Only `RTFData` is needed, not PlainText or other formats

## Background Media (Images and Videos)

Background media is added using an `RVMediaCue` element placed between the `cues` array and `displayElements` array in a slide.

### Background Image Structure

```xml
<RVMediaCue UUID="[UUID]" actionType="0" alignment="4" behavior="1" dateAdded="" delayTime="0.000000" displayName="image" enabled="false" nextCueUUID="" rvXMLIvarName="backgroundMediaCue" tags="" timeStamp="0.000000">
    <RVImageElement UUID="[UUID]" bezelRadius="0.000000" displayDelay="0.000000" displayName="ImageElement" drawingFill="false" drawingShadow="false" drawingStroke="false" fillColor="0 0 0 0" flippedHorizontally="false" flippedVertically="false" format="PNG image" fromTemplate="false" imageOffset="{0, 0}" locked="false" manufactureName="" manufactureURL="" opacity="1.000000" persistent="false" rotation="0.000000" rvXMLIvarName="element" scaleBehavior="3" scaleSize="{1, 1}" source="file:///absolute/path/to/image.png" typeID="0">
        <RVRect3D rvXMLIvarName="position">{0 0 0 0 0}</RVRect3D>
        <shadow rvXMLIvarName="shadow">0.000000|0 0 0 0.3333333432674408|{4, -4}</shadow>
        <dictionary rvXMLIvarName="stroke">
            <NSColor rvXMLDictionaryKey="RVShapeElementStrokeColorKey">0 0 0 1</NSColor>
            <NSNumber hint="float" rvXMLDictionaryKey="RVShapeElementStrokeWidthKey">1.000000</NSNumber>
        </dictionary>
    </RVImageElement>
</RVMediaCue>
```

Key attributes for images:
- `behavior="1"` - Static image
- `format` - "PNG image" or "JPEG image" based on file type
- `source` - Absolute file path with `file://` prefix
- `scaleBehavior="3"` - Fit to screen

### Background Video Structure

```xml
<RVMediaCue UUID="[UUID]" actionType="0" alignment="4" behavior="2" dateAdded="" delayTime="0.000000" displayName="video" enabled="false" nextCueUUID="" rvXMLIvarName="backgroundMediaCue" tags="" timeStamp="0.000000">
    <RVVideoElement UUID="[UUID]" audioVolume="1.000000" bezelRadius="0.000000" displayDelay="0.000000" displayName="VideoElement" drawingFill="false" drawingShadow="false" drawingStroke="false" endPoint="30030" fieldType="0" fillColor="0 0 0 0" flippedHorizontally="false" flippedVertically="false" format="'avc1'" frameRate="29.970030" fromTemplate="false" imageOffset="{0, 0}" inPoint="0" locked="false" manufactureName="" manufactureURL="" naturalSize="{1920, 1080}" opacity="1.000000" outPoint="30030" persistent="false" playRate="1.000000" playbackBehavior="1" rotation="0.000000" rvXMLIvarName="element" scaleBehavior="3" scaleSize="{1, 1}" source="file:///absolute/path/to/video.mp4" timeScale="1000" typeID="0">
        <RVRect3D rvXMLIvarName="position">{0 0 0 1920 1080}</RVRect3D>
        <shadow rvXMLIvarName="shadow">0.000000|0 0 0 0.3333333432674408|{4, -4}</shadow>
        <dictionary rvXMLIvarName="stroke">
            <NSColor rvXMLDictionaryKey="RVShapeElementStrokeColorKey">0 0 0 1</NSColor>
            <NSNumber hint="float" rvXMLDictionaryKey="RVShapeElementStrokeWidthKey">1.000000</NSNumber>
        </dictionary>
    </RVVideoElement>
</RVMediaCue>
```

Key attributes for videos:
- `behavior="2"` - Loop video (use "1" for play once)
- `audioVolume="1.000000"` - Full volume
- `format="'avc1'"` - H.264 video codec
- `frameRate` - Video frame rate
- `naturalSize="{1920, 1080}"` - Video resolution
- `position` - Use video resolution (e.g., `{0 0 0 1920 1080}`)
- `endPoint` and `outPoint` - Video duration in time units
- `timeScale="1000"` - Time scale for video timing

### Media Path Format

All media paths must:
1. Be absolute paths (not relative)
2. Use `file://` prefix
3. Be properly URL-encoded if they contain spaces or special characters

Example:
```
file:///Users/username/Desktop/media/background.png
file:///Users/username/Desktop/videos/intro.mp4
```

## RTF Encoding for Mac

The RTF must use Mac Cocoa format:

```rtf
{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset134 PingFangSC-Semibold;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\csgray\c100000;\cssrgb\c0\c0\c0;}
\pard\pardirnatural\qc\partightenfactor0

\f0\b\fs113\fsmilli57000 \cf2 \kerning1\expnd8\expndtw40
\outl0\strokewidth-40 \strokec3 Your Text Here }
```

Key RTF components:
- `\cocoartf2822` - Mac RTF version
- `\cf2` - White text color (references color table)
- `\strokec3` - Black outline color
- `\fs113\fsmilli57000` - Font size (57 points)
- Font: PingFangSC-Semibold (or Arial for English)

### Python Example for RTF Encoding
```python
import base64

def encode_text_for_mac(text):
    rtf_template = r"""{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset134 PingFangSC-Semibold;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\csgray\c100000;\cssrgb\c0\c0\c0;}
\pard\pardirnatural\qc\partightenfactor0

\f0\b\fs113\fsmilli57000 \cf2 \kerning1\expnd8\expndtw40
\outl0\strokewidth-40 \strokec3 """ + text + r""" }"""
    
    return base64.b64encode(rtf_template.encode('utf-8')).decode('ascii')
```

## Complete Minimal Example

```xml
<RVPresentationDocument CCLIArtistCredits="" CCLIAuthor="" CCLICopyrightYear="" CCLIDisplay="false" CCLIPublisher="" CCLISongNumber="" CCLISongTitle="Sample" backgroundColor="" buildNumber="100991749" category="Presentation" chordChartPath="" docType="0" drawingBackgroundColor="false" height="768" lastDateUsed="" notes="" os="2" resourcesDirectory="" selectedArrangementID="" usedCount="0" uuid="A1B2C3D4-E5F6-7890-ABCD-EF1234567890" versionNumber="600" width="1024"><RVTimeline duration="0.000000" loop="false" playBackRate="0.000000" rvXMLIvarName="timeline" selectedMediaTrackIndex="0" timeOffset="0.000000"><array rvXMLIvarName="timeCues"></array><array rvXMLIvarName="mediaTracks"></array></RVTimeline><array rvXMLIvarName="groups"><RVSlideGrouping color="0.2637968361377716 0.2637968361377716 0.2637968361377716 1" name="Group" uuid="B2C3D4E5-F6A7-8901-BCDE-F23456789012"><array rvXMLIvarName="slides"><RVDisplaySlide UUID="C3D4E5F6-A7B8-9012-CDEF-345678901234" backgroundColor="0 0 0 1" chordChartPath="" drawingBackgroundColor="false" enabled="true" highlightColor="0 0 0 0" hotKey="" label="" notes="" socialItemCount="1"><array rvXMLIvarName="cues"></array><array rvXMLIvarName="displayElements"><RVTextElement UUID="D4E5F6A7-B8C9-0123-DEFA-456789012345" additionalLineFillHeight="0.000000" adjustsHeightToFit="false" bezelRadius="0.000000" displayDelay="0.000000" displayName="TextElement" drawLineBackground="false" drawingFill="false" drawingShadow="false" drawingStroke="false" fillColor="0 0 0 1" fromTemplate="true" lineBackgroundType="0" lineFillVerticalOffset="0.000000" locked="false" opacity="1.000000" persistent="false" revealType="0" rotation="0.000000" source="" textSourceRemoveLineReturnsOption="false" typeID="0" useAllCaps="false" verticalAlignment="1"><RVRect3D rvXMLIvarName="position">{0 69 0 1024 434}</RVRect3D><shadow rvXMLIvarName="shadow">0.000000|0 0 0 0.3333333432674408|{3.9999997911970171, -3.999999397539229}</shadow><dictionary rvXMLIvarName="stroke"><NSColor rvXMLDictionaryKey="RVShapeElementStrokeColorKey">0 0 0 1</NSColor><NSNumber hint="float" rvXMLDictionaryKey="RVShapeElementStrokeWidthKey">1.000000</NSNumber></dictionary><NSString rvXMLIvarName="RTFData">e1xydGYxXGFuc2lcYW5zaWNwZzEyNTJcY29jb2FydGYyODIyClxjb2NvYXRleHRzY2FsaW5nMFxjb2NvYXBsYXRmb3JtMHtcZm9udHRibFxmMFxmbmlsXGZjaGFyc2V0MTM0IFBpbmdGYW5nU0MtU2VtaWJvbGQ7fQp7XGNvbG9ydGJsO1xyZWQyNTVcZ3JlZW4yNTVcYmx1ZTI1NTtccmVkMjU1XGdyZWVuMjU1XGJsdWUyNTU7XHJlZDBcZ3JlZW4wXGJsdWUwO30Ke1wqXGV4cGFuZGVkY29sb3J0Ymw7O1xjc2dyYXlcYzEwMDAwMDtcY3NzcmdiXGMwXGMwXGMwO30KXHBhcmRccGFyZGlybmF0dXJhbFxxY1xwYXJ0aWdodGVuZmFjdG9yMAoKXGYwXGJcZnMxMTNcZnNtaWxsaTU3MDAwIFxjZjIgXGtlcm5pbmcxXGV4cG5kOFxleHBuZHR3NDAKXG91dGwwXHN0cm9rZXdpZHRoLTQwIFxzdHJva2VjMyBIZWxsbyEgfQ==</NSString></RVTextElement></array></RVDisplaySlide></array></RVSlideGrouping></array><array rvXMLIvarName="arrangements"></array></RVPresentationDocument>
```

## Text Templates

In the simple format shown above, text templates are not explicitly referenced by name. The text styling is embedded directly in the RTF data. However, ProPresenter 6 templates work as follows:

1. **fromTemplate="true"** - This attribute indicates the text element uses template formatting
2. **Template data is embedded** - The actual template styling (font, size, color, outline) is stored in the RTF data, not referenced by name
3. **No template name field** - Unlike some other presentation software, PP6 doesn't store a template name reference in simple text elements

If you need specific template styling:
- Modify the RTF encoding to match your desired template (font, size, color, outline)
- The template is essentially the RTF formatting itself
- You can create different "templates" by using different RTF formatting strings

## Text Positioning

Text position is defined in the `RVRect3D` element within each `RVTextElement`:

```xml
<RVRect3D rvXMLIvarName="position">{X Y Z Width Height}</RVRect3D>
```

### Position Format: `{X Y Z Width Height}`

- **X**: Horizontal position from left edge (pixels)
- **Y**: Vertical position from top edge (pixels)
- **Z**: Depth/layer (typically 0)
- **Width**: Text box width (pixels)
- **Height**: Text box height (pixels)

### Common Position Examples (for 1024×768 resolution):

1. **Centered Text** (default):
   ```xml
   {0 69 0 1024 434}
   ```
   - X=0, Y=69: Starts at left edge, 69 pixels from top
   - Width=1024: Full width of screen
   - Height=434: Leaves margin at top and bottom

2. **Full Screen Text**:
   ```xml
   {0 0 0 1024 768}
   ```
   - Covers entire screen

3. **Lower Third**:
   ```xml
   {0 500 0 1024 268}
   ```
   - Positioned in bottom third of screen

4. **Custom Box** (e.g., left side only):
   ```xml
   {50 100 0 400 300}
   ```
   - X=50: 50 pixels from left
   - Y=100: 100 pixels from top
   - Width=400, Height=300: Custom size

### Adjusting for Different Resolutions:

For 1920×1080 (HD):
- Centered: `{0 100 0 1920 600}`
- Full screen: `{0 0 0 1920 1080}`
- Lower third: `{0 720 0 1920 360}`

The text will be centered within the defined box based on the RTF alignment settings (e.g., `\qc` for center alignment).

## Python Implementation

A complete Python implementation (`generate_pp6.py`) is available that:

### Features
1. **Automatic File Discovery** - Finds all media and text files in a directory:
   - Text files: `*.txt`
   - Images: `*.png`, `*.jpg`, `*.jpeg`
   - Videos: `*.mp4`

2. **Sorted Slide Order** - Files are sorted alphabetically by filename

3. **Flexible Slide Generation**:
   - Creates media-only slides for images/videos
   - Creates text-only slides for text files
   - Automatically pairs text with media if counts match

4. **Full Format Support**:
   - Proper RTF encoding for Mac
   - Background image support
   - Background video support with correct attributes
   - UUID generation

### Usage
```python
from pathlib import Path
generator = PP6Generator()
generator.generate_from_directory("source_materials/doc1", "output.pro6")
```

### Directory Structure Example
```
source_materials/doc1/
├── 01_intro.txt      # Text for slide 1
├── 02_background.png # Background for slide 2
├── 03_video.mp4      # Video background for slide 3
└── 04_outro.txt      # Text for slide 4
```

## Important Notes

1. **No XML Declaration** - Do not include `<?xml version="1.0" encoding="utf-8"?>`
2. **Compact Format** - No line breaks or indentation in the actual file
3. **Mac-Specific** - This format works on Mac ProPresenter 6. Windows may require different encoding
4. **UUID Format** - All UUIDs should be uppercase with hyphens
5. **Text Color** - White text (`\cf2`) with black outline (`\strokec3`) for visibility on black background
6. **Required Attribute** - `fromTemplate="true"` is essential for text display
7. **Template Styling** - Templates are represented by the RTF formatting, not by name references
8. **Media Paths** - Must be absolute paths with `file://` prefix

## Troubleshooting

If text doesn't appear:
1. Verify `fromTemplate="true"` is set
2. Check RTF encoding is correct (Mac Cocoa format)
3. Ensure text color is white (`\cf2`) not black
4. Confirm `os="2"` for Mac compatibility
5. Validate all UUIDs are unique and properly formatted

If media doesn't appear:
1. Check file paths are absolute with `file://` prefix
2. Verify media files exist at specified locations
3. Ensure proper attributes for media type (image vs video)
4. Check `rvXMLIvarName="backgroundMediaCue"` is set
5. Verify position values match media type
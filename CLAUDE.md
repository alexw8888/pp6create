# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is for creating a Python program to generate ProPresenter 6 (.pro6) documents and playlist directories programmatically. ProPresenter 6 is presentation software used primarily for worship services and events.

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
```bash
# Generate a single PP6 document
python generate_pp6_doc.py --title "My Song" --author "John Doe" --content song_lyrics.txt

# Generate a PP6 playlist with sample documents
python generate_pp6_playlist.py --name "Sunday Service" --generate-docs

# Generate a playlist from existing documents
python generate_pp6_playlist.py doc1.pro6 doc2.pro6 doc3.pro6

# Validate XML output
xmllint --noout generated.pro6
```

## Architecture Considerations

The implemented Python modules include:
1. **generate_pp6_doc.py** - Core document generator with:
   - XML structure creation for individual .pro6 files
   - Base64 encoding for all text formats (PlainText, RTFData, WinFlowData)
   - UUID generation for all elements
   - Media file path encoding
   - CLI interface for creating documents

2. **generate_pp6_playlist.py** - Playlist generator with:
   - Complete playlist directory creation
   - data.pro6pl playlist file generation
   - Media file discovery and copying
   - Cross-platform path handling (Windows/macOS)
   - Document scanning for media references
   - CLI interface for playlist creation

## Important Notes

- The pp6_creation_guide.md contains the complete XML specification
- Sample .pro6 files in pp6playlist/ can be used as reference templates
- Chinese text support is important (note the Chinese filenames in samples)
- Media files should maintain relative paths when possible

## Development Environment

- Need to use python venv
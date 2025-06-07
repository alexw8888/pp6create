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
Since no Python files exist yet, typical development commands would be:
```bash
# Run the generator (once created)
python generate_pp6.py

# Validate XML output
xmllint --noout generated.pro6

# Test with sample data
python test_generator.py
```

## Architecture Considerations

The Python program should include:
1. **XML Generator Module** - Core XML structure creation
2. **Text Encoder Module** - Handle Base64 encoding for all text formats
3. **Media Handler** - Process and encode media file paths
4. **Validator** - Ensure generated documents meet PP6 requirements
5. **CLI Interface** - Accept input data and output .pro6 files

## Important Notes

- The pp6_creation_guide.md contains the complete XML specification
- Sample .pro6 files in pp6playlist/ can be used as reference templates
- Chinese text support is important (note the Chinese filenames in samples)
- Media files should maintain relative paths when possible

## Development Environment

- Need to use python venv
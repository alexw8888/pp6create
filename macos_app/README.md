# ProPresenter 6 Generator CLI - macOS App

A command-line interface for generating ProPresenter 6 playlists and PowerPoint presentations from source materials.

## Build

To build the CLI app:

```bash
./build_cli_app.sh
```

This creates a standalone executable at `dist/pp6generator` (12M size).

## Directory Structure

```
macos_app/
├── pp6_cli_app.py          # CLI application source
├── build_cli_app.sh        # Build script
└── dist/
    └── pp6generator        # Built CLI executable (12M)
```

## Distribution

The CLI app is designed to work with an external `source_materials` folder:

```
pp6generator-cli/
├── pp6generator            # 12M executable
└── source_materials/       # External content folder
    ├── 1-worship/
    ├── 2-song1/
    └── 3-sermon/
```

To create a distribution package:

```bash
# After building
cp dist/pp6generator .
cp -r ../source_materials .
zip -r pp6generator-cli.zip pp6generator source_materials/
```

## Usage

The CLI app works identically to `generate_presentation.py`:

```bash
# Show help
./pp6generator --help

# Generate from default source_materials folder
./pp6generator

# Generate from specific folder
./pp6generator --source /path/to/materials

# Generate only PowerPoint
./pp6generator --format pptx

# Generate with custom output name
./pp6generator --output "Sunday Service"
```

## Features

- Works identically whether run from terminal or double-clicked in Finder
- Output files are always created next to the executable
- External `source_materials` folder (not bundled in executable)
- Supports all formats: ProPresenter 6 (.pro6plx) and PowerPoint (.pptx)
- Automatic song detection and arrangement support
- JSON-based precise text positioning
- Chinese text support

## Technical Details

- Built with PyInstaller using `--onefile --console` flags
- Uses external resource detection relative to executable location
- Implements working directory management for consistent behavior
- Includes all required Python dependencies (PIL, python-pptx, lxml, etc.)
- Compatible with both development and bundled execution modes
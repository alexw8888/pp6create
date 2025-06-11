#!/usr/bin/env python3
"""
Unified Presentation Generator
Generates presentations in both ProPresenter 6 (.pro6) and PowerPoint (.pptx) formats
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict, Optional
import json

# Import existing generators
from generate_pp6_doc import PP6Generator
from generate_pp6_playlist import PP6PlaylistGenerator

# Import PowerPoint components
from pptx_generator import PPTXGenerator


class UnifiedPresentationGenerator:
    """Main class that coordinates generation for different presentation formats"""
    
    def __init__(self):
        self.supported_formats = ['pro6', 'pptx', 'both']
        
    def generate(self, source_dir: str, output_format: str, output_path: Optional[str] = None, 
                 process_all_subdirs: bool = False, **kwargs) -> List[str]:
        """
        Generate presentation(s) in specified format(s)
        
        Args:
            source_dir: Directory containing source materials
            output_format: Target format ('pro6', 'pptx', or 'both')
            output_path: Output file path (optional, auto-generated if not provided)
            process_all_subdirs: Process all subdirectories (like playlist generation)
            **kwargs: Additional format-specific options
            
        Returns:
            List of generated file paths
        """
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {output_format}. Choose from {self.supported_formats}")
        
        generated_files = []
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        # Check if we should process all subdirectories
        if process_all_subdirs or self._should_process_all_subdirs(source_path):
            # Process all subdirectories like playlist generation
            return self._generate_from_all_subdirs(source_dir, output_format, output_path, **kwargs)
        
        # Single directory processing
        # Determine output base name
        if output_path:
            output_base = Path(output_path).stem
        else:
            output_base = source_path.name.replace('_', ' ').replace('-', ' ').title()
        
        # Generate based on format
        if output_format in ['pro6', 'both']:
            pro6_path = self._generate_pro6(source_dir, output_base, **kwargs)
            generated_files.append(pro6_path)
            
        if output_format in ['pptx', 'both']:
            pptx_path = self._generate_pptx(source_dir, output_base, **kwargs)
            generated_files.append(pptx_path)
            
        return generated_files
    
    def _should_process_all_subdirs(self, source_path: Path) -> bool:
        """Check if we should process all subdirectories"""
        # If source_materials is the directory, process all subdirs
        if source_path.name == 'source_materials':
            return True
        
        # Check if directory has subdirectories but no direct content files
        subdirs = [d for d in source_path.iterdir() if d.is_dir()]
        files = [f for f in source_path.iterdir() if f.is_file() and not f.name.startswith('.')]
        
        return len(subdirs) > 0 and len(files) == 0
    
    def _generate_from_all_subdirs(self, source_dir: str, output_format: str, 
                                   output_path: Optional[str], **kwargs) -> List[str]:
        """Generate presentations from all subdirectories"""
        source_path = Path(source_dir)
        generated_files = []
        
        # Get all subdirectories and sort them
        subdirs = sorted([d for d in source_path.iterdir() if d.is_dir()], 
                        key=lambda x: self._natural_sort_key(x.name))
        
        print(f"Processing {len(subdirs)} subdirectories from {source_dir}")
        
        # For PP6: Use playlist generator for complete playlist
        if output_format in ['pro6', 'both']:
            print("\nGenerating ProPresenter 6 playlist...")
            playlist_name = output_path or "GeneratedPlaylist"
            
            # Import and use the playlist generator
            from generate_pp6_playlist import PP6PlaylistGenerator, main as playlist_main
            import sys
            
            # Save original argv
            original_argv = sys.argv
            
            # Set up argv for playlist generator
            sys.argv = ['generate_pp6_playlist.py', '--name', playlist_name]
            
            try:
                # Run playlist generator
                playlist_main()
                generated_files.append(f"{playlist_name}.pro6plx")
            finally:
                # Restore original argv
                sys.argv = original_argv
        
        # For PPTX: Create single presentation with all content
        if output_format in ['pptx', 'both']:
            print("\nGenerating PowerPoint presentation...")
            pptx_name = output_path or "GeneratedPresentation"
            
            # Create single PPTX generator instance
            generator = PPTXGenerator(
                width=kwargs.get('width', 1024),
                height=kwargs.get('height', 768)
            )
            
            # Process each subdirectory
            for i, subdir in enumerate(subdirs):
                print(f"  Processing {subdir.name}...")
                
                # Check for JSON files first
                json_files = list(subdir.glob('*.json'))
                
                if json_files:
                    # Use JSON-based generation
                    generator.generate_from_json_directory(str(subdir))
                else:
                    # Use regular generation
                    generator.generate_from_directory(str(subdir))
            
            # Save the complete presentation
            output_file = f"{pptx_name}.pptx"
            generator.save(output_file)
            generated_files.append(output_file)
        
        return generated_files
    
    def _natural_sort_key(self, s: str):
        """Natural sort key for alphanumeric sorting"""
        import re
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split('([0-9]+)', s)]
    
    def _generate_pro6(self, source_dir: str, output_base: str, **kwargs) -> str:
        """Generate ProPresenter 6 document"""
        # Create PP6 generator with dimensions from kwargs
        width = kwargs.get('width', 1024)
        height = kwargs.get('height', 768)
        generator = PP6Generator(width=width, height=height)
        output_file = f"{output_base}.pro6"
        
        # Check for JSON files first
        source_path = Path(source_dir)
        json_files = list(source_path.glob('*.json'))
        
        if json_files:
            # Use JSON-based generation
            generator.generate_from_json_directory(source_dir, output_file)
        else:
            # Check for song files
            txt_files = list(source_path.glob('*.txt'))
            is_song = False
            song_file = None
            
            for txt_file in txt_files:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Arrangement' in content:
                        is_song = True
                        song_file = txt_file
                        break
            
            if is_song and song_file:
                # Generate as song
                title = kwargs.get('title', output_base)
                lines_per_slide = kwargs.get('lines_per_slide', None)
                doc = generator.create_song_document(title, str(song_file), lines_per_slide)
                xml_content = generator.format_xml(doc)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                print(f"Generated song document: {output_file}")
            else:
                # Generate regular document
                generator.generate_from_directory(source_dir, output_file)
        
        return output_file
    
    def _generate_pptx(self, source_dir: str, output_base: str, **kwargs) -> str:
        """Generate PowerPoint presentation"""
        # Create PowerPoint generator with optional dimensions
        width = kwargs.get('width', 1024)
        height = kwargs.get('height', 768)
        generator = PPTXGenerator(width=width, height=height)
        
        # Override settings if provided
        if 'font_size' in kwargs:
            generator.font_size = kwargs['font_size']
        if 'lines_per_slide' in kwargs:
            generator.page_break_every = kwargs['lines_per_slide']
        
        # Check for JSON files first
        source_path = Path(source_dir)
        json_files = list(source_path.glob('*.json'))
        
        if json_files:
            # Use JSON-based generation
            generator.generate_from_json_directory(source_dir)
        else:
            # Use regular generation
            generator.generate_from_directory(source_dir)
        
        # Save the presentation
        output_file = f"{output_base}.pptx"
        generator.save(output_file)
        
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Unified Presentation Generator - Create presentations in ProPresenter 6 or PowerPoint format'
    )
    
    # Main arguments
    parser.add_argument('--source', default='source_materials',
                       help='Source directory containing materials (default: source_materials)')
    parser.add_argument('--format', choices=['pro6', 'pptx', 'both'], default='both',
                       help='Output format (default: both)')
    
    # Optional arguments
    parser.add_argument('--output', help='Output file path (auto-generated if not provided)')
    parser.add_argument('--title', help='Presentation title')
    
    # Format-specific options
    parser.add_argument('--width', type=int, default=1024, help='Slide width in pixels')
    parser.add_argument('--height', type=int, default=768, help='Slide height in pixels')
    parser.add_argument('--font-size', type=int, help='Font size for text')
    parser.add_argument('--lines-per-slide', type=int, help='Lines per slide for songs')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create generator
    generator = UnifiedPresentationGenerator()
    
    # Prepare kwargs
    kwargs = {}
    if args.title:
        kwargs['title'] = args.title
    if args.width:
        kwargs['width'] = args.width
    if args.height:
        kwargs['height'] = args.height
    if args.font_size:
        kwargs['font_size'] = args.font_size
    if args.lines_per_slide:
        kwargs['lines_per_slide'] = args.lines_per_slide
    
    try:
        # Generate presentation(s)
        generated_files = generator.generate(
            source_dir=args.source,
            output_format=args.format,
            output_path=args.output,
            **kwargs
        )
        
        print(f"\nSuccessfully generated:")
        for file_path in generated_files:
            print(f"  - {file_path}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def generate_presentation(source_dir: str, format: str = 'both', output_name: Optional[str] = None, **kwargs):
    """
    Wrapper function for GUI integration
    
    Args:
        source_dir: Directory containing source materials
        format: Output format ('pro6', 'pptx', or 'both')
        output_name: Output file name (without extension)
        **kwargs: Additional options
        
    Returns:
        Output directory path where files were generated
    """
    generator = UnifiedPresentationGenerator()
    
    # Generate presentations
    generated_files = generator.generate(
        source_dir=source_dir,
        output_format=format,
        output_path=output_name,
        process_all_subdirs=True,  # Always process subdirs for GUI
        **kwargs
    )
    
    # Return the source directory (where files are generated)
    return source_dir


if __name__ == "__main__":
    exit(main())
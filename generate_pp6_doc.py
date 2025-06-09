#!/usr/bin/env python3
"""
ProPresenter 6 Document Generator (Refactored)
Reads text files from source_materials directory and generates .pro6 XML documents
"""

import os
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional
import json
from dotenv import load_dotenv

# Import from our new modules
import pp6_xml_elements as xml_elements
import pp6_color_utils as color_utils
import pp6_song_parser as song_parser

# Load environment variables
load_dotenv()


class PP6Generator:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.build_number = "100991749"
        self.version_number = "600"
        
    def generate_uuid(self) -> str:
        """Generate a valid UUID4 in uppercase format"""
        return str(uuid.uuid4()).upper()
    
    def format_xml(self, elem: ET.Element) -> str:
        """Convert ElementTree to XML string without declaration"""
        # Convert to string without pretty printing to match sample format
        xml_string = ET.tostring(elem, encoding='unicode')
        return xml_string
    
    def create_slide(self, text: str = None, background_image: str = None, label: str = "") -> Tuple[ET.Element, str]:
        """Create a slide with optional text content and background image"""
        slide_uuid = self.generate_uuid()
        slide = xml_elements.create_slide(
            slide_uuid, text, background_image, label, 
            element_uuid_gen=self.generate_uuid, width=self.width
        )
        return slide, slide_uuid
    
    def create_document(self, title: str, slides_data: List[Union[str, Tuple[Optional[str], Optional[str], str]]]) -> ET.Element:
        """Create a complete ProPresenter 6 document
        
        Args:
            title: Document title
            slides_data: List of either:
                - str: text content for slide
                - Tuple[Optional[str], Optional[str], str]: (text, background_image_path, label)
        """
        doc_uuid = self.generate_uuid()
        
        # Root element - matching sample order and attributes
        root = ET.Element('RVPresentationDocument', {
            'CCLIArtistCredits': '',
            'CCLIAuthor': '',
            'CCLICopyrightYear': '',
            'CCLIDisplay': 'false',
            'CCLIPublisher': '',
            'CCLISongNumber': '',
            'CCLISongTitle': title,
            'backgroundColor': '',
            'buildNumber': self.build_number,
            'category': 'Presentation',
            'chordChartPath': '',
            'docType': '0',
            'drawingBackgroundColor': 'false',
            'height': str(self.height),
            'lastDateUsed': '',
            'notes': '',
            'os': '2',
            'resourcesDirectory': '',
            'selectedArrangementID': '',
            'usedCount': '0',
            'uuid': doc_uuid,
            'versionNumber': self.version_number,
            'width': str(self.width)
        })
        
        # Timeline
        timeline = ET.SubElement(root, 'RVTimeline', {
            'duration': '0.000000',
            'loop': 'false',
            'playBackRate': '0.000000',
            'rvXMLIvarName': 'timeline',
            'selectedMediaTrackIndex': '0',
            'timeOffset': '0.000000'
        })
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'timeCues'})
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'mediaTracks'})
        
        # Groups array
        groups_array = ET.SubElement(root, 'array', {'rvXMLIvarName': 'groups'})
        
        # Create a single group for all slides
        group_uuid = self.generate_uuid()
        group = ET.SubElement(groups_array, 'RVSlideGrouping', {
            'color': '0.2637968361377716 0.2637968361377716 0.2637968361377716 1',
            'name': 'Group',
            'uuid': group_uuid
        })
        
        slides_array = ET.SubElement(group, 'array', {'rvXMLIvarName': 'slides'})
        
        # Add slides
        for i, slide_info in enumerate(slides_data):
            if isinstance(slide_info, tuple):
                text, bg_image, label = slide_info
            else:
                text = slide_info
                bg_image = None
                label = ""
            
            slide, slide_uuid = self.create_slide(text, bg_image, label)
            slides_array.append(slide)
        
        # Arrangements array (empty like in sample)
        arrangements_array = ET.SubElement(root, 'array', {'rvXMLIvarName': 'arrangements'})
        
        return root
    
    def create_song_document(self, title: str, song_file_path: str, lines_per_slide: int = None) -> ET.Element:
        """Create a ProPresenter 6 song document with arrangement support
        
        Args:
            title: Song title
            song_file_path: Path to song text file with sections and arrangement
            lines_per_slide: Number of lines per slide (default from env or 4)
        """
        # Get lines per slide from environment or use default
        if lines_per_slide is None:
            lines_per_slide = int(os.getenv('PAGE_BREAK_EVERY', '4'))
        
        # Check for media files in the same directory
        song_dir = Path(song_file_path).parent
        media_files = []
        
        # Collect all image files
        for ext in ['.png', '.jpg', '.jpeg']:
            media_files.extend(song_dir.glob(f'*{ext}'))
        
        # Collect all video files
        media_files.extend(song_dir.glob('*.mp4'))
        
        # Sort media files by name
        media_files.sort(key=lambda x: x.name)
        
        # Parse the song file
        sections, arrangement = song_parser.parse_song_file(song_file_path)
        
        if not sections:
            raise ValueError("No sections found in song file")
        
        doc_uuid = self.generate_uuid()
        
        # Root element
        root = ET.Element('RVPresentationDocument', {
            'CCLIArtistCredits': '',
            'CCLIAuthor': '',
            'CCLICopyrightYear': '',
            'CCLIDisplay': 'false',
            'CCLIPublisher': '',
            'CCLISongNumber': '',
            'CCLISongTitle': title,
            'backgroundColor': '0 0 0 0',
            'buildNumber': self.build_number,
            'category': 'Presentation',
            'chordChartPath': '',
            'docType': '0',
            'drawingBackgroundColor': 'false',
            'height': str(self.height),
            'lastDateUsed': '2025-06-07T16:09:41-07:00',
            'notes': '',
            'os': '2',
            'resourcesDirectory': '',
            'selectedArrangementID': '',
            'usedCount': '0',
            'uuid': doc_uuid,
            'versionNumber': self.version_number,
            'width': str(self.width)
        })
        
        # Timeline
        timeline = ET.SubElement(root, 'RVTimeline', {
            'duration': '0.000000',
            'loop': 'false',
            'playBackRate': '1.000000',
            'rvXMLIvarName': 'timeline',
            'selectedMediaTrackIndex': '0',
            'timeOffset': '0.000000'
        })
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'timeCues'})
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'mediaTracks'})
        
        # Groups array
        groups_array = ET.SubElement(root, 'array', {'rvXMLIvarName': 'groups'})
        
        # Create unique sections (not duplicates from arrangement)
        unique_sections = []
        seen = set()
        for section in sections.keys():
            if section not in seen:
                unique_sections.append(section)
                seen.add(section)
        
        # Track group UUIDs for arrangement
        section_to_group_uuid = {}
        media_group_uuid = None  # Track media group UUID separately
        
        # Create a group for each unique section
        for section_name in unique_sections:
            section_lines = sections[section_name]
            
            # Skip empty sections
            if not any(line.strip() for line in section_lines):
                continue
            
            group_uuid = self.generate_uuid()
            section_to_group_uuid[section_name] = group_uuid
            display_name = color_utils.get_section_display_name(section_name)
            color = color_utils.get_section_color(section_name)
            
            group = ET.SubElement(groups_array, 'RVSlideGrouping', {
                'color': color,
                'name': display_name,
                'uuid': group_uuid
            })
            
            slides_array = ET.SubElement(group, 'array', {'rvXMLIvarName': 'slides'})
            
            # Split section content into slides
            slide_texts = []
            current_slide_lines = []
            
            for line in section_lines:
                current_slide_lines.append(line.rstrip())  # Remove trailing whitespace but keep blank lines
                
                # Break slide when we reach the target number of total lines (including blank lines)
                if len(current_slide_lines) >= lines_per_slide:
                    slide_texts.append('\n'.join(current_slide_lines))
                    current_slide_lines = []
            
            # Add remaining lines as last slide
            if current_slide_lines:
                slide_texts.append('\n'.join(current_slide_lines))
            
            # Create slides for this section
            for i, slide_text in enumerate(slide_texts):
                slide_label = f"{section_name}-{i+1}" if len(slide_texts) > 1 else ""
                slide, slide_uuid = self.create_slide(slide_text, None, slide_label)
                slides_array.append(slide)
        
        # Add media files as separate slides if found
        if media_files:
            media_group_uuid = self.generate_uuid()
            media_group = ET.SubElement(groups_array, 'RVSlideGrouping', {
                'color': color_utils.SECTION_COLORS['default'],
                'name': 'Media',
                'uuid': media_group_uuid
            })
            
            media_slides_array = ET.SubElement(media_group, 'array', {'rvXMLIvarName': 'slides'})
            
            # Create a slide for each media file
            for media_file in media_files:
                media_label = media_file.stem
                media_slide, media_slide_uuid = self.create_slide(None, str(media_file), media_label)
                media_slides_array.append(media_slide)
        
        # Arrangements array
        arrangements_array = ET.SubElement(root, 'array', {'rvXMLIvarName': 'arrangements'})
        
        # Create arrangement based on the song file
        if arrangement:
            arrangement_uuid = self.generate_uuid()
            song_arrangement = ET.SubElement(arrangements_array, 'RVSongArrangement', {
                'color': '0 0 0 0',
                'name': 'arrangement1',
                'uuid': arrangement_uuid
            })
            
            # Add group IDs array
            group_ids_array = ET.SubElement(song_arrangement, 'array', {'rvXMLIvarName': 'groupIDs'})
            
            # Add media group at the beginning if it exists
            if media_group_uuid:
                ns_string = ET.SubElement(group_ids_array, 'NSString')
                ns_string.text = media_group_uuid
            
            # Add group IDs in arrangement order
            for section in arrangement:
                if section in section_to_group_uuid:
                    ns_string = ET.SubElement(group_ids_array, 'NSString')
                    ns_string.text = section_to_group_uuid[section]
            
            # Set the selected arrangement ID in root
            root.set('selectedArrangementID', arrangement_uuid)
        
        return root
    
    def generate_from_directory(self, source_dir: str, output_file: str):
        """Generate PP6 document from directory using unified JSON/media processing rules"""
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise ValueError(f"Source directory {source_dir} does not exist")
        
        # Check if directory has JSON files
        json_files = list(source_path.glob('*.json'))
        
        if json_files:
            # Use unified JSON/media processing
            self.generate_from_unified_directory(source_dir, output_file)
        else:
            # Legacy processing for directories without JSON
            self._generate_from_legacy_directory(source_dir, output_file)
    
    def _generate_from_legacy_directory(self, source_dir: str, output_file: str):
        """Legacy processing for directories without JSON files"""
        source_path = Path(source_dir)
        
        # Collect media files only (no text files in legacy mode)
        image_files = []
        video_files = []
        
        # Collect image files
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(source_path.glob(ext))
        
        # Collect video files
        video_files = list(source_path.glob('*.mp4'))
        
        # Combine all media files
        media_files = image_files + video_files
        media_files.sort(key=lambda x: x.name)
        
        # Create slides for media files
        slides_data = []
        for media_file in media_files:
            label = media_file.stem
            slides_data.append((None, str(media_file), label))
        
        if not slides_data:
            raise ValueError(f"No media files found in {source_dir}")
        
        # Generate title from directory name
        title = source_path.name.replace('_', ' ').title()
        
        # Create document
        doc = self.create_document(title, slides_data)
        
        # Write to file
        xml_content = self.format_xml(doc)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Generated {output_file} with {len(slides_data)} slides from {source_dir}")
        print(f"  - {len(image_files)} image files")
        print(f"  - {len(video_files)} video files")
    
    def generate_from_unified_directory(self, source_dir: str, output_file: str):
        """Generate PP6 document using unified JSON/media processing rules"""
        source_path = Path(source_dir)
        
        # Collect all files
        json_files = sorted(source_path.glob('*.json'), key=lambda x: x.name)
        image_files = []
        video_files = []
        
        # Collect image files
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(source_path.glob(ext))
        
        # Collect video files
        video_files.extend(source_path.glob('*.mp4'))
        
        # Combine all media files
        all_media_files = sorted(image_files + video_files, key=lambda x: x.name)
        
        # Create a set of all unique base names
        all_base_names = set()
        for f in json_files:
            all_base_names.add(f.stem)
        for f in all_media_files:
            all_base_names.add(f.stem)
        
        # Process each unique base name
        slides_data = []
        for base_name in sorted(all_base_names):
            # Check for JSON file
            json_file = source_path / f"{base_name}.json"
            has_json = json_file.exists()
            
            # Check for media file
            media_file = None
            for ext in ['.png', '.jpg', '.jpeg', '.mp4']:
                potential_media = source_path / f"{base_name}{ext}"
                if potential_media.exists():
                    media_file = str(potential_media)
                    break
            
            if has_json:
                # Load JSON configuration
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Extract configuration
                text = config.get('text', '')
                
                # Check if JSON specifies a media file
                json_media = config.get('media')
                if json_media:
                    # Use the media file specified in JSON
                    json_media_path = source_path / json_media
                    if json_media_path.exists():
                        media_file = str(json_media_path)
                
                # Handle position
                if 'x' in config and 'y' in config:
                    x = config.get('x', 231)
                    y = config.get('y', 653)
                    width = config.get('width', 374)
                    height = config.get('height', 55)
                    position = f"{{{x} {y} 0 {width} {height}}}"
                else:
                    position = config.get('position')
                
                font_size = config.get('fontSize', 59)
                font_bold = config.get('fontBold', False)
                font_name = config.get('fontName', 'PingFangSC-Regular')
                
                # Map font families
                font_family = config.get('fontFamily', '').lower()
                if font_family == 'arial':
                    font_name = 'Arial'
                elif font_family == 'helvetica':
                    font_name = 'Helvetica'
                
                simple_format = config.get('simpleFormat', True)
                vertical_alignment = config.get('verticalAlignment', '0')
                label = config.get('label', base_name)
                background_color = color_utils.convert_color_to_rgba(config.get('backgroundColor', '0 0 0 1'))
                text_color = config.get('color', '#000000')
                
                # Create slide data
                slide_info = {
                    'text': text,
                    'background': media_file,  # Can be None
                    'label': label,
                    'position': position,
                    'font_size': font_size,
                    'font_bold': font_bold,
                    'font_name': font_name,
                    'simple_format': simple_format,
                    'vertical_alignment': vertical_alignment,
                    'background_color': background_color,
                    'color': text_color,
                    'countdown_message': config.get('countdown_message', False),
                    'clear_props': config.get('clear_props', False)
                }
                slides_data.append(slide_info)
            else:
                # No JSON - image only slide
                if media_file:
                    slide_info = {
                        'text': '',
                        'background': media_file,
                        'label': base_name,
                        'position': None,
                        'font_size': 59,
                        'font_bold': False,
                        'font_name': 'PingFangSC-Regular',
                        'simple_format': True,
                        'vertical_alignment': '0',
                        'background_color': '0 0 0 1'
                    }
                    slides_data.append(slide_info)
        
        if not slides_data:
            raise ValueError(f"No content files found in {source_dir}")
        
        # Generate title from directory name
        title = source_path.name.replace('_', ' ').replace('-', ' ').title()
        
        # Create document with unified slides
        doc = self.create_json_document(title, slides_data)
        
        # Write to file
        xml_content = self.format_xml(doc)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Generated {output_file} with {len(slides_data)} slides from {source_dir}")
        print(f"  - {len(json_files)} JSON configuration files")
        print(f"  - {len(all_media_files)} media files")
    
    def generate_from_json_directory(self, source_dir: str, output_file: str):
        """Redirect to unified directory processing"""
        self.generate_from_unified_directory(source_dir, output_file)
    
    def create_json_document(self, title: str, slides_data: List[Dict]) -> ET.Element:
        """Create a ProPresenter 6 document from JSON-configured slides"""
        doc_uuid = self.generate_uuid()
        
        # Root element
        root = ET.Element('RVPresentationDocument', {
            'CCLIArtistCredits': '',
            'CCLIAuthor': '',
            'CCLICopyrightYear': '',
            'CCLIDisplay': 'false',
            'CCLIPublisher': '',
            'CCLISongNumber': '',
            'CCLISongTitle': title,
            'backgroundColor': '0 0 0 0',
            'buildNumber': self.build_number,
            'category': 'Presentation',
            'chordChartPath': '',
            'docType': '0',
            'drawingBackgroundColor': 'false',
            'height': str(self.height),
            'lastDateUsed': '',
            'notes': '',
            'os': '2',
            'resourcesDirectory': '',
            'selectedArrangementID': '',
            'usedCount': '0',
            'uuid': doc_uuid,
            'versionNumber': self.version_number,
            'width': str(self.width)
        })
        
        # Timeline
        timeline = ET.SubElement(root, 'RVTimeline', {
            'duration': '0.000000',
            'loop': 'false',
            'playBackRate': '1.000000',
            'rvXMLIvarName': 'timeline',
            'selectedMediaTrackIndex': '-1',
            'timeOffset': '0.000000'
        })
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'timeCues'})
        ET.SubElement(timeline, 'array', {'rvXMLIvarName': 'mediaTracks'})
        
        # Groups array
        groups_array = ET.SubElement(root, 'array', {'rvXMLIvarName': 'groups'})
        
        # Create a single group for all slides
        group_uuid = self.generate_uuid()
        group = ET.SubElement(groups_array, 'RVSlideGrouping', {
            'color': '0.2627451121807098 0.2627451121807098 0.2627451121807098 1',
            'name': 'Group',
            'uuid': group_uuid
        })
        
        slides_array = ET.SubElement(group, 'array', {'rvXMLIvarName': 'slides'})
        
        # Add slides with JSON configuration
        for slide_config in slides_data:
            slide, slide_uuid = self.create_json_slide(slide_config)
            slides_array.append(slide)
        
        # Arrangements array (empty)
        ET.SubElement(root, 'array', {'rvXMLIvarName': 'arrangements'})
        
        return root
    
    def create_json_slide(self, config: Dict) -> Tuple[ET.Element, str]:
        """Create a slide from JSON configuration"""
        slide_uuid = self.generate_uuid()
        
        background_color = config.get('background_color', '0 0 0 1')
        slide = ET.Element('RVDisplaySlide', {
            'UUID': slide_uuid,
            'backgroundColor': background_color,
            'chordChartPath': '',
            'drawingBackgroundColor': 'true' if background_color != '0 0 0 1' else 'false',
            'enabled': 'true',
            'highlightColor': '1 1 1 0',
            'hotKey': '',
            'label': config.get('label', ''),
            'notes': '',
            'socialItemCount': '1' if config.get('text') else '0'
        })
        
        # Cues array - add cues based on config
        cues_array = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'cues'})
        if config.get('countdown_message', False):
            message_cue = xml_elements.create_message_cue(self.generate_uuid(), self.generate_uuid())
            cues_array.append(message_cue)
        if config.get('clear_props', False):
            clear_cue = xml_elements.create_clear_cue(self.generate_uuid())
            cues_array.append(clear_cue)
        
        # Add background media if provided
        if config.get('background') and os.path.exists(config['background']):
            bg_cue = xml_elements.create_background_media_cue(
                config['background'], self.generate_uuid(), self.generate_uuid()
            )
            slide.insert(1, bg_cue)  # Insert after cues array
        
        # Display elements array with text
        display_elements = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'displayElements'})
        
        if config.get('text'):
            text_element = xml_elements.create_text_element(
                text=config['text'],
                slide_uuid=slide_uuid,
                element_uuid=self.generate_uuid(),
                position=config.get('position'),
                font_size=config.get('font_size', 59),
                font_bold=config.get('font_bold', False),
                font_name=config.get('font_name', 'PingFangSC-Regular'),
                simple_format=config.get('simple_format', True),
                vertical_alignment=config.get('vertical_alignment', '0'),
                text_color=config.get('color', '#000000'),
                default_width=self.width
            )
            display_elements.append(text_element)
        
        return slide, slide_uuid


def main():
    """Main function to run the generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ProPresenter 6 documents')
    parser.add_argument('--type', choices=['document', 'song'], default='document',
                       help='Type of PP6 document to generate')
    parser.add_argument('--source', help='Source directory or file path')
    parser.add_argument('--output', help='Output .pro6 file path')
    parser.add_argument('--title', help='Document/song title')
    parser.add_argument('--lines-per-slide', type=int, default=None,
                       help='Lines per slide for songs (default: from PAGE_BREAK_EVERY env or 4)')
    parser.add_argument('--width', type=int, default=1024, help='Slide width in pixels')
    parser.add_argument('--height', type=int, default=768, help='Slide height in pixels')
    
    args = parser.parse_args()
    
    generator = PP6Generator(width=args.width, height=args.height)
    
    if args.type == 'song':
        # Generate song document
        if not args.source or not args.output:
            print("Error: For songs, --source (song text file) and --output are required")
            return
        
        title = args.title or Path(args.source).stem.replace('_', ' ').title()
        
        try:
            doc = generator.create_song_document(title, args.source, args.lines_per_slide)
            xml_content = generator.format_xml(doc)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"Generated song document: {args.output}")
            
        except Exception as e:
            print(f"Error generating song document: {e}")
    
    else:
        # Generate regular document from directory
        source_dir = args.source or "source_materials/doc1"
        output_file = args.output or "generated_doc1.pro6"
        
        try:
            # Check if directory contains JSON files
            source_path = Path(source_dir)
            if source_path.exists() and list(source_path.glob('*.json')):
                generator.generate_from_json_directory(source_dir, output_file)
            else:
                generator.generate_from_directory(source_dir, output_file)
            
        except Exception as e:
            print(f"Error generating document: {e}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
ProPresenter 6 Document Generator
Reads text files from source_materials directory and generates .pro6 XML documents
"""

import os
import base64
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional


class PP6Generator:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.build_number = "100991749"
        self.version_number = "600"
        
    def generate_uuid(self) -> str:
        """Generate a valid UUID4 in uppercase format"""
        return str(uuid.uuid4()).upper()
    
    def encode_text(self, text: str) -> str:
        """Encode text in RTF format matching ProPresenter 6 Mac format"""
        # RTF format for Mac ProPresenter 6
        rtf_template = r"""{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset134 PingFangSC-Semibold;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\csgray\c100000;\cssrgb\c0\c0\c0;}
\pard\pardirnatural\qc\partightenfactor0

\f0\b\fs113\fsmilli57000 \cf2 \kerning1\expnd8\expndtw40
\outl0\strokewidth-40 \strokec3 """ + text + r""" }"""
        rtf_b64 = base64.b64encode(rtf_template.encode('utf-8')).decode('ascii')
        return rtf_b64
    
    def create_text_element(self, text: str, slide_uuid: str, position: str = None) -> ET.Element:
        """Create an RVTextElement with properly encoded text"""
        rtf_encoded = self.encode_text(text)
        element_uuid = self.generate_uuid()
        
        text_elem = ET.Element('RVTextElement', {
            'UUID': element_uuid,
            'additionalLineFillHeight': '0.000000',
            'adjustsHeightToFit': 'false',
            'bezelRadius': '0.000000',
            'displayDelay': '0.000000',
            'displayName': 'TextElement',
            'drawLineBackground': 'false',
            'drawingFill': 'false',
            'drawingShadow': 'false',
            'drawingStroke': 'false',
            'fillColor': '0 0 0 1',
            'fromTemplate': 'true',
            'lineBackgroundType': '0',
            'lineFillVerticalOffset': '0.000000',
            'locked': 'false',
            'opacity': '1.000000',
            'persistent': 'false',
            'revealType': '0',
            'rotation': '0.000000',
            'source': '',
            'textSourceRemoveLineReturnsOption': 'false',
            'typeID': '0',
            'useAllCaps': 'false',
            'verticalAlignment': '1'
        })
        
        # Position - centered text area by default
        position_elem = ET.SubElement(text_elem, 'RVRect3D', {'rvXMLIvarName': 'position'})
        if position:
            position_elem.text = position
        else:
            # Default centered position
            position_elem.text = f'{{0 69 0 {self.width} 434}}'
        
        # Shadow
        shadow = ET.SubElement(text_elem, 'shadow', {'rvXMLIvarName': 'shadow'})
        shadow.text = '0.000000|0 0 0 0.3333333432674408|{3.9999997911970171, -3.999999397539229}'
        
        # Stroke
        stroke = ET.SubElement(text_elem, 'dictionary', {'rvXMLIvarName': 'stroke'})
        stroke_color = ET.SubElement(stroke, 'NSColor', {'rvXMLDictionaryKey': 'RVShapeElementStrokeColorKey'})
        stroke_color.text = '0 0 0 1'
        stroke_width = ET.SubElement(stroke, 'NSNumber', {
            'hint': 'float',
            'rvXMLDictionaryKey': 'RVShapeElementStrokeWidthKey'
        })
        stroke_width.text = '1.000000'
        
        # Only RTF Data
        rtf_data = ET.SubElement(text_elem, 'NSString', {'rvXMLIvarName': 'RTFData'})
        rtf_data.text = rtf_encoded
        
        return text_elem
    
    def create_background_media_cue(self, media_path: str) -> ET.Element:
        """Create a background media cue for image or video"""
        cue_uuid = self.generate_uuid()
        element_uuid = self.generate_uuid()
        
        # Convert to absolute path with file:// URL format
        abs_path = os.path.abspath(media_path)
        file_url = f"file://{abs_path}"
        
        # Determine if it's an image or video
        ext = Path(media_path).suffix.lower()
        is_video = ext in ['.mp4', '.mov', '.avi']
        
        # Create media cue
        media_cue = ET.Element('RVMediaCue', {
            'UUID': cue_uuid,
            'actionType': '0',
            'alignment': '4',
            'behavior': '1' if not is_video else '2',  # 2 for loop video
            'dateAdded': '',
            'delayTime': '0.000000',
            'displayName': Path(media_path).stem,
            'enabled': 'false',
            'nextCueUUID': '',
            'rvXMLIvarName': 'backgroundMediaCue',
            'tags': '',
            'timeStamp': '0.000000'
        })
        
        if is_video:
            # Create video element with proper attributes
            video_elem = ET.SubElement(media_cue, 'RVVideoElement', {
                'UUID': element_uuid,
                'audioVolume': '1.000000',
                'bezelRadius': '0.000000',
                'displayDelay': '0.000000',
                'displayName': 'VideoElement',
                'drawingFill': 'false',
                'drawingShadow': 'false',
                'drawingStroke': 'false',
                'endPoint': '30030',  # Default endpoint
                'fieldType': '0',
                'fillColor': '0 0 0 0',
                'flippedHorizontally': 'false',
                'flippedVertically': 'false',
                'format': "'avc1'",
                'frameRate': '29.970030',
                'fromTemplate': 'false',
                'imageOffset': '{0, 0}',
                'inPoint': '0',
                'locked': 'false',
                'manufactureName': '',
                'manufactureURL': '',
                'naturalSize': '{1920, 1080}',  # Default HD size
                'opacity': '1.000000',
                'outPoint': '30030',
                'persistent': 'false',
                'playRate': '1.000000',
                'playbackBehavior': '1',
                'rotation': '0.000000',
                'rvXMLIvarName': 'element',
                'scaleBehavior': '3',
                'scaleSize': '{1, 1}',
                'source': file_url,
                'timeScale': '1000',
                'typeID': '0'
            })
            element = video_elem
        else:
            # Create image element
            image_elem = ET.SubElement(media_cue, 'RVImageElement', {
                'UUID': element_uuid,
                'bezelRadius': '0.000000',
                'displayDelay': '0.000000',
                'displayName': 'ImageElement',
                'drawingFill': 'false',
                'drawingShadow': 'false',
                'drawingStroke': 'false',
                'fillColor': '0 0 0 0',
                'flippedHorizontally': 'false',
                'flippedVertically': 'false',
                'format': 'PNG image' if ext == '.png' else 'JPEG image',
                'fromTemplate': 'false',
                'imageOffset': '{0, 0}',
                'locked': 'false',
                'manufactureName': '',
                'manufactureURL': '',
                'opacity': '1.000000',
                'persistent': 'false',
                'rotation': '0.000000',
                'rvXMLIvarName': 'element',
                'scaleBehavior': '3',
                'scaleSize': '{1, 1}',
                'source': file_url,
                'typeID': '0'
            })
            element = image_elem
        
        # Position
        position = ET.SubElement(element, 'RVRect3D', {'rvXMLIvarName': 'position'})
        if is_video:
            position.text = '{0 0 0 1920 1080}'  # Full HD position for video
        else:
            position.text = '{0 0 0 0 0}'  # Default for images
        
        # Shadow
        shadow = ET.SubElement(element, 'shadow', {'rvXMLIvarName': 'shadow'})
        shadow.text = '0.000000|0 0 0 0.3333333432674408|{4, -4}'
        
        # Stroke
        stroke = ET.SubElement(element, 'dictionary', {'rvXMLIvarName': 'stroke'})
        stroke_color = ET.SubElement(stroke, 'NSColor', {'rvXMLDictionaryKey': 'RVShapeElementStrokeColorKey'})
        stroke_color.text = '0 0 0 1'
        stroke_width = ET.SubElement(stroke, 'NSNumber', {
            'hint': 'float',
            'rvXMLDictionaryKey': 'RVShapeElementStrokeWidthKey'
        })
        stroke_width.text = '1.000000'
        
        return media_cue
    
    def create_slide(self, text: str = None, background_image: str = None, label: str = "") -> Tuple[ET.Element, str]:
        """Create a slide with optional text content and background image"""
        slide_uuid = self.generate_uuid()
        
        slide = ET.Element('RVDisplaySlide', {
            'UUID': slide_uuid,
            'backgroundColor': '0 0 0 1',
            'chordChartPath': '',
            'drawingBackgroundColor': 'false',
            'enabled': 'true',
            'highlightColor': '0 0 0 0',
            'hotKey': '',
            'label': label,
            'notes': '',
            'socialItemCount': '1' if text else '0'
        })
        
        # Empty cues array
        cues = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'cues'})
        
        # Add background media if provided
        if background_image and os.path.exists(background_image):
            bg_cue = self.create_background_media_cue(background_image)
            slide.insert(1, bg_cue)  # Insert after cues array
        
        # Display elements array with text
        display_elements = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'displayElements'})
        if text:
            text_element = self.create_text_element(text, slide_uuid)
            display_elements.append(text_element)
        
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
    
    def format_xml(self, elem: ET.Element) -> str:
        """Convert ElementTree to XML string without declaration"""
        # Convert to string without pretty printing to match sample format
        xml_string = ET.tostring(elem, encoding='unicode')
        return xml_string
    
    def generate_from_directory(self, source_dir: str, output_file: str):
        """Generate PP6 document from all media and text files in a directory"""
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise ValueError(f"Source directory {source_dir} does not exist")
        
        # Collect all relevant files
        text_files = list(source_path.glob('*.txt'))
        image_files = []
        video_files = []
        
        # Collect image files
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(source_path.glob(ext))
        
        # Collect video files
        video_files = list(source_path.glob('*.mp4'))
        
        # Combine all media files
        media_files = image_files + video_files
        
        # Sort all files by name
        text_files.sort(key=lambda x: x.name)
        media_files.sort(key=lambda x: x.name)
        
        # Create slides based on available content
        slides_data = []
        
        # Strategy: pair text files with media files if counts match,
        # otherwise create separate slides
        if len(text_files) == len(media_files) and len(text_files) > 0:
            # Pair each text with corresponding media
            for text_file, media_file in zip(text_files, media_files):
                with open(text_file, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
                slides_data.append((text_content, str(media_file), ""))
        else:
            # Create separate slides for media and text
            # First add media-only slides
            for media_file in media_files:
                label = media_file.stem  # filename without extension
                slides_data.append((None, str(media_file), label))
            
            # Then add text-only slides
            for text_file in text_files:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
                    if text_content:
                        slides_data.append((text_content, None, ""))
        
        if not slides_data:
            raise ValueError(f"No content files found in {source_dir}")
        
        # Generate title from directory name
        title = source_path.name.replace('_', ' ').title()
        
        # Create document
        doc = self.create_document(title, slides_data)
        
        # Write to file
        xml_content = self.format_xml(doc)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Generated {output_file} with {len(slides_data)} slides from {source_dir}")
        print(f"  - {len(text_files)} text files")
        print(f"  - {len(image_files)} image files")
        print(f"  - {len(video_files)} video files")


def main():
    """Main function to run the generator"""
    generator = PP6Generator()
    
    # Generate from doc1
    source_dir = "source_materials/doc1"
    output_file = "generated_doc1.pro6"
    
    try:
        generator.generate_from_directory(source_dir, output_file)
        
    except Exception as e:
        print(f"Error generating document: {e}")


if __name__ == "__main__":
    main()
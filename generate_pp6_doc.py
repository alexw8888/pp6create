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
import re
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PP6Generator:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.build_number = "100991749"
        self.version_number = "600"
        
        # Section colors for songs (matching arrangement.pro6)
        self.section_colors = {
            'verse': '0 0 0.9981992244720459 1',  # Blue
            'chorus': '0.9859541654586792 0 0.02694005146622658 1',  # Red
            'bridge': '1 0.5 0 1',  # Orange
            'prechorus': '0.1352526992559433 1 0.0248868502676487 1',  # Green
            'tag': '0.6 0.3 0.1 1',  # Brown
            'intro': '0.5 0.5 0.5 1',  # Gray
            'outro': '0.5 0.5 0.5 1',  # Gray
            'coda': '0 0.4 0 1',  # Darker green
            'default': '0.2637968361377716 0.2637968361377716 0.2637968361377716 1'  # Dark gray
        }
        
    def generate_uuid(self) -> str:
        """Generate a valid UUID4 in uppercase format"""
        return str(uuid.uuid4()).upper()
    
    def convert_color_to_rgba(self, color: str) -> str:
        """Convert color from hex or name to PP6 RGBA format"""
        if color.startswith('#'):
            # Convert hex to RGBA
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return f"{r} {g} {b} 1"
            elif len(hex_color) == 8:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                a = int(hex_color[6:8], 16) / 255.0
                return f"{r} {g} {b} {a}"
        elif ' ' in color and len(color.split()) == 4:
            # Already in RGBA format
            return color
        else:
            # Default to black
            return "0 0 0 1"
    
    def encode_text(self, text: str, font_size: int = 114, font_bold: bool = True, 
                    font_name: str = "PingFangSC-Semibold", simple_format: bool = False,
                    text_color: str = "#000000") -> str:
        """Encode text in RTF format matching ProPresenter 6 Mac format"""
        # Convert text to RTF with proper encoding for Chinese characters
        rtf_text = ""
        for char in text:
            if char == '\n':
                rtf_text += '\\\n'
            elif ord(char) > 127:
                # Try to encode as GB2312 (Chinese encoding)
                try:
                    gb_bytes = char.encode('gb2312')
                    rtf_text += ''.join([f"\\'{b:02x}" for b in gb_bytes])
                except:
                    # If not in GB2312, use Unicode encoding
                    code = ord(char)
                    rtf_text += f"\\u{code}?"
            else:
                rtf_text += char
        
        # Parse text color
        if text_color.startswith('#'):
            hex_color = text_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
        else:
            # Default to black
            r, g, b = 0, 0, 0
        
        if simple_format:
            # Simple format with custom text color
            rtf_template = r"""{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset134 """ + font_name + r""";\f1\fswiss\fcharset0 Helvetica;}
{\colortbl;\red""" + str(r) + r"""\green""" + str(g) + r"""\blue""" + str(b) + r""";}
{\*\expandedcolortbl;;}
\deftab720
\pard\pardeftab720\partightenfactor0

\f0""" + (r"\b" if font_bold else "") + r"\fs" + str(font_size) + r" \cf1 " + rtf_text + r"""
\f1  }"""
        else:
            # Original format with outlines
            rtf_template = r"""{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset134 """ + font_name + r""";}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\csgray\c100000;\cssrgb\c0\c0\c0;}
\pard\pardirnatural\qc\partightenfactor0

\f0""" + (r"\b" if font_bold else "") + r"\fs" + str(font_size) + r""" \cf2 \kerning1\expnd8\expndtw40
\outl0\strokewidth-40 \strokec3 """ + rtf_text + r"""
}"""
        rtf_b64 = base64.b64encode(rtf_template.encode('utf-8')).decode('ascii')
        return rtf_b64
    
    def create_text_element(self, text: str, slide_uuid: str, position: str = None, 
                          font_size: int = 114, font_bold: bool = True, 
                          font_name: str = "PingFangSC-Semibold", simple_format: bool = False,
                          vertical_alignment: str = "1", text_color: str = "#000000") -> ET.Element:
        """Create an RVTextElement with properly encoded text"""
        rtf_encoded = self.encode_text(text, font_size, font_bold, font_name, simple_format, text_color)
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
            'fillColor': '1 1 1 1',
            'fromTemplate': 'false',
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
            'verticalAlignment': vertical_alignment
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
        shadow.text = '0.000000|0 0 0 0.3294117748737335|{4, -4}'
        
        # Stroke
        stroke = ET.SubElement(text_elem, 'dictionary', {'rvXMLIvarName': 'stroke'})
        stroke_color = ET.SubElement(stroke, 'NSColor', {'rvXMLDictionaryKey': 'RVShapeElementStrokeColorKey'})
        stroke_color.text = '0 0 0 1'
        stroke_width = ET.SubElement(stroke, 'NSNumber', {
            'hint': 'double',
            'rvXMLDictionaryKey': 'RVShapeElementStrokeWidthKey'
        })
        stroke_width.text = '0.000000'
        
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
            'behavior': '2',  # 2 for both images and videos in gathering.pro6
            'dateAdded': '',
            'delayTime': '0.000000',
            'displayName': Path(media_path).stem,
            'enabled': 'true',
            'nextCueUUID': '00000000-0000-0000-0000-000000000000',
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
                'scaleBehavior': '0',
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
                'scaleBehavior': '0',
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
    
    def create_message_cue(self) -> ET.Element:
        """Create an RVMessageCue element for countdown timers and automated actions"""
        cue_uuid = self.generate_uuid()
        message_uuid = self.generate_uuid()
        
        message_cue = ET.Element('RVMessageCue', {
            'UUID': cue_uuid,
            'actionType': '0',
            'delayTime': '0.000000',
            'displayName': 'Message',
            'enabled': 'false',
            'messageUUID': message_uuid,
            'timeStamp': '0.000000'
        })
        
        # Values dictionary with empty message
        values_dict = ET.SubElement(message_cue, 'dictionary', {'rvXMLIvarName': 'values'})
        message_string = ET.SubElement(values_dict, 'NSString', {'rvXMLDictionaryKey': 'Message'})
        message_string.text = ''
        
        return message_cue
    
    def create_clear_cue(self) -> ET.Element:
        """Create an RVClearCue element for clearing props and stage displays"""
        cue_uuid = self.generate_uuid()
        
        clear_cue = ET.Element('RVClearCue', {
            'UUID': cue_uuid,
            'actionType': '4',
            'delayTime': '0.000000',
            'displayName': 'Clear Props',
            'enabled': 'false',
            'timeStamp': '0.000000'
        })
        
        return clear_cue
    
    def create_slide(self, text: str = None, background_image: str = None, label: str = "") -> Tuple[ET.Element, str]:
        """Create a slide with optional text content and background image"""
        slide_uuid = self.generate_uuid()
        
        slide = ET.Element('RVDisplaySlide', {
            'UUID': slide_uuid,
            'backgroundColor': '0 0 0 1',
            'chordChartPath': '',
            'drawingBackgroundColor': 'false',
            'enabled': 'true',
            'highlightColor': '1 1 1 0',
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
    
    def parse_song_file(self, filepath: str) -> Tuple[Dict[str, List[str]], List[str]]:
        """Parse song file to extract sections and arrangement"""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
        
        # First pass: find arrangement line to get valid section names
        arrangement = []
        arrangement_line_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('Arrangement'):
                arrangement_line_index = i
                if i + 1 < len(lines):
                    arrangement = lines[i + 1].strip().split()
                break
        
        # Extract unique section names from arrangement (case insensitive)
        valid_sections = set(arrangement)
        
        # Create case-insensitive mapping from arrangement to actual section headers
        arrangement_to_section = {}
        
        # Second pass: parse sections and build case-insensitive mapping
        sections = {}
        current_section = None
        
        for i, line in enumerate(lines):
            # Skip the arrangement line and the line after it
            if i == arrangement_line_index or i == arrangement_line_index + 1:
                continue
                
            line_stripped = line.strip()
            
            # Check if this line matches any arrangement section (case insensitive)
            matched_arrangement = None
            for arr_section in valid_sections:
                if line_stripped.lower() == arr_section.lower():
                    matched_arrangement = arr_section
                    break
            
            if matched_arrangement:
                current_section = line_stripped  # Use the actual section header as found
                sections[current_section] = []
                # Map arrangement name to actual section header
                arrangement_to_section[matched_arrangement] = line_stripped
            elif current_section:
                # Add line to current section (including blank lines)
                sections[current_section].append(line)
        
        # Update arrangement to use actual section headers
        updated_arrangement = []
        for arr_section in arrangement:
            if arr_section in arrangement_to_section:
                updated_arrangement.append(arrangement_to_section[arr_section])
            else:
                updated_arrangement.append(arr_section)  # Keep original if no mapping found
        
        return sections, updated_arrangement
    
    def get_section_color(self, section_name: str) -> str:
        """Get color for a section based on its type with graduated colors for verses and choruses"""
        section_lower = section_name.lower()
        
        # Try to determine section type from name
        for key in self.section_colors:
            if key in section_lower:
                return self.section_colors[key]
        
        # Check common abbreviations with graduated colors
        if section_lower.startswith('v'):
            # Extract number from verse (V1, V2, V3, etc.)
            number_match = re.search(r'(\d+)', section_name)
            if number_match:
                verse_num = int(number_match.group(1))
                return self._get_graduated_verse_color(verse_num)
            return self.section_colors['verse']
        elif section_lower.startswith('c') and not section_lower.startswith('co'):
            # Extract number from chorus (C1, C2, C3, etc.)
            number_match = re.search(r'(\d+)', section_name)
            if number_match:
                chorus_num = int(number_match.group(1))
                return self._get_graduated_chorus_color(chorus_num)
            return self.section_colors['chorus']
        elif section_lower.startswith('b'):
            return self.section_colors['bridge']
        elif section_lower.startswith('pc'):
            return self.section_colors['prechorus']
        elif section_lower.startswith('t'):
            return self.section_colors['tag']
        elif section_lower.startswith('i'):
            return self.section_colors['intro']
        elif section_lower.startswith('o'):
            return self.section_colors['outro']
        elif section_lower.startswith('co'):
            return self.section_colors['coda']
        
        return self.section_colors['default']
    
    def _get_graduated_verse_color(self, verse_num: int) -> str:
        """Get graduated blue color for verses (V1 = blue, V2 = lighter blue, V3 = even lighter blue)"""
        # Base verse color: '0 0 0.9981992244720459 1' (blue)
        # Use a more dramatic lightening by reducing the blue value and adding other colors
        
        if verse_num == 1:
            return '0 0 0.9981992244720459 1'  # Full blue
        elif verse_num == 2:
            # Medium blue: reduce blue intensity and add some green/red for lighter appearance
            return '0.2 0.2 0.9 1'  # Lighter blue
        elif verse_num == 3:
            # Light blue: more green/red for much lighter appearance
            return '0.4 0.4 0.8 1'  # Much lighter blue
        else:
            # For V4 and beyond, keep getting lighter
            lightness = min(0.7, 0.4 + (verse_num - 3) * 0.1)
            blue_intensity = max(0.6, 0.8 - (verse_num - 3) * 0.05)
            return f'{lightness} {lightness} {blue_intensity} 1'
    
    def _get_graduated_chorus_color(self, chorus_num: int) -> str:
        """Get graduated red color for choruses (C1 = red, C2 = lighter red, C3 = even lighter red)"""
        # Base chorus color: '0.9859541654586792 0 0.02694005146622658 1' (red)
        base_red = 0.9859541654586792
        base_green = 0.0
        base_blue = 0.02694005146622658
        
        if chorus_num == 1:
            return f'{base_red} {base_green} {base_blue} 1'  # Full red
        elif chorus_num == 2:
            # Make 30% lighter by moving towards white
            lighter_red = base_red + (1.0 - base_red) * 0.3
            lighter_green = base_green + (1.0 - base_green) * 0.3
            lighter_blue = base_blue + (1.0 - base_blue) * 0.3
            return f'{lighter_red} {lighter_green} {lighter_blue} 1'
        elif chorus_num == 3:
            # Make 60% lighter by moving towards white
            much_lighter_red = base_red + (1.0 - base_red) * 0.6
            much_lighter_green = base_green + (1.0 - base_green) * 0.6
            much_lighter_blue = base_blue + (1.0 - base_blue) * 0.6
            return f'{much_lighter_red} {much_lighter_green} {much_lighter_blue} 1'
        else:
            # For C4 and beyond, keep getting lighter
            lightness_factor = min(0.8, 0.3 + (chorus_num - 2) * 0.15)
            graduated_red = base_red + (1.0 - base_red) * lightness_factor
            graduated_green = base_green + (1.0 - base_green) * lightness_factor
            graduated_blue = base_blue + (1.0 - base_blue) * lightness_factor
            return f'{graduated_red} {graduated_green} {graduated_blue} 1'
    
    def get_section_display_name(self, section_name: str) -> str:
        """Get display name for a section"""
        # Map common abbreviations to full names
        section_lower = section_name.lower()
        
        if section_lower.startswith('v'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Verse {number.group()}"
            return "Verse"
        elif section_lower.startswith('co'):
            # Handle "coda" before checking for "chorus"
            number = re.search(r'\d+', section_name)
            if number:
                return f"Coda {number.group()}"
            return "Coda"
        elif section_lower.startswith('c') and not section_lower.startswith('ch'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Chorus {number.group()}"
            return "Chorus"
        elif section_lower.startswith('b'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Bridge {number.group()}"
            return "Bridge"
        elif section_lower.startswith('pc'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Pre-Chorus {number.group()}"
            return "Pre-Chorus"
        elif section_lower.startswith('t'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Tag {number.group()}"
            return "Tag"
        elif section_lower.startswith('i'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Intro {number.group()}"
            return "Intro"
        elif section_lower.startswith('o'):
            number = re.search(r'\d+', section_name)
            if number:
                return f"Outro {number.group()}"
            return "Outro"
        
        return section_name
    
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
        sections, arrangement = self.parse_song_file(song_file_path)
        
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
            display_name = self.get_section_display_name(section_name)
            color = self.get_section_color(section_name)
            
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
                'color': self.section_colors['default'],
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
                background_color = self.convert_color_to_rgba(config.get('backgroundColor', '0 0 0 1'))
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
            message_cue = self.create_message_cue()
            cues_array.append(message_cue)
        if config.get('clear_props', False):
            clear_cue = self.create_clear_cue()
            cues_array.append(clear_cue)
        
        # Add background media if provided
        if config.get('background') and os.path.exists(config['background']):
            bg_cue = self.create_background_media_cue(config['background'])
            slide.insert(1, bg_cue)
        
        # Display elements array with text
        display_elements = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'displayElements'})
        
        if config.get('text'):
            text_element = self.create_text_element(
                text=config['text'],
                slide_uuid=slide_uuid,
                position=config.get('position'),
                font_size=config.get('font_size', 59),
                font_bold=config.get('font_bold', False),
                font_name=config.get('font_name', 'PingFangSC-Regular'),
                simple_format=config.get('simple_format', True),
                vertical_alignment=config.get('vertical_alignment', '0'),
                text_color=config.get('color', '#000000')
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
    
    args = parser.parse_args()
    
    generator = PP6Generator()
    
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
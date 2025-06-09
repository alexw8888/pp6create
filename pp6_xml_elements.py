"""
ProPresenter 6 XML Element Creation Module
Handles creation of various XML elements for PP6 documents
"""

import base64
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, Optional, Dict


def encode_text(text: str, font_size: int = 114, font_bold: bool = True, 
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


def create_text_element(text: str, slide_uuid: str, element_uuid: str, position: str = None, 
                      font_size: int = 114, font_bold: bool = True, 
                      font_name: str = "PingFangSC-Semibold", simple_format: bool = False,
                      vertical_alignment: str = "1", text_color: str = "#000000",
                      default_width: int = 1024) -> ET.Element:
    """Create an RVTextElement with properly encoded text"""
    rtf_encoded = encode_text(text, font_size, font_bold, font_name, simple_format, text_color)
    
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
        position_elem.text = f'{{0 69 0 {default_width} 434}}'
    
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


def create_background_media_cue(media_path: str, cue_uuid: str, element_uuid: str) -> ET.Element:
    """Create a background media cue for image or video"""
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
        'behavior': '2',  # 2 for both images and videos
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


def create_message_cue(cue_uuid: str, message_uuid: str) -> ET.Element:
    """Create an RVMessageCue element for countdown timers and automated actions"""
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


def create_clear_cue(cue_uuid: str) -> ET.Element:
    """Create an RVClearCue element for clearing props and stage displays"""
    clear_cue = ET.Element('RVClearCue', {
        'UUID': cue_uuid,
        'actionType': '4',
        'delayTime': '0.000000',
        'displayName': 'Clear Props',
        'enabled': 'false',
        'timeStamp': '0.000000'
    })
    
    return clear_cue


def create_slide(slide_uuid: str, text: str = None, background_image: str = None, 
                label: str = "", element_uuid_gen=None, width: int = 1024) -> ET.Element:
    """Create a slide with optional text content and background image"""
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
        if element_uuid_gen:
            bg_cue = create_background_media_cue(background_image, element_uuid_gen(), element_uuid_gen())
            slide.insert(1, bg_cue)  # Insert after cues array
    
    # Display elements array with text
    display_elements = ET.SubElement(slide, 'array', {'rvXMLIvarName': 'displayElements'})
    if text and element_uuid_gen:
        text_element = create_text_element(text, slide_uuid, element_uuid_gen(), default_width=width)
        display_elements.append(text_element)
    
    return slide
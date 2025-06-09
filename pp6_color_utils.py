"""
ProPresenter 6 Color Utilities Module
Handles color conversions and section color management
"""

import re
from typing import Dict


# Section colors for songs
SECTION_COLORS = {
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


def convert_color_to_rgba(color: str) -> str:
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


def get_section_color(section_name: str) -> str:
    """Get color for a section based on its type with graduated colors for verses and choruses"""
    section_lower = section_name.lower()
    
    # Try to determine section type from name
    for key in SECTION_COLORS:
        if key in section_lower:
            return SECTION_COLORS[key]
    
    # Check common abbreviations with graduated colors
    if section_lower.startswith('v'):
        # Extract number from verse (V1, V2, V3, etc.)
        number_match = re.search(r'(\d+)', section_name)
        if number_match:
            verse_num = int(number_match.group(1))
            return _get_graduated_verse_color(verse_num)
        return SECTION_COLORS['verse']
    elif section_lower.startswith('c') and not section_lower.startswith('co'):
        # Extract number from chorus (C1, C2, C3, etc.)
        number_match = re.search(r'(\d+)', section_name)
        if number_match:
            chorus_num = int(number_match.group(1))
            return _get_graduated_chorus_color(chorus_num)
        return SECTION_COLORS['chorus']
    elif section_lower.startswith('b'):
        return SECTION_COLORS['bridge']
    elif section_lower.startswith('pc'):
        return SECTION_COLORS['prechorus']
    elif section_lower.startswith('t'):
        return SECTION_COLORS['tag']
    elif section_lower.startswith('i'):
        return SECTION_COLORS['intro']
    elif section_lower.startswith('o'):
        return SECTION_COLORS['outro']
    elif section_lower.startswith('co'):
        return SECTION_COLORS['coda']
    
    return SECTION_COLORS['default']


def _get_graduated_verse_color(verse_num: int) -> str:
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


def _get_graduated_chorus_color(chorus_num: int) -> str:
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


def get_section_display_name(section_name: str) -> str:
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
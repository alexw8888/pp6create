"""
ProPresenter 6 Song Parser Module
Handles parsing of song files with sections and arrangements
"""

from typing import Dict, List, Tuple


def parse_song_file(filepath: str) -> Tuple[Dict[str, List[str]], List[str]]:
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
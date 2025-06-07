#!/usr/bin/env python3
"""
ProPresenter 6 Playlist Generator
Generates PP6 playlist directories with proper structure and data.pro6pl file
"""

import os
import shutil
import xml.etree.ElementTree as ET
import uuid
from urllib.parse import quote, unquote
from pathlib import Path
import platform
import argparse
import zipfile
from typing import List, Dict, Tuple
from generate_pp6_doc import PP6Generator  # Import existing document generator


class PP6PlaylistGenerator:
    """Generator for ProPresenter 6 playlist directories"""
    
    def __init__(self, playlist_name: str = "MyPlaylist", output_dir: str = "generated_playlist"):
        self.playlist_name = playlist_name
        self.output_dir = output_dir
        self.playlist_path = Path(output_dir)
        self.documents = []
        self.media_files = {}  # Maps source paths to destination paths
        self.os_type = 2 if platform.system() == "Darwin" else 1  # 2 for macOS, 1 for Windows
        
    def add_document(self, doc_path: str, display_name: str = None):
        """Add a ProPresenter 6 document to the playlist"""
        doc_path = Path(doc_path)
        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")
        
        if display_name is None:
            display_name = doc_path.stem
            
        self.documents.append({
            'path': doc_path,
            'display_name': display_name,
            'uuid': str(uuid.uuid4()).upper()
        })
        
    def scan_document_media(self, doc_path: Path) -> List[str]:
        """Scan a PP6 document for media references"""
        media_refs = []
        try:
            tree = ET.parse(doc_path)
            root = tree.getroot()
            
            # Find all media elements (RVImageElement and RVVideoElement)
            for elem in root.findall(".//RVImageElement") + root.findall(".//RVVideoElement"):
                source = elem.get('source')
                if source:
                    # Decode the path
                    if source.startswith('file:///'):
                        path = source[7:]  # Remove file:// prefix (keep one slash)
                    elif source.startswith('file://'):
                        path = source[7:]  # Remove file:// prefix
                    else:
                        # URL-encoded Windows path
                        path = unquote(source)
                        if self.os_type == 1:  # Windows
                            # Fix drive letter formatting
                            if len(path) > 2 and path[1] == ':':
                                path = path[0].upper() + ':\\' + path[2:].replace('/', '\\')
                    
                    media_refs.append(path)
                    
        except Exception as e:
            print(f"Error scanning document {doc_path}: {e}")
            
        return media_refs
    
    def calculate_media_destination(self, source_path: str) -> Path:
        """Calculate where to copy media file in playlist structure"""
        source = Path(source_path)
        
        # For system media (ProgramData or Renewed Vision Media)
        if 'ProgramData' in source.parts:
            idx = source.parts.index('ProgramData')
            return Path(*source.parts[idx:])
        elif 'Renewed Vision Media' in source.parts:
            idx = source.parts.index('Renewed Vision Media')
            return Path('ProgramData', 'Renewed Vision Media', *source.parts[idx+1:])
        
        # For user media, preserve the Users/username/... structure
        if 'Users' in source.parts:
            idx = source.parts.index('Users')
            return Path(*source.parts[idx:])
        
        # Fallback: put in a media subdirectory
        return Path('Media') / source.name
    
    def copy_media_file(self, source: str, relative_dest: Path):
        """Copy a media file to the playlist directory"""
        source_path = Path(source)
        if not source_path.exists():
            print(f"Warning: Media file not found: {source}")
            return
        
        dest_path = self.playlist_path / relative_dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(source_path, dest_path)
            self.media_files[str(source_path)] = relative_dest
        except Exception as e:
            print(f"Error copying media file {source}: {e}")
    
    def encode_path_for_platform(self, path: str) -> str:
        """Encode path based on platform"""
        if self.os_type == 1:  # Windows
            # Convert to Windows path and URL encode
            path = path.replace('/', '\\')
            # URL encode with specific replacements for Windows
            encoded = quote(path, safe='')
            # Windows uses specific encoding for colons and backslashes
            encoded = encoded.replace('%3A', '%3A').replace('%5C', '%5C')
            return encoded
        else:  # macOS
            # Use file:// prefix for macOS
            return f"file://{path}"
    
    def generate_playlist_xml(self) -> ET.Element:
        """Generate the data.pro6pl XML structure"""
        # Create root element
        root = ET.Element("RVPlaylistDocument")
        root.set("CCLIArtistCredits", "")
        root.set("CCLIAuthor", "")
        root.set("CCLICopyrightInfo", "")
        root.set("CCLIPublisher", "")
        root.set("CCLISongNumber", "")
        root.set("CCLISongTitle", "")
        root.set("backgroundColor", "0 0 0 1")
        root.set("creatorCode", str(self.os_type))
        root.set("docType", "0")
        root.set("drawingBackgroundColor", "false")
        root.set("height", "768")
        root.set("lastDateUsed", "2025-01-07T00:00:00")
        root.set("notes", "")
        root.set("os", str(self.os_type))
        root.set("resourcesDirectory", "")
        root.set("selectedArrangementID", "")
        root.set("usedCount", "0")
        root.set("uuid", str(uuid.uuid4()).upper())
        root.set("versionNumber", "600")
        root.set("width", "1024")
        
        # Add empty arrays
        for array_name in ["array", "arrangements", "groups"]:
            ET.SubElement(root, array_name)
        
        # Create root playlist node
        root_node = ET.SubElement(root, "RVPlaylistNode")
        root_node.set("displayName", self.playlist_name)
        root_node.set("type", "3")
        root_node.set("uuid", str(uuid.uuid4()).upper())
        
        # Create playlistNodes array
        playlist_nodes = ET.SubElement(root_node, "playlistNodes")
        
        # Add documents to playlist
        for doc in self.documents:
            doc_node = ET.SubElement(playlist_nodes, "RVPlaylistNode")
            doc_node.set("displayName", doc['display_name'])
            doc_node.set("type", "0")
            doc_node.set("uuid", doc['uuid'])
            
            # Add document cue
            doc_cue = ET.SubElement(doc_node, "RVDocumentCue")
            doc_cue.set("UUID", doc['uuid'])
            doc_cue.set("displayName", doc['display_name'])
            doc_cue.set("delayTime", "0")
            doc_cue.set("timeStamp", "0")
            
            # Set file path based on platform
            doc_filename = doc['path'].name
            if self.os_type == 2:  # macOS
                # Use tilde path for macOS
                doc_path = f"~/Documents/ProPresenter6/{doc_filename}"
            else:  # Windows
                # Use full path for Windows, URL encoded
                doc_path = f"C:\\Users\\{os.environ.get('USERNAME', 'user')}\\Documents\\ProPresenter6\\{doc_filename}"
                doc_path = quote(doc_path, safe='')
            
            doc_cue.set("filePath", doc_path)
            
            # Add empty sub-elements
            for elem in ["RVOPreset", "array", "displayTags", "flags", "notes"]:
                ET.SubElement(doc_cue, elem)
            
            # Add empty playlistNodes
            ET.SubElement(doc_node, "playlistNodes")
        
        return root
    
    def create_playlist(self, documents: List[str] = None):
        """Create a complete PP6 playlist directory"""
        # Create output directory
        self.playlist_path.mkdir(parents=True, exist_ok=True)
        
        # If documents provided, add them
        if documents:
            for doc in documents:
                self.add_document(doc)
        
        # Copy documents and scan for media
        all_media = set()
        for doc_info in self.documents:
            # Copy document to playlist
            dest_doc = self.playlist_path / doc_info['path'].name
            shutil.copy2(doc_info['path'], dest_doc)
            
            # Scan for media references
            media_refs = self.scan_document_media(doc_info['path'])
            all_media.update(media_refs)
        
        # Copy all media files
        print(f"Found {len(all_media)} media files to copy...")
        for media_path in all_media:
            if Path(media_path).exists():
                dest = self.calculate_media_destination(media_path)
                self.copy_media_file(media_path, dest)
        
        # Generate and save playlist XML
        playlist_xml = self.generate_playlist_xml()
        
        # Pretty format and save
        self.indent_xml(playlist_xml)
        tree = ET.ElementTree(playlist_xml)
        playlist_file = self.playlist_path / "data.pro6pl"
        tree.write(playlist_file, encoding='utf-8', xml_declaration=True)
        
        print(f"Playlist created at: {self.playlist_path}")
        print(f"- Documents: {len(self.documents)}")
        print(f"- Media files: {len(self.media_files)}")
    
    def indent_xml(self, elem, level=0):
        """Add pretty-print indentation to XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def create_pro6plx(self):
        """Create a .pro6plx file (zipped playlist directory)"""
        # Create the .pro6plx filename based on playlist name
        pro6plx_file = f"{self.playlist_name}.pro6plx"
        
        # Create a zip file
        with zipfile.ZipFile(pro6plx_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the playlist directory and add all files
            for root, dirs, files in os.walk(self.playlist_path):
                for file in files:
                    file_path = Path(root) / file
                    # Calculate the archive name (relative path from playlist directory)
                    arcname = file_path.relative_to(self.playlist_path.parent)
                    zipf.write(file_path, arcname)
        
        print(f"Created .pro6plx file: {pro6plx_file}")
        return pro6plx_file


def main():
    parser = argparse.ArgumentParser(description='Generate ProPresenter 6 playlists')
    parser.add_argument('--name', default='MyPlaylist', help='Playlist name')
    parser.add_argument('--output', default='generated_playlist', help='Output directory')
    parser.add_argument('--generate-docs', action='store_true', 
                       help='Generate sample documents from source_materials')
    parser.add_argument('documents', nargs='*', help='PP6 documents to include')
    
    args = parser.parse_args()
    
    # Create playlist generator
    generator = PP6PlaylistGenerator(args.name, args.output)
    
    # If no documents specified and no --generate-docs flag, automatically generate docs
    if not args.documents and not args.generate_docs:
        args.generate_docs = True
        print("No documents specified, automatically generating sample documents...")
    
    # If --generate-docs flag is set, generate documents first
    if args.generate_docs:
        print("Generating sample documents...")
        doc_generator = PP6Generator()
        
        # Generate documents from source_materials subdirectories
        source_dir = Path("source_materials")
        generated_docs = []
        
        if source_dir.exists():
            for subdir in source_dir.iterdir():
                if subdir.is_dir():
                    output_file = f"generated_{subdir.name}.pro6"
                    doc_generator.generate_from_directory(str(subdir), output_file)
                    generated_docs.append(output_file)
                    print(f"Generated: {output_file}")
        
        # Add generated documents to playlist
        for doc in generated_docs:
            generator.add_document(doc)
    
    # Add any documents specified on command line
    for doc in args.documents:
        generator.add_document(doc)
    
    # Create the playlist
    generator.create_playlist()
    
    # Create the .pro6plx file
    generator.create_pro6plx()


if __name__ == "__main__":
    main()
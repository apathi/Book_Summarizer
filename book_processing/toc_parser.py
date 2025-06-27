#!/usr/bin/env python3
"""
📋 Table of Contents Parser
Extracts chapter information from book TOCs with multi-page support
Returns both chapters and section data for precise section detection
"""

import re
import fitz
from typing import List, Dict, Optional, Tuple
from .utils import sanitize_filename


class TOCParser:
    """Handles Table of Contents extraction and parsing"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def find_toc_pages(self, pdf_path: str) -> Optional[List[int]]:
        """Find Table of Contents pages in PDF - supports multi-page TOCs"""
        try:
            with fitz.open(pdf_path) as pdf:
                toc_pages = []

                # Scan pages 3-15 for TOC start
                for page_num in range(3, min(16, len(pdf))):
                    page = pdf[page_num]
                    text = page.get_text()

                    if self._is_toc_start_page(text):
                        if self.verbose:
                            print(f"📋 Found TOC starting on page {page_num + 1}")
                        toc_pages.append(page_num)

                        # Continue checking next pages for TOC continuation
                        next_page = page_num + 1
                        max_toc_end = min(page_num + 15, len(pdf))  # Allow up to 15 pages for TOC
                        while next_page < max_toc_end:
                            next_text = pdf[next_page].get_text()

                            if self._is_toc_continuation_page(next_text):
                                if self.verbose:
                                    print(f"📋 TOC continues on page {next_page + 1}")
                                toc_pages.append(next_page)
                                next_page += 1
                            else:
                                if self.verbose:
                                    print(f"📋 TOC ends at page {next_page + 1}")
                                break
                        break

                return toc_pages if toc_pages else None

        except Exception as e:
            print(f"❌ Error finding TOC: {e}")
            return None

    def _is_toc_start_page(self, text: str) -> bool:
        """Detect if this is the start of a Table of Contents"""
        text_lower = text.lower()

        # Look for TOC indicators
        toc_indicators = [
            "table of contents",
            "contents",
        ]

        has_toc_header = any(indicator in text_lower for indicator in toc_indicators)

        # Must also have chapter patterns
        chapter_patterns = [
            r'chapter\s+\d+',
            r'\d+\.\s+\w+.*\d+',  # "1. Chapter Name ... 25"
            r'chapter\s+[ivx]+',  # Roman numerals
        ]

        has_chapters = any(re.search(pattern, text_lower) for pattern in chapter_patterns)

        return has_toc_header and has_chapters

    def _is_toc_continuation_page(self, text: str) -> bool:
        """Detect if this page continues the Table of Contents"""
        text_lower = text.lower()

        # Look for chapter continuation patterns
        continuation_patterns = [
            r'chapter\s+\d+',  # "chapter 30"
            r'\d+\.\s+\w+.*\d+',  # "30. Building a Team ... 450"
            r'appendix\s+[a-z]',  # "appendix a"
            r'interview\s+\d+',  # "interview 1"
            r'acknowledgments',  # end matter
            r'index',  # end matter
            r'bibliography',  # end matter
        ]

        # Must have multiple chapter-like entries (not just one stray reference)
        chapter_matches = 0
        for pattern in continuation_patterns:
            matches = re.findall(pattern, text_lower)
            chapter_matches += len(matches)

        # If we have 2+ chapter-like entries, likely a TOC continuation
        if chapter_matches >= 2:
            return True

        # Check for TOC end indicators
        end_indicators = [
            r'^\s*\d+\s*$',  # Just page numbers alone
            r'preface',
            r'introduction\s*$',  # Introduction as separate section
            r'part\s+i\b',  # "Part I" (start of content)
        ]

        # If we see end indicators, stop TOC parsing
        for pattern in end_indicators:
            if re.search(pattern, text_lower):
                return False

        return chapter_matches >= 1  # At least 1 chapter-like entry

    def extract_chapters_from_toc(self, pdf_path: str, toc_pages: List[int]) -> Tuple[List[Dict], Dict[str, Dict]]:
        """Extract chapter information and section data from multi-page Table of Contents"""
        if not toc_pages:
            return [], {}

        try:
            with fitz.open(pdf_path) as pdf:
                all_toc_text = ""

                # Combine text from all TOC pages
                for page_num in toc_pages:
                    page = pdf[page_num]
                    page_text = page.get_text()
                    all_toc_text += page_text + "\n"

                # Parse combined TOC text
                lines = all_toc_text.split('\n')
                if self.verbose:
                    print(f"🔍 Parsing {len(lines)} TOC lines from {len(toc_pages)} pages...")

                chapters = []
                sections = {}  # New: track section information for precise detection
                current_section = None
                current_section_title = None
                
                # Track if we find Part-based sections to infer Part I if missing
                found_part_sections = False

                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue

                    # Check for Part-based sections first (Part I, Part II, etc.)
                    part_match = re.match(r'^Part\s+([IVX]+|[1-9]|[1-9]\d*):\s*(.+)', line, re.IGNORECASE)
                    if part_match:
                        part_num = part_match.group(1)
                        part_title = part_match.group(2).strip()
                        
                        # Convert Part number to letter for consistency (Part I -> A, Part II -> B, etc.)
                        if part_num in ['I', '1']:
                            section_letter = 'A'
                        elif part_num in ['II', '2']:
                            section_letter = 'B'
                        elif part_num in ['III', '3']:
                            section_letter = 'C'
                        elif part_num in ['IV', '4']:
                            section_letter = 'D'
                        elif part_num in ['V', '5']:
                            section_letter = 'E'
                        else:
                            # For Part VI+ or unusual numbering, continue with F, G, etc.
                            section_letter = chr(ord('F') + int(part_num) - 6) if part_num.isdigit() else 'F'
                        
                        # Store section information
                        sections[section_letter] = {
                            'title': part_title,
                            'letter': section_letter,
                            'full_title': f"Part {part_num}: {part_title}",
                            'part_num': part_num,
                            'is_part_based': True
                        }
                        
                        current_section = section_letter
                        current_section_title = part_title
                        found_part_sections = True
                        
                        if self.verbose:
                            print(f"📂 Found Part-based section: Part {part_num}: {part_title} (mapped to {section_letter})")
                        continue
                    
                    # Check for traditional section headers (A. Something, B. Something, etc.)
                    section_match = re.match(r'^([A-Z])\.\s*(.+)', line)
                    if section_match:
                        section_letter = section_match.group(1)
                        section_title = section_match.group(2).strip()

                        # Store section information for chapter detector
                        sections[section_letter] = {
                            'title': section_title,
                            'letter': section_letter,
                            'full_title': f"{section_letter}. {section_title}",
                            'is_part_based': False
                        }

                        current_section = section_letter
                        current_section_title = section_title

                        if self.verbose:
                            print(f"📂 Found section: {section_letter}. {section_title}")
                        continue

                    # Check for chapter patterns - enhanced for multi-line format
                    chapter_patterns = [
                        r'^(\d+)\.\s*(.+?)(?:\s+(\d+))?$',  # "1. Chapter Name 25"
                        r'^CHAPTER\s+(\d+)\s+(.+?)(?:\s+(\d+))?$',  # "CHAPTER 1 NAME 25"
                        r'^Chapter\s+(\d+):\s*(.+?)(?:\s+(\d+))?$',  # "Chapter 1: Name 25"
                        r'^Chapter\s+(\d+):\s*(.+?)\s+(\d+)$',  # "Chapter 1: Understanding the Infrastructure ... 3"
                        r'^Chapter\s+(\d+):\s*(.+?)\s*(\d+)\s*$',  # "Chapter 1: Title 3" (flexible spacing)
                        r'^Chapter\s+(\d+):\s*(.+?)\s*[\x08]*\s*$',  # "Chapter 1: Title" with backspace chars - NEW for multi-line
                    ]

                    for pattern in chapter_patterns:
                        match = re.match(pattern, line, re.IGNORECASE)
                        if match:
                            chapter_id = match.group(1)
                            title = match.group(2).strip()
                            page_num = match.group(3) if len(match.groups()) >= 3 and match.group(3) else None

                            # NEW: If no page number found in same line, check next line
                            if not page_num and i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if next_line.isdigit():
                                    page_num = next_line
                                    if self.verbose:
                                        print(f"📋 Found page number on next line: {page_num}")

                            # Clean up title (remove page numbers, dots, backspace chars, etc.)
                            title = re.sub(r'\s*\.+\s*\d*$', '', title)
                            title = re.sub(r'\s*[\x08]+\s*$', '', title)  # Remove backspace chars
                            title = title.strip()

                            chapter = {
                                'id': chapter_id,
                                'title': title,
                                'page': int(page_num) if page_num else None,
                                'section': current_section,
                                'section_title': current_section_title,
                                'source': 'toc'
                            }

                            chapters.append(chapter)
                            if self.verbose:
                                print(f"📖 Found chapter: {chapter_id}. {title} (page {page_num})")
                            break

                # Handle missing Part I inference
                if found_part_sections and 'A' not in sections and 'B' in sections:
                    # We found Part II but not Part I - infer Part I exists
                    # Find chapters before the first chapter of Part II
                    first_part_b_chapter = None
                    for ch in chapters:
                        if ch.get('section') == 'B':
                            first_part_b_chapter = ch
                            break
                    
                    # Assign early chapters to Part I
                    if first_part_b_chapter:
                        for ch in chapters:
                            if ch.get('section') is None:
                                # Check if this chapter comes before Part II's first chapter
                                ch_id = int(ch['id']) if ch['id'].isdigit() else 999
                                part_b_id = int(first_part_b_chapter['id']) if first_part_b_chapter['id'].isdigit() else 999
                                
                                if ch_id < part_b_id:
                                    ch['section'] = 'A'
                                    ch['section_title'] = 'Lay of the Land'  # Generic title
                        
                        # Add inferred Part I to sections
                        sections['A'] = {
                            'title': 'Lay of the Land',
                            'letter': 'A', 
                            'full_title': 'Part I: Lay of the Land',
                            'part_num': 'I',
                            'is_part_based': True,
                            'inferred': True
                        }
                        
                        if self.verbose:
                            print("📂 Inferred Part I from chapter structure")

                if self.verbose:
                    section_count = len(sections)
                    print(f"✅ Parsed: {section_count} sections, {len(chapters)} chapters")

                    # Show section summary for debugging
                    if sections:
                        print("📋 Sections found:")
                        for letter, info in sections.items():
                            title_suffix = " (inferred)" if info.get('inferred') else ""
                            print(f"   {letter}: {info['title']}{title_suffix}")

                return chapters, sections

        except Exception as e:
            print(f"❌ Error extracting TOC chapters: {e}")
            return [], {}
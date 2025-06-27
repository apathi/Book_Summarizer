#!/usr/bin/env python3
"""
🔍 Chapter Detector
Scans PDFs to find actual chapter start pages with position-based section detection
Clean implementation focused on accuracy
"""

import re
import fitz
from typing import Dict, List, Optional, Tuple
from .utils import format_page_range


class ChapterDetector:
    """Detects chapter boundaries in PDF documents with position-based section detection"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def scan_for_chapters(self, pdf_path: str, toc_pages: list = None, toc_sections: dict = None,
                          toc_chapters: list = None) -> Dict[str, int]:
        """Scan PDF for actual chapter start pages with position-based section detection"""
        found_pages = {}

        # DEBUG: Check what we received
        if self.verbose:
            print(f"🔍 DEBUG: toc_chapters received: {toc_chapters is not None}")
            if toc_chapters:
                print(f"   📊 TOC chapters count: {len(toc_chapters)}")
                # Safe string concatenation handling None values
                sample_info = []
                for ch in toc_chapters[:3]:
                    ch_id = ch.get('id', 'None')
                    ch_section = ch.get('section', 'No-section')
                    if ch_id is None:
                        ch_id = 'None'
                    if ch_section is None:
                        ch_section = 'No-section'
                    sample_info.append(f"{ch_id}:{ch_section}")
                print(f"   📋 Sample chapters: {sample_info}")

        # Extract section first chapters dynamically from TOC data (with fallback)
        if toc_chapters:
            section_first_chapters = self._extract_section_first_chapters(toc_chapters)
            if self.verbose:
                print(f"🎯 Dynamically found section first chapters: {section_first_chapters}")
        else:
            # Fallback to hardcoded for safety
            section_first_chapters = {
                'C': '4',  # Product Skills starts with Chapter 4
                'D': '10',  # Execution Skills starts with Chapter 10
                'E': '14',  # Strategic Skills starts with Chapter 14
                'F': '19',  # Leadership Skills starts with Chapter 19
                'G': '27',  # People Management starts with Chapter 27
                'H': '32',  # Careers starts with Chapter 32
                'I': '37',  # Product Leader Q&A starts with Chapter 37
                'J': '48',  # Additional Reading starts with Chapter 48
            }
            if self.verbose:
                print(f"🎯 Using fallback hardcoded section first chapters: {section_first_chapters}")

        first_chapter_ids = list(section_first_chapters.values())

        if self.verbose:
            print(f"🎯 Section first chapters to enhance: {first_chapter_ids}")
            if not section_first_chapters:
                print("📋 No sections found - will process as flat chapter structure")
                print("🚫 Section page enhancement will be skipped")

        try:
            # SMART TOC DETECTION: Check if TOC already has page numbers
            toc_has_pages = False
            if toc_chapters:
                pages_count = sum(1 for ch in toc_chapters if ch.get('page') is not None and ch.get('page') != 0)
                toc_has_pages = pages_count > 0
                if self.verbose:
                    print(f"📊 TOC chapters with page numbers: {pages_count}/{len(toc_chapters)}")

            if toc_has_pages:
                # TOC already has page numbers - use them directly
                if self.verbose:
                    print("✅ TOC contains page numbers - using TOC pages directly")
                    print("🚫 Skipping PDF pattern scanning")

                # Extract page numbers directly from TOC
                for chapter in toc_chapters:
                    chapter_id = chapter.get('id')
                    page_num = chapter.get('page')
                    if chapter_id and page_num:
                        found_pages[chapter_id] = {'page': page_num, 'type': 'toc', 'source_page': page_num}
                        if self.verbose:
                            print(f"📖 Chapter {chapter_id} from TOC: page {page_num}")

                if self.verbose:
                    print(f"✅ Found {len(found_pages)} chapters from TOC")

            else:
                # TOC missing page numbers - use original PDF scanning logic
                if self.verbose:
                    print("🔍 TOC missing page numbers - scanning PDF for chapter patterns")

                # Set up skip pages
                skip_pages = set()
                if toc_pages:
                    for toc_page in toc_pages:
                        skip_pages.add(toc_page)
                else:
                    skip_pages = set(range(3))

                found_pages = self._scan_pdf_for_chapters(pdf_path, toc_pages, skip_pages)

            # Apply section enhancement if needed
            if section_first_chapters and first_chapter_ids:
                # Books WITH sections - apply section page enhancement
                with fitz.open(pdf_path) as pdf:
                    enhanced_pages = self._enhance_with_section_pages(found_pages, pdf, first_chapter_ids)
                if self.verbose:
                    print("✅ Section enhancement applied")
            else:
                # Books WITHOUT sections - use chapters as-is
                enhanced_pages = found_pages
                if self.verbose:
                    print("✅ No section enhancement needed - using flat chapter structure")

            # Convert to simple format
            simple_found_pages = {}
            for chapter_id, chapter_data in enhanced_pages.items():
                simple_found_pages[chapter_id] = chapter_data['page']

            return simple_found_pages

        except Exception as e:
            print(f"❌ Error scanning for chapters: {e}")
            return {}

    def scan_for_chapters_epub_only(self, epub_path: str, toc_pages: list = None, toc_sections: dict = None) -> Dict[
        str, int]:
        """Simple EPUB chapter scanning - NO PDF logic, NO sections, NO smart detection"""

        if self.verbose:
            print("📖 EPUB-only chapter scanning (no PDF features)")

        # For EPUB, just return empty - let EPUB processor handle everything
        return {}

    def _extract_section_first_chapters(self, toc_chapters: list) -> dict:
        """Extract first chapter of each section from TOC data"""

        if not toc_chapters:
            return {}

        section_first_chapters = {}

        # Group chapters by section and find the first one
        for chapter in sorted(toc_chapters, key=lambda x: int(x['id']) if x['id'].isdigit() else 999):
            section = chapter.get('section')
            if section and section not in section_first_chapters:
                section_first_chapters[section] = chapter['id']
                if self.verbose:
                    print(f"📋 Section {section} starts with Chapter {chapter['id']}")

        return section_first_chapters

    def _scan_pdf_for_chapters(self, pdf_path: str, toc_pages: list, skip_pages: set) -> dict:
        """Original PDF scanning logic extracted as separate method"""
        found_pages = {}

        try:
            with fitz.open(pdf_path) as pdf:
                if self.verbose:
                    print("🔍 Scanning PDF for actual chapter pages...")

                total_pages = len(pdf)
                progress_interval = max(1, total_pages // 20)

                # Configure skip pages
                if toc_pages:
                    for toc_page in toc_pages:
                        skip_pages.add(toc_page)
                    if self.verbose:
                        print(f"🚫 Skipping TOC pages: {sorted(skip_pages)}")
                else:
                    skip_pages = set(range(3))

                for page_num in range(total_pages):
                    if page_num in skip_pages:
                        continue

                    page = pdf[page_num]
                    text = page.get_text()

                    # Show progress
                    if self.verbose and (page_num % progress_interval == 0 or page_num == total_pages - 1):
                        progress = (page_num + 1) / total_pages * 100
                        print(f"🔄 Scanning page {page_num + 1}/{total_pages} ({progress:.1f}%)")

                    # Debug section-like pages
                    chapter_references = len(re.findall(r'Chapter\s+\d+', text, re.IGNORECASE))
                    if self.verbose and chapter_references > 3:
                        print(f"🔍 SECTION PAGE DEBUG - Page {page_num + 1}:")
                        print(f"  📊 Chapter references: {chapter_references}")

                    # Find real chapter headers
                    primary_patterns = [r'^\s*CHAPTER\s+(\d+)(?:\s*$|\s*\n)']
                    found_real_chapter = False

                    for pattern in primary_patterns:
                        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                        for match in matches:
                            chapter_id = match.group(1)

                            if self._validate_chapter_conditionally(text, match, page_num, chapter_id):
                                if self._add_chapter_with_override(found_pages, chapter_id, page_num + 1, 'real'):
                                    found_real_chapter = True
                                    if self.verbose:
                                        print(f"📖 Found CHAPTER {chapter_id} on page {page_num + 1}")

                    # Fallback: references
                    if not found_real_chapter:
                        fallback_patterns = [r'^\s*Chapter\s+(\d+):']
                        for pattern in fallback_patterns:
                            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                            for match in matches:
                                chapter_id = match.group(1)
                                if self._basic_validate_chapter(text, match, page_num):
                                    if self._add_chapter_with_override(found_pages, chapter_id, page_num + 1,
                                                                       'reference'):
                                        if self.verbose:
                                            print(f"📖 Found Chapter {chapter_id} (reference) on page {page_num + 1}")

                if self.verbose:
                    print(f"✅ Found {len(found_pages)} actual chapter pages")

                return found_pages

        except Exception as e:
            print(f"❌ Error scanning for chapters: {e}")
            return {}

    def _enhance_with_section_pages(self, found_pages: dict, pdf, first_chapter_ids: list) -> dict:
        """Enhance chapter page assignments to include section pages for first chapters"""

        if self.verbose:
            print("\n🎯 STEP 2.5: Position-based section page enhancement...")

        enhanced_pages = {}

        for chapter_id, chapter_data in found_pages.items():
            original_page = chapter_data['page']

            if chapter_id in first_chapter_ids:
                # This is the first chapter of a section - look for section page
                if self.verbose:
                    print(f"\n🔍 Analyzing Chapter {chapter_id} (first chapter of section):")
                    print(f"  📖 Originally detected on page {original_page}")

                section_page = self._find_section_page_for_chapter(chapter_id, original_page, pdf)

                if section_page != original_page:
                    # Found a section page - update the assignment
                    enhanced_pages[chapter_id] = {
                        'page': section_page,
                        'type': 'real_with_section',
                        'source_page': original_page,
                        'section_page': section_page
                    }
                    if self.verbose:
                        print(
                            f"  ✅ Enhanced: Chapter {chapter_id} now starts on page {section_page} (includes section)")
                        print(f"     └── Section page: {section_page}, Real chapter: {original_page}")
                else:
                    # No section page found - keep original
                    enhanced_pages[chapter_id] = chapter_data
                    if self.verbose:
                        print(f"  ⚠️  No section page found - keeping original page {original_page}")
            else:
                # Not a first chapter - keep original assignment
                enhanced_pages[chapter_id] = chapter_data
                if self.verbose and chapter_id in ['5', '11', '15', '20']:  # Sample some non-first chapters
                    print(f"  📄 Chapter {chapter_id}: keeping original page {original_page} (not section start)")

        if self.verbose:
            section_enhanced = sum(1 for data in enhanced_pages.values() if data.get('type') == 'real_with_section')
            print(f"\n✅ Section enhancement complete: {section_enhanced} chapters enhanced with section pages")

        return enhanced_pages

    def _find_section_page_for_chapter(self, chapter_id: str, chapter_page: int, pdf) -> int:
        """Find the section page for a first chapter by looking backward for section indicators"""

        if self.verbose:
            print(f"    🔍 Looking for section page before Chapter {chapter_id} (page {chapter_page})...")

        # Look 1-4 pages back for section indicators (graphics or Part headers)
        for lookback in range(1, 5):  # Check pages -1, -2, -3, -4
            candidate_page = chapter_page - lookback

            if candidate_page <= 0 or candidate_page > len(pdf):
                continue

            try:
                # Get text from candidate page (convert to 0-based indexing)
                text = pdf[candidate_page - 1].get_text()
                is_minimal = self._is_minimal_content_page(text)
                is_part_page = self._is_part_section_page(text)

                if self.verbose:
                    lines_count = len([line.strip() for line in text.split('\n') if line.strip()])
                    print(f"      📄 Page {candidate_page}: {lines_count} lines, minimal={is_minimal}, part_page={is_part_page}")

                    # Show first few lines for debugging
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if lines:
                        preview_lines = lines[:3]  # First 3 lines
                        print(f"        └── Content preview: {preview_lines}")
                    else:
                        print(f"        └── Content preview: [EMPTY]")

                if is_minimal or is_part_page:
                    if self.verbose:
                        section_type = "Part section" if is_part_page else "minimal content"
                        print(f"    ✅ Found section page: {candidate_page} ({section_type})")
                    return candidate_page

            except Exception as e:
                if self.verbose:
                    print(f"      ❌ Error reading page {candidate_page}: {e}")
                continue

        if self.verbose:
            print(f"    ⚠️  No section page found - using original page {chapter_page}")
        return chapter_page

    def _is_minimal_content_page(self, text: str) -> bool:
        """Check if page has minimal content (likely graphics/section page)"""

        if not text or not text.strip():
            return True  # Empty page

        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Very strict threshold - graphics pages should have almost no extractable text
        # Usually just page numbers, minimal metadata, or footer text
        return len(lines) <= 2
    
    def _is_part_section_page(self, text: str) -> bool:
        """Check if page contains Part section header (Part I, Part II, etc.)"""
        
        if not text or not text.strip():
            return False
        
        # Look for Part section patterns
        part_patterns = [
            r'\bPart\s+[IVX]+\b',           # Part I, Part II, Part III, Part IV, Part V
            r'\bPart\s+[1-9]\b',            # Part 1, Part 2, Part 3
            r'\bPART\s+[IVX]+\b',           # PART I, PART II (uppercase)
            r'\bPART\s+[1-9]\b',            # PART 1, PART 2 (uppercase)
        ]
        
        text_upper = text.upper()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Check if any line contains a Part pattern
        for line in lines[:10]:  # Check first 10 lines
            for pattern in part_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Additional validation: Part pages typically have limited content
                    # Usually just the Part header and maybe a subtitle
                    if len(lines) <= 15:  # Part pages are usually sparse
                        if self.verbose:
                            print(f"        └── Detected Part section: {line}")
                        return True
        
        return False

    def _add_chapter_with_override(self, found_pages: dict, chapter_id: str, page_num: int, chapter_type: str) -> bool:
        """Add chapter with override logic"""

        if chapter_id in found_pages:
            existing_data = found_pages[chapter_id]
            existing_type = existing_data['type']

            if chapter_type == 'real' and existing_type == 'reference':
                found_pages[chapter_id] = {'page': page_num, 'type': 'real', 'source_page': page_num}
                if self.verbose:
                    print(
                        f"🔄 Overriding Chapter {chapter_id}: reference (page {existing_data['page']}) → real (page {page_num})")
                return True
            elif chapter_type == 'reference' and existing_type == 'real':
                if self.verbose:
                    print(f"⚠️ Skipping Chapter {chapter_id} reference on page {page_num} - real chapter already found")
                return False
            elif chapter_type == 'reference' and existing_type == 'reference':
                if self.verbose:
                    print(f"⚠️ Skipping Chapter {chapter_id} reference on page {page_num} - reference already found")
                return False
        else:
            found_pages[chapter_id] = {'page': page_num, 'type': chapter_type, 'source_page': page_num}
            return True

        return False

    def _validate_chapter_conditionally(self, text: str, match, page_num: int, chapter_id: str) -> bool:
        """Conditional validation for chapters"""

        match_start = match.start()
        line_start = text.rfind('\n', 0, match_start) + 1
        line_end = text.find('\n', match_start)
        if line_end == -1:
            line_end = len(text)

        line_with_match = text[line_start:line_end].strip()

        # Must be proper format
        if not re.match(r'^\s*CHAPTER\s+\d+\s*$', line_with_match, re.IGNORECASE):
            return False

        # Basic position check
        text_before_match = text[line_start:match_start].strip()
        if len(text_before_match) > 10:
            return False

        # Check page type
        chapter_references = len(re.findall(r'Chapter\s+\d+', text, re.IGNORECASE))

        if chapter_references > 3:
            # Multi-chapter page - strict validation
            return self._strict_validate_chapter(text, match, page_num, chapter_id)
        else:
            # Single chapter page - basic validation
            if self.verbose:
                print(f"  ✅ Single chapter page for Chapter {chapter_id} - basic validation")
            return True

    def _strict_validate_chapter(self, text: str, match, page_num: int, chapter_id: str) -> bool:
        """Strict validation for multi-chapter pages"""

        # Check for content after header
        text_after_match = text[match.end():]
        lines_after = text_after_match.split('\n')[:8]
        content_lines = [line.strip() for line in lines_after if line.strip()]

        substantial_content = 0
        for line in content_lines:
            if len(line) > 30 and not line.startswith('Chapter') and ':' not in line[:15]:
                substantial_content += 1

        if substantial_content < 1:
            if self.verbose:
                print(f"  ⚠️ Chapter {chapter_id} on page {page_num + 1}: insufficient content")
            return False

        # Check for section header
        section_keywords = ['PRODUCT SKILLS', 'EXECUTION SKILLS', 'STRATEGIC SKILLS', 'LEADERSHIP SKILLS',
                            'MANAGEMENT SKILLS']
        text_before_match = text[:match.start()]
        has_section_header = any(keyword in text_before_match.upper() for keyword in section_keywords)

        if has_section_header:
            if self.verbose:
                print(f"  ✅ Chapter {chapter_id} on page {page_num + 1}: real chapter after section header")
            return True
        else:
            if self.verbose:
                print(f"  ⚠️ Chapter {chapter_id} on page {page_num + 1}: no section header, likely reference")
            return False

    def _basic_validate_chapter(self, text: str, match, page_num: int) -> bool:
        """Basic validation for reference patterns"""

        match_start = match.start()
        line_start = text.rfind('\n', 0, match_start) + 1
        line_end = text.find('\n', match_start)
        if line_end == -1:
            line_end = len(text)

        line_with_match = text[line_start:line_end].strip()
        text_before_match = text[line_start:match_start].strip()

        if len(text_before_match) > 5:
            return False

        if '...' in line_with_match or line_with_match.count('.') > 3:
            return False

        return True

    def merge_toc_with_pages(self, toc_chapters: List[Dict], found_pages: Dict[str, int]) -> List[Dict]:
        """Merge TOC chapters with actual page numbers"""
        if self.verbose:
            print("🔗 Merging TOC with actual page numbers...")

        merged_chapters = []
        toc_ids = {ch['id'] for ch in toc_chapters}
        pdf_ids = set(found_pages.keys())
        all_ids = toc_ids | pdf_ids

        for chapter_id in sorted(all_ids, key=lambda x: int(x) if x.isdigit() else 999):
            if chapter_id in toc_ids:
                chapter = next(ch for ch in toc_chapters if ch['id'] == chapter_id)
                if chapter_id in pdf_ids:
                    chapter['page'] = found_pages[chapter_id]
                    chapter['source'] = 'pattern'
                    if self.verbose:
                        print(f"✅ Chapter {chapter_id} from pattern: page {found_pages[chapter_id]}")
                merged_chapters.append(chapter)
            else:
                chapter = {
                    'id': chapter_id,
                    'title': f'Chapter {chapter_id}',
                    'page': found_pages[chapter_id],
                    'section': 'Additional',
                    'section_title': 'Additional Chapters',
                    'source': 'pdf_only'
                }
                merged_chapters.append(chapter)
                if self.verbose:
                    print(f"✅ Chapter {chapter_id} from PDF only: page {found_pages[chapter_id]}")

        return merged_chapters

    def calculate_page_ranges(self, chapters: List[Dict], total_pages: int) -> List[Dict]:
        """Calculate page ranges for each chapter"""
        if self.verbose:
            print("📊 Calculating page ranges...")

        sorted_chapters = sorted(chapters, key=lambda x: x.get('page') or 0)

        for i, chapter in enumerate(sorted_chapters):
            start_page = chapter.get('page')
            if start_page is None:
                continue

            chapter['start_page'] = start_page

            if i < len(sorted_chapters) - 1:
                next_chapter = sorted_chapters[i + 1]
                next_page = next_chapter.get('page')
                if next_page:
                    chapter['end_page'] = next_page - 1
                else:
                    chapter['end_page'] = None
            else:
                chapter['end_page'] = None

            # Validate ranges
            end_page = chapter['end_page']
            if end_page is not None and end_page < start_page:
                if self.verbose:
                    print(f"⚠️ Invalid page range for Chapter {chapter['id']}: {start_page}-{end_page}")
                chapter['end_page'] = start_page + 1
                if self.verbose:
                    print(f"🔧 Fixed to: {start_page}-{chapter['end_page']}")

            chapter['page_range'] = format_page_range(start_page, chapter['end_page'])

            if self.verbose:
                title = chapter.get('title', f"Chapter {chapter['id']}")
                print(f"📖 Chapter {chapter['id']}: {title}... ({chapter['page_range']})")

        return sorted_chapters
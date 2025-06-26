#!/usr/bin/env python3
"""
📊 Report Generator
Creates processing reports and manages output organization
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from .utils import estimate_file_size, sanitize_filename


class ReportGenerator:
    """Handles report generation and output organization"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def generate_processing_report(self, book_name: str, file_type: str,
                                   chapters: List[Dict], extracted_files: List[str],
                                   output_path: Path) -> Dict:
        """Generate comprehensive processing report"""

        # Clean chapters data for JSON serialization (remove EPUB objects)
        clean_chapters = []
        for chapter in chapters:
            if isinstance(chapter, dict):
                clean_chapter = {}
                for key, value in chapter.items():
                    if key == 'item':
                        # Skip EPUB item objects that can't be serialized
                        continue
                    elif key == 'content' and hasattr(value, 'decode'):
                        # Convert bytes content to string
                        try:
                            clean_chapter[key] = value.decode('utf-8', errors='ignore')[
                                                 :500] + "..."  # Truncate for JSON
                        except:
                            clean_chapter[key] = str(value)[:500] + "..."
                    else:
                        clean_chapter[key] = value
                clean_chapters.append(clean_chapter)
            else:
                clean_chapters.append(chapter)

        report = {
            "book_info": {
                "book_name": book_name,
                "file_type": file_type,
                "total_chapters": len(chapters),
                "total_files": len(extracted_files) if extracted_files else 0,
                "processing_date": datetime.now().isoformat()
            },
            "chapters": clean_chapters,
            "extracted_files": extracted_files if extracted_files else []
        }

        # Save report to JSON file
        report_file = output_path / f"{book_name}_processing_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            if self.verbose:
                print(f"📋 Processing report saved: {report_file.name}")

        except Exception as e:
            print(f"⚠️  Could not save processing report: {e}")

        return report

    def create_extraction_preview(self, book_name: str, chapters: List[Dict],
                                  output_path: Path) -> str:
        """Create visual preview of extraction plan"""

        preview = f"\n📋 EXTRACTION PREVIEW for '{book_name}'\n"
        preview += "=" * 70 + "\n"
        preview += f"📁 {book_name}_chapters/\n"

        # Group chapters by section with proper None handling
        sections = {}
        for chapter in chapters:
            section = chapter.get('section', 'Unknown')
            section_title = chapter.get('section_title', 'Unknown Section')

            # FIXED: Handle None section_title (common in flat structure books)
            if section_title is None:
                section_title = 'Chapters'

            # Create section key with proper None handling
            if section and section != 'Unknown':
                section_key = f"{section}._{section_title.replace(' ', '_')}"
            else:
                section_key = sanitize_filename(section_title)

            if section_key not in sections:
                sections[section_key] = []
            sections[section_key].append(chapter)

        # Generate preview by section
        total_pages = 0
        for section_key, section_chapters in sections.items():
            preview += f"├── 📁 {section_key}/\n"

            for chapter in sorted(section_chapters,
                                  key=lambda x: int(x.get('id', 0)) if str(x.get('id', '')).isdigit() else 999):
                chapter_id = chapter.get('id', '?')
                title = chapter.get('title', 'Unknown')
                page_range = chapter.get('page_range', 'unknown pages')

                # Calculate page count
                start_page = chapter.get('start_page', 0)
                end_page = chapter.get('end_page')
                if end_page and start_page:
                    page_count = end_page - start_page + 1
                    total_pages += page_count
                else:
                    page_count = 0  # Unknown for last chapter

                file_size = estimate_file_size(page_count)
                safe_title = sanitize_filename(title)
                filename = f"Chapter_{chapter_id}-{safe_title}.pdf"

                preview += f"│   ├── {filename} ({page_range})\n"
                preview += f"│   │   📄 {page_count} pages, ~{file_size}\n"

        preview += f"└── 📋 {book_name}_processing_report.json\n\n"
        preview += "=" * 70 + "\n"
        preview += "📊 SUMMARY:\n"
        preview += f"   • Total chapters: {len(chapters)}\n"
        preview += f"   • Total pages: ~{total_pages}\n"

        # Estimate total size
        if total_pages < 50:
            total_size = "~5MB+"
        elif total_pages < 200:
            total_size = "~10-20MB"
        elif total_pages < 500:
            total_size = "~20-50MB"
        else:
            total_size = "~50MB+"

        preview += f"   • Estimated total size: {total_size}\n"
        preview += "=" * 70 + "\n"

        return preview

    def print_processing_summary(self, chapters: List[Dict], extracted_files: List[str]):
        """Print final processing summary"""

        total_extracted = len(extracted_files) if extracted_files else 0
        print(f"\n🎉 Complete! Extracted {total_extracted} chapters")

        if self.verbose:
            # Show section breakdown with proper None handling
            print("📊 Chapters by section:")

            section_counts = {}
            for chapter in chapters:
                section = chapter.get('section_title', 'Unknown Section')

                # Handle None section for flat structure books
                if section is None:
                    section = 'Chapters'  # Default for books without sections

                if section not in section_counts:
                    section_counts[section] = 0
                section_counts[section] += 1

            # Display summary
            for section, count in section_counts.items():
                # Extra safety check - ensure section is never None
                if section is None:
                    section = 'Chapters'
                clean_section = section.replace('_', ' ')
                print(f"   • {clean_section}: {count} chapters")

    def organize_output_structure(self, chapters: List[Dict], base_output_path: Path) -> Dict[str, Path]:
        """Create organized directory structure for chapters"""

        section_dirs = {}

        # Create directories for each section with proper None handling
        for chapter in chapters:
            section = chapter.get('section', 'Unknown')
            section_title = chapter.get('section_title', 'Unknown Section')

            # Handle None section_title (common in flat structure books)
            if section_title is None:
                section_title = 'Chapters'

            # Create section key with proper None handling
            if section and section != 'Unknown':
                section_key = f"{section}._{section_title.replace(' ', '_')}"
            else:
                section_key = sanitize_filename(section_title)

            if section_key not in section_dirs:
                section_dir = base_output_path / section_key
                section_dir.mkdir(parents=True, exist_ok=True)
                section_dirs[section_key] = section_dir

                if self.verbose:
                    print(f"📁 Created: {section_key}")

        return section_dirs
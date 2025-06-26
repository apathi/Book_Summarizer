#!/usr/bin/env python3
"""
📄 Enhanced PDF Processor
Complete PDF processing workflow with TOC parsing, chapter detection, and extraction
"""

from pathlib import Path
from typing import List, Dict
from .toc_parser import TOCParser
from .chapter_detector import ChapterDetector
from .report_generator import ReportGenerator
from .utils import sanitize_filename


class PDFProcessor:
    """Enhanced PDF processor with complete workflow"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.toc_parser = TOCParser(verbose=verbose)
        self.chapter_detector = ChapterDetector(verbose=verbose)
        self.report_generator = ReportGenerator(verbose=verbose)

    def process_pdf_book(self, pdf_path: str, output_dir: str) -> bool:
        """Complete PDF processing workflow - moved from main.py"""

        try:
            pdf_path = Path(pdf_path)
            book_name = pdf_path.stem

            if self.verbose:
                print(f"🚀 Processing .PDF: {pdf_path}")

            # STEP 1: Parse TOC (with sections and chapters)
            if self.verbose:
                print("\n📋 STEP 1: Finding Table of Contents...")

            toc_pages = self.toc_parser.find_toc_pages(pdf_path)
            toc_chapters, toc_sections = self.toc_parser.extract_chapters_from_toc(pdf_path, toc_pages)

            if not toc_chapters:
                print("❌ No chapters found in Table of Contents")
                return False

            # STEP 2: Scan for actual chapter pages
            if self.verbose:
                print("\n🔍 STEP 2: Scanning for chapter pages...")

            found_pages = self.chapter_detector.scan_for_chapters(pdf_path, toc_pages, toc_sections, toc_chapters)

            if not found_pages:
                print("❌ No chapter pages detected")
                return False

            # STEP 3: Merge TOC with actual pages
            if self.verbose:
                print("\n🔗 STEP 3: Merging TOC with found pages...")

            final_chapters = self.chapter_detector.merge_toc_with_pages(toc_chapters, found_pages)

            # STEP 4: Calculate page ranges
            if self.verbose:
                print("\n📊 STEP 4: Calculating page ranges...")

            total_pages = self._get_pdf_page_count(pdf_path)
            final_chapters = self.chapter_detector.calculate_page_ranges(final_chapters, total_pages)

            # STEP 5: Show preview and get confirmation
            output_path = Path(output_dir) / f"{book_name}_chapters"
            if self.verbose:
                print("\n👀 STEP 5: Preview...")
                preview = self.report_generator.create_extraction_preview(book_name, final_chapters, output_path)
                print(preview)

            if not self._get_user_confirmation():
                print("❌ Processing cancelled by user")
                return False

            # STEP 6: Create directories
            if self.verbose:
                print("\n📁 STEP 6: Creating directories...")

            section_dirs = self._create_pdf_section_directories(output_path, final_chapters)

            # STEP 7: Extract chapters
            if self.verbose:
                print(f"\n🔄 STEP 7: Extracting {len(final_chapters)} chapters...")

            extracted_files = self.create_chapter_pdfs(
                str(pdf_path), final_chapters, output_path, section_dirs
            )

            # STEP 8: Generate reports and show completion
            self.report_generator.generate_processing_report(
                book_name, "PDF", final_chapters, extracted_files, output_path
            )
            self.report_generator.print_processing_summary(final_chapters, extracted_files)

            print(f"📁 Saved to: {output_path}")
            print(f"\n✅ Book processing completed successfully!")
            print(f"📊 Processed {len(extracted_files)} chapters")
            print(f"📁 Output: {output_path}")

            return True

        except Exception as e:
            print(f"❌ Processing failed: {e}")
            if self.verbose:
                import traceback
                print(f"🔍 Debug info: {traceback.format_exc()}")
            return False

    def create_chapter_pdfs(self, pdf_path: str, chapters: List[Dict],
                            output_path: Path, section_dirs: Dict[str, str]) -> List[str]:
        """Extract individual PDF chapters - existing functionality preserved"""

        # This method contains the original PDF extraction logic
        # Keeping it exactly as it was to preserve functionality

        try:
            import PyPDF2
        except ImportError:
            print("❌ Missing PyPDF2 library. Install with: pip install PyPDF2")
            return []

        extracted_files = []

        try:
            with open(pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                total_pages = len(reader.pages)

                for chapter in chapters:
                    try:
                        chapter_id = chapter['id']
                        title = chapter.get('title', 'Unknown')
                        start_page = chapter.get('start_page')
                        end_page = chapter.get('end_page')
                        section_title = chapter.get('section_title')

                        if not start_page:
                            if self.verbose:
                                print(f"⚠️  Skipping chapter {chapter_id}: no start page")
                            continue

                        # Determine output directory
                        if section_title and section_title in section_dirs:
                            output_dir = Path(section_dirs[section_title])
                        else:
                            # Fallback to first available section directory
                            if section_dirs:
                                output_dir = Path(next(iter(section_dirs.values())))
                            else:
                                output_dir = output_path / "Chapters"
                                output_dir.mkdir(exist_ok=True)

                        # Create filename
                        safe_title = sanitize_filename(title)
                        filename = f"Chapter_{chapter_id}-{safe_title}.pdf"
                        chapter_file = output_dir / filename

                        # Create chapter PDF
                        writer = PyPDF2.PdfWriter()

                        # Determine actual end page
                        actual_end = min(end_page or total_pages, total_pages)

                        # Add pages (convert to 0-based indexing)
                        for page_num in range(start_page - 1, actual_end):
                            if page_num < total_pages:
                                writer.add_page(reader.pages[page_num])

                        # Write chapter PDF
                        with open(chapter_file, 'wb') as output_file:
                            writer.write(output_file)

                        extracted_files.append(str(chapter_file))

                        if self.verbose:
                            page_count = actual_end - (start_page - 1)
                            print(f"✅ Created: {filename} ({page_count} pages)")

                    except Exception as e:
                        if self.verbose:
                            print(f"❌ Error creating chapter {chapter.get('id', '?')}: {e}")
                        continue

                return extracted_files

        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return extracted_files

    def _get_pdf_page_count(self, pdf_path: Path) -> int:
        """Get total page count of PDF - moved from main.py"""
        try:
            import fitz
            with fitz.open(pdf_path) as pdf:
                return len(pdf)
        except Exception:
            return 0

    def _create_pdf_section_directories(self, output_dir: Path, chapters: List[Dict]) -> Dict[str, str]:
        """Create section directories for PDF books - moved from main.py"""

        output_dir.mkdir(parents=True, exist_ok=True)

        section_dirs = {}
        sections = set()

        for chapter in chapters:
            section_letter = chapter.get('section')  # "C", "D", "E", etc.
            section_title = chapter.get('section_title', 'Unknown Section')  # "Product Skills"

            # Handle None section_title for flat structure books
            if section_title is None:
                section_title = 'Chapters'  # Default for books without sections

            if section_letter and section_title:
                # Create full section identifier: "C._Product_Skills"
                full_section_key = f"{section_letter}._{section_title}"
                sections.add(full_section_key)
            else:
                # Fallback for chapters without proper section data
                sections.add(section_title)

        for section_key in sections:
            if '._' in section_key:
                # Proper section format: "C._Product Skills"
                section_dir_name = sanitize_filename(section_key)  # "C._Product_Skills"
                original_section_title = section_key.split('._', 1)[1]  # "Product Skills"
            else:
                # Fallback format
                section_dir_name = sanitize_filename(section_key)
                original_section_title = section_key

            section_path = output_dir / section_dir_name
            section_path.mkdir(exist_ok=True)
            section_dirs[original_section_title] = str(section_path)

            if self.verbose:
                print(f"📁 Created: {section_dir_name}")

        return section_dirs

    def _get_user_confirmation(self) -> bool:
        """Get user confirmation to proceed - moved from main.py"""
        try:
            response = input("🚀 Proceed with chapter extraction? [Y/n]: ").strip().lower()
            return response in ['', 'y', 'yes']
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False
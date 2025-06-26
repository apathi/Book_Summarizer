#!/usr/bin/env python3
"""
📚 Enhanced EPUB Processor
Complete EPUB processing with image extraction and PDF conversion
"""

import json
import re
from pathlib import Path
from typing import List, Dict

from .epub_image_extractor import EPUBImageExtractor
from .html_to_pdf_converter import HTMLToPDFConverter
from .utils import sanitize_filename

# EPUB specific imports
try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False


class EPUBProcessor:
    """Enhanced EPUB processor with complete workflow"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.image_extractor = EPUBImageExtractor(verbose=verbose)
        self.html_to_pdf_converter = HTMLToPDFConverter(verbose=verbose)

    def process_epub_book(self, epub_path: str, output_dir: str) -> bool:
        """Complete EPUB processing workflow"""

        if not EPUB_AVAILABLE:
            print("❌ EPUB processing not available - missing libraries")
            print("Install with: pip install ebooklib beautifulsoup4")
            return False

        try:
            epub_path = Path(epub_path)
            book_name = epub_path.stem

            # STEP 1: Extract EPUB structure directly (no TOC parsing)
            if self.verbose:
                print("\n📋 STEP 1: Extracting EPUB chapters directly...")

            book = epub.read_epub(str(epub_path))
            chapters = self._extract_epub_chapters_direct(book)

            if not chapters:
                print("❌ No chapters found in EPUB")
                return False

            # STEP 2: Show preview with smart numbering
            if self.verbose:
                self._show_epub_preview(book_name, chapters)

            # Ask for confirmation
            if not self._get_user_confirmation():
                print("❌ Processing cancelled by user")
                return False

            # STEP 3: Create directories
            output_path = self._create_epub_directories(book_name, output_dir)

            # STEP 4: Extract chapters with smart renumbering
            extracted_files = self._extract_epub_chapters_with_images(chapters, output_path, str(epub_path))

            # STEP 5: Save processing report and show summary
            self._finalize_epub_processing(book_name, chapters, extracted_files, output_path)

            return True

        except Exception as e:
            print(f"❌ Processing failed: {e}")
            if self.verbose:
                import traceback
                print(f"🔍 Debug info: {traceback.format_exc()}")
            return False

    def _extract_epub_chapters_direct(self, book) -> List[Dict]:
        """Extract chapters from EPUB using direct document iteration"""
        chapters = []

        if self.verbose:
            print("📖 Extracting EPUB chapters using direct document iteration...")

        # Get all document items from the book
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Extract text to check if it's substantial content
                try:
                    content = item.get_body_content()
                    if isinstance(content, bytes):
                        content_str = content.decode('utf-8', errors='ignore')
                    else:
                        content_str = str(content)

                    soup = BeautifulSoup(content_str, 'html.parser')
                    text = soup.get_text().strip()

                    # Skip very short sections (likely not chapters)
                    if len(text) < 500:
                        if self.verbose:
                            print(f"⏭️  Skipping short content: {item.get_name()} ({len(text)} chars)")
                        continue

                    # Skip navigation files
                    item_name = item.get_name().lower()
                    if 'nav' in item_name or 'toc' in item_name:
                        if self.verbose:
                            print(f"⏭️  Skipping navigation: {item.get_name()}")
                        continue

                    # Try to get chapter title
                    title = self._extract_epub_title(soup, item, text)

                    chapters.append({
                        'item': item,
                        'title': title,
                        'content': content,
                        'text_length': len(text)
                    })

                    if self.verbose:
                        print(f"📖 Found chapter: {title} ({len(text)} chars)")

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️  Error processing {item.get_name()}: {e}")
                    continue

        if self.verbose:
            print(f"✅ Found {len(chapters)} chapters in EPUB")

        return chapters

    def _extract_epub_title(self, soup, item, text: str) -> str:
        """Extract title from EPUB chapter"""

        # Method 1: Look for main heading in content
        for tag in ['h1', 'h2', 'h3']:
            heading = soup.find(tag)
            if heading and heading.get_text().strip():
                title = heading.get_text().strip()
                # Clean up title
                title = re.sub(r'\s+', ' ', title)  # Normalize spaces
                if 3 < len(title) < 100:  # Reasonable title length
                    return title

        # Method 2: Look for title in the first paragraph or div
        if text:
            # Get first substantial line
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for line in lines[:5]:  # Check first 5 lines
                if 5 < len(line) < 100 and not line.startswith('Copyright'):
                    # Look for chapter patterns
                    if re.match(r'^(Chapter|CHAPTER)\s+\d+', line):
                        return line
                    elif re.match(r'^[A-Z][a-z]', line) and len(line.split()) <= 8:
                        return line

        # Method 3: Use item name as fallback, but clean it up
        item_name = item.get_name()
        if item_name:
            # Clean up filename
            name = Path(item_name).stem
            if 'split' in name.lower():
                # Try to match with content
                if 'introduction' in text.lower()[:200]:
                    return "Introduction"
                elif 'chapter 1' in text.lower()[:200]:
                    return "Chapter 1"
                elif 'chapter 2' in text.lower()[:200]:
                    return "Chapter 2"
                else:
                    return f"Chapter {name.split('_')[-1]}"
            else:
                return re.sub(r'[_-]', ' ', name).title()

        # Method 4: Generic fallback
        return "Unknown Chapter"

    def _show_epub_preview(self, book_name: str, chapters: List[Dict]) -> None:
        """Show EPUB extraction preview"""
        print("\n👀 STEP 2: Preview...")
        print(f"\n📋 EXTRACTION PREVIEW for '{book_name}'")
        print("=" * 70)
        print(f"📁 {book_name}_chapters/")
        print(f"├── 📁 Chapters/")

        # Preview with smart numbering
        real_chapter_counter = 1
        extra_counter = 1

        for i, chapter in enumerate(chapters, 1):
            raw_title = chapter['title']

            # Fixed chapter detection logic
            is_real_chapter = re.search(r'^(CHAPTER|Chapter)\s+\d+\s+\w', raw_title, re.IGNORECASE)

            cleaned_title = self._clean_chapter_title(raw_title)
            safe_title = sanitize_filename(cleaned_title)

            if is_real_chapter:
                filename = f"Chapter_{real_chapter_counter:02d}-{safe_title}.pdf"
                real_chapter_counter += 1
            else:
                filename = f"Extra_{extra_counter:02d}-{safe_title}.pdf"
                extra_counter += 1

            print(f"│   ├── {filename}")
        print("=" * 70)

    def _get_user_confirmation(self) -> bool:
        """Get user confirmation to proceed"""
        try:
            response = input("🚀 Proceed with chapter extraction? [Y/n]: ").strip().lower()
            return response in ['', 'y', 'yes']
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False

    def _create_epub_directories(self, book_name: str, output_dir: str) -> Path:
        """Create directory structure for EPUB processing"""
        if self.verbose:
            print("\n📁 STEP 3: Creating directories...")

        output_path = Path(output_dir) / f"{book_name}_chapters"
        output_path.mkdir(parents=True, exist_ok=True)
        chapters_dir = output_path / "Chapters"
        chapters_dir.mkdir(exist_ok=True)

        if self.verbose:
            print(f"📁 Created: Chapters")

        return output_path

    def _extract_epub_chapters_with_images(self, chapters: List[Dict], output_path: Path, epub_path: str) -> List[str]:
        """Extract chapters with image processing and PDF conversion"""
        if self.verbose:
            print(f"\n🔄 STEP 4: Extracting {len(chapters)} chapters with smart numbering...")

        extracted_files = []
        real_chapter_counter = 1
        extra_counter = 1
        chapters_dir = output_path / "Chapters"

        for i, chapter in enumerate(chapters, 1):
            if self.verbose:
                print(f"📄 [{i}/{len(chapters)}] {chapter['title'][:40]}...")

            # Determine if this is a real chapter or supporting content
            raw_title = chapter['title']

            # Better pattern that requires text after chapter number
            is_real_chapter = re.search(r'^(CHAPTER|Chapter)\s+\d+\s+\w', raw_title, re.IGNORECASE)

            if self.verbose:
                print(f"🔍 Title analysis: '{raw_title}' → Real chapter: {is_real_chapter is not None}")

            # Clean title for filename
            cleaned_title = self._clean_chapter_title(raw_title)
            safe_title = sanitize_filename(cleaned_title)

            # Create appropriate filename based on content type
            if is_real_chapter:
                filename = f"Chapter_{real_chapter_counter:02d}-{safe_title}.html"
                if self.verbose:
                    print(f"📖 Real chapter detected - numbering as Chapter_{real_chapter_counter:02d}")
                chapter_counter_to_use = real_chapter_counter
                real_chapter_counter += 1
            else:
                filename = f"Extra_{extra_counter:02d}-{safe_title}.html"
                if self.verbose:
                    print(f"📄 Supporting content - numbering as Extra_{extra_counter:02d}")
                chapter_counter_to_use = extra_counter
                extra_counter += 1

            if self.verbose and raw_title != cleaned_title:
                print(f"🧹 Cleaned title: '{raw_title}' → '{cleaned_title}'")

            chapter_file = chapters_dir / filename

            # Create HTML file with proper content and image extraction
            success = self._create_epub_chapter_html_with_images(
                chapter, str(chapter_file), chapter_counter_to_use, epub_path
            )

            if success:
                # Convert HTML to PDF and delete HTML + images
                pdf_success = self.html_to_pdf_converter.convert_html_to_pdf(
                    str(chapter_file),
                    delete_html=True,
                    cleanup_images=True
                )

                if pdf_success:
                    # Add PDF file to extracted files (HTML was deleted)
                    pdf_filename = filename.replace('.html', '.pdf')
                    pdf_path = chapters_dir / pdf_filename
                    extracted_files.append(str(pdf_path))

                    if self.verbose:
                        print(f"✅ Created: {pdf_filename}")
                else:
                    # PDF conversion failed, keep HTML
                    extracted_files.append(str(chapter_file))
                    if self.verbose:
                        print(f"✅ Created: {filename} (PDF conversion failed, kept HTML)")
            else:
                if self.verbose:
                    print(f"❌ Failed: {filename}")

        return extracted_files

    def _create_epub_chapter_html_with_images(self, chapter_data: Dict, output_path: str, chapter_num: int,
                                              epub_path: str) -> bool:
        """Create individual HTML file for chapter with image extraction"""
        try:
            # Get content
            content = chapter_data.get('content', '')
            if not content:
                if self.verbose:
                    print(f"❌ No content found for chapter {chapter_num}")
                return False

            # Handle content conversion properly
            if isinstance(content, bytes):
                try:
                    content_str = content.decode('utf-8')
                except UnicodeDecodeError:
                    content_str = content.decode('utf-8', errors='ignore')
            else:
                content_str = str(content)

            # Ensure we have actual content
            if len(content_str.strip()) < 10:
                if self.verbose:
                    print(f"❌ Content too short for chapter {chapter_num}: {len(content_str)} chars")
                return False

            # Extract inner content from body tag to avoid nesting
            try:
                content_soup = BeautifulSoup(content_str, 'html.parser')
                body_tag = content_soup.find('body')

                if body_tag:
                    inner_content = ''.join(str(child) for child in body_tag.children)
                else:
                    inner_content = content_str

            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Error parsing content, using as-is: {e}")
                inner_content = content_str

            # Determine chapter type based on filename
            output_file = Path(output_path)
            chapter_type = "Extra" if "Extra_" in output_file.name else "Chapter"

            # Extract images and update content paths
            output_dir = Path(output_path).parent
            extracted_images, inner_content = self.image_extractor.extract_chapter_images(
                epub_path, chapter_num, inner_content, output_dir, chapter_type
            )

            if self.verbose and extracted_images:
                print(f"🖼️  Processed {len(extracted_images)} images for {chapter_type.lower()} {chapter_num}")

            # Create clean HTML content
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chapter_data['title']}</title>
    <style>
        body {{
            font-family: serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="chapter-content">
        {inner_content}
    </div>
</body>
</html>"""

            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Error creating HTML file with images: {e}")
            return False

    def _clean_chapter_title(self, title: str) -> str:
        """Remove redundant chapter numbering from title for filename"""
        if not title:
            return title

        # Remove "CHAPTER X" or "Chapter X" prefix
        cleaned = re.sub(r'^(CHAPTER|Chapter)\s+\d+\s*', '', title, flags=re.IGNORECASE)

        # If we removed something, clean up any remaining artifacts
        if cleaned != title:
            cleaned = cleaned.strip()
            # Remove leading colon, dash, or period
            cleaned = re.sub(r'^[:\-\.\s]+', '', cleaned)
            cleaned = cleaned.strip()

        # Return cleaned title, or original if cleaning made it empty
        return cleaned if cleaned else title

    def _finalize_epub_processing(self, book_name: str, chapters: List[Dict], extracted_files: List[str],
                                  output_path: Path) -> None:
        """Save processing report and show completion summary"""
        # Save processing report
        report_path = output_path / f"{book_name}_processing_report.json"
        self._save_processing_report(chapters, extracted_files, report_path)

        # Show completion summary
        self._show_completion_summary(chapters, extracted_files, output_path)

    def _save_processing_report(self, chapters: List[Dict], extracted_files: List[str], report_path: Path) -> None:
        """Save processing report as JSON"""
        try:
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
                    "total_chapters": len(chapters),
                    "total_files": len(extracted_files) if extracted_files else 0,
                    "processing_date": str(Path().cwd())  # Placeholder
                },
                "chapters": clean_chapters,
                "extracted_files": extracted_files if extracted_files else []
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            if self.verbose:
                print(f"📋 Processing report saved: {report_path.name}")

        except Exception as e:
            print(f"⚠️ Failed to save processing report: {e}")

    def _show_completion_summary(self, chapters: List[Dict], extracted_files: List[str], output_path: Path) -> None:
        """Show completion summary"""
        total_extracted = len(extracted_files) if extracted_files else 0

        print(f"\n🎉 Complete! Extracted {total_extracted} chapters")
        print("📊 Chapters by section:")
        print(f"   • Chapters: {total_extracted} chapters")
        print(f"📁 Saved to: {output_path}")
        print(f"\n✅ Book processing completed successfully!")
        print(f"📊 Processed {total_extracted} chapters")
        print(f"📁 Output: {output_path}")
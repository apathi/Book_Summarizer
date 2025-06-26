#!/usr/bin/env python3
"""
📄 HTML to PDF Converter
Handles conversion of HTML files to PDF using various backends
"""

import os
from pathlib import Path


class HTMLToPDFConverter:
    """Handles HTML to PDF conversion with multiple backend support"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.preferred_backend = 'playwright'  # Default to playwright

    def convert_html_to_pdf(self, html_file_path: str, delete_html: bool = True, cleanup_images: bool = True) -> bool:
        """Convert HTML file to PDF and optionally delete HTML and image folders"""
        try:
            if self.verbose:
                print(f"🔧 Converting HTML to PDF: {Path(html_file_path).name}")

            # Try playwright first (most reliable)
            if self._convert_with_playwright(html_file_path):
                if delete_html:
                    self._cleanup_html(html_file_path)
                if cleanup_images:
                    self._cleanup_image_folder(html_file_path)
                return True

            # Fallback to weasyprint if available
            if self._convert_with_weasyprint(html_file_path):
                if delete_html:
                    self._cleanup_html(html_file_path)
                if cleanup_images:
                    self._cleanup_image_folder(html_file_path)
                return True

            # If all backends fail
            if self.verbose:
                print(f"❌ All PDF conversion backends failed for: {Path(html_file_path).name}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"❌ Error in HTML to PDF conversion: {e}")
            return False

    def _convert_with_playwright(self, html_file_path: str) -> bool:
        """Convert HTML to PDF using playwright"""
        try:
            from playwright.sync_api import sync_playwright

            pdf_path = html_file_path.replace('.html', '.pdf')

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()

                # Load the HTML file
                page.goto(f"file://{os.path.abspath(html_file_path)}")

                # Generate PDF with options to match source material
                page.pdf(
                    path=pdf_path,
                    format='A4',
                    margin={
                        'top': '1in',
                        'right': '1in',
                        'bottom': '1in',
                        'left': '1in'
                    },
                    print_background=True  # Include background colors and images
                )

                browser.close()

            if self.verbose:
                print(f"✅ PDF created with playwright: {Path(pdf_path).name}")
            return True

        except ImportError:
            if self.verbose:
                print("⚠️  Playwright not available, trying fallback...")
            return False
        except Exception as e:
            if self.verbose:
                print(f"❌ Playwright conversion failed: {e}")
            return False

    def _convert_with_weasyprint(self, html_file_path: str) -> bool:
        """Convert HTML to PDF using weasyprint (fallback)"""
        try:
            from weasyprint import HTML, CSS

            pdf_path = html_file_path.replace('.html', '.pdf')

            # Convert HTML to PDF with custom CSS
            html_doc = HTML(filename=html_file_path)

            # Custom CSS to match source material
            pdf_css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1in;
                }
                body {
                    font-family: serif;
                    line-height: 1.6;
                    color: #333;
                }
                h1, h2, h3 {
                    page-break-after: avoid;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    page-break-inside: avoid;
                }
                .chapter-content {
                    orphans: 3;
                    widows: 3;
                }
            ''')

            html_doc.write_pdf(pdf_path, stylesheets=[pdf_css])

            if self.verbose:
                print(f"✅ PDF created with weasyprint: {Path(pdf_path).name}")
            return True

        except ImportError:
            if self.verbose:
                print("⚠️  WeasyPrint not available")
            return False
        except Exception as e:
            if self.verbose:
                print(f"❌ WeasyPrint conversion failed: {e}")
            return False

    def _cleanup_html(self, html_file_path: str) -> None:
        """Delete HTML file after successful PDF conversion"""
        try:
            os.remove(html_file_path)
            if self.verbose:
                print(f"🗑️  Deleted HTML file: {Path(html_file_path).name}")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Failed to delete HTML file: {e}")

    def _cleanup_image_folder(self, html_file_path: str) -> None:
        """Delete chapter-specific image folder after PDF conversion"""
        try:
            # Determine image folder name based on HTML file
            html_path = Path(html_file_path)
            html_stem = html_path.stem  # e.g., "Chapter_01-Critiquing_Design"

            # Extract chapter number pattern (Chapter_XX or Extra_XX)
            import re
            match = re.match(r'(Chapter_\d+|Extra_\d+)', html_stem)
            if match:
                chapter_prefix = match.group(1)  # e.g., "Chapter_01"
                image_folder = html_path.parent / f"{chapter_prefix}_images"

                if image_folder.exists() and image_folder.is_dir():
                    import shutil
                    shutil.rmtree(image_folder)
                    if self.verbose:
                        print(f"🗑️  Deleted image folder: {image_folder.name}")

        except Exception as e:
            if self.verbose:
                print(f"⚠️  Failed to delete image folder: {e}")

    def set_backend(self, backend: str) -> None:
        """Set preferred conversion backend"""
        if backend in ['playwright', 'weasyprint']:
            self.preferred_backend = backend
        else:
            raise ValueError(f"Unsupported backend: {backend}")
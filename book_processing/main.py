#!/usr/bin/env python3
"""
📚 Book Processor Main
Pure orchestrator - routes to appropriate processors
"""

from pathlib import Path
from .toc_parser import TOCParser
from .chapter_detector import ChapterDetector
from .pdf_processor import PDFProcessor
from .epub_processor import EPUBProcessor


class BookProcessor:
    """Main orchestrator that routes to appropriate processors"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.toc_parser = TOCParser(verbose=verbose)
        self.chapter_detector = ChapterDetector(verbose=verbose)
        self.pdf_processor = PDFProcessor(verbose=verbose)
        self.epub_processor = EPUBProcessor(verbose=verbose)

    def process_book(self, file_path: str, output_dir: str) -> bool:
        """Process a book file (PDF or EPUB) and extract chapters"""

        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        # File format detection and routing
        file_extension = file_path.suffix.lower()

        if file_extension == '.pdf':
            return self._process_pdf_book(str(file_path), output_dir)
        elif file_extension == '.epub':
            return self._process_epub_book(str(file_path), output_dir)
        else:
            print(f"❌ Unsupported file format: {file_extension}")
            print("📋 Supported formats: .pdf, .epub")
            return False

    def _process_pdf_book(self, pdf_path: str, output_dir: str) -> bool:
        """Delegate PDF processing to enhanced PDFProcessor"""

        if self.verbose:
            print(f"🚀 Processing .PDF: {pdf_path}")

        return self.pdf_processor.process_pdf_book(pdf_path, output_dir)

    def _process_epub_book(self, epub_path: str, output_dir: str) -> bool:
        """Delegate EPUB processing to EPUBProcessor"""

        if self.verbose:
            print(f"🚀 Processing .EPUB: {epub_path}")

        return self.epub_processor.process_epub_book(epub_path, output_dir)
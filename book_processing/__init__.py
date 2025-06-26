"""
📚 Book Processing Package
Modular system for extracting individual chapters from PDF/EPUB books

Main components:
- TOC Parser: Extract table of contents from books
- Chapter Detector: Find chapter boundaries in PDFs
- PDF Processor: Handle PDF operations and text extraction
- EPUB Processor: Handle EPUB-specific operations
- Image Handler: Extract and manage images from chapters
- Report Generator: Create processing reports and logs
"""

from .main import BookProcessor
from .toc_parser import TOCParser
from .chapter_detector import ChapterDetector
from .pdf_processor import PDFProcessor
from .epub_processor import EPUBProcessor
from .image_handler import ImageHandler
from .report_generator import ReportGenerator
from .utils import setup_logging, validate_file, sanitize_filename

__version__ = "1.0.0"
__author__ = "Book Processing System"

__all__ = [
    'BookProcessor',
    'TOCParser',
    'ChapterDetector',
    'PDFProcessor',
    'EPUBProcessor',
    'ImageHandler',
    'ReportGenerator',
    'setup_logging',
    'validate_file',
    'sanitize_filename'
]
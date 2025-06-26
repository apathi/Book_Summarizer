#!/usr/bin/env python3
"""
📚 Book Chapter Processor - Command Line Interface
Extracts individual chapters from PDF/EPUB books with clean organization

Usage:
    python book_processor.py "books/mybook.pdf" --output "chapters"
    python book_processor.py "books/mybook.epub" --output "chapters" --verbose
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from book_processing.main import BookProcessor
    from book_processing.utils import validate_file
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory with book_processing/ folder")
    sys.exit(1)


def main():
    """Command line interface for book processing"""

    parser = argparse.ArgumentParser(
        description='Extract individual chapters from PDF/EPUB books',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python book_processor.py "books/pm-book.pdf" --output "chapters"
  python book_processor.py "books/textbook.epub" --output "study_materials" --verbose

Supported formats: PDF, EPUB
Output: Individual chapter files organized by book sections
        """
    )

    parser.add_argument(
        'file_path',
        help='Path to PDF or EPUB book file'
    )

    parser.add_argument(
        '--output', '-o',
        default='book_chapters',
        help='Output directory for extracted chapters (default: book_chapters)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed progress'
    )

    args = parser.parse_args()

    # Validate input file
    if not validate_file(args.file_path):
        sys.exit(1)

    # Initialize processor
    processor = BookProcessor(verbose=args.verbose)

    # Process the book
    result = processor.process_book(args.file_path, args.output)

    #if result.get("success"):
    if result:
        print("\n✅ Book processing completed successfully!")
    else:
        print(f"\n❌ Processing failed: ")
        sys.exit(1)


if __name__ == "__main__":
    main()



# Example usage:

# python book_processor.py "books/cracking-the-pm-career.pdf"
# python book_processor.py "books/cracking-the-pm-career.pdf" --output "book_chapters" --verbose
# python book_processor.py "books/the-pm-interview.pdf" --output "book_chapters" --verbose

# python book_processor.py "books/decode-and-conquer.epub" --output "book_chapters" --verbose
# python book_processor.py "books/The Law of Success.epub" --output "book_chapters" --verbose

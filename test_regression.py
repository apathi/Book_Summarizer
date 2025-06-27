#!/usr/bin/env python3
"""
🧪 BookProcessor Regression Test Suite

Comprehensive testing to ensure changes don't break backward compatibility.
Compares current processing results (up to preview stage) against baseline reports.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from book_processing.main import BookProcessor


class RegressionTester:
    """Tests book processing against baseline results using preview-stage comparison"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.book_processor = BookProcessor(verbose=False)
        
    def load_baseline(self, baseline_path: str) -> Dict:
        """Load baseline processing report"""
        try:
            with open(baseline_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load baseline {baseline_path}: {e}")
    
    def process_book_to_preview(self, book_path: str) -> Tuple[List[Dict], Dict]:
        """Process a book up to preview stage using the same code path as production"""
        if self.verbose:
            print(f"      Processing {book_path} through preview stage...")
        
        # Use the same BookProcessor workflow but stop at preview stage
        file_path = Path(book_path)
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.epub':
            # Use EPUB processor's preview method
            return self._get_epub_preview(book_path)
        elif file_extension == '.pdf':
            # Use PDF processor's preview method  
            return self._get_pdf_preview(book_path)
        else:
            raise Exception(f"Unsupported file format: {file_extension}")
    
    def _get_epub_preview(self, epub_path: str) -> Tuple[List[Dict], Dict]:
        """Get EPUB preview using the same processor as production"""
        try:
            # Use the actual EPUB processor from production code
            import ebooklib
            from ebooklib import epub
            book = epub.read_epub(epub_path)
            chapters = self.book_processor.epub_processor._extract_epub_chapters_direct(book)
            
            if not chapters:
                raise Exception(f"No chapters found in EPUB {epub_path}")
            
            # EPUBs don't have sections typically
            sections = {}
            return chapters, sections
            
        except Exception as e:
            raise Exception(f"Failed to process EPUB preview: {e}")
    
    def _get_pdf_preview(self, pdf_path: str) -> Tuple[List[Dict], Dict]:
        """Get PDF preview using the same processors as production"""
        try:
            # Use the actual processors from production code
            toc_parser = self.book_processor.toc_parser
            chapter_detector = self.book_processor.chapter_detector
            
            # Step 1: Parse TOC
            toc_pages = toc_parser.find_toc_pages(pdf_path)
            if not toc_pages:
                raise Exception(f"No TOC found in {pdf_path}")
            
            # Step 2: Extract chapters and sections
            chapters, sections = toc_parser.extract_chapters_from_toc(pdf_path, toc_pages)
            if not chapters:
                raise Exception(f"No chapters found in {pdf_path}")
            
            # Step 3: Chapter detection
            found_pages = chapter_detector.scan_for_chapters(pdf_path, toc_pages, sections, chapters)
            
            # Step 4: Merge TOC with found pages
            merged_chapters = chapter_detector.merge_toc_with_pages(chapters, found_pages)
            
            # Step 5: Calculate page ranges (STOP HERE - this is our preview data)
            import fitz
            with fitz.open(pdf_path) as pdf:
                total_pages = len(pdf)
            final_chapters = chapter_detector.calculate_page_ranges(merged_chapters, total_pages)
            
            return final_chapters, sections
            
        except Exception as e:
            raise Exception(f"Failed to process PDF preview: {e}")
    
    def compare_chapters(self, baseline_chapters: List[Dict], current_chapters: List[Dict], is_epub: bool = False) -> Tuple[bool, List[str]]:
        """Compare baseline vs current chapters - returns (success, differences)"""
        differences = []
        
        # Check chapter count
        if len(baseline_chapters) != len(current_chapters):
            differences.append(f"Chapter count mismatch: {len(baseline_chapters)} baseline vs {len(current_chapters)} current")
            return False, differences
        
        # Check each chapter field-by-field
        for i, (base_ch, curr_ch) in enumerate(zip(baseline_chapters, current_chapters)):
            ch_diffs = []
            
            # Different fields for EPUB vs PDF
            if is_epub:
                # EPUB books only have title and content fields typically
                fields_to_check = ['title']
                # Note: EPUB chapters might not have consistent structure, so we focus on titles
            else:
                # PDF books have full metadata
                fields_to_check = ['id', 'title', 'start_page', 'end_page', 'section', 'page_range']
            
            for field in fields_to_check:
                base_val = base_ch.get(field)
                curr_val = curr_ch.get(field)
                
                # Special handling for end_page (can be None)
                if field == 'end_page' and base_val is None and curr_val is None:
                    continue
                    
                if base_val != curr_val:
                    ch_diffs.append(f"{field}: '{base_val}' → '{curr_val}'")
            
            if ch_diffs:
                ch_title = base_ch.get('title', 'Unknown')[:30] + '...' if len(base_ch.get('title', '')) > 30 else base_ch.get('title', 'Unknown')
                chapter_id = base_ch.get('id', i+1)  # Use index if no ID for EPUB
                differences.append(f"Chapter {chapter_id} ({ch_title}): {', '.join(ch_diffs)}")
        
        return len(differences) == 0, differences
    
    def compare_sections(self, baseline_chapters: List[Dict], current_sections: Dict) -> Tuple[bool, List[str]]:
        """Compare section structure between baseline and current"""
        differences = []
        
        # Extract sections from baseline chapters
        baseline_sections = {}
        for ch in baseline_chapters:
            section = ch.get('section')
            section_title = ch.get('section_title')
            if section and section not in baseline_sections:
                baseline_sections[section] = section_title
        
        # Compare section letters
        base_letters = set(baseline_sections.keys())
        curr_letters = set(current_sections.keys())
        
        if base_letters != curr_letters:
            missing_in_current = base_letters - curr_letters
            extra_in_current = curr_letters - base_letters
            if missing_in_current:
                differences.append(f"Missing sections in current: {sorted(missing_in_current)}")
            if extra_in_current:
                differences.append(f"Extra sections in current: {sorted(extra_in_current)}")
        
        # Compare section titles (for common sections)
        for letter in base_letters & curr_letters:
            base_title = baseline_sections.get(letter)
            curr_title = current_sections.get(letter, {}).get('title')
            if base_title != curr_title:
                differences.append(f"Section {letter} title: '{base_title}' → '{curr_title}'")
        
        return len(differences) == 0, differences
    
    def test_book(self, book_name: str, book_path: str, baseline_path: str) -> bool:
        """Test a single book against baseline"""
        print(f"\n📖 TESTING: {book_name}")
        print("-" * 70)
        
        try:
            # Detect if this is an EPUB book
            is_epub = book_path.endswith('.epub')
            
            # Load baseline
            baseline_data = self.load_baseline(baseline_path)
            baseline_chapters = baseline_data['chapters']
            
            # Process with current system (up to preview stage)
            current_chapters, current_sections = self.process_book_to_preview(book_path)
            
            if self.verbose:
                print(f"      Book type: {'EPUB' if is_epub else 'PDF'}")
                print(f"      Loaded {len(baseline_chapters)} baseline chapters")
                print(f"      Generated {len(current_chapters)} current chapters")
                print(f"      Found {len(current_sections)} sections")
            
            # Compare chapters (pass is_epub flag)
            ch_success, ch_diffs = self.compare_chapters(baseline_chapters, current_chapters, is_epub)
            
            # Compare sections (only for PDFs)
            if not is_epub:
                sec_success, sec_diffs = self.compare_sections(baseline_chapters, current_sections)
            else:
                sec_success, sec_diffs = True, []  # EPUBs typically don't have sections
            
            # Report results
            if ch_success and sec_success:
                print(f"   ✅ PASSED - All {len(baseline_chapters)} chapters match perfectly")
                if is_epub:
                    print(f"   ✅ EPUB format (no sections)")
                elif current_sections:
                    print(f"   ✅ Sections: {sorted(current_sections.keys())}")
                else:
                    print(f"   ✅ No sections (flat structure)")
                return True
            else:
                print(f"   ❌ FAILED - Differences detected:")
                
                if ch_diffs:
                    print(f"\n   📋 Chapter differences ({len(ch_diffs)}):")
                    for diff in ch_diffs[:5]:  # Show first 5
                        print(f"      • {diff}")
                    if len(ch_diffs) > 5:
                        print(f"      ... and {len(ch_diffs) - 5} more differences")
                
                if sec_diffs:
                    print(f"\n   📂 Section differences:")
                    for diff in sec_diffs:
                        print(f"      • {diff}")
                
                return False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            if self.verbose:
                import traceback
                print(f"   🔍 Debug: {traceback.format_exc()}")
            return False


def main():
    """Run regression tests on all books"""
    parser = argparse.ArgumentParser(description='BookProcessor Regression Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--book', '-b', help='Test specific book only (e.g., cracking-the-pm-career)')
    args = parser.parse_args()
    
    print("🧪 BOOKPROCESSOR REGRESSION TEST SUITE")
    print("=" * 70)
    
    # Define test cases
    all_test_cases = [
        {
            'name': 'cracking-the-pm-career',
            'book_path': 'books/cracking-the-pm-career.pdf',
            'baseline_path': 'test_chapters_clean_section/cracking-the-pm-career_chapters/cracking-the-pm-career_processing_report.json'
        },
        {
            'name': 'the-pm-interview',
            'book_path': 'books/the-pm-interview.pdf',
            'baseline_path': 'test_chapters_clean_section/the-pm-interview_chapters/the-pm-interview_processing_report.json'
        },
        {
            'name': 'decode-and-conquer',
            'book_path': 'books/decode-and-conquer.epub',
            'baseline_path': 'test_chapters_clean_section/decode-and-conquer_chapters/decode-and-conquer_processing_report.json'
        },
        {
            'name': 'AI Product Managers Handbook - 2nd edition 2024',
            'book_path': 'books/AI Product Managers Handbook - 2nd edition 2024.pdf',
            'baseline_path': 'test_chapters_clean_section/AI Product Managers Handbook - 2nd edition 2024_chapters/AI Product Managers Handbook - 2nd edition 2024_processing_report.json'
        }
    ]
    
    # Filter test cases if specific book requested
    if args.book:
        test_cases = [tc for tc in all_test_cases if tc['name'] == args.book]
        if not test_cases:
            print(f"❌ Unknown book: {args.book}")
            print(f"Available books: {[tc['name'] for tc in all_test_cases]}")
            return 1
    else:
        test_cases = all_test_cases
    
    # Run tests
    tester = RegressionTester(verbose=args.verbose)
    results = []
    
    for test_case in test_cases:
        # Check if baseline exists
        if not Path(test_case['baseline_path']).exists():
            print(f"\n⚠️  SKIPPED: {test_case['name']} - No baseline found at {test_case['baseline_path']}")
            results.append((test_case['name'], None))
            continue
        
        # Check if book exists
        if not Path(test_case['book_path']).exists():
            print(f"\n⚠️  SKIPPED: {test_case['name']} - Book not found at {test_case['book_path']}")
            results.append((test_case['name'], None))
            continue
        
        # Run test
        success = tester.test_book(
            test_case['name'],
            test_case['book_path'],
            test_case['baseline_path']
        )
        results.append((test_case['name'], success))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    passed = sum(1 for _, success in results if success is True)
    failed = sum(1 for _, success in results if success is False)
    skipped = sum(1 for _, success in results if success is None)
    
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⚠️  Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n🎉 ALL TESTS PASSED - Backward compatibility confirmed!")
        return 0
    elif failed > 0:
        print("\n❌ REGRESSION DETECTED - Some tests failed!")
        print("   📋 Review the differences above and fix before proceeding.")
        return 1
    else:
        print("\n⚠️  NO TESTS RUN - Check baseline and book paths.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
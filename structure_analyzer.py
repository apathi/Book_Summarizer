#!/usr/bin/env python3
"""
📄 Book Structure Analyzer
Analyzes PDF book structure to identify chapter boundaries and organizational patterns
"""

import PyPDF2
import pdfplumber
from pathlib import Path
import re
from typing import List, Dict, Optional, Tuple
import json


def extract_pages_text(pdf_path: str, start_page: int = 0, end_page: int = 30) -> Optional[List[Dict]]:
    """
    Extract text from specific page range of PDF
    
    Args:
        pdf_path: Path to the PDF file
        start_page: Starting page number (0-indexed)
        end_page: Ending page number (0-indexed)
    
    Returns:
        List of dictionaries with page number and text content
    """
    try:
        print(f"📄 Extracting pages {start_page}-{end_page} from: {Path(pdf_path).name}")
        
        pages_data = []
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                actual_end = min(end_page, total_pages)
                
                print(f"📊 PDF has {total_pages} pages, extracting pages {start_page}-{actual_end}")
                
                for page_num in range(start_page, actual_end):
                    page = pdf.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        pages_data.append({
                            'page_number': page_num + 1,  # 1-indexed for display
                            'text': page_text.strip()
                        })
                
                print(f"✅ Extracted text from {len(pages_data)} pages using pdfplumber")
                return pages_data
                
        except Exception as e:
            print(f"⚠️  pdfplumber failed: {e}")
            
            # Fallback to PyPDF2
            print("🔄 Trying PyPDF2 as fallback...")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                actual_end = min(end_page, total_pages)
                
                for page_num in range(start_page, actual_end):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': page_text.strip()
                        })
                
                print(f"✅ Extracted text from {len(pages_data)} pages using PyPDF2")
                return pages_data
    
    except Exception as e:
        print(f"❌ Error extracting pages: {e}")
        return None


def analyze_chapter_patterns(pages_data: List[Dict]) -> Dict:
    """
    Analyze text patterns to identify potential chapter boundaries
    
    Args:
        pages_data: List of page dictionaries with text content
    
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        'potential_chapter_markers': [],
        'formatting_patterns': [],
        'structural_elements': [],
        'repeated_headers_footers': [],
        'page_breaks': [],
        'numbering_patterns': []
    }
    
    # Common chapter indicators
    chapter_patterns = [
        r'CHAPTER\s+\d+',
        r'Chapter\s+\d+',
        r'LESSON\s+\d+',
        r'Lesson\s+\d+',
        r'PART\s+\d+',
        r'Part\s+\d+',
        r'^\d+\.\s+[A-Z]',  # Numbered sections like "1. INTRODUCTION"
        r'^[IVX]+\.\s+[A-Z]',  # Roman numerals
        r'^\d+$',  # Standalone numbers
        r'^[A-Z\s]{10,}$',  # All caps headers
    ]
    
    formatting_patterns = [
        r'^[A-Z\s]{5,}$',  # All caps text (potential headers)
        r'^\s*\d+\s*$',  # Standalone page numbers
        r'^[^\w]*[A-Z][a-z]',  # Lines starting with capital letters
        r'\n\s*\n',  # Multiple line breaks
    ]
    
    for page_data in pages_data:
        page_num = page_data['page_number']
        text = page_data['text']
        lines = text.split('\n')
        
        # Check for chapter patterns
        for pattern in chapter_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_start = text.rfind('\n', 0, match.start()) + 1
                line_end = text.find('\n', match.end())
                if line_end == -1:
                    line_end = len(text)
                full_line = text[line_start:line_end].strip()
                
                analysis['potential_chapter_markers'].append({
                    'page': page_num,
                    'pattern': pattern,
                    'match': match.group(),
                    'full_line': full_line,
                    'position': match.start()
                })
        
        # Analyze line patterns
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for formatting patterns
            for pattern in formatting_patterns:
                if re.match(pattern, line):
                    analysis['formatting_patterns'].append({
                        'page': page_num,
                        'line_number': i + 1,
                        'pattern': pattern,
                        'text': line[:100]  # First 100 chars
                    })
        
        # Look for repeated elements (headers/footers)
        if len(lines) > 0:
            first_line = lines[0].strip()
            last_line = lines[-1].strip()
            
            if first_line and len(first_line) < 100:
                analysis['repeated_headers_footers'].append({
                    'page': page_num,
                    'type': 'header',
                    'text': first_line
                })
            
            if last_line and len(last_line) < 100:
                analysis['repeated_headers_footers'].append({
                    'page': page_num,
                    'type': 'footer',
                    'text': last_line
                })
    
    return analysis


def find_structure_indicators(pages_data: List[Dict]) -> Dict:
    """
    Identify structural indicators and organization patterns
    
    Args:
        pages_data: List of page dictionaries
    
    Returns:
        Dictionary with structural analysis
    """
    structure = {
        'table_of_contents': None,
        'title_page': None,
        'preface_intro': [],
        'chapter_starts': [],
        'consistent_formatting': [],
        'book_sections': []
    }
    
    for page_data in pages_data:
        page_num = page_data['page_number']
        text = page_data['text'].lower()
        
        # Look for table of contents
        if any(keyword in text for keyword in ['table of contents', 'contents', 'index']):
            structure['table_of_contents'] = {
                'page': page_num,
                'indicators': [kw for kw in ['table of contents', 'contents', 'index'] if kw in text]
            }
        
        # Look for title page indicators
        title_indicators = ['paramahansa yogananda', 'law of success', 'title', 'author']
        if any(indicator in text for indicator in title_indicators):
            if not structure['title_page']:
                structure['title_page'] = page_num
        
        # Look for preface/introduction
        if any(keyword in text for keyword in ['preface', 'introduction', 'foreword', 'prologue']):
            structure['preface_intro'].append({
                'page': page_num,
                'type': [kw for kw in ['preface', 'introduction', 'foreword', 'prologue'] if kw in text]
            })
    
    return structure


def generate_enhancement_suggestions(analysis: Dict, structure: Dict) -> List[str]:
    """
    Generate suggestions for enhancing the book processing system
    
    Args:
        analysis: Chapter pattern analysis results
        structure: Structural analysis results
    
    Returns:
        List of enhancement suggestions
    """
    suggestions = []
    
    # Analyze chapter markers
    chapter_markers = analysis['potential_chapter_markers']
    if chapter_markers:
        patterns = set(marker['pattern'] for marker in chapter_markers)
        suggestions.append(f"📍 Detected {len(patterns)} different chapter patterns: {', '.join(patterns)}")
        suggestions.append("💡 Enhance chapter detector to recognize these specific patterns")
    
    # Analyze formatting consistency
    formatting = analysis['formatting_patterns']
    if formatting:
        suggestions.append(f"🎨 Found {len(formatting)} formatting patterns that could indicate structure")
        suggestions.append("💡 Implement formatting-based chapter detection for books without explicit chapter markers")
    
    # Table of contents analysis
    if structure['table_of_contents']:
        suggestions.append("📋 Book has a table of contents - enhance TOC parser for this format")
    else:
        suggestions.append("❌ No traditional table of contents found - need content-based chapter detection")
    
    # Structural recommendations
    if structure['preface_intro']:
        suggestions.append("📖 Book has introductory sections - implement intro/main content separation")
    
    # Header/footer analysis
    headers_footers = analysis['repeated_headers_footers']
    if headers_footers:
        suggestions.append(f"🔄 Found {len(headers_footers)} potential headers/footers - implement cleanup filters")
    
    # General recommendations
    suggestions.extend([
        "🤖 Implement ML-based content segmentation for books without clear chapter markers",
        "📏 Add content-length-based chunking as fallback for unstructured books",
        "🔍 Enhance text pattern recognition for spiritual/philosophical texts",
        "📊 Implement semantic analysis to identify topic transitions"
    ])
    
    return suggestions


def main():
    """Main function to analyze the book structure"""
    pdf_path = "books/AI Product Managers Handbook - 2nd edition 2024.pdf"
    
    print("🔍 Starting book structure analysis...")
    
    # Extract first 30 pages
    pages_data = extract_pages_text(pdf_path, start_page=0, end_page=30)
    
    if not pages_data:
        print("❌ Failed to extract text from PDF")
        return
    
    print(f"\n📖 Analyzing {len(pages_data)} pages...")
    
    # Analyze patterns
    analysis = analyze_chapter_patterns(pages_data)
    structure = find_structure_indicators(pages_data)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 BOOK STRUCTURE ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📋 BOOK: The Law of Success - Paramahansa Yogananda")
    print(f"📄 Pages analyzed: {len(pages_data)}")
    
    print(f"\n🔍 CHAPTER MARKERS FOUND: {len(analysis['potential_chapter_markers'])}")
    for marker in analysis['potential_chapter_markers'][:10]:  # Show first 10
        print(f"   Page {marker['page']}: {marker['full_line']}")
    
    print(f"\n🎨 FORMATTING PATTERNS: {len(analysis['formatting_patterns'])}")
    pattern_counts = {}
    for pattern in analysis['formatting_patterns']:
        pattern_counts[pattern['pattern']] = pattern_counts.get(pattern['pattern'], 0) + 1
    for pattern, count in pattern_counts.items():
        print(f"   {pattern}: {count} occurrences")
    
    print(f"\n📖 STRUCTURAL ELEMENTS:")
    print(f"   Title page: Page {structure['title_page']}")
    print(f"   Table of contents: {structure['table_of_contents']}")
    print(f"   Preface/Intro sections: {len(structure['preface_intro'])}")
    
    print(f"\n💡 ENHANCEMENT SUGGESTIONS:")
    suggestions = generate_enhancement_suggestions(analysis, structure)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # Save detailed results
    results = {
        'analysis': analysis,
        'structure': structure,
        'suggestions': suggestions,
        'pages_analyzed': len(pages_data)
    }
    
    output_file = "ai_pm_handbook_structure_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
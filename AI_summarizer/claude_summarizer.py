#!/usr/bin/env python3
"""
📚 Claude Chapter Summarizer
Converts book chapters to Notion-ready study guides using Claude API

Usage:
    python claude_summarizer.py "path/to/Chapter_01-Introduction.pdf"
    python claude_summarizer.py "path/to/chapters_folder/" --batch
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load variables from .env file
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("⚠️  Falling back to system environment variables only")

# Import shared modules
from prompt_template import get_summarization_prompt
from pdf_text_extractor import extract_text_from_pdf, check_content_length

# Claude API
try:
    import anthropic
    print("✅ Anthropic library imported successfully")
except ImportError:
    print("❌ Missing anthropic library. Install with: pip install anthropic")
    sys.exit(1)


class ClaudeSummarizer:
    """Summarizes book chapters using Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Claude API key"""
        # Priority: 1. Passed parameter, 2. Environment variable
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            print("❌ Claude API key not found!")
            print("\n🔧 Setup Instructions:")
            print("1. Get API key from: https://console.anthropic.com/")
            print("2. Create a .env file in your project directory")
            print("3. Add this line to .env: ANTHROPIC_API_KEY=your_actual_key_here")
            print("4. Install python-dotenv: pip install python-dotenv")
            print("\n💡 Alternative methods:")
            print("   • Set environment variable: export ANTHROPIC_API_KEY='your-key-here'")
            print("   • Pass directly: ClaudeSummarizer(api_key='your-key')")
            sys.exit(1)

        # Validate API key format (should start with 'sk-ant-')
        if not self.api_key.startswith('sk-ant-'):
            print("⚠️  Warning: Anthropic API key should start with 'sk-ant-'")
            print("⚠️  Please verify your API key is correct")

        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("🔑 Claude API client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Claude client: {e}")
            sys.exit(1)

    def summarize_chapter(self, chapter_path: str) -> Optional[str]:
        """Summarize a single chapter using Claude"""
        try:
            chapter_file = Path(chapter_path)
            chapter_title = chapter_file.stem

            print(f"\n🚀 Processing: {chapter_title}")
            print("=" * 60)

            # Step 1: Extract text from PDF
            content = extract_text_from_pdf(chapter_path)
            if not content:
                print(f"❌ Failed to extract content from: {chapter_file.name}")
                return None

            # Step 2: Check content length (Claude's limits)
            max_tokens = 180000  # Claude 3.5 Sonnet context limit (leave room for response)
            if not check_content_length(content, max_tokens):
                return None

            # Step 3: Get prompt from shared template
            prompt = get_summarization_prompt(chapter_title, content)

            # Step 4: Send to Claude
            print("🤖 Sending to Claude for summarization...")

            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=8000,
                    temperature=0.1,  # Low temperature for consistent, factual output
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                summary = response.content[0].text
                print(f"✅ Received summary: {len(summary)} characters")
                return summary

            except Exception as api_error:
                print(f"❌ Claude API error: {api_error}")
                if "authentication" in str(api_error).lower() or "api_key" in str(api_error).lower():
                    print("💡 Tip: Check your ANTHROPIC_API_KEY in the .env file")
                return None

        except Exception as e:
            print(f"❌ Error processing chapter: {e}")
            return None

    def save_summary(self, summary: str, chapter_path: str) -> bool:
        """Save summary as Notion-ready markdown file"""
        try:
            chapter_file = Path(chapter_path)
            output_file = chapter_file.parent / f"{chapter_file.stem}_claude_summary.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)

            print(f"💾 Saved summary: {output_file.name}")
            return True

        except Exception as e:
            print(f"❌ Error saving summary: {e}")
            return False

    def process_single_chapter(self, chapter_path: str) -> bool:
        """Process a single chapter file"""
        if not Path(chapter_path).exists():
            print(f"❌ File not found: {chapter_path}")
            return False

        if not chapter_path.lower().endswith('.pdf'):
            print(f"❌ Not a PDF file: {chapter_path}")
            return False

        # Summarize
        summary = self.summarize_chapter(chapter_path)
        if not summary:
            return False

        # Save
        return self.save_summary(summary, chapter_path)

    def process_folder(self, folder_path: str, recursive: bool = False) -> int:
        """Process PDF files in a folder (optionally recursive)"""
        folder = Path(folder_path)
        if not folder.exists():
            print(f"❌ Folder not found: {folder_path}")
            return 0

        # Get PDF files based on recursive flag
        if recursive:
            pdf_files = list(folder.rglob("*.pdf"))  # Recursive search
            print(f"📁 Searching recursively in: {folder_path}")
        else:
            pdf_files = list(folder.glob("*.pdf"))  # Single folder only
            print(f"📁 Searching in: {folder_path}")

        if not pdf_files:
            recursive_note = " (including subdirectories)" if recursive else ""
            print(f"❌ No PDF files found in: {folder_path}{recursive_note}")
            return 0

        print(f"📄 Found {len(pdf_files)} PDF files to process")

        success_count = 0
        for pdf_file in sorted(pdf_files):
            print(f"\n📄 Processing {pdf_file.name}...")
            print(f"   📂 Location: {pdf_file.parent}")

            if self.process_single_chapter(str(pdf_file)):
                success_count += 1
            else:
                print(f"⚠️  Failed to process: {pdf_file.name}")

        print(f"\n🎉 Complete! Successfully processed {success_count}/{len(pdf_files)} chapters")
        return success_count


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Summarize book chapters using Claude API')
    parser.add_argument('path', help='Path to PDF file or folder containing PDFs')
    parser.add_argument('--batch', action='store_true', help='Process all PDFs in folder')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursively search subdirectories for PDFs')
    parser.add_argument('--api-key', help='Claude API key (optional, uses .env file or environment variable)')

    args = parser.parse_args()

    # Initialize summarizer
    try:
        summarizer = ClaudeSummarizer(api_key=args.api_key)
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Process files
    path = Path(args.path)

    if args.batch or path.is_dir():
        # Process folder (with optional recursion)
        summarizer.process_folder(str(path), recursive=args.recursive)
    else:
        # Process single file
        if not path.exists():
            print(f"❌ File not found: {args.path}")
            return

        success = summarizer.process_single_chapter(str(path))
        if success:
            print("\n🎉 Chapter summarization complete!")
        else:
            print("\n❌ Chapter summarization failed!")


if __name__ == "__main__":
    main()

# USAGE EXAMPLES:
#
# Process a single chapter:
# python claude_summarizer.py "Chapter_01-Introduction.pdf"
# python claude_summarizer.py "book_chapters/decode-and-conquer_chapters/Chapter_14-Getting_Analytical_Metrics.pdf"
#
# Process all PDFs in a single folder:
# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters" --batch
#
# Process all PDFs recursively (including subdirectories):
# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters" --batch --recursive
#
# Alternative recursive syntax:
# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters" -r
#
# Process with custom API key:
# python claude_summarizer.py "chapters/" --batch -r --api-key "your-key-here"
#
# Process entire books collection recursively:
# python claude_summarizer.py "book_chapters/" --batch --recursive

######################################## MORE REAL EXAMPLES ################################################

# export ANTHROPIC_API_KEY='your-api-key-here'
# python claude_summarizer.py "book_chapters/decode-and-conquer_chapters/Chapter_06-Designing_a_Desktop_Application.pdf"
# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters/C._Product_Skills/Chapter_4-User_Insight.pdf"
# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters/C._Product_Skills/Chapter_5-Data_Insight.pdf"
# python claude_summarizer.py "book_chapters/decode-and-conquer_chapters/Chapter_07-Designing_a_Webpage_or_Website.pdf"

# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters/D._Execution_Skills/Chapter_11-Scoping_and_Incremental_Development.pdf"

# python claude_summarizer.py "book_chapters/cracking-the-pm-career_chapters"

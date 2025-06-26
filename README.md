# 📚 BookProcessor - AI-Powered Book Chapter Extraction & Summarization

> **Transform books into structured chapters and AI-powered study guides**

A comprehensive Python system for processing PDF and EPUB books into individual chapters and generating AI-powered study summaries using ChatGPT and Claude APIs.

## ✨ Current Working Features

### 📄 Book Processing
- **PDF Processing**: Extract chapters from PDFs with table of contents parsing
- **EPUB Support**: Process EPUB books with image preservation and smart chapter detection  
- **🤖 AI Summarization**: Generate study guides using OpenAI ChatGPT and Anthropic Claude
- **🖼️ Image Handling**: Preserve images in EPUB→PDF conversion
- **📁 Smart Organization**: Automatic section-based folder structure
- **🔒 Secure API Management**: Environment-based API key configuration

### 📊 Currently Working Books

#### ✅ **Successfully Processed Books:**

1. **cracking-the-pm-career.pdf**
   - ✅ **Section Structure**: A._Foreword, B._Product_Manager_Role, C._Product_Skills, etc.
   - ✅ **Chapter Count**: 57 chapters across 11 sections
   - ✅ **Output Location**: `test_chapters_clean_section/cracking-the-pm-career_chapters/`

2. **decode-and-conquer.epub**
   - ✅ **Structure**: Flat "Chapters/" organization
   - ✅ **Chapter Count**: 24 chapters (16 real + 8 extra content)
   - ✅ **Output Location**: `test_chapters_clean_section/decode-and-conquer_chapters/`

3. **the-pm-interview.pdf**
   - ✅ **Structure**: Flat "Chapters/" organization  
   - ✅ **Chapter Count**: 26 chapters
   - ✅ **Output Location**: `test_chapters_clean_section/the-pm-interview_chapters/`

#### ⚠️ **Books Currently Being Fixed:**

4. **AI Product Managers Handbook - 2nd edition 2024.pdf**
   - ❌ **Issue**: Part-based structure not detected, wrong page ranges
   - 🔧 **Status**: Analysis complete, fix in development
   - 📍 **Problem**: Should have 4 Parts (Part I-IV) with 19 chapters, currently all in "Additional" section

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (`.venv/`)
- OpenAI and/or Anthropic API keys

### Installation
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies  
pip install -r requirements.txt
playwright install chromium

# Set up API keys
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### Process a Book
```bash
# Process PDF book
python book_processor.py "books/your-book.pdf" --output "book_chapters" --verbose

# Process EPUB book  
python book_processor.py "books/your-book.epub" --output "book_chapters" --verbose
```

#### Generate AI Summaries
```bash
cd AI_summarizer

# Single chapter
python chatgpt_summarizer.py "../book_chapters/book-name_chapters/Chapter_01-Title.pdf"
python claude_summarizer.py "../book_chapters/book-name_chapters/Chapter_01-Title.pdf"

# Batch process all chapters
python chatgpt_summarizer.py "../book_chapters/book-name_chapters" --batch --recursive
python claude_summarizer.py "../book_chapters/book-name_chapters" --batch --recursive
```

## 📁 Project Structure

```
BookProcessor/
├── book_processor.py              # 🚀 Main CLI entry point
├── AI_summarizer/                 # 🤖 AI integration tools
│   ├── chatgpt_summarizer.py     # OpenAI ChatGPT  
│   ├── claude_summarizer.py      # Anthropic Claude
│   ├── pdf_text_extractor.py     # Text extraction
│   └── prompt_template.py        # AI prompts
├── book_processing/               # ⚙️ Core processing engine
│   ├── main.py                   # Processing orchestrator (45 lines)
│   ├── pdf_processor.py          # PDF workflow (200 lines)
│   ├── epub_processor.py         # EPUB workflow (400 lines)
│   ├── toc_parser.py             # Table of Contents parsing
│   ├── chapter_detector.py       # Chapter detection algorithms
│   └── [supporting modules...]
├── books/                        # 📚 Source materials
├── book_chapters/               # 📁 Main processed output
├── test_chapters_clean_section/ # 🧪 Test processing output
├── docs/                       # 📖 Comprehensive documentation
└── requirements.txt            # 📦 Dependencies
```

## 🔧 Supported Book Formats

### PDF Books
- **Sectioned Structure**: Books with hierarchical organization (A. Section, B. Section)
  - Example: `cracking-the-pm-career.pdf`
- **Flat Structure**: Simple chapter sequences (Chapter 1, Chapter 2)
  - Example: `the-pm-interview.pdf`
- **Part Structure**: Books with Part I, Part II organization
  - Example: `AI Product Managers Handbook` (in development)

### EPUB Books  
- **Direct Extraction**: Chapter-by-chapter processing
- **Image Preservation**: Embedded images converted to PDFs
- **Smart Classification**: Distinguishes chapters from supporting content
  - Example: `decode-and-conquer.epub`

## 🤖 AI Summarization

### Supported Providers
- **OpenAI ChatGPT**: GPT-4o model (120K context, 4K output)
- **Anthropic Claude**: Claude-3.5-Sonnet (180K context, 8K output)

### Output Format
- **Notion-Ready**: Direct import to Notion workspaces
- **Study-Optimized**: Frameworks, examples, and memory aids
- **Markdown Format**: Clean, portable documentation

## 🛠️ Current Development

### 🔧 Active Issues Being Fixed
1. **Part-based Structure Detection**: Enhancing TOC parser for "Part I, Part II" books
2. **Page Range Accuracy**: Fixing chapter start detection vs header references  
3. **Section Introduction Inclusion**: First chapter in each part includes section intro pages

### 📋 Development Status
- ✅ Core PDF/EPUB processing working
- ✅ AI summarization working
- ✅ Section-based organization (A, B, C format) working
- 🔧 Part-based organization (Part I, II, III format) in development

## 📖 Documentation

See `/docs` folder for comprehensive documentation:
- Architecture & Data Flow
- Technical Specifications  
- Installation & Setup Guide
- Usage Examples & Workflows
- Troubleshooting Guide

## 🔒 Security

- API keys stored in `.env` files (excluded from version control)
- Input validation for file formats and accessibility
- Automatic cleanup of temporary files
- Error handling with graceful degradation

## 🤝 Current Team

- **Development**: Active development on Part-based structure detection
- **Testing**: Validated with 3 working books, 1 book in development

---

**⭐ Status**: Production-ready for A/B/C sectioned books, Part-based books in active development
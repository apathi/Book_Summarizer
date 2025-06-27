# 📚 BookSummarizer - AI-Powered Book Chapter Extraction & Summarization

> **Transform books into structured chapters and AI-powered study guides**

A comprehensive Python system for processing PDF and EPUB books by extracting individual chapters and generating AI-powered study summaries using ChatGPT and Claude APIs.

## ✨ Book Summarizer - Key Highlights

- **PDF Processing**: Extract chapters from PDFs with table of contents parsing
- **EPUB Support**: Process EPUB books with image preservation and smart chapter detection
- 🎯 **Production-Ready**: Comprehensive regression testing with baselines for backward compatibility
- 🧠 **Dual AI Support**: Generate study guides using ChatGPT (120K context) & Claude (180K context)
- 📊 **Smart Processing**: 8-step PDF workflow, 4-step EPUB workflow with intelligent detection
- 🖼️ **Image Intelligence**: EPUB images automatically preserved during PDF conversion
- 📁 **Auto-Organization**: Section-based folders (A, B, C) or flat structure based on book type
- 🔧 **Modular Design**: Ultra-minimal 45-line orchestrator with specialized processors
- 🧪 **Quality Assured**: Regression tests prevent processing errors across 50+ chapters



## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (`.venv/`)
- OpenAI and/or Anthropic API keys for summarization

### Key Dependencies
- `PyPDF2`, `pdfplumber` - PDF processing
- `ebooklib`, `beautifulsoup4` - EPUB processing  
- `playwright` - HTML→PDF conversion
- `openai`, `anthropic` - AI summarization
- `python-dotenv` - Environment management

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

#### Example workflow 

```bash
# Example workflow
python book_processor.py "books/cracking-the-pm-career.pdf" --output "study_materials" --verbose
cd AI_summarizer  
python chatgpt_summarizer.py "../study_materials/cracking-the-pm-career_chapters" --batch -r
python claude_summarizer.py "../study_materials/cracking-the-pm-career_chapters" --batch -r
```
**Result**:
```
study_materials/cracking-the-pm-career_chapters/
├── A._Foreword/
│   ├── Chapter_01-Introduction.pdf
│   ├── Chapter_01-Introduction_chatgpt_summary.md
│   └── Chapter_01-Introduction_claude_summary.md
├── C._Product_Skills/
│   └── [more chapters with summaries...]
└── cracking-the-pm-career_processing_report.json
```



#### Run Regression Tests
```bash
# Test all books for backward compatibility
python test_regression.py

# Verbose output for debugging
python test_regression.py --verbose

# Test specific book only
python test_regression.py --book cracking-the-pm-career
```

## 📁 Project Structure

```
BookProcessor/
├── book_processor.py              # 🚀 Main CLI entry point
├── test_regression.py             # 🧪 Regression test suite
├── AI_summarizer/                 # 🤖 AI integration tools
│   ├── chatgpt_summarizer.py     # OpenAI ChatGPT integration
│   ├── claude_summarizer.py      # Anthropic Claude integration
│   ├── pdf_text_extractor.py     # PDF text extraction utilities
│   └── prompt_template.py        # Shared AI prompt templates
├── book_processing/               # ⚙️ Core processing engine
│   ├── main.py                   # Processing orchestrator (45 lines)
│   ├── pdf_processor.py          # PDF workflow (200 lines)
│   ├── epub_processor.py         # EPUB workflow with image extraction (400 lines)
│   ├── toc_parser.py             # Table of Contents parsing
│   ├── chapter_detector.py       # Chapter detection algorithms
│   ├── epub_image_extractor.py   # EPUB image extraction & processing
│   ├── html_to_pdf_converter.py  # HTML→PDF conversion (Playwright/WeasyPrint)
│   ├── report_generator.py       # Processing reports & summaries
│   └── utils.py                  # Shared utility functions
├── books/                         # 📚 Source PDF/EPUB books
├── book_chapters/                 # 📁 Processed output (chapters & summaries)
├── docs/                          # 📖 Comprehensive documentation (6 guides)
└── requirements.txt               # 📦 Python dependencies
```

## 🏗️ System Architecture

Clean, modular design with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                          │
│                 book_processor.py                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Orchestrator                                │
│              book_processing/main.py                        │
│                   (45 lines)                               │
└─────────────┬───────────────────────┬───────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│     PDF Processor       │ │    EPUB Processor       │
│   Complete Workflow     │ │   Complete Workflow     │
│     (200 lines)         │ │     (400 lines)         │
└─────────┬───────────────┘ └─────────┬───────────────┘
          │                           │
          ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Shared Components                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ TOC Parser  │ │Chapter      │ │Report       │           │
│  │             │ │Detector     │ │Generator    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │EPUB Image   │ │HTML→PDF     │ │Utilities    │           │
│  │Extractor    │ │Converter    │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Delegation Pattern**: Main orchestrator delegates to specialized processors
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Processors receive dependencies at initialization
- **Error Boundaries**: Graceful degradation with informative error messages

## 🔧 Supported Book Formats

### PDF Books
- **Sectioned Structure**: Books with hierarchical organization (A. Section, B. Section)
  - Example: `cracking-the-pm-career.pdf`
- **Flat Structure**: Simple chapter sequences (Chapter 1, Chapter 2)
  - Example: `the-pm-interview.pdf`
- **Part Structure**: Books with Part I, Part II organization
  - Example: `AI Product Managers Handbook`

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for ChatGPT API
- **Anthropic** for Claude API  
- **PyPDF2/pdfplumber** for PDF processing
- **ebooklib** for EPUB handling
- **Playwright** for HTML→PDF conversion

---

**⭐ Status**: Production-ready for all book formats with comprehensive regression testing
**⭐ If this project helps you, please consider giving it a star!**
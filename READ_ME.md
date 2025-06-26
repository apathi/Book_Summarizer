# 📚 Book Summarizer

> **Transform books into structured chapters and AI-powered study guides**

A comprehensive Python system for processing PDF and EPUB books into individual chapters, with integrated AI summarization using ChatGPT and Claude APIs. For full doumentation on the system see /docs folder.

## ✨ Key Features

- **📄 PDF Processing**: Extract chapters from complex PDFs with table of contents parsing
- **📚 EPUB Support**: Process EPUB books with image preservation and smart chapter detection  
- **🤖 AI Summarization**: Generate study guides using OpenAI ChatGPT and Anthropic Claude
- **🖼️ Image Handling**: Preserve images in EPUB→PDF conversion
- **📁 Smart Organization**: Automatic section-based folder structure
- **🔒 Secure API Management**: Environment-based API key configuration
- **⚡ Batch Processing**: Process multiple books and chapters efficiently

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd BookProcessor

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### API Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### Basic Usage

```bash
# Process a PDF book
python book_processor.py "books/your-book.pdf" --output "book_chapters" --verbose

# Process an EPUB book  
python book_processor.py "books/your-book.epub" --output "book_chapters" --verbose

# Generate AI summaries
cd AI_summarizer
python chatgpt_summarizer.py "../book_chapters/book-name_chapters/Chapter_01-Title.pdf"
python claude_summarizer.py "../book_chapters/book-name_chapters" --batch --recursive
```

## 📖 Example Workflow

1. **Process Book**: Extract chapters with preserved structure
2. **Generate Summaries**: Create AI-powered study guides
3. **Study Material**: Use organized chapters and summaries for learning

```bash
# Complete workflow example
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

## 🛠️ Requirements

- **Python**: 3.12+ 
- **System**: macOS, Linux, Windows
- **Memory**: 4GB+ RAM recommended
- **APIs**: OpenAI and/or Anthropic accounts (for summarization)

### Key Dependencies
- `PyPDF2`, `pdfplumber` - PDF processing
- `ebooklib`, `beautifulsoup4` - EPUB processing  
- `playwright` - HTML→PDF conversion
- `openai`, `anthropic` - AI summarization
- `python-dotenv` - Environment management

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
│   ├── main.py                   # Processing orchestrator
│   ├── pdf_processor.py          # PDF workflow
│   ├── epub_processor.py         # EPUB workflow
│   └── [supporting modules...]
├── books/                        # 📚 Source materials
├── book_chapters/               # 📁 Processed output
└── requirements.txt             # 📦 Dependencies
```

## 🔧 Advanced Usage

### Batch Processing
```bash
# Process multiple books
for book in books/*.pdf; do
    python book_processor.py "$book" --output "book_chapters" --verbose
done

# Summarize all chapters recursively
python chatgpt_summarizer.py "book_chapters/" --batch --recursive
```

### Custom Output Location
```bash
python book_processor.py "books/study-guide.pdf" --output "custom_location" --verbose
```

### API Key Alternatives
```bash
# Pass API key directly (not recommended for production)
python chatgpt_summarizer.py "chapter.pdf" --api-key "your-key-here"

# Use environment variables
export OPENAI_API_KEY="your-key"
python chatgpt_summarizer.py "chapter.pdf"
```

## 🎯 Supported Book Formats

### PDF Books
- **Sectioned Structure**: Books with hierarchical organization (A. Section, B. Section)
- **Flat Structure**: Simple chapter sequences (Chapter 1, Chapter 2)
- **Table of Contents**: Automatic TOC parsing and validation
- **Page Detection**: Smart chapter boundary detection

### EPUB Books  
- **Direct Extraction**: Chapter-by-chapter processing
- **Image Preservation**: Embedded images converted to PDFs
- **Smart Classification**: Distinguishes chapters from supporting content
- **HTML Processing**: Clean conversion to structured PDFs

## 🤖 AI Summarization

### Supported Providers
- **OpenAI ChatGPT**: GPT-4o model with 120K context limit
- **Anthropic Claude**: Claude-3.5-Sonnet with 180K context limit

### Output Format
- **Notion-Ready**: Direct import to Notion workspaces
- **Study-Optimized**: Frameworks, examples, and memory aids
- **Markdown Format**: Clean, portable documentation

## 🔒 Security

- **API Keys**: Stored in `.env` files (excluded from version control)
- **Input Validation**: File format and accessibility verification
- **Error Handling**: Graceful failure with informative messages
- **Cleanup**: Automatic removal of temporary files

## 🐛 Troubleshooting

### Common Issues

**Virtual Environment**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

**Missing Dependencies**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

**API Key Problems**:
```bash
# Verify .env file exists and has correct format
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

**Processing Failures**:
```bash
# Use verbose mode for detailed error information
python book_processor.py "books/book.pdf" --verbose
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code  
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for ChatGPT API
- **Anthropic** for Claude API  
- **PyPDF2/pdfplumber** for PDF processing
- **ebooklib** for EPUB handling
- **Playwright** for HTML→PDF conversion

## 📞 Support

- **Issues**: [Report bugs and feature requests](<repository-url>/issues)
- **Documentation**: [Full documentation](<repository-url>/docs)
- **Discussions**: [Community discussions](<repository-url>/discussions)

---

**⭐ If this project helps you, please consider giving it a star!**
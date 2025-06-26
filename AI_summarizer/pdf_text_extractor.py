#!/usr/bin/env python3
"""
📄 PDF Text Extraction Module
Shared PDF text extraction and validation utilities for chapter summarizers

This module provides consistent PDF processing functionality across
both Claude and ChatGPT summarizers.
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from PDF file using multiple extraction methods

    Args:
        pdf_path: Path to the PDF file to process

    Returns:
        Extracted text content as string, or None if extraction fails

    Uses pdfplumber as primary method with PyPDF2 as fallback for maximum compatibility
    """
    try:
        print(f"📄 Extracting text from: {Path(pdf_path).name}")

        # Method 1: Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_content = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"

                if text_content.strip():
                    print(f"✅ Extracted {len(text_content)} characters using pdfplumber")
                    return text_content.strip()
        except Exception as e:
            print(f"⚠️  pdfplumber failed: {e}")

        # Method 2: Fallback to PyPDF2
        print("🔄 Trying PyPDF2 as fallback...")
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"

            if text_content.strip():
                print(f"✅ Extracted {len(text_content)} characters using PyPDF2")
                return text_content.strip()
            else:
                raise Exception("No text content extracted")

    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return None


def check_content_length(content: str, max_tokens: int) -> bool:
    """
    Check if content fits within the specified token limit

    Args:
        content: Text content to check
        max_tokens: Maximum allowed tokens for the target LLM

    Returns:
        True if content fits, False if too large

    Uses rough estimation of 1 token ≈ 4 characters for token counting
    """
    # Rough estimate: 1 token ≈ 4 characters
    estimated_tokens = len(content) // 4

    if estimated_tokens > max_tokens:
        print(f"❌ Content too large: ~{estimated_tokens} tokens (max: {max_tokens})")
        print("   File too big for context window")
        return False

    print(f"✅ Content size OK: ~{estimated_tokens} tokens")
    return True


def get_pdf_info(pdf_path: str) -> dict:
    """
    Get basic information about a PDF file

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with PDF metadata (pages, size, etc.)
    """
    try:
        file_size = Path(pdf_path).stat().st_size

        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)

        return {
            "file_size": file_size,
            "page_count": page_count,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        }
    except Exception as e:
        print(f"⚠️  Could not get PDF info: {e}")
        return {
            "file_size": 0,
            "page_count": 0,
            "file_size_mb": 0
        }
#!/usr/bin/env python3
"""
🛠️ Shared Utilities
Common functions used across the book processing system
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    return logging.getLogger(__name__)


def validate_file(file_path: str) -> bool:
    """Validate if file exists and is readable"""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        if not path.is_file():
            print(f"❌ Not a file: {file_path}")
            return False

        # Check if file is readable
        with open(file_path, 'rb') as f:
            f.read(1)

        return True

    except Exception as e:
        print(f"❌ Cannot read file {file_path}: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove extra spaces and replace with underscores
    sanitized = re.sub(r'\s+', '_', sanitized.strip())

    # Remove leading/trailing dots and underscores
    sanitized = sanitized.strip('._')

    # Limit length to 200 characters
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized if sanitized else 'untitled'


def estimate_file_size(pages: int) -> str:
    """Estimate file size based on page count"""
    if pages <= 3:
        return "~200-500KB"
    elif pages <= 10:
        return "~500KB-2MB"
    elif pages <= 20:
        return "~2-5MB"
    else:
        return "~5MB+"


def format_page_range(start_page: int, end_page: Optional[int]) -> str:
    """Format page range for display"""
    if end_page is None:
        return f"pages {start_page}-end"
    else:
        return f"pages {start_page}-{end_page}"


def create_directory_structure(base_path: Path, sections: list) -> None:
    """Create directory structure for organized chapter output"""
    base_path.mkdir(parents=True, exist_ok=True)

    for section in sections:
        section_dir = base_path / section
        section_dir.mkdir(exist_ok=True)
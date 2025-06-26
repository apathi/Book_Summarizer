#!/usr/bin/env python3
"""
🖼️ Image Handler
Manages image extraction, processing, and cleanup for book chapters
"""

import os
import shutil
import fitz
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .utils import sanitize_filename


class ImageHandler:
    """Handles image extraction and processing from books"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        if not PIL_AVAILABLE:
            print("⚠️  Advanced image processing requires: pip install Pillow")

    def extract_images_from_pdf_page(self, pdf_path: str, page_num: int,
                                     output_dir: Path) -> List[str]:
        """Extract all images from a specific PDF page"""

        images = []

        try:
            with fitz.open(pdf_path) as pdf:
                if page_num >= len(pdf):
                    return images

                page = pdf[page_num]
                image_list = page.get_images()

                if not image_list:
                    return images

                output_dir.mkdir(parents=True, exist_ok=True)

                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(pdf, xref)

                        # Skip if image is too small or not RGB/GRAY
                        if pix.width < 50 or pix.height < 50:
                            pix = None
                            continue

                        # Convert CMYK to RGB if needed
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                            img_path = output_dir / img_filename
                            pix.save(str(img_path))
                            images.append(str(img_path))

                            if self.verbose:
                                print(f"  📷 Extracted: {img_filename}")
                        else:  # CMYK
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                            img_path = output_dir / img_filename
                            pix1.save(str(img_path))
                            images.append(str(img_path))
                            pix1 = None

                            if self.verbose:
                                print(f"  📷 Extracted (CMYK→RGB): {img_filename}")

                        pix = None

                    except Exception as e:
                        if self.verbose:
                            print(f"  ⚠️  Could not extract image {img_index + 1}: {e}")
                        continue

                return images

        except Exception as e:
            if self.verbose:
                print(f"❌ Error extracting images from page {page_num + 1}: {e}")
            return images

    def extract_images_from_chapter(self, pdf_path: str, start_page: int,
                                    end_page: Optional[int], chapter_id: str,
                                    output_dir: Path) -> List[str]:
        """Extract all images from a chapter's page range"""

        all_images = []

        # Create chapter-specific image directory
        chapter_img_dir = output_dir / f"Chapter_{chapter_id}_images"

        try:
            with fitz.open(pdf_path) as pdf:
                # Determine page range
                if end_page is None:
                    page_range = range(start_page - 1, len(pdf))  # Convert to 0-based
                else:
                    page_range = range(start_page - 1, end_page)  # Convert to 0-based

                total_images = 0
                for page_num in page_range:
                    page_images = self.extract_images_from_pdf_page(
                        pdf_path, page_num, chapter_img_dir
                    )
                    all_images.extend(page_images)
                    total_images += len(page_images)

                if total_images > 0 and self.verbose:
                    print(f"  📷 Extracted {total_images} images for Chapter {chapter_id}")
                elif total_images == 0:
                    # Remove empty directory
                    if chapter_img_dir.exists():
                        chapter_img_dir.rmdir()

                return all_images

        except Exception as e:
            if self.verbose:
                print(f"❌ Error extracting chapter images: {e}")
            return all_images

    def optimize_image(self, image_path: str, max_width: int = 1200,
                       quality: int = 85) -> bool:
        """Optimize image size and quality"""

        if not PIL_AVAILABLE:
            return False

        try:
            with Image.open(image_path) as img:
                # Get original size
                original_size = img.size

                # Calculate new size if needed
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background

                # Save optimized image
                img.save(image_path, 'JPEG', quality=quality, optimize=True)

                if self.verbose:
                    print(f"  🔧 Optimized: {Path(image_path).name} ({original_size} → {img.size})")

                return True

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Could not optimize {Path(image_path).name}: {e}")
            return False

    def cleanup_images(self, image_dir: Path, keep_images: bool = True) -> None:
        """Clean up extracted images"""

        if not image_dir.exists():
            return

        try:
            if not keep_images:
                # Remove all images
                shutil.rmtree(image_dir)
                if self.verbose:
                    print(f"🗑️  Removed image directory: {image_dir.name}")
            else:
                # Just optimize existing images
                image_files = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
                for image_file in image_files:
                    self.optimize_image(str(image_file))

                if self.verbose and image_files:
                    print(f"🔧 Optimized {len(image_files)} images in {image_dir.name}")

        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error cleaning up images: {e}")

    def get_image_info(self, image_path: str) -> Dict:
        """Get information about an image file"""

        if not PIL_AVAILABLE:
            return {"error": "PIL not available"}

        try:
            with Image.open(image_path) as img:
                return {
                    "filename": Path(image_path).name,
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format,
                    "file_size": Path(image_path).stat().st_size
                }
        except Exception as e:
            return {"error": str(e)}

    def create_image_index(self, images: List[str], output_file: Path) -> bool:
        """Create an index of all extracted images"""

        try:
            index_content = "# Extracted Images Index\n\n"

            for image_path in images:
                image_info = self.get_image_info(image_path)
                if "error" not in image_info:
                    index_content += f"## {image_info['filename']}\n"
                    index_content += f"- Size: {image_info['size']}\n"
                    index_content += f"- Mode: {image_info['mode']}\n"
                    index_content += f"- Format: {image_info['format']}\n"
                    index_content += f"- File Size: {image_info['file_size']} bytes\n\n"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(index_content)

            return True

        except Exception as e:
            if self.verbose:
                print(f"⚠️  Could not create image index: {e}")
            return False
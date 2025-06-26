#!/usr/bin/env python3
"""
🖼️ EPUB Image Extractor
Handles extraction of images from EPUB files and updates HTML paths
"""

import re
import zipfile
from pathlib import Path
from typing import List, Tuple


class EPUBImageExtractor:
    """Handles image extraction from EPUB files"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def extract_chapter_images(self, epub_file_path: str, chapter_num: int,
                               chapter_content: str, output_dir: Path, chapter_type: str = "Chapter") -> Tuple[
        List[str], str]:
        """Extract images for a specific chapter and update HTML paths"""
        if self.verbose:
            print(f"🖼️  Extracting images for {chapter_type.lower()} {chapter_num}...")

        try:
            # Create chapter-specific image directory with proper naming
            if chapter_type == "Extra":
                chapter_images_dir = output_dir / f"Extra_{chapter_num:02d}_images"
            else:
                chapter_images_dir = output_dir / f"Chapter_{chapter_num:02d}_images"

            chapter_images_dir.mkdir(exist_ok=True)

            extracted_images = []
            updated_content = chapter_content

            # Find all image references in the chapter content
            img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
            img_matches = re.findall(img_pattern, chapter_content, re.IGNORECASE)

            if not img_matches:
                if self.verbose:
                    print(f"📷 No images found in {chapter_type.lower()} {chapter_num}")
                return extracted_images, updated_content

            if self.verbose:
                print(f"📷 Found {len(img_matches)} image references")

            # Extract images from EPUB ZIP file
            with zipfile.ZipFile(epub_file_path, 'r') as epub_zip:
                epub_files = epub_zip.namelist()

                for img_src in img_matches:
                    try:
                        # Clean the image path (remove any HTML encoding)
                        clean_img_src = img_src.strip()

                        # Find the image file in EPUB
                        matching_files = [f for f in epub_files if f.endswith(Path(clean_img_src).name)]

                        if matching_files:
                            epub_img_path = matching_files[0]
                            img_filename = Path(epub_img_path).name

                            # Extract image data
                            img_data = epub_zip.read(epub_img_path)

                            # Save to chapter image directory
                            local_img_path = chapter_images_dir / img_filename
                            with open(local_img_path, 'wb') as f:
                                f.write(img_data)

                            extracted_images.append(str(local_img_path))

                            # Update HTML content with new relative path
                            if chapter_type == "Extra":
                                new_img_src = f"Extra_{chapter_num:02d}_images/{img_filename}"
                            else:
                                new_img_src = f"Chapter_{chapter_num:02d}_images/{img_filename}"
                            updated_content = updated_content.replace(img_src, new_img_src)

                            if self.verbose:
                                print(f"✅ Extracted: {img_filename}")

                        else:
                            # Image not found - add placeholder
                            placeholder_text = f"[Image not found: {clean_img_src}]"
                            updated_content = re.sub(
                                r'<img[^>]*src=["\']' + re.escape(img_src) + r'["\'][^>]*>',
                                f'<p style="color: red; font-style: italic;">{placeholder_text}</p>',
                                updated_content,
                                flags=re.IGNORECASE
                            )
                            if self.verbose:
                                print(f"⚠️  Image not found, added placeholder: {clean_img_src}")

                    except Exception as e:
                        if self.verbose:
                            print(f"❌ Error processing image {img_src}: {e}")
                        # Add error placeholder
                        error_text = f"[Error loading image: {img_src}]"
                        updated_content = re.sub(
                            r'<img[^>]*src=["\']' + re.escape(img_src) + r'["\'][^>]*>',
                            f'<p style="color: red; font-style: italic;">{error_text}</p>',
                            updated_content,
                            flags=re.IGNORECASE
                        )

            if self.verbose:
                print(f"🖼️  {chapter_type} {chapter_num}: Extracted {len(extracted_images)} images")
            return extracted_images, updated_content

        except Exception as e:
            if self.verbose:
                print(f"❌ Error extracting images for {chapter_type.lower()} {chapter_num}: {e}")
            return [], chapter_content
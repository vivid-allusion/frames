#!/usr/bin/env python3
"""
Test script to validate TEXT SOURCE markdown parsing.
"""

from pathlib import Path
from src.processing.markdown_parser import extract_prompt_text, extract_image_url

# Test with the example files
test_files = [
    "/Users/ruben/Nextcloud/01 - PROJECTS/251230_WBT/02_GENERATIONS/251231_151521_IMG-TO-IMG-MD/ari_foldman 2/frame_0288.md",
    "/Users/ruben/Nextcloud/01 - PROJECTS/251230_WBT/02_GENERATIONS/251231_151521_IMG-TO-IMG-MD/ari_foldman 2/frame_0757.md",
    "/Users/ruben/Nextcloud/01 - PROJECTS/251230_WBT/02_GENERATIONS/251231_151521_IMG-TO-IMG-MD/ari_foldman 2/frame_1560.md",
]

print("Testing TEXT SOURCE markdown parsing...")
print("=" * 80)

for test_file in test_files:
    file_path = Path(test_file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path.name}")
        continue

    print(f"\n📄 Testing: {file_path.name}")
    print("-" * 80)

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Test image URL extraction
        image_url = extract_image_url(content)
        print(f"✅ Image URL: {image_url}")

        # Test prompt text extraction
        prompt_text = extract_prompt_text(content)
        print(f"✅ Prompt Text: {prompt_text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
print("Test complete!")

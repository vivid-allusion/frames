#!/usr/bin/env python3
"""
Test script to validate TEXT SOURCE markdown validation.
"""

from pathlib import Path
from src.processing.validator import GenericValidator
from src.exceptions import ValidationError

# Test with the example files
test_dir = Path(
    "/Users/ruben/Nextcloud/01 - PROJECTS/251230_WBT/02_GENERATIONS/251231_151521_IMG-TO-IMG-MD/ari_foldman 2"
)

# Get all markdown files
md_files = list(test_dir.glob("*.md"))[:5]  # Test first 5 files

# Create tuples of (absolute_path, relative_path) as expected by validator
prompt_files = [(f, f.relative_to(test_dir)) for f in md_files]

print("Testing TEXT SOURCE markdown validation...")
print(f"Found {len(prompt_files)} markdown files to validate")
print("=" * 80)

validator = GenericValidator()

try:
    validator.validate_markdown_files(prompt_files)
    print("\n✅ All files passed validation!")
except ValidationError as e:
    print(f"\n❌ Validation failed:\n{e}")

print("\n" + "=" * 80)

# Test with a malformed markdown (missing TEXT SOURCE)
print("\nTesting malformed markdown detection...")
print("-" * 80)

malformed_content = """# Test File

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

This is some text but no TEXT SOURCE line.
"""

# Write temporary test file
temp_file = Path("/tmp/test_malformed.md")
temp_file.write_text(malformed_content)

try:
    validator._validate_single_markdown(temp_file, Path("test_malformed.md"))
    print("❌ Should have failed for missing TEXT SOURCE")
except ValidationError as e:
    print(f"✅ Correctly rejected malformed file: {e}")
finally:
    temp_file.unlink()

# Test with empty TEXT SOURCE
print("\nTesting empty TEXT SOURCE detection...")
print("-" * 80)

empty_content = """# Test File

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:

"""

temp_file = Path("/tmp/test_empty.md")
temp_file.write_text(empty_content)

try:
    validator._validate_single_markdown(temp_file, Path("test_empty.md"))
    print("❌ Should have failed for empty TEXT SOURCE")
except ValidationError as e:
    print(f"✅ Correctly rejected empty TEXT SOURCE: {e}")
finally:
    temp_file.unlink()

print("\n" + "=" * 80)
print("Validation tests complete!")

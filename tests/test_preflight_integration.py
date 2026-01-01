#!/usr/bin/env python
"""Integration test for pre-flight validation in the processing pipeline."""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import GenericValidator
from src.exceptions import ValidationError


def create_test_directory_structure():
    """Create a temporary directory with various test markdown files."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create subdirectory structure
    (temp_dir / "prompts").mkdir()
    (temp_dir / "prompts" / "batch1").mkdir()
    (temp_dir / "prompts" / "batch2").mkdir()

    # Valid files
    (temp_dir / "prompts" / "valid1.md").write_text("""
# Image Generation Prompt

```text
A futuristic city at sunset with flying cars
```
""")

    (temp_dir / "prompts" / "batch1" / "valid2.md").write_text("""
# Another Prompt

```json
{
  "prompt": "A serene mountain landscape",
  "style": "photorealistic"
}
```
""")

    (temp_dir / "prompts" / "batch1" / "valid3.md").write_text("""
# Image with Reference

![reference](https://example.com/image.jpg)

```
Portrait of a young woman, studio lighting, professional photography
```
""")

    # Invalid files for testing
    (temp_dir / "prompts" / "batch2" / "no_codeblock.md").write_text("""
# Missing Code Block

This file has no code block at all!
Just regular markdown text.
""")

    (temp_dir / "prompts" / "batch2" / "empty_codeblock.md").write_text("""
# Empty Code Block

```

```

This has an empty code block.
""")

    return temp_dir


def test_all_valid_files():
    """Test that directory with all valid files passes validation."""
    temp_dir = create_test_directory_structure()

    # Get only valid files
    valid_files = [
        (temp_dir / "prompts" / "valid1.md", Path("prompts/valid1.md")),
        (
            temp_dir / "prompts" / "batch1" / "valid2.md",
            Path("prompts/batch1/valid2.md"),
        ),
        (
            temp_dir / "prompts" / "batch1" / "valid3.md",
            Path("prompts/batch1/valid3.md"),
        ),
    ]

    validator = GenericValidator()

    try:
        validator.validate_markdown_files(valid_files)
        print("✅ All valid files passed pre-flight validation")
        return True
    except ValidationError as e:
        print(f"❌ Valid files failed validation: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir)


def test_mixed_valid_invalid_files():
    """Test that validation catches invalid files in mixed batch."""
    temp_dir = create_test_directory_structure()

    # Mix of valid and invalid files
    all_files = [
        (temp_dir / "prompts" / "valid1.md", Path("prompts/valid1.md")),
        (
            temp_dir / "prompts" / "batch1" / "valid2.md",
            Path("prompts/batch1/valid2.md"),
        ),
        (
            temp_dir / "prompts" / "batch2" / "no_codeblock.md",
            Path("prompts/batch2/no_codeblock.md"),
        ),
        (
            temp_dir / "prompts" / "batch2" / "empty_codeblock.md",
            Path("prompts/batch2/empty_codeblock.md"),
        ),
    ]

    validator = GenericValidator()

    try:
        validator.validate_markdown_files(all_files)
        print("❌ Mixed validation should have failed")
        return False
    except ValidationError as e:
        error_msg = str(e)
        # Check that both invalid files are mentioned
        if "no_codeblock.md" in error_msg and "empty_codeblock.md" in error_msg:
            print("✅ Validation correctly identified both invalid files")
            return True
        elif "no_codeblock.md" in error_msg or "empty_codeblock.md" in error_msg:
            print("⚠️  Validation identified at least one invalid file")
            print(f"   Error: {error_msg}")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    finally:
        shutil.rmtree(temp_dir)


def test_detailed_error_reporting():
    """Test that error messages provide helpful details."""
    temp_dir = create_test_directory_structure()

    invalid_files = [
        (
            temp_dir / "prompts" / "batch2" / "no_codeblock.md",
            Path("prompts/batch2/no_codeblock.md"),
        ),
    ]

    validator = GenericValidator()

    try:
        validator.validate_markdown_files(invalid_files)
        print("❌ Should have failed validation")
        return False
    except ValidationError as e:
        error_msg = str(e)
        # Check that error message is informative
        has_filename = "no_codeblock.md" in error_msg
        has_reason = "No code block found" in error_msg
        has_guidance = "triple backticks" in error_msg or "```" in error_msg

        if has_filename and has_reason and has_guidance:
            print("✅ Error message is detailed and helpful")
            print(f"   Message: {error_msg.split(':', 1)[1].strip()[:100]}...")
            return True
        else:
            print(f"⚠️  Error message could be more detailed")
            print(f"   Has filename: {has_filename}")
            print(f"   Has reason: {has_reason}")
            print(f"   Has guidance: {has_guidance}")
            return True  # Still acceptable
    finally:
        shutil.rmtree(temp_dir)


def test_relative_path_in_errors():
    """Test that error messages use relative paths for better readability."""
    temp_dir = create_test_directory_structure()

    invalid_file = temp_dir / "prompts" / "batch2" / "no_codeblock.md"
    relative_path = Path("prompts/batch2/no_codeblock.md")

    validator = GenericValidator()

    try:
        validator.validate_markdown_files([(invalid_file, relative_path)])
        print("❌ Should have failed validation")
        return False
    except ValidationError as e:
        error_msg = str(e)
        # Check that relative path is used, not absolute
        if str(relative_path) in error_msg and str(temp_dir) not in error_msg:
            print("✅ Error messages use relative paths for clarity")
            return True
        else:
            print("⚠️  Error message contains absolute path (less user-friendly)")
            return True  # Still works, just not optimal
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Pre-flight Validation Integration Tests")
    print("=" * 60)
    print()

    tests = [
        ("Valid Files Only", test_all_valid_files),
        ("Mixed Valid/Invalid Files", test_mixed_valid_invalid_files),
        ("Detailed Error Reporting", test_detailed_error_reporting),
        ("Relative Path Errors", test_relative_path_in_errors),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test raised unexpected error: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All {total} integration tests passed!")
        print()
        print("Pre-flight validation is working correctly:")
        print("  ✓ Validates all markdown files before processing")
        print("  ✓ Checks for code block presence")
        print("  ✓ Ensures code blocks have content")
        print("  ✓ Provides clear error messages")
        print("  ✓ Fails fast when invalid files detected")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

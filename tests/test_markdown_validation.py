#!/usr/bin/env python
"""Unit tests for markdown pre-flight validation with TEXT SOURCE format."""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import GenericValidator
from src.exceptions import ValidationError


def create_test_file(content: str, filename: str = "test.md") -> Path:
    """Create a temporary markdown file with given content."""
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / filename
    test_file.write_text(content)
    return test_file


def test_valid_markdown_with_content():
    """Test that valid markdown with TEXT SOURCE passes validation."""
    content = """# Test Markdown

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:

This is a valid prompt text
"""
    test_file = create_test_file(content)
    validator = GenericValidator()

    try:
        # Should not raise any exception
        validator.validate_markdown_files([(test_file, Path("test.md"))])
        print("✅ Valid markdown with TEXT SOURCE passed validation")
        return True
    except ValidationError as e:
        print(f"❌ Valid markdown failed validation: {e}")
        return False
    finally:
        shutil.rmtree(test_file.parent)


def test_markdown_without_text_source():
    """Test that markdown without TEXT SOURCE fails validation."""
    content = """# Test Markdown

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

This is just regular text without TEXT SOURCE marker.
"""
    test_file = create_test_file(content)
    validator = GenericValidator()

    try:
        validator.validate_markdown_files([(test_file, Path("test.md"))])
        print("❌ Markdown without TEXT SOURCE should have failed validation")
        return False
    except ValidationError as e:
        if "No TEXT SOURCE" in str(e):
            print("✅ Markdown without TEXT SOURCE correctly rejected")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    finally:
        shutil.rmtree(test_file.parent)


def test_markdown_with_empty_text_source():
    """Test that markdown with empty TEXT SOURCE fails validation."""
    content = """# Test Markdown

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:

"""
    test_file = create_test_file(content)
    validator = GenericValidator()

    try:
        validator.validate_markdown_files([(test_file, Path("test.md"))])
        print("❌ Markdown with empty TEXT SOURCE should have failed validation")
        return False
    except ValidationError as e:
        if "empty" in str(e).lower():
            print("✅ Markdown with empty TEXT SOURCE correctly rejected")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    finally:
        shutil.rmtree(test_file.parent)


def test_markdown_with_multiline_text():
    """Test that markdown with multi-line TEXT SOURCE passes validation."""
    content = """# Test Markdown

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:

This is a multi-line prompt.
It has multiple lines of text.
And that's perfectly valid.
"""
    test_file = create_test_file(content)
    validator = GenericValidator()

    try:
        validator.validate_markdown_files([(test_file, Path("test.md"))])
        print("✅ Markdown with multi-line TEXT SOURCE passed validation")
        return True
    except ValidationError as e:
        print(f"❌ Markdown with multi-line text failed validation: {e}")
        return False
    finally:
        shutil.rmtree(test_file.parent)


def test_multiple_files_batch_validation():
    """Test validation of multiple files at once."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create valid file
    valid_file = temp_dir / "valid.md"
    valid_file.write_text("**TEXT SOURCE:** test.txt:\n\nValid content")

    # Create invalid file
    invalid_file = temp_dir / "invalid.md"
    invalid_file.write_text("No TEXT SOURCE here")

    validator = GenericValidator()

    try:
        validator.validate_markdown_files(
            [(valid_file, Path("valid.md")), (invalid_file, Path("invalid.md"))]
        )
        print("❌ Batch validation should have failed with one invalid file")
        return False
    except ValidationError as e:
        error_msg = str(e)
        if "invalid.md" in error_msg and "No TEXT SOURCE" in error_msg:
            print("✅ Batch validation correctly identified invalid file")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    finally:
        shutil.rmtree(temp_dir)


def test_markdown_with_whitespace_only():
    """Test that TEXT SOURCE with only whitespace fails validation."""
    content = """# Test Markdown

**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:
   
   
"""
    test_file = create_test_file(content)
    validator = GenericValidator()

    try:
        validator.validate_markdown_files([(test_file, Path("test.md"))])
        print("❌ Markdown with whitespace-only TEXT SOURCE should have failed")
        return False
    except ValidationError as e:
        if "empty" in str(e).lower():
            print("✅ Whitespace-only TEXT SOURCE correctly rejected")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    finally:
        shutil.rmtree(test_file.parent)


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Markdown Pre-flight Validation Tests")
    print("=" * 60)

    tests = [
        test_valid_markdown_with_content,
        test_markdown_without_text_source,
        test_markdown_with_empty_text_source,
        test_markdown_with_multiline_text,
        test_multiple_files_batch_validation,
        test_markdown_with_whitespace_only,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} raised unexpected error: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All {total} tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

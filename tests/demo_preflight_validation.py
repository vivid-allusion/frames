#!/usr/bin/env python
"""
Demonstration of pre-flight validation feature.

This script shows how the pre-flight validation catches invalid markdown files
before any API calls are made, saving time and preventing errors.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import GenericValidator
from src.exceptions import ValidationError


def demo_scenario_1():
    """Scenario 1: All files are valid - processing would continue."""
    print("\n" + "=" * 70)
    print("SCENARIO 1: All markdown files are valid")
    print("=" * 70)

    temp_dir = Path(tempfile.mkdtemp())

    # Create valid markdown files
    files = []
    for i in range(1, 4):
        md_file = temp_dir / f"prompt_{i}.md"
        md_file.write_text(f"""
# Image Generation Request {i}

```text
Generate a beautiful landscape photo with mountains and lakes
```
""")
        files.append((md_file, Path(f"prompt_{i}.md")))

    validator = GenericValidator()

    try:
        print(f"\n📂 Checking {len(files)} markdown files...")
        validator.validate_markdown_files(files)
        print("\n✅ RESULT: Pre-flight validation PASSED")
        print("   → Processing would continue to API calls")
    except ValidationError as e:
        print(f"\n❌ RESULT: Validation failed: {e}")
    finally:
        shutil.rmtree(temp_dir)


def demo_scenario_2():
    """Scenario 2: Some files are invalid - processing stops immediately."""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Invalid files detected (missing code blocks)")
    print("=" * 70)

    temp_dir = Path(tempfile.mkdtemp())

    # Create mixed valid/invalid files
    valid1 = temp_dir / "valid_prompt_1.md"
    valid1.write_text("""
# Valid Prompt

```text
A sunset over the ocean
```
""")

    invalid1 = temp_dir / "invalid_no_codeblock.md"
    invalid1.write_text("""
# Oops, forgot the code block!

Just some text here, but no triple backticks.
This will be caught by pre-flight validation.
""")

    valid2 = temp_dir / "valid_prompt_2.md"
    valid2.write_text("""
# Another Valid Prompt

```json
{
  "prompt": "A futuristic city",
  "style": "cyberpunk"
}
```
""")

    invalid2 = temp_dir / "invalid_empty_codeblock.md"
    invalid2.write_text("""
# Empty Code Block Problem

```

```
""")

    files = [
        (valid1, Path("valid_prompt_1.md")),
        (invalid1, Path("invalid_no_codeblock.md")),
        (valid2, Path("valid_prompt_2.md")),
        (invalid2, Path("invalid_empty_codeblock.md")),
    ]

    validator = GenericValidator()

    try:
        print(f"\n📂 Checking {len(files)} markdown files...")
        validator.validate_markdown_files(files)
        print("\n✅ RESULT: All files valid")
    except ValidationError as e:
        print("\n❌ RESULT: Pre-flight validation FAILED")
        print("\n📋 Validation Error Details:")
        print("-" * 70)
        print(str(e))
        print("-" * 70)
        print("\n💡 BENEFIT: Processing stopped BEFORE making any API calls!")
        print("   • No API costs incurred for invalid inputs")
        print("   • No time wasted processing valid files only to fail later")
        print("   • Clear error messages help fix issues quickly")
    finally:
        shutil.rmtree(temp_dir)


def demo_scenario_3():
    """Scenario 3: Show what validation accepts."""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Various valid code block formats")
    print("=" * 70)

    temp_dir = Path(tempfile.mkdtemp())

    # Different valid formats
    examples = [
        (
            "text_format.md",
            """
```text
Simple text prompt
```
""",
        ),
        (
            "json_format.md",
            """
```json
{"prompt": "JSON payload", "param": "value"}
```
""",
        ),
        (
            "no_language.md",
            """
```
Code block without language specifier
```
""",
        ),
        (
            "with_image.md",
            """
![reference](https://example.com/ref.jpg)

```
Text prompt with image reference above
```
""",
        ),
        (
            "multiline.md",
            """
```text
This is a longer prompt
that spans multiple lines
and includes various details
```
""",
        ),
    ]

    files = []
    for filename, content in examples:
        md_file = temp_dir / filename
        md_file.write_text(content)
        files.append((md_file, Path(filename)))

    validator = GenericValidator()

    print(f"\n📂 Testing {len(files)} different markdown formats...")
    print("\nAccepted formats:")
    for filename, _ in examples:
        print(f"  • {filename}")

    try:
        validator.validate_markdown_files(files)
        print("\n✅ RESULT: All formats accepted!")
        print("\n📝 Summary of accepted code block formats:")
        print("  • ```text ... ```")
        print("  • ```json ... ```")
        print("  • ``` ... ``` (no language)")
        print("  • With or without image references")
        print("  • Single or multi-line content")
    except ValidationError as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all demonstration scenarios."""
    print("\n" + "=" * 70)
    print("PRE-FLIGHT MARKDOWN VALIDATION - FEATURE DEMONSTRATION")
    print("=" * 70)
    print("\nThis feature validates all markdown files BEFORE processing begins.")
    print("Benefits:")
    print("  1. Fail-fast: Catch errors before making API calls")
    print("  2. Cost savings: Don't waste API credits on invalid inputs")
    print("  3. Time savings: Don't process valid files only to fail later")
    print("  4. Clear errors: Know exactly which files need fixing")

    # Run all scenarios
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n🎯 Key Takeaway:")
    print("   Pre-flight validation ensures all markdown files are properly")
    print("   formatted before any processing begins, preventing wasted API")
    print("   calls and providing clear feedback for fixing issues.")
    print()


if __name__ == "__main__":
    main()

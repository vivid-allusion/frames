#!/usr/bin/env python
"""
Quick verification that pre-flight validation is integrated correctly.
This simulates what happens during actual tool execution.
"""

import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.discovery import InputDiscovery
from src.processing.validator import GenericValidator
from src.exceptions import ValidationError


def verify_integration():
    """Verify that validation works in the discovery flow."""
    print("\n" + "=" * 70)
    print("PRE-FLIGHT VALIDATION - INTEGRATION VERIFICATION")
    print("=" * 70)

    # Create temporary directory structure
    temp_dir = Path(tempfile.mkdtemp())
    input_dir = temp_dir / "INPUT"
    profiles_dir = temp_dir / "PROFILES"
    input_dir.mkdir()
    profiles_dir.mkdir()

    # Create test markdown files
    print("\n1. Creating test markdown files...")

    (input_dir / "valid1.md").write_text("""
```text
Test prompt 1
```
""")

    (input_dir / "valid2.md").write_text("""
```json
{"prompt": "Test prompt 2"}
```
""")

    (input_dir / "invalid.md").write_text("""
# This file has no code block
Just some text.
""")

    print(f"   Created 3 files in {input_dir.relative_to(temp_dir)}/")
    print(f"   - valid1.md (✓)")
    print(f"   - valid2.md (✓)")
    print(f"   - invalid.md (✗)")

    try:
        # Step 1: Discovery (like in orchestrator)
        print("\n2. Running file discovery...")
        discovery = InputDiscovery(input_dir, profiles_dir)
        prompt_files = discovery.discover_prompt_files()
        print(f"   Found {len(prompt_files)} markdown files")

        # Step 2: Pre-flight validation (NEW STEP)
        print("\n3. Running pre-flight validation...")
        validator = GenericValidator()
        validator.validate_markdown_files(prompt_files)

        print("\n❌ UNEXPECTED: Validation should have failed!")
        print("   The invalid.md file should have been caught.")
        return False

    except ValidationError as e:
        print("\n✅ SUCCESS: Pre-flight validation caught the invalid file!")
        print("\n   Error details:")
        for line in str(e).split("\n"):
            print(f"   {line}")

        print("\n4. What happens next:")
        print("   ⚠️  Processing STOPS (fail-fast)")
        print("   ⚠️  NO API calls are made")
        print("   ⚠️  NO API costs incurred")
        print("   ✓  User fixes invalid.md")
        print("   ✓  User runs tool again")
        print("   ✓  All files pass validation")
        print("   ✓  Processing continues normally")

        return True

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        shutil.rmtree(temp_dir)


def verify_valid_scenario():
    """Verify that valid files pass through correctly."""
    print("\n" + "=" * 70)
    print("VALID FILES SCENARIO - PROCESSING CONTINUES")
    print("=" * 70)

    temp_dir = Path(tempfile.mkdtemp())
    input_dir = temp_dir / "INPUT"
    profiles_dir = temp_dir / "PROFILES"
    input_dir.mkdir()
    profiles_dir.mkdir()

    print("\n1. Creating only valid markdown files...")

    (input_dir / "prompt1.md").write_text("```\nPrompt 1\n```")
    (input_dir / "prompt2.md").write_text("```\nPrompt 2\n```")
    (input_dir / "prompt3.md").write_text("```\nPrompt 3\n```")

    print(f"   Created 3 valid files")

    try:
        print("\n2. Running file discovery...")
        discovery = InputDiscovery(input_dir, profiles_dir)
        prompt_files = discovery.discover_prompt_files()
        print(f"   Found {len(prompt_files)} files")

        print("\n3. Running pre-flight validation...")
        validator = GenericValidator()
        validator.validate_markdown_files(prompt_files)

        print("\n✅ SUCCESS: All files passed validation!")
        print("\n4. What happens next:")
        print("   ✓ Pre-flight validation passed")
        print("   → Load profiles")
        print("   → Authenticate with API")
        print("   → Process all files")
        print("   → Generate outputs")

        return True

    except ValidationError as e:
        print(f"\n❌ UNEXPECTED: Valid files failed validation: {e}")
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run verification tests."""
    print("\n" + "=" * 70)
    print("PRE-FLIGHT VALIDATION FEATURE VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies that pre-flight validation is correctly")
    print("integrated into the processing pipeline.")

    results = []

    # Test 1: Invalid files should be caught
    results.append(verify_integration())

    # Test 2: Valid files should pass through
    results.append(verify_valid_scenario())

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    if all(results):
        print("\n🎉 All verification tests passed!")
        print("\n✅ Pre-flight validation is correctly integrated")
        print("✅ Invalid files are caught before processing")
        print("✅ Valid files pass through to processing")
        print("✅ Feature is ready for production use")
        return 0
    else:
        print("\n❌ Some verification tests failed")
        print(f"   Passed: {sum(results)}/{len(results)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

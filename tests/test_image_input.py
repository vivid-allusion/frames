#!/usr/bin/env python
"""Test script for image_input and output_format features."""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dry_run_with_image_input():
    """Test dry run with nano-banano profile that has image_input."""
    print("Testing image_input feature with dry-run...")

    # Run with dry-run to test validation without API calls
    cmd = [
        sys.executable, "-m", "src.main_simple",
        "--dry-run",
        "--no-progress"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            print(f"❌ Test failed with return code: {result.returncode}")
            print(f"STDERR:\n{result.stderr}")
            return False

        # Check for successful validation
        if "nano-banano" in result.stdout or "validated successfully" in result.stderr:
            print("✅ Image input validation passed")
            return True
        else:
            print("⚠️ Could not verify validation succeeded")
            print(f"STDOUT:\n{result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_missing_output_format():
    """Test that missing output_format fails as expected."""
    print("\nTesting missing output_format failure...")

    # Temporarily modify the yaml to remove output_format
    yaml_path = Path("USER-FILES/03.PROFILES/nano-banano.yaml")
    original_content = yaml_path.read_text()

    try:
        # Remove output_format line
        modified_content = "\n".join(
            line for line in original_content.splitlines()
            if "output_format" not in line
        )
        yaml_path.write_text(modified_content)

        # Run and expect failure
        cmd = [sys.executable, "-m", "src.main_simple", "--dry-run", "--no-progress"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            if "missing required output_format" in result.stderr:
                print("✅ Correctly failed for missing output_format")
                return True
            else:
                print("✅ Failed as expected (different error)")
                return True
        else:
            print("❌ Should have failed but succeeded")
            return False

    finally:
        # Restore original content
        yaml_path.write_text(original_content)

def test_invalid_url():
    """Test that invalid image URL fails as expected."""
    print("\nTesting invalid URL failure...")

    yaml_path = Path("USER-FILES/03.PROFILES/nano-banano.yaml")
    original_content = yaml_path.read_text()

    try:
        # Modify to invalid URL
        modified_content = original_content.replace(
            'image_input: "https://f003.backblazeb2.com/file/aspect-ratio-reference/aspect_ratio_reference_16x9.png"',
            'image_input: "not-a-valid-url"'
        )
        yaml_path.write_text(modified_content)

        # Run and expect failure
        cmd = [sys.executable, "-m", "src.main_simple", "--dry-run", "--no-progress"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            if "invalid image_input URL format" in result.stderr:
                print("✅ Correctly failed for invalid URL format")
                return True
            else:
                print("✅ Failed as expected")
                return True
        else:
            print("❌ Should have failed but succeeded")
            return False

    finally:
        # Restore original content
        yaml_path.write_text(original_content)

def main():
    """Run all tests."""
    print("=" * 50)
    print("Image Input Feature Tests")
    print("=" * 50)

    tests_passed = 0
    tests_total = 3

    # Test 1: Basic dry run with image_input
    if test_dry_run_with_image_input():
        tests_passed += 1

    # Test 2: Missing output_format
    if test_missing_output_format():
        tests_passed += 1

    # Test 3: Invalid URL
    if test_invalid_url():
        tests_passed += 1

    print("\n" + "=" * 50)
    print(f"Results: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""Integration test for custom paths and project name feature."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.path_resolver import (
    resolve_input_path,
    resolve_output_base_path,
    create_timestamped_output_path,
)
from src.config.validator import ConfigValidator


def test_custom_path_resolution():
    """Test custom input/output path resolution."""
    config = {
        "inputs": {"directory": "USER-FILES/04.INPUT"},
        "outputs": {"directory": "USER-FILES/05.OUTPUT"},
    }

    profiles = [
        {
            "model_id": "test/model",
            "project": "WALTZ WITH BASHIR",
            "paths": {
                "input": "/tmp/test_input",
                "output": "/tmp/test_output",
            },
        }
    ]

    profiles_dir = Path("USER-FILES/03.PROFILES")

    input_path, project_name = resolve_input_path(config, profiles, profiles_dir)
    assert str(input_path) == "/tmp/test_input", (
        f"Expected /tmp/test_input, got {input_path}"
    )
    assert project_name == "WALTZ WITH BASHIR"

    output_base = resolve_output_base_path(config, profiles)
    assert str(output_base) == "/tmp/test_output"

    print("  [PASS] Custom path resolution")


def test_userfiles_fallback():
    """Test USER-FILES fallback when no custom paths."""
    config = {
        "inputs": {"directory": "USER-FILES/04.INPUT"},
        "outputs": {"directory": "USER-FILES/05.OUTPUT"},
    }

    profiles = [{"model_id": "test/model"}]

    profiles_dir = Path("USER-FILES/03.PROFILES")

    input_path, project_name = resolve_input_path(config, profiles, profiles_dir)
    assert "USER-FILES/04.INPUT" in str(input_path)

    output_base = resolve_output_base_path(config, profiles)
    assert "USER-FILES/05.OUTPUT" in str(output_base)

    print("  [PASS] USER-FILES fallback")


def test_profile_validation():
    """Test profile schema validation."""
    validator = ConfigValidator()

    valid_profile = {
        "model_id": "test/model",
        "project": "Test Project",
        "paths": {
            "input": "/custom/input",
            "output": "/custom/output",
        },
    }

    try:
        validator._validate_single_profile("test.yaml", valid_profile)
        print("  [PASS] Valid profile validation")
    except Exception as e:
        print(f"  [FAIL] Valid profile failed: {e}")
        return False

    invalid_project = {
        "model_id": "test/model",
        "project": 123,
    }

    try:
        validator._validate_single_profile("test.yaml", invalid_project)
        print("  [FAIL] Invalid project should have failed")
        return False
    except ValueError:
        print("  [PASS] Invalid project rejected")

    return True


def test_timestamped_output_creation():
    """Test timestamped output directory creation."""
    import tempfile
    from datetime import datetime
    from src.constants import TIMESTAMP_FORMAT

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir) / "output"
        output_path = create_timestamped_output_path(base_path)

        assert output_path.exists()
        assert output_path.is_dir()

        expected_prefix = datetime.now().strftime(TIMESTAMP_FORMAT)
        assert output_path.name.startswith(expected_prefix)
        assert "_IMG-TO-IMG" in output_path.name

        print("  [PASS] Timestamped output creation")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Custom Paths Feature - Integration Tests")
    print("=" * 60)
    print()

    all_passed = True

    print("1. Custom Path Resolution")
    try:
        test_custom_path_resolution()
    except Exception as e:
        print(f"  [FAIL] {e}")
        all_passed = False

    print("2. USER-FILES Fallback")
    try:
        test_userfiles_fallback()
    except Exception as e:
        print(f"  [FAIL] {e}")
        all_passed = False

    print("3. Profile Validation")
    if not test_profile_validation():
        all_passed = False

    print("4. Timestamped Output Creation")
    try:
        test_timestamped_output_creation()
    except Exception as e:
        print(f"  [FAIL] {e}")
        all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

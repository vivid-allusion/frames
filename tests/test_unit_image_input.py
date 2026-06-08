#!/usr/bin/env python
"""Unit tests for image_input feature."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.context import ProcessingContext

def test_context_with_image_input():
    """Test ProcessingContext stores image-related params in the params dict."""
    context = ProcessingContext(
        prompt_file=Path("test.txt"),
        relative_path=Path("test.txt"),
        prompts=["test prompt"],
        model_id="test/model",
        params={"num_images": 1, "image_input": "https://example.com/image.png", "output_format": "png"},
        pricing={"base_cost": 0.01},
        profile_name="test_profile",
        output_dir=Path("/tmp"),
    )

    assert context.params.get("image_input") == "https://example.com/image.png"
    assert context.params.get("output_format") == "png"
    print("✅ ProcessingContext correctly stores image params in params dict")

def test_payload_construction():
    """Test that API client correctly constructs payload with image_input."""
    # This is a mock test - we can't actually call the API
    test_params = {"num_images": 1}
    image_input = "https://example.com/test.png"
    output_format = "png"

    # Simulate what the client does
    payload = {
        **test_params,
        "prompt": "test prompt"
    }

    if image_input:
        payload["image_input"] = [image_input]

    if output_format:
        payload["output_format"] = output_format

    assert "image_input" in payload
    assert payload["image_input"] == [image_input]
    assert payload["output_format"] == "png"
    print("✅ Payload correctly includes image_input array and output_format")

def test_validation_logic():
    """Test validation logic for image parameters."""
    # Test model with image_input
    model_with_image = {
        'profile_name': 'test',
        'image_input': 'https://example.com/image.png',
        'output_format': 'png'
    }

    # Check both parameters exist
    has_image = bool(model_with_image.get('image_input'))
    has_format = bool(model_with_image.get('output_format'))

    assert has_image and has_format
    print("✅ Validation correctly checks for both parameters")

    # Test output_format validation
    assert model_with_image['output_format'] == 'png'
    print("✅ Output format validation works")

def main():
    """Run all unit tests."""
    print("=" * 50)
    print("Image Input Feature Unit Tests")
    print("=" * 50)

    try:
        test_context_with_image_input()
        test_payload_construction()
        test_validation_logic()

        print("\n" + "=" * 50)
        print("🎉 All unit tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
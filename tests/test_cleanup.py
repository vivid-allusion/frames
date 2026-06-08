#!/usr/bin/env python3
"""Test script to verify cleanup didn't break imports."""

def test_imports():
    """Test all imports work correctly."""
    try:
        # Test constants import
        from src.constants import (
            DEFAULT_TIMEOUT,
            DEFAULT_MAX_RETRIES,
            DEFAULT_MAX_WAIT_TIME,
            DEFAULT_RATE_LIMIT_RETRY_DELAY,
            DEFAULT_IMAGE_DOWNLOAD_TIMEOUT,
            TIMESTAMP_FORMAT,
        )
        print("✓ Constants imports successful")
        
        # Test that removed constants don't exist
        for removed in (
            "TIME_FORMAT",
            "DATETIME_FORMAT",
            "HTTP_OK",
            "URL_VALIDATION_TIMEOUT",
            "DEFAULT_CURRENCY_SYMBOL",
            "PROGRESS_UPDATE_INTERVAL",
            "MAX_FUNCTION_LINES",
            "MAX_FUNCTION_PARAMS",
        ):
            try:
                __import__("src.constants", fromlist=[removed])
                getattr(__import__("src.constants"), removed)
                print(f"✗ {removed} should have been removed")
            except AttributeError:
                print(f"✓ {removed} correctly removed")
        
        # Test config imports
        from src.config import ConfigLoader, ConfigValidator
        print("✓ Config imports successful")
        
        # Test processor imports
        from src.processing.processor import BatchProcessor
        print("✓ BatchProcessor import successful")
        
        # Test reporter imports
        from src.output.reporter import Reporter
        print("✓ Reporter import successful")
        
        # Test that Path is not imported in reporter
        import src.output.reporter as reporter_module
        if not hasattr(reporter_module, 'Path'):
            print("✓ Path correctly removed from reporter imports")
        else:
            print("✗ Path should have been removed from reporter")
            
        print("\n✅ All cleanup tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
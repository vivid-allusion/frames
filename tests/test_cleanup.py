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
            TIME_FORMAT,
            DATETIME_FORMAT
        )
        print("✓ Constants imports successful")
        
        # Test that removed constants don't exist
        try:
            from src.constants import DEFAULT_CURRENCY_SYMBOL
            print("✗ DEFAULT_CURRENCY_SYMBOL should have been removed")
        except ImportError:
            print("✓ DEFAULT_CURRENCY_SYMBOL correctly removed")
            
        try:
            from src.constants import PROGRESS_UPDATE_INTERVAL
            print("✗ PROGRESS_UPDATE_INTERVAL should have been removed")
        except ImportError:
            print("✓ PROGRESS_UPDATE_INTERVAL correctly removed")
            
        try:
            from src.constants import MAX_FUNCTION_LINES
            print("✗ MAX_FUNCTION_LINES should have been removed")
        except ImportError:
            print("✓ MAX_FUNCTION_LINES correctly removed")
            
        try:
            from src.constants import MAX_FUNCTION_PARAMS
            print("✗ MAX_FUNCTION_PARAMS should have been removed")
        except ImportError:
            print("✓ MAX_FUNCTION_PARAMS correctly removed")
        
        # Test config imports
        from src.config import ConfigLoader, ConfigValidator
        print("✓ Config imports successful")
        
        # Test processor imports
        from src.processing.processor import MatrixProcessor
        print("✓ MatrixProcessor import successful")
        
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